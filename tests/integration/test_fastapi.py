import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from authmate import (
    AccessContext,
    AuthMate,
    AuthorizationDecision,
    DecisionReason,
    ResourceRef,
)
from authmate.errors import AuthMateConfigurationError
from authmate.fastapi import AuthMateSecurity
from tests.contract.fakes import (
    FakeAuthorizationProvider,
    FakePrincipalProvider,
    decision,
    principal,
)


def app_for(authorization):
    record = principal()
    service = AuthMate(
        principal_provider=FakePrincipalProvider(record),
        authorization_provider=FakeAuthorizationProvider(authorization),
    )
    security = AuthMateSecurity(service, context_dependency=lambda: AccessContext(actor=record.ref))
    resource = ResourceRef(type="report.document", id="r-1")

    async def current_resource() -> ResourceRef:
        return ResourceRef(type="report.document", id=resource.id)

    app = FastAPI()
    require = security.require("report.read", resource_dependency=current_resource)

    @app.get("/reports")
    async def route(_decision=Depends(require)):
        return {"ok": True}

    @app.on_event("shutdown")
    async def shutdown():
        await service.aclose()

    return app


def test_allow_and_denial_responses() -> None:
    allow = AuthorizationDecision(
        allowed=True,
        reason=DecisionReason.ALLOWED,
        action="report.read",
        resource=ResourceRef(type="report.document", id="r-1"),
    )
    with TestClient(app_for(allow)) as client:
        assert client.get("/reports").json() == {"ok": True}
    deny = AuthorizationDecision(
        allowed=False,
        reason=DecisionReason.DENIED,
        action="report.read",
        resource=ResourceRef(type="report.document", id="r-1"),
    )
    with TestClient(app_for(deny)) as client:
        response = client.get("/reports")
        assert response.status_code == 403
        assert response.json() == {"detail": {"code": "authorization_denied"}}


def test_unavailable_response_and_host_errors_propagate() -> None:
    record = principal()
    service = AuthMate(
        principal_provider=FakePrincipalProvider(record, error=RuntimeError("backend")),
        authorization_provider=FakeAuthorizationProvider(None),
    )
    security = AuthMateSecurity(service, context_dependency=lambda: AccessContext(actor=record.ref))
    app = FastAPI()
    require = security.require("report.read")

    @app.get("/reports")
    async def route(_decision=Depends(require)):
        return {"ok": True}

    with TestClient(app) as client:
        response = client.get("/reports")
        assert response.status_code == 503
        assert response.json() == {"detail": {"code": "authmate_unavailable"}}

    auth = AuthMate(
        principal_provider=FakePrincipalProvider(record),
        authorization_provider=FakeAuthorizationProvider(decision(record)),
    )
    security = AuthMateSecurity(
        auth, context_dependency=lambda: (_ for _ in ()).throw(HTTPException(status_code=401))
    )
    app = FastAPI()
    require = security.require("report.read")

    @app.get("/auth")
    async def auth_route(_decision=Depends(require)):
        return {"ok": True}

    with TestClient(app) as client:
        assert client.get("/auth").status_code == 401


def test_configuration_is_rejected_early() -> None:
    record = principal()
    service = AuthMate(
        principal_provider=FakePrincipalProvider(record),
        authorization_provider=FakeAuthorizationProvider(decision(record)),
    )
    with pytest.raises(AuthMateConfigurationError):
        AuthMateSecurity(service, context_dependency=None)  # type: ignore[arg-type]
    security = AuthMateSecurity(service, context_dependency=lambda: AccessContext(actor=record.ref))
    with pytest.raises(AuthMateConfigurationError):
        security.require("bad action")
    with pytest.raises(AuthMateConfigurationError):
        security.require("report.read", resource_dependency=object())  # type: ignore[arg-type]
    with pytest.raises(AuthMateConfigurationError):
        security._require_context(object())
    with pytest.raises(AuthMateConfigurationError):
        security._require_resource(object())
