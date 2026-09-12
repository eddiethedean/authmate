import json
import pickle

import pytest

from authmate import SecretValue
from authmate.errors import SecretClosedError


def test_secret_is_redacted_and_closes() -> None:
    secret = SecretValue("top-secret")
    assert secret.reveal() == "top-secret"
    assert "top-secret" not in repr(secret)
    assert "top-secret" not in str(secret)
    secret.close()
    secret.close()
    with pytest.raises(SecretClosedError):
        secret.reveal()
    with pytest.raises(TypeError):
        pickle.dumps(secret)
    with pytest.raises(TypeError):
        json.dumps(secret)


def test_secret_context_managers_close() -> None:
    with SecretValue(3) as secret:
        assert secret.reveal() == 3
    with pytest.raises(SecretClosedError):
        secret.reveal()


@pytest.mark.asyncio
async def test_async_secret_context_manager_closes() -> None:
    async with SecretValue("value") as secret:
        assert secret.reveal() == "value"
    with pytest.raises(SecretClosedError):
        secret.reveal()
