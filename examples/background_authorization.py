"""Run one direct authorization check without an HTTP adapter."""

import asyncio
from uuid import uuid4

from authmate import (
    AccessContext,
    AuthMate,
    AuthorizationDecision,
    PrincipalKind,
    PrincipalRecord,
    PrincipalRef,
)


class Principals:
    async def get_principal(self, ref: PrincipalRef) -> PrincipalRecord:
        return PrincipalRecord(ref=ref, display_name="Example user", enabled=True)

    async def aclose(self) -> None:
        return None


class Policy:
    async def authorize(self, *, principal, action, resource) -> AuthorizationDecision:
        allowed = action == "report.read"
        return AuthorizationDecision(
            allowed=allowed,
            reason="allowed" if allowed else "denied",
            action=action,
            resource=resource,
        )

    async def aclose(self) -> None:
        return None


async def authorize_report() -> bool:
    actor = PrincipalRef(id=uuid4(), kind=PrincipalKind.USER)
    service = AuthMate(principal_provider=Principals(), authorization_provider=Policy())
    try:
        decision = await service.authorize(context=AccessContext(actor=actor), action="report.read")
        return decision.allowed
    finally:
        await service.aclose()


if __name__ == "__main__":
    print(asyncio.run(authorize_report()))
