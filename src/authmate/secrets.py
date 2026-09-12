"""Redacted, explicitly closable secret values for protocol testing."""

from __future__ import annotations

from typing import Any, Generic, NoReturn, TypeVar, cast

from .errors import SecretClosedError

T = TypeVar("T")


class SecretValue(Generic[T]):
    """A non-serializable wrapper with deterministic redaction and cleanup."""

    __slots__ = ("_closed", "_value")
    _REDACTED = "SecretValue(<redacted>)"

    def __init__(self, value: T) -> None:
        self._value: T | None = value
        self._closed = False

    def reveal(self) -> T:
        """Return the wrapped value until the lease is closed."""

        if self._closed:
            raise SecretClosedError()
        return cast(T, self._value)

    def close(self) -> None:
        """Drop AuthMate's reference; repeated closes are harmless."""

        self._value = None
        self._closed = True

    def __enter__(self) -> SecretValue[T]:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    async def __aenter__(self) -> SecretValue[T]:
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return self._REDACTED

    def __str__(self) -> str:
        return self._REDACTED

    def __reduce__(self) -> NoReturn:
        raise TypeError("SecretValue cannot be serialized")


__all__ = ["SecretValue"]
