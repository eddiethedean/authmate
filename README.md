# AuthMate

**AuthMate** is a planned FastAPI-native identity, authorization, service-account,
credential, and secret-resolution package. It defines broadly useful public
contracts that applications and adapters can consume independently.

> Independent by default, composable by contract.

## Status

This repository currently contains architecture and implementation plans only.
There is no AuthMate runtime package or passing implementation/security test suite.
Start with the [planning index](docs/plans/README.md) and
[critical review](docs/plans/PLAN_REVIEW.md).

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
