"""FastAPI dependency adaptation without owning authentication."""

from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from fastapi import Depends, HTTPException

from .errors import (
    AuthMateConfigurationError,
    AuthMateUnavailableError,
    AuthorizationDeniedError,
)
from .models import AccessContext, AuthorizationDecision, ResourceRef, validate_action
from .service import AuthMate

ContextDependency = Callable[..., AccessContext | Awaitable[AccessContext]]
ResourceDependency = Callable[..., ResourceRef | Awaitable[ResourceRef]]


class AuthMateSecurity:
    """Create FastAPI dependencies backed by an existing AuthMate facade."""

    def __init__(self, authmate: AuthMate, *, context_dependency: ContextDependency) -> None:
        if not isinstance(authmate, AuthMate) or not callable(context_dependency):
            raise AuthMateConfigurationError()
        self._authmate = authmate
        self._context_dependency = context_dependency

    def require(
        self,
        action: str,
        *,
        resource_dependency: ResourceDependency | None = None,
    ) -> Callable[..., Awaitable[AuthorizationDecision]]:
        """Build a dependency that delegates to AuthMate.require exactly once."""

        try:
            validated_action = validate_action(action)
        except (TypeError, ValueError) as exc:
            raise AuthMateConfigurationError() from exc

        if resource_dependency is not None and not callable(resource_dependency):
            raise AuthMateConfigurationError()

        if resource_dependency is None:

            async def dependency(
                context: Annotated[AccessContext, Depends(self._context_dependency)],
            ) -> AuthorizationDecision:
                verified_context = self._require_context(context)
                return await self._enforce(
                    context=verified_context,
                    action=validated_action,
                    resource=None,
                )

            return dependency

        async def dependency_with_resource(
            context: Annotated[AccessContext, Depends(self._context_dependency)],
            resource: Annotated[ResourceRef, Depends(resource_dependency)],
        ) -> AuthorizationDecision:
            verified_context = self._require_context(context)
            verified_resource = self._require_resource(resource)
            return await self._enforce(
                context=verified_context,
                action=validated_action,
                resource=verified_resource,
            )

        return dependency_with_resource

    @staticmethod
    def _require_context(value: Any) -> AccessContext:
        if not isinstance(value, AccessContext):
            raise AuthMateConfigurationError()
        return value

    @staticmethod
    def _require_resource(value: Any) -> ResourceRef:
        if not isinstance(value, ResourceRef):
            raise AuthMateConfigurationError()
        return value

    async def _enforce(
        self,
        *,
        context: AccessContext,
        action: str,
        resource: ResourceRef | None,
    ) -> AuthorizationDecision:
        try:
            return await self._authmate.require(
                context=context,
                action=action,
                resource=resource,
            )
        except AuthorizationDeniedError:
            raise HTTPException(
                status_code=403,
                detail={"code": "authorization_denied"},
            ) from None
        except AuthMateUnavailableError:
            raise HTTPException(
                status_code=503,
                detail={"code": "authmate_unavailable"},
            ) from None


__all__ = ["AuthMateSecurity", "ContextDependency", "ResourceDependency"]
