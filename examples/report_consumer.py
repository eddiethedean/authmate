"""Minimal FastAPI consumer using host-owned context and resource lookups."""

from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException

from authmate import (
    AccessContext,
    AuthMate,
    AuthorizationDecision,
    DecisionReason,
    PrincipalKind,
    PrincipalRecord,
    PrincipalRef,
    ResourceRef,
)
from authmate.fastapi import AuthMateSecurity


class Principals:
    async def get_principal(self, ref: PrincipalRef) -> PrincipalRecord:
        return PrincipalRecord(ref=ref, display_name="Example user", enabled=True)

    async def aclose(self) -> None:
        return None


class Policy:
    def __init__(self, actor: PrincipalRef) -> None:
        self.actor = actor

    async def authorize(
        self,
        *,
        principal: PrincipalRecord,
        action: str,
        resource: ResourceRef | None,
    ) -> AuthorizationDecision:
        allowed = (
            principal.ref == self.actor
            and action == "report.read"
            and resource is not None
            and resource.id != "00000000-0000-0000-0000-000000000000"
        )
        return AuthorizationDecision(
            allowed=allowed,
            reason=DecisionReason.ALLOWED if allowed else DecisionReason.DENIED,
            action=action,
            resource=resource,
        )

    async def aclose(self) -> None:
        return None


def build_app(actor: PrincipalRef | None = None) -> FastAPI:
    actor = actor or PrincipalRef(id=uuid4(), kind=PrincipalKind.USER)
    service = AuthMate(principal_provider=Principals(), authorization_provider=Policy(actor))
    security = AuthMateSecurity(service, context_dependency=lambda: AccessContext(actor=actor))

    async def current_report(report_id: UUID) -> ResourceRef:
        if report_id.int == 0:
            raise HTTPException(status_code=404, detail="report not found")
        return ResourceRef(type="report.document", id=str(report_id))

    app = FastAPI()
    require_report = security.require("report.read", resource_dependency=current_report)

    @app.get("/reports/{report_id}")
    async def get_report(
        _decision: AuthorizationDecision = Depends(require_report),
    ) -> dict[str, bool]:
        return {"ok": True}

    @app.on_event("shutdown")
    async def close_service() -> None:
        await service.aclose()

    return app
