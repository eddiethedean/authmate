"""Immutable, validated values shared by AuthMate consumers and providers."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
    StringConstraints,
    TypeAdapter,
    field_validator,
    model_validator,
)

_DOTTED_NAME_PATTERN = r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$"
_REASON_PATTERN = r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$"
_CORRELATION_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
_PROVIDER_PATTERN = r"^[a-z][a-z0-9_-]{0,62}$"

ActionName = Annotated[
    StrictStr,
    StringConstraints(pattern=_DOTTED_NAME_PATTERN, min_length=3, max_length=200),
]
ResourceType = Annotated[
    StrictStr,
    StringConstraints(pattern=_DOTTED_NAME_PATTERN, min_length=3, max_length=100),
]
EventType = Annotated[
    StrictStr,
    StringConstraints(pattern=_DOTTED_NAME_PATTERN, min_length=3, max_length=200),
]
ProviderAlias = Annotated[
    StrictStr,
    StringConstraints(pattern=_PROVIDER_PATTERN, min_length=1, max_length=63),
]
CorrelationId = Annotated[
    StrictStr,
    StringConstraints(pattern=_CORRELATION_PATTERN, min_length=1, max_length=128),
]

ACTION_ADAPTER = TypeAdapter(ActionName)


class AuthMateModel(BaseModel):
    """Base configuration for public immutable contract values."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=False,
        validate_assignment=True,
    )


def _reject_control_or_outer_whitespace(value: str, *, field_name: str) -> str:
    if value != value.strip() or any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError(f"{field_name} contains invalid whitespace or control characters")
    return value


def _require_non_nil(value: UUID, *, field_name: str) -> UUID:
    if value.int == 0:
        raise ValueError(f"{field_name} must not be nil")
    return value


def _as_utc(value: datetime, *, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value.astimezone(UTC)


class PrincipalKind(StrEnum):
    """Kinds of principals known by the contract preview."""

    USER = "user"
    SERVICE_ACCOUNT = "service_account"


class PrincipalRef(AuthMateModel):
    """An immutable principal identifier; it is not authentication proof."""

    id: UUID
    kind: PrincipalKind

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: UUID) -> UUID:
        return _require_non_nil(value, field_name="id")


class PrincipalRecord(AuthMateModel):
    """Current provider-owned principal state used for an authorization check."""

    ref: PrincipalRef
    display_name: StrictStr = Field(min_length=1, max_length=200)
    enabled: StrictBool
    expires_at: datetime | None = None
    version: StrictInt = Field(default=0, ge=0)

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str) -> str:
        return _reject_control_or_outer_whitespace(value, field_name="display_name")

    @field_validator("expires_at")
    @classmethod
    def normalize_expiry(cls, value: datetime | None) -> datetime | None:
        return None if value is None else _as_utc(value, field_name="expires_at")


class ResourceRef(AuthMateModel):
    """Exact consumer resource identity supplied by a trusted consumer lookup."""

    type: ResourceType
    id: StrictStr = Field(min_length=1, max_length=255)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        return _reject_control_or_outer_whitespace(value, field_name="resource id")


class AccessContext(AuthMateModel):
    """Verified actor context supplied by a trusted host integration."""

    actor: PrincipalRef
    effective: PrincipalRef | None = None
    correlation_id: CorrelationId | None = None

    @model_validator(mode="after")
    def validate_distinct_effective(self) -> AccessContext:
        if self.effective is not None and self.effective == self.actor:
            raise ValueError("effective must be omitted for a direct actor")
        return self


class DecisionReason(StrEnum):
    """Stable reasons attached to authorization decisions."""

    ALLOWED = "allowed"
    DENIED = "denied"
    PRINCIPAL_NOT_FOUND = "principal_not_found"
    PRINCIPAL_DISABLED = "principal_disabled"
    PRINCIPAL_EXPIRED = "principal_expired"
    DELEGATION_NOT_SUPPORTED = "delegation_not_supported"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_CONTRACT_VIOLATION = "provider_contract_violation"


class AuthorizationDecision(AuthMateModel):
    """A single authorization evaluation; never a reusable capability."""

    allowed: StrictBool
    reason: DecisionReason
    action: ActionName
    resource: ResourceRef | None = None
    policy_revision: StrictStr | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("policy_revision")
    @classmethod
    def validate_policy_revision(cls, value: str | None) -> str | None:
        return (
            None
            if value is None
            else _reject_control_or_outer_whitespace(value, field_name="policy_revision")
        )

    @model_validator(mode="after")
    def validate_allowed_reason(self) -> AuthorizationDecision:
        if self.allowed and self.reason is not DecisionReason.ALLOWED:
            raise ValueError("allowed decisions must use reason 'allowed'")
        if not self.allowed and self.reason is DecisionReason.ALLOWED:
            raise ValueError("denied decisions cannot use reason 'allowed'")
        return self


class CredentialRef(AuthMateModel):
    """Opaque credential identifier reserved for later resolver integration."""

    id: UUID

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: UUID) -> UUID:
        return _require_non_nil(value, field_name="id")


class SecretReference(AuthMateModel):
    """Provider alias and opaque key; it is never resolved in phase 0.1."""

    provider: ProviderAlias
    key: StrictStr = Field(min_length=1, max_length=255)

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        return _reject_control_or_outer_whitespace(value, field_name="secret key")


class AuditOutcome(StrEnum):
    """Outcome vocabulary for the preview audit protocol."""

    SUCCEEDED = "succeeded"
    DENIED = "denied"
    FAILED = "failed"


class AuditEvent(AuthMateModel):
    """Bounded event value for the unwired phase 0.1 audit protocol."""

    id: UUID
    event_type: EventType
    occurred_at: datetime
    outcome: AuditOutcome
    actor: PrincipalRef | None = None
    effective: PrincipalRef | None = None
    action: ActionName | None = None
    resource: ResourceRef | None = None
    reason_code: StrictStr | None = Field(default=None, min_length=1, max_length=100)
    correlation_id: CorrelationId | None = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: UUID) -> UUID:
        return _require_non_nil(value, field_name="id")

    @field_validator("occurred_at")
    @classmethod
    def normalize_occurred_at(cls, value: datetime) -> datetime:
        return _as_utc(value, field_name="occurred_at")

    @field_validator("reason_code")
    @classmethod
    def validate_reason_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        _reject_control_or_outer_whitespace(value, field_name="reason_code")
        if not re.fullmatch(_REASON_PATTERN, value):
            raise ValueError("reason_code has an invalid format")
        return value


def validate_action(value: Any) -> str:
    """Validate an action at a service/dependency boundary."""

    return ACTION_ADAPTER.validate_python(value)


__all__ = [
    "AccessContext",
    "ActionName",
    "AuditEvent",
    "AuditOutcome",
    "AuthorizationDecision",
    "CredentialRef",
    "DecisionReason",
    "EventType",
    "PrincipalKind",
    "PrincipalRecord",
    "PrincipalRef",
    "ProviderAlias",
    "ResourceRef",
    "ResourceType",
    "SecretReference",
    "validate_action",
]
