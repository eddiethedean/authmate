"""The phase 0.1 authorization service facade."""

from __future__ import annotations

import asyncio
import math
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import TypeVar

from pydantic import ValidationError

from .errors import (
    AuthMateClosedError,
    AuthMateUnavailableError,
    AuthorizationDeniedError,
    InvalidAuthorizationRequestError,
)
from .models import (
    AccessContext,
    AuthorizationDecision,
    DecisionReason,
    PrincipalRecord,
    ResourceRef,
    validate_action,
)
from .protocols import AuthorizationProvider, PrincipalProvider

T = TypeVar("T")


class AuthMate:
    """Authorize direct, non-HTTP calls through one provider-neutral service path."""

    def __init__(
        self,
        *,
        principal_provider: PrincipalProvider,
        authorization_provider: AuthorizationProvider,
        provider_timeout_seconds: float = 5.0,
    ) -> None:
        if isinstance(provider_timeout_seconds, bool) or not isinstance(
            provider_timeout_seconds, (int, float)
        ):
            raise ValueError("provider timeout must be a finite number")
        if not math.isfinite(float(provider_timeout_seconds)) or not (
            0.01 <= float(provider_timeout_seconds) <= 60.0
        ):
            raise ValueError("provider timeout must be between 0.01 and 60 seconds")
        self._principal_provider = principal_provider
        self._authorization_provider = authorization_provider
        self._timeout = float(provider_timeout_seconds)
        self._condition = asyncio.Condition()
        self._state = "open"
        self._in_flight = 0
        self._shutdown_task: asyncio.Task[None] | None = None

    async def authorize(
        self,
        *,
        context: AccessContext,
        action: str,
        resource: ResourceRef | None = None,
    ) -> AuthorizationDecision:
        """Return a single authorization decision and never turn failure into allow."""

        await self._enter_operation()
        try:
            return await self._authorize_inner(context=context, action=action, resource=resource)
        finally:
            await self._exit_operation()

    async def can(
        self,
        *,
        context: AccessContext,
        action: str,
        resource: ResourceRef | None = None,
    ) -> bool:
        """Return only whether the current request is allowed."""

        decision = await self.authorize(context=context, action=action, resource=resource)
        return decision.allowed

    async def require(
        self,
        *,
        context: AccessContext,
        action: str,
        resource: ResourceRef | None = None,
    ) -> AuthorizationDecision:
        """Return an allow decision or raise a sanitized domain error."""

        decision = await self.authorize(context=context, action=action, resource=resource)
        if decision.allowed:
            return decision
        if decision.reason in {
            DecisionReason.PROVIDER_UNAVAILABLE,
            DecisionReason.PROVIDER_CONTRACT_VIOLATION,
        }:
            raise AuthMateUnavailableError(decision=decision)
        raise AuthorizationDeniedError(decision)

    async def aclose(self) -> None:
        """Drain entered calls and close owned providers once in reverse order."""

        async with self._condition:
            if self._shutdown_task is None:
                self._state = "closing"
                self._shutdown_task = asyncio.create_task(self._shutdown())
            task = self._shutdown_task
        await asyncio.shield(task)

    async def _authorize_inner(
        self,
        *,
        context: AccessContext,
        action: str,
        resource: ResourceRef | None,
    ) -> AuthorizationDecision:
        if not isinstance(context, AccessContext):
            raise InvalidAuthorizationRequestError()
        if resource is not None and not isinstance(resource, ResourceRef):
            raise InvalidAuthorizationRequestError()
        try:
            valid_action = validate_action(action)
        except (ValidationError, TypeError, ValueError) as exc:
            raise InvalidAuthorizationRequestError() from exc

        if context.effective is not None:
            return self._deny(valid_action, resource, DecisionReason.DELEGATION_NOT_SUPPORTED)

        try:
            record = await self._call_provider(
                lambda: self._principal_provider.get_principal(context.actor),
            )
        except _ProviderUnavailable:
            return self._deny(valid_action, resource, DecisionReason.PROVIDER_UNAVAILABLE)

        if record is None:
            return self._deny(valid_action, resource, DecisionReason.PRINCIPAL_NOT_FOUND)
        if not isinstance(record, PrincipalRecord):
            return self._deny(
                valid_action,
                resource,
                DecisionReason.PROVIDER_CONTRACT_VIOLATION,
            )
        try:
            record = PrincipalRecord.model_validate(record.model_dump(mode="python"))
        except Exception as exc:
            del exc
            return self._deny(valid_action, resource, DecisionReason.PROVIDER_CONTRACT_VIOLATION)
        if record.ref != context.actor:
            return self._deny(
                valid_action,
                resource,
                DecisionReason.PROVIDER_CONTRACT_VIOLATION,
            )
        now = datetime.now(UTC)
        if not record.enabled:
            return self._deny(valid_action, resource, DecisionReason.PRINCIPAL_DISABLED)
        if record.expires_at is not None and record.expires_at <= now:
            return self._deny(valid_action, resource, DecisionReason.PRINCIPAL_EXPIRED)

        try:
            decision = await self._call_provider(
                lambda: self._authorization_provider.authorize(
                    principal=record, action=valid_action, resource=resource
                ),
            )
        except _ProviderUnavailable:
            return self._deny(valid_action, resource, DecisionReason.PROVIDER_UNAVAILABLE)

        if not isinstance(decision, AuthorizationDecision):
            return self._deny(
                valid_action,
                resource,
                DecisionReason.PROVIDER_CONTRACT_VIOLATION,
            )
        try:
            decision = AuthorizationDecision.model_validate(decision.model_dump(mode="python"))
        except Exception as exc:
            del exc
            return self._deny(valid_action, resource, DecisionReason.PROVIDER_CONTRACT_VIOLATION)
        if decision.action != valid_action or decision.resource != resource:
            return self._deny(
                valid_action,
                resource,
                DecisionReason.PROVIDER_CONTRACT_VIOLATION,
            )
        return decision

    async def _call_provider(self, operation: Callable[[], Awaitable[T]]) -> T:
        try:
            awaitable = operation()
            async with asyncio.timeout(self._timeout):
                return await awaitable
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise _ProviderUnavailable() from exc

    @staticmethod
    def _deny(
        action: str,
        resource: ResourceRef | None,
        reason: DecisionReason,
    ) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=False,
            reason=reason,
            action=action,
            resource=resource,
        )

    async def _enter_operation(self) -> None:
        async with self._condition:
            if self._state != "open":
                raise AuthMateClosedError()
            self._in_flight += 1

    async def _exit_operation(self) -> None:
        async with self._condition:
            self._in_flight -= 1
            if self._state == "closing" and self._in_flight == 0:
                self._condition.notify_all()

    async def _shutdown(self) -> None:
        async with self._condition:
            while self._in_flight:
                await self._condition.wait()

        errors: list[Exception] = []
        seen: set[int] = set()
        for provider in (self._authorization_provider, self._principal_provider):
            provider_id = id(provider)
            if provider_id in seen:
                continue
            seen.add(provider_id)
            try:
                await provider.aclose()
            except Exception as exc:
                errors.append(exc)

        async with self._condition:
            self._state = "closed"
            self._condition.notify_all()
        if errors:
            raise ExceptionGroup("AuthMate provider cleanup failed", errors)


class _ProviderUnavailable(Exception):
    """Private sentinel that prevents provider text from reaching public errors."""


__all__ = ["AuthMate"]
