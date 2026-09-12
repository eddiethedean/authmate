"""AuthMate's phase 0.1 contract-preview API."""

from .errors import (
    AuthMateClosedError,
    AuthMateConfigurationError,
    AuthMateError,
    AuthMateUnavailableError,
    AuthorizationDeniedError,
    InvalidAuthorizationRequestError,
    ProviderContractError,
    ProviderUnavailableError,
    SecretClosedError,
)
from .models import (
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
from .secrets import SecretValue
from .service import AuthMate

__version__ = "0.1.0"

__all__ = [
    "AccessContext",
    "AuthMate",
    "AuthMateClosedError",
    "AuthMateConfigurationError",
    "AuthMateError",
    "AuthMateUnavailableError",
    "AuditEvent",
    "AuditOutcome",
    "AuthorizationDecision",
    "AuthorizationDeniedError",
    "CredentialRef",
    "DecisionReason",
    "InvalidAuthorizationRequestError",
    "PrincipalKind",
    "PrincipalRecord",
    "PrincipalRef",
    "ProviderContractError",
    "ProviderUnavailableError",
    "ResourceRef",
    "SecretClosedError",
    "SecretReference",
    "SecretValue",
    "validate_action",
    "__version__",
]
