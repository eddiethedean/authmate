import subprocess
import sys
from importlib.metadata import metadata

import authmate


def test_public_version_and_import_boundary() -> None:
    assert authmate.__version__ == "0.1.0"
    assert "AuthMate" in authmate.__all__
    assert metadata("authmate")["License-Expression"] == "MIT"


def test_malformed_provider_fixture_fails_static_contract_check() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "--config-file=/dev/null",
            "tests/static/invalid_provider.py",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "PrincipalRecord" in result.stdout + result.stderr


def test_runtime_import_boundary() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import authmate, authmate.models, authmate.protocols, authmate.service",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
