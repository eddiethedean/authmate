# AuthMate

AuthMate is a provider-neutral authorization boundary for Python services. Version
0.1.0 is a stateless contract preview: it validates shared values, coordinates
principal and authorization providers, and supplies a small FastAPI adapter. It
does not authenticate requests, persist data, implement RBAC, manage credentials,
or provide a production-readiness guarantee.

> Independent by default, composable by contract.

## Status

The phase 0.1 runtime is implemented under `src/authmate`. Read the
[quickstart](docs/quickstart.md) and [planning index](docs/plans/README.md) for the
public contract and release boundary.

## Supported runtime

Python 3.11 through 3.14. Install this checkout with `uv sync --group dev`.
AuthMate is distributed under the [MIT License](LICENSE).

## Quick start

Providers are host-owned and implement the protocols in `authmate.protocols`.
The service calls the principal provider first, then the authorization provider
only for an enabled, non-expired principal.

```python
from uuid import uuid4
from authmate import (
    AccessContext,
    AuthMate,
    AuthorizationDecision,
    PrincipalKind,
    PrincipalRecord,
    PrincipalRef,
)

actor = PrincipalRef(id=uuid4(), kind=PrincipalKind.USER)


class Principals:
    async def get_principal(self, ref):
        return PrincipalRecord(ref=ref, display_name="Ada", enabled=True)

    async def aclose(self):
        pass


class Policy:
    async def authorize(self, *, principal, action, resource):
        return AuthorizationDecision(
            allowed=True, reason="allowed", action=action, resource=resource
        )

    async def aclose(self):
        pass


async def check_request():
    service = AuthMate(principal_provider=Principals(), authorization_provider=Policy())
    try:
        return await service.require(context=AccessContext(actor=actor), action="report.read")
    finally:
        await service.aclose()
```

See [the phase 0.1 quickstart](docs/quickstart.md) for FastAPI integration,
provider contracts, lifecycle behavior, and deliberate non-goals.

## Development

```sh
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run mypy --strict src/authmate tests
uv run pytest --cov=authmate --cov-branch --cov-fail-under=95
uv build
uv run twine check dist/*
```

## Planned MVP

- Users, operator provisioning, opaque SQL-backed browser sessions, and revocation.
- Service accounts, revocable API tokens, and generic delegated identity.
- Exact RBAC scopes, FastAPI dependencies, and Python service APIs.
- Credential metadata, exact secret-use grants, and approved environment references.
- Durable SQL audit, rate limiting, CSRF protection, and explicit recovery procedures.
- Typed public contracts, controlled model/provider extensions, and reviewed migrations.

PostgreSQL is the production reference; SQLite supports local development. No Redis,
broker, external identity service, or external secret manager is required. Encrypted
SQL secret storage, federation, tenancy, and richer extensions have later release gates.

## Architecture principles

- AuthMate owns its security semantics and public contracts; consumers adapt to them.
- Mandatory service checks remain authoritative with custom providers.
- Pydantic public contracts are separate from SQLModel/SQLAlchemy persistence.
- FastAPI composition uses explicit DI, lifespan, security, and OpenAPI integration.
- Core requires SQL-backed state, not process-local caches or additional services.

Hedron, ShuETL, and other applications may build optional adapters against AuthMate.
Core contains no consumer workflow records, callbacks, domain imports, or release
dependencies. Consumer-owned compatibility tests establish supported combinations.
See [Consumer Contracts](docs/plans/CONSUMER_CONTRACTS.md) and
[MVP gates](docs/plans/MVP.md).
