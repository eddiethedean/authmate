"""Provider-neutral extension protocols for AuthMate."""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager as AsyncContextManager
from typing import Any, Protocol

from .models import (
    AccessContext,
    AuditEvent,
    AuthorizationDecision,
    CredentialRef,
    PrincipalRecord,
    PrincipalRef,
    ResourceRef,
    SecretReference,
)
from .secrets import SecretValue


class PrincipalProvider(Protocol):
    """Load current principal state from a host-owned source."""

    async def get_principal(self, ref: PrincipalRef) -> PrincipalRecord | None: ...

    async def aclose(self) -> None: ...


class AuthorizationProvider(Protocol):
    """Evaluate one authorization request for a current principal."""

    async def authorize(
        self,
        *,
        principal: PrincipalRecord,
        action: str,
        resource: ResourceRef | None,
    ) -> AuthorizationDecision: ...

    async def aclose(self) -> None: ...


class CredentialResolver(Protocol):
    """Future credential-to-secret boundary; unwired in phase 0.1."""

    def resolve(
        self,
        *,
        context: AccessContext,
        credential: CredentialRef,
    ) -> AsyncContextManager[SecretValue[Any]]: ...

    async def aclose(self) -> None: ...


class SecretProvider(Protocol):
    """Future provider-specific secret boundary; unwired in phase 0.1."""

    def resolve(self, reference: SecretReference) -> AsyncContextManager[SecretValue[Any]]: ...

    async def aclose(self) -> None: ...


class AuditSink(Protocol):
    """Future audit delivery boundary; unwired in phase 0.1."""

    async def record(self, event: AuditEvent) -> None: ...

    async def aclose(self) -> None: ...


__all__ = [
    "AuditSink",
    "AuthorizationProvider",
    "CredentialResolver",
    "PrincipalProvider",
    "SecretProvider",
]
