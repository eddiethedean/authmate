# AuthMate Planning Pack

**AuthMate** is a FastAPI-native identity, authorization,
service-account, credential, and secret-resolution layer designed to
work standalone and as a first-class companion to **Hedron** and
**ShuETL**.

> AuthMate gives FastAPI applications a composable security control
> plane for users, permissions, service identities, and delegated
> credentials.

## Ecosystem boundary

```text
Hedron    -> presentation / UI
AuthMate  -> identity / authorization / credentials
ShuETL    -> pipeline control plane
ETLantic  -> pipeline runtime
```

AuthMate core must contain no Hedron or ShuETL domain logic.
Integrations use public protocols, FastAPI dependencies, and optional
adapters.

## Core principles

> **Independent by default, composable by contract.**

> **Own the contracts; reuse the mechanics.**

> **Secure defaults, extensible by contract.**

> **Extensibility must never weaken security invariants implicitly.**

AuthMate is intentionally customizable without forks. Major capabilities should expose typed extension surfaces while AuthMate preserves security-critical invariants.

## Documents

VISION, ARCHITECTURE, IDENTITY_AND_AUTHORIZATION,
CREDENTIALS_AND_SECRETS, EXTENSIBILITY, API_DESIGN, HEDRON_INTEGRATION,
SHUETL_INTEGRATION, SECURITY_AND_AUDIT, MVP, ROADMAP,
DESIGN_DECISIONS, DEPENDENCY_STRATEGY, PYDANTIC_STRATEGY, and
FASTAPI_STRATEGY.

## Dependency philosophy

AuthMate should use mature libraries for password hashing, cryptography, OAuth/OIDC, configuration, pagination, and optional policy evaluation while keeping its own stable domain contracts.

See `DEPENDENCY_STRATEGY.md`.

## Pydantic-first contracts

Pydantic is a first-class architectural dependency, not merely FastAPI request validation.

Public domain models, configuration, discriminated unions, validation, serialization boundaries, extension payloads, and generated JSON Schema should use Pydantic wherever appropriate.

See `PYDANTIC_STRATEGY.md`.

## FastAPI-native architecture

FastAPI is a first-class integration substrate, not merely the HTTP server.

The package should fully use FastAPI routing, dependency injection, security primitives, lifespan, OpenAPI, exception handling, and testing overrides while preserving clear domain boundaries.

See `FASTAPI_STRATEGY.md`.

## SQL-only infrastructure baseline

> **SQL-only infrastructure baseline.**

Core production capability must require only the FastAPI application process and a relational SQL database.

No Redis, RabbitMQ, Kafka, Elasticsearch/OpenSearch, object store, Vault, external scheduler, separate worker service, or other infrastructure may be required for the default production deployment.

Additional services may only extend scale, interoperability, or specialized functionality.

For local development, SQLite should remain sufficient wherever practical.

## Extensibility

AuthMate should support controlled extension of user/service-account/group metadata, token claims, authenticators, authorization providers, credential types, secret providers, audit metadata, and lifecycle behavior.

Developer-extensible SQLModel persistence should pair with AuthMate-managed Alembic migrations so safe schema additions can be applied without requiring normal use of the Alembic CLI.

See `EXTENSIBILITY.md`.
