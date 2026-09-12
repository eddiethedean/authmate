from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from authmate import (
    AccessContext,
    AuditEvent,
    AuditOutcome,
    AuthorizationDecision,
    CredentialRef,
    DecisionReason,
    PrincipalKind,
    PrincipalRecord,
    PrincipalRef,
    ResourceRef,
    SecretReference,
    validate_action,
)


def test_models_are_immutable_and_serializable() -> None:
    ref = PrincipalRef(id=uuid4(), kind=PrincipalKind.USER)
    record = PrincipalRecord(ref=ref, display_name="Ada", enabled=True)
    assert record.model_dump(mode="json")["ref"]["kind"] == "user"
    with pytest.raises(ValidationError):
        PrincipalRecord(  # type: ignore[call-arg]
            ref=ref, display_name="Ada", enabled=True, unknown=1
        )
    with pytest.raises(ValidationError):
        record.display_name = "Grace"


@pytest.mark.parametrize(
    "value", ["Report.read", "report", "report.read ", "report..read", "a" * 201, 3]
)
def test_action_validation_rejects_invalid_values(value: object) -> None:
    with pytest.raises((ValidationError, TypeError)):
        validate_action(value)


def test_timestamps_normalize_and_ids_cannot_be_nil() -> None:
    ref = PrincipalRef(id=uuid4(), kind=PrincipalKind.USER)
    record = PrincipalRecord(
        ref=ref,
        display_name="Ada",
        enabled=True,
        expires_at=datetime(2030, 1, 1, 12, tzinfo=UTC),
    )
    assert record.expires_at is not None
    assert record.expires_at.tzinfo == UTC
    with pytest.raises(ValidationError):
        PrincipalRef(id=UUID(int=0), kind=PrincipalKind.USER)
    with pytest.raises(ValidationError):
        PrincipalRecord(ref=ref, display_name=" Ada", enabled=True)
    with pytest.raises(ValidationError):
        PrincipalRecord(ref=ref, display_name="Ada\n", enabled=True)


def test_context_decision_and_audit_invariants() -> None:
    ref = PrincipalRef(id=uuid4(), kind=PrincipalKind.USER)
    with pytest.raises(ValidationError):
        AccessContext(actor=ref, effective=ref)
    resource = ResourceRef(type="report.document", id="r-1")
    with pytest.raises(ValidationError):
        AuthorizationDecision(allowed=True, reason=DecisionReason.DENIED, action="report.read")
    event = AuditEvent(
        id=uuid4(),
        event_type="authorization.checked",
        occurred_at=datetime(2030, 1, 1, tzinfo=UTC),
        outcome=AuditOutcome.SUCCEEDED,
        actor=ref,
        action="report.read",
        resource=resource,
    )
    assert event.occurred_at.tzinfo == UTC


def test_remaining_validation_boundaries() -> None:
    ref = PrincipalRef(id=uuid4(), kind=PrincipalKind.USER)
    with pytest.raises(ValidationError):
        PrincipalRecord(ref=ref, display_name="Ada", enabled=True, expires_at=datetime(2030, 1, 1))
    with pytest.raises(ValidationError):
        ResourceRef(type="report.document", id="x\x00")
    with pytest.raises(ValidationError):
        CredentialRef(id=UUID(int=0))
    with pytest.raises(ValidationError):
        SecretReference(provider="Vault", key="key")
    with pytest.raises(ValidationError):
        SecretReference(provider="vault", key=" key")
    with pytest.raises(ValidationError):
        AuditEvent(
            id=uuid4(),
            event_type="authorization.checked",
            occurred_at=datetime.now(UTC),
            outcome=AuditOutcome.FAILED,
            reason_code="Bad.Code",
        )


@pytest.mark.parametrize(
    ("label", "factory"),
    [
        (
            "principal id bytes",
            lambda ref: PrincipalRef(id=ref.id.bytes, kind=cast(Any, "user")),
        ),
        (
            "principal kind bytes",
            lambda ref: PrincipalRef(id=ref.id, kind=cast(Any, b"user")),
        ),
        (
            "principal expiry bytes",
            lambda ref: PrincipalRecord(
                ref=ref,
                display_name="Ada",
                enabled=True,
                expires_at=cast(Any, b"2030-01-01T00:00:00Z"),
            ),
        ),
        (
            "decision reason bytes",
            lambda ref: AuthorizationDecision(
                allowed=True, reason=cast(Any, b"allowed"), action="report.read"
            ),
        ),
        (
            "audit timestamp integer",
            lambda ref: AuditEvent(
                id=uuid4(),
                event_type="authorization.checked",
                occurred_at=cast(Any, 0),
                outcome=cast(Any, "succeeded"),
            ),
        ),
    ],
)
def test_coercive_primitive_types_are_rejected(
    label: str, factory: Callable[[PrincipalRef], object]
) -> None:
    ref = PrincipalRef(id=uuid4(), kind=PrincipalKind.USER)
    with pytest.raises(ValidationError):
        factory(ref)
