# Dependency Strategy

## Principle

AuthMate should own identity, authorization, credential, and service-account domain semantics while delegating commodity security and pagination mechanics to mature libraries.

> **Own the contracts; reuse the mechanics.**

## Core dependencies

```text
fastapi
fastapi-pagination
pydantic
pydantic-settings
sqlmodel
sqlalchemy>=2
alembic
pwdlib[argon2]
itsdangerous
cryptography
```

## fastapi-pagination

Use `fastapi-pagination` for bounded collection APIs such as users, roles, service accounts, credentials, grants, sessions where applicable, and audit events.

AuthMate owns authorization, filtering rules, resource visibility, and response semantics. `fastapi-pagination` owns pagination mechanics and SQLModel/SQLAlchemy integration.

Pagination must occur after authorization/query scoping so totals and page contents cannot leak records the principal is not allowed to discover.

Do not expose dependency-specific implementation types as AuthMate domain contracts.

### pwdlib[argon2]
Use for password hashing and verification. AuthMate owns password lifecycle and policy; `pwdlib` owns hashing mechanics.

### itsdangerous
Use for bounded signed, time-limited application tokens such as invitation, email-verification, and password-reset tokens.

### cryptography
Use for any AuthMate-managed encrypted-secret provider. Never implement custom cryptographic primitives.

### pydantic-settings
Use for configuration and supported environment/secret-source loading where semantics fit.

## Optional dependencies

### Authlib
Package as `authmate[oidc]` for OAuth2/OpenID Connect protocol mechanics.

### PyCasbin
Package as `authmate[casbin]` for advanced authorization behind the stable `AuthorizationProvider` contract.

## Reference-only libraries

FastAPI Users is useful to study for registration/reset/verification/authentication patterns, but AuthMate should not be architected around its internals.

AuthX may be studied for JWT/cookie/CSRF/token handling patterns but is not a core dependency because it overlaps AuthMate's domain responsibilities.

## Rules

- Public AuthMate contracts never expose third-party implementation types.
- Optional libraries are imported lazily.
- Missing extras produce actionable install guidance.
- Every backend conforms to the same AuthMate contracts.
- Security dependency upgrades receive explicit review.

## SQLModel

Prefer `sqlmodel` for ordinary persisted AuthMate entities because it aligns naturally with FastAPI/Pydantic while retaining SQLAlchemy underneath.

Keep direct `sqlalchemy` available for low-level session/transaction/query/security mechanics and Alembic migrations.

## Infrastructure dependency rule

Python package dependencies are allowed when they run in-process. The restriction applies to **external infrastructure/services**, not libraries.

Allowed defaults include FastAPI, `fastapi-pagination`, Pydantic, SQLModel, SQLAlchemy, cryptography, and other in-process libraries.

Redis, RabbitMQ, Kafka, OpenSearch/Elasticsearch, object storage, Vault/cloud secret managers, external schedulers, and separate workers cannot be required baseline infrastructure. Optional adapters may support them.
