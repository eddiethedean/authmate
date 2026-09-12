import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from authmate import AccessContext, AuthMate, AuthorizationDecision, DecisionReason, ResourceRef
from authmate.errors import (
    AuthMateClosedError,
    AuthorizationDeniedError,
    InvalidAuthorizationRequestError,
)
from tests.contract.fakes import (
    FakeAuthorizationProvider,
    FakePrincipalProvider,
    decision,
    principal,
)


def setup_service(*, record=None, authorization=None, **kwargs):
    record = record or principal()
    resource = ResourceRef(type="report.document", id="r-1")
    authorization = authorization or decision(record, resource=resource)
    pp = FakePrincipalProvider(record)
    ap = FakeAuthorizationProvider(authorization)
    return (
        AuthMate(principal_provider=pp, authorization_provider=ap, **kwargs),
        pp,
        ap,
        record.ref,
        resource,
    )


@pytest.mark.asyncio
async def test_authorize_allow_and_require() -> None:
    service, pp, ap, actor, resource = setup_service()
    context = AccessContext(actor=actor)
    assert (
        await service.authorize(context=context, action="report.read", resource=resource)
    ).allowed
    assert await service.can(context=context, action="report.read", resource=resource)
    assert pp.calls == 2 and ap.calls == 2
    await service.aclose()
    assert pp.closed == ap.closed == 1


@pytest.mark.asyncio
async def test_concurrent_calls_keep_request_resources_independent() -> None:
    record = principal()
    first = ResourceRef(type="report.document", id="first")
    second = ResourceRef(type="report.document", id="second")

    class RecordingAuthorizationProvider(FakeAuthorizationProvider):
        async def authorize(self, *, principal, action, resource):
            self.calls += 1
            return AuthorizationDecision(
                allowed=True,
                reason=DecisionReason.ALLOWED,
                action=action,
                resource=resource,
            )

    pp = FakePrincipalProvider(record)
    ap = RecordingAuthorizationProvider(None)
    service = AuthMate(principal_provider=pp, authorization_provider=ap)
    results = await asyncio.gather(
        service.authorize(
            context=AccessContext(actor=record.ref), action="report.read", resource=first
        ),
        service.authorize(
            context=AccessContext(actor=record.ref), action="report.read", resource=second
        ),
    )
    assert [result.resource for result in results] == [first, second]
    assert ap.calls == 2
    await service.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "record, reason",
    [
        (None, "principal_not_found"),
        (principal(enabled=False), "principal_disabled"),
        (
            principal(expires_at=datetime.now(UTC) - timedelta(seconds=1)),
            "principal_expired",
        ),
    ],
)
async def test_principal_state_short_circuits(record: object, reason: str) -> None:
    if record is None:
        missing = principal()
        pp = FakePrincipalProvider(None)
        resource = ResourceRef(type="report.document", id="r-1")
        ap = FakeAuthorizationProvider(decision(missing, resource=resource))
        service = AuthMate(principal_provider=pp, authorization_provider=ap)
        actor = missing.ref
    else:
        service, pp, ap, actor, resource = setup_service(record=record)
    result = await service.authorize(
        context=AccessContext(actor=actor), action="report.read", resource=resource
    )
    assert result.reason.value == reason and ap.calls == 0
    await service.aclose()


@pytest.mark.asyncio
async def test_delegation_is_explicit_denial() -> None:
    service, pp, ap, actor, resource = setup_service()
    effective = principal().ref
    result = await service.authorize(
        context=AccessContext(actor=actor, effective=effective),
        action="report.read",
        resource=resource,
    )
    assert result.reason.value == "delegation_not_supported" and pp.calls == 0
    await service.aclose()


@pytest.mark.asyncio
async def test_invalid_request_and_require_denial() -> None:
    record = principal()
    resource = ResourceRef(type="report.document", id="r-1")
    service, pp, ap, actor, resource = setup_service(
        record=record,
        authorization=AuthorizationDecision(
            allowed=False, reason=DecisionReason.DENIED, action="report.read", resource=resource
        ),
    )
    with pytest.raises(InvalidAuthorizationRequestError):
        await service.authorize(context="wrong", action="report.read")
    with pytest.raises(AuthorizationDeniedError) as error:
        await service.require(
            context=AccessContext(actor=actor), action="report.read", resource=resource
        )
    assert error.value.decision is not None
    await service.aclose()


@pytest.mark.asyncio
async def test_provider_failure_timeout_and_cancellation_are_safe() -> None:
    record = principal()
    pp = FakePrincipalProvider(record, error=RuntimeError("secret backend detail"))
    ap = FakeAuthorizationProvider(None)
    service = AuthMate(
        principal_provider=pp, authorization_provider=ap, provider_timeout_seconds=0.01
    )
    result = await service.authorize(context=AccessContext(actor=record.ref), action="report.read")
    assert result.reason.value == "provider_unavailable"
    await service.aclose()

    pp = FakePrincipalProvider(record, delay=0.05)
    service = AuthMate(
        principal_provider=pp, authorization_provider=ap, provider_timeout_seconds=0.01
    )
    result = await service.authorize(context=AccessContext(actor=record.ref), action="report.read")
    assert result.reason.value == "provider_unavailable"
    await service.aclose()

    pp = FakePrincipalProvider(record)
    ap = FakeAuthorizationProvider(None, error=asyncio.CancelledError())
    service = AuthMate(principal_provider=pp, authorization_provider=ap)
    with pytest.raises(asyncio.CancelledError):
        await service.authorize(context=AccessContext(actor=record.ref), action="report.read")
    await service.aclose()


@pytest.mark.asyncio
async def test_contract_violation_is_denied() -> None:
    record = principal()
    pp = FakePrincipalProvider(record)
    ap = FakeAuthorizationProvider(object())
    service = AuthMate(principal_provider=pp, authorization_provider=ap)
    result = await service.authorize(context=AccessContext(actor=record.ref), action="report.read")
    assert result.reason.value == "provider_contract_violation"
    await service.aclose()


@pytest.mark.asyncio
async def test_invalid_and_mismatched_provider_values_are_denied() -> None:
    record = principal()
    pp = FakePrincipalProvider(object())
    ap = FakeAuthorizationProvider(None)
    service = AuthMate(principal_provider=pp, authorization_provider=ap)
    result = await service.authorize(context=AccessContext(actor=record.ref), action="report.read")
    assert result.reason.value == "provider_contract_violation"
    await service.aclose()


@pytest.mark.asyncio
async def test_wrong_provider_objects_cannot_become_valid_models() -> None:
    record = principal()
    resource = ResourceRef(type="report.document", id="r-1")

    class ModelDumpingObject:
        def __init__(self, payload: object) -> None:
            self.payload = payload

        def model_dump(self, *, mode: str) -> object:
            return self.payload

    service = AuthMate(
        principal_provider=FakePrincipalProvider(
            ModelDumpingObject(record.model_dump(mode="python"))
        ),
        authorization_provider=FakeAuthorizationProvider(None),
    )
    result = await service.authorize(
        context=AccessContext(actor=record.ref), action="report.read", resource=resource
    )
    assert result.reason is DecisionReason.PROVIDER_CONTRACT_VIOLATION
    await service.aclose()

    service = AuthMate(
        principal_provider=FakePrincipalProvider(record),
        authorization_provider=FakeAuthorizationProvider(
            ModelDumpingObject(
                AuthorizationDecision(
                    allowed=True,
                    reason=DecisionReason.ALLOWED,
                    action="report.read",
                    resource=resource,
                ).model_dump(mode="python")
            )
        ),
    )
    result = await service.authorize(
        context=AccessContext(actor=record.ref), action="report.read", resource=resource
    )
    assert result.reason is DecisionReason.PROVIDER_CONTRACT_VIOLATION
    await service.aclose()

    wrong = principal()
    service = AuthMate(
        principal_provider=FakePrincipalProvider(wrong),
        authorization_provider=FakeAuthorizationProvider(None),
    )
    result = await service.authorize(context=AccessContext(actor=record.ref), action="report.read")
    assert result.reason.value == "provider_contract_violation"
    await service.aclose()

    service = AuthMate(
        principal_provider=FakePrincipalProvider(record),
        authorization_provider=FakeAuthorizationProvider(
            AuthorizationDecision(allowed=True, reason=DecisionReason.ALLOWED, action="other.read")
        ),
    )
    result = await service.authorize(context=AccessContext(actor=record.ref), action="report.read")
    assert result.reason.value == "provider_contract_violation"
    await service.aclose()


@pytest.mark.asyncio
async def test_invalid_resource_action_and_auth_provider_error() -> None:
    service, _pp, _ap, actor, resource = setup_service()
    with pytest.raises(InvalidAuthorizationRequestError):
        await service.authorize(context=AccessContext(actor=actor), action="bad action")
    with pytest.raises(InvalidAuthorizationRequestError):
        await service.authorize(
            context=AccessContext(actor=actor), action="report.read", resource="wrong"
        )
    await service.aclose()

    record = principal()
    service = AuthMate(
        principal_provider=FakePrincipalProvider(record),
        authorization_provider=FakeAuthorizationProvider(None, error=RuntimeError("down")),
    )
    result = await service.authorize(context=AccessContext(actor=record.ref), action="report.read")
    assert result.reason.value == "provider_unavailable"
    await service.aclose()


@pytest.mark.asyncio
async def test_close_drains_calls_and_deduplicates_shared_provider() -> None:
    record = principal()
    shared = FakePrincipalProvider(record, delay=-1)
    service = AuthMate(
        principal_provider=shared,
        authorization_provider=FakeAuthorizationProvider(None),
    )
    operation = asyncio.create_task(
        service.authorize(context=AccessContext(actor=record.ref), action="report.read")
    )
    await shared.started.wait()
    closing = asyncio.create_task(service.aclose())
    closing_again = asyncio.create_task(service.aclose())
    await asyncio.sleep(0)
    with pytest.raises(AuthMateClosedError):
        await service.authorize(context=AccessContext(actor=record.ref), action="report.read")
    shared.release.set()
    await operation
    await closing
    await closing_again
    assert shared.closed == 1
    await service.aclose()
    assert shared.closed == 1


@pytest.mark.asyncio
async def test_close_failure_is_reported_and_service_stays_closed() -> None:
    class ClosingProvider(FakePrincipalProvider):
        async def aclose(self) -> None:
            self.closed += 1
            raise RuntimeError("backend detail")

    record = principal()
    pp = ClosingProvider(record)
    ap = FakeAuthorizationProvider(decision(record))
    service = AuthMate(principal_provider=pp, authorization_provider=ap)
    with pytest.raises(ExceptionGroup):
        await service.aclose()
    with pytest.raises(AuthMateClosedError):
        await service.authorize(context=AccessContext(actor=record.ref), action="report.read")


def test_timeout_bounds() -> None:
    record = principal()
    for value in (0, 61, float("inf"), True):
        with pytest.raises(ValueError):
            AuthMate(
                principal_provider=FakePrincipalProvider(record),
                authorization_provider=FakeAuthorizationProvider(None),
                provider_timeout_seconds=value,
            )
