"""Sanitized AuthMate exception types."""

from __future__ import annotations

from .models import AuthorizationDecision


class AuthMateError(Exception):
    """Base exception with a stable code and constant safe message."""

    code = "authmate_error"
    safe_message = "AuthMate error"

    def __init__(self, *, decision: AuthorizationDecision | None = None) -> None:
        super().__init__(self.safe_message)
        self.decision = decision

    def __str__(self) -> str:
        return self.safe_message


class InvalidAuthorizationRequestError(AuthMateError):
    code = "invalid_authorization_request"
    safe_message = "invalid authorization request"


class AuthorizationDeniedError(AuthMateError):
    code = "authorization_denied"
    safe_message = "authorization denied"

    def __init__(self, decision: AuthorizationDecision) -> None:
        super().__init__(decision=decision)


class AuthMateUnavailableError(AuthMateError):
    code = "authmate_unavailable"
    safe_message = "authorization service unavailable"


class ProviderUnavailableError(AuthMateUnavailableError):
    code = "provider_unavailable"
    safe_message = "provider unavailable"


class ProviderContractError(AuthMateUnavailableError):
    code = "provider_contract_violation"
    safe_message = "provider contract violation"


class AuthMateConfigurationError(AuthMateError):
    code = "authmate_configuration_error"
    safe_message = "invalid AuthMate integration configuration"


class AuthMateClosedError(AuthMateError):
    code = "authmate_closed"
    safe_message = "AuthMate is closed"


class SecretClosedError(AuthMateError):
    code = "secret_closed"
    safe_message = "secret value is closed"


__all__ = [
    "AuthMateClosedError",
    "AuthMateConfigurationError",
    "AuthMateError",
    "AuthMateUnavailableError",
    "AuthorizationDeniedError",
    "InvalidAuthorizationRequestError",
    "ProviderContractError",
    "ProviderUnavailableError",
    "SecretClosedError",
]
