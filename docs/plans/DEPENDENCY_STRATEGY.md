# Dependency Strategy

AuthMate owns security semantics and public contracts while reusing maintained
validation, SQL, password hashing, pagination, and optional protocol/crypto mechanics.

## MVP dependencies

| Dependency | Role |
| --- | --- |
| FastAPI | Routing, DI, request/security extraction, OpenAPI |
| Pydantic v2, pydantic-settings | Explicit public/config/extension validation |
| SQLModel, SQLAlchemy 2, Alembic | Internal tables, async transactions, reviewed migrations |
| pwdlib[argon2] | Explicitly configured Argon2id hashing/verification/rehash |
| fastapi-pagination | Collection-query mechanics behind AuthMate-owned Page schemas |
| aiosqlite (development extra) | Async SQLite local-development driver |
| psycopg with async support (PostgreSQL extra) | Production reference database driver |

Select compatible versions and packaging/driver extras in Phase 0, then publish the
exact tested matrix. Do not present the table as a verified lockfile. CI must test
minimum-supported and current-compatible dependency sets. AuthMate's core package
must import without optional provider/consumer dependencies installed.

Use standard-library CSPRNG and digest/constant-time primitives for opaque random
tokens; this does not justify implementing custom ciphers, password hashes, or JWT
validation. Opaque sessions need neither JWT signing nor itsdangerous.

Pagination always follows authorized query scoping. Public page/cursor/error models
are owned by AuthMate; third-party pagination types are not stable domain contracts.
Restrict totals and list visibility as specified in [API Design](API_DESIGN.md).

## Optional/future dependencies

`cryptography` belongs to the separately gated encrypted SQL provider. Authlib belongs
to a future OIDC adapter. PyCasbin may back a later policy adapter if requirements
justify it. `itsdangerous` can support a future bounded signed application token,
but does not provide one-time consumption/revocation by itself and is not an MVP
session dependency. Consumer adapters depend on AuthMate and their consumer packages;
core does not depend on Hedron/ShuETL/ETLantic.

All optional imports are lazy and missing extras produce actionable safe errors.
Every provider must pass the same security/lifecycle conformance checks. Dependency
upgrades require changelog/advisory review and the relevant regression suite. Reusing
a library does not transfer responsibility for correct configuration or integration.

## Infrastructure rule

In-process Python libraries are permitted. Redis, brokers, external identity/secret
managers, external schedulers, and separate worker services are never necessary for
baseline correctness. Runtime security state and mandatory audit live in SQL. The
host still provisions TLS, configuration, keys when needed, and operational maintenance.
