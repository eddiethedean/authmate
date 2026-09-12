from __future__ import annotations

import asyncio
from typing import Any
from uuid import uuid4

from authmate import (
    AuthorizationDecision,
    DecisionReason,
    PrincipalKind,
    PrincipalRecord,
    PrincipalRef,
    ResourceRef,
)


def principal(*, enabled: bool = True, expires_at: Any = None) -> PrincipalRecord:
    return PrincipalRecord(
        ref=PrincipalRef(id=uuid4(), kind=PrincipalKind.USER),
        display_name="Test user",
        enabled=enabled,
        expires_at=expires_at,
    )


class FakePrincipalProvider:
    def __init__(
        self, record: Any = None, *, error: BaseException | None = None, delay: float = 0
    ) -> None:
        self.record = record
        self.error = error
        self.delay = delay
        self.calls = 0
        self.closed = 0
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def get_principal(self, ref: PrincipalRef) -> Any:
        self.calls += 1
        self.started.set()
        if self.delay:
            await asyncio.sleep(self.delay)
        if not self.release.is_set() and self.delay == -1:
            await self.release.wait()
        if self.error:
            raise self.error
        return self.record

    async def aclose(self) -> None:
        self.closed += 1


class FakeAuthorizationProvider:
    def __init__(
        self, decision: Any, *, error: BaseException | None = None, delay: float = 0
    ) -> None:
        self.decision = decision
        self.error = error
        self.delay = delay
        self.calls = 0
        self.closed = 0
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def authorize(
        self, *, principal: PrincipalRecord, action: str, resource: ResourceRef | None
    ) -> Any:
        self.calls += 1
        self.started.set()
        if self.delay:
            await asyncio.sleep(self.delay)
        if not self.release.is_set() and self.delay == -1:
            await self.release.wait()
        if self.error:
            raise self.error
        return self.decision

    async def aclose(self) -> None:
        self.closed += 1


def decision(
    actor: PrincipalRecord,
    *,
    action: str = "report.read",
    allowed: bool = True,
    resource: ResourceRef | None = None,
) -> AuthorizationDecision:
    return AuthorizationDecision(
        allowed=allowed,
        reason=DecisionReason.ALLOWED if allowed else DecisionReason.DENIED,
        action=action,
        resource=resource,
    )
