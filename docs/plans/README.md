# AuthMate Planning Pack

**AuthMate** is a FastAPI-native identity, authorization,
service-account, credential, and secret-resolution layer designed to
work standalone and as a first-class companion to **Hedron** and
**ShuETL**.

> AuthMate gives FastAPI applications a composable security control
> plane for users, permissions, service identities, and delegated
> credentials.

## Ecosystem boundary

``` text
Hedron    -> presentation / UI
AuthMate  -> identity / authorization / credentials
ShuETL    -> pipeline control plane
ETLantic  -> pipeline runtime
```

AuthMate core must contain no Hedron or ShuETL domain logic.
Integrations use public protocols, FastAPI dependencies, and optional
adapters.

## Documents

VISION, ARCHITECTURE, IDENTITY_AND_AUTHORIZATION,
CREDENTIALS_AND_SECRETS, API_DESIGN, HEDRON_INTEGRATION,
SHUETL_INTEGRATION, SECURITY_AND_AUDIT, MVP, ROADMAP, and
DESIGN_DECISIONS.

## Dependency philosophy

> **Own the contracts; reuse the mechanics.**

AuthMate should use mature libraries for password hashing, cryptography, OAuth/OIDC, configuration, and optional policy evaluation while keeping its own stable domain contracts.

See `DEPENDENCY_STRATEGY.md`.

## Pydantic-first contracts

Pydantic is a first-class architectural dependency, not merely FastAPI request validation.

Public domain models, configuration, discriminated unions, validation, serialization boundaries, and generated JSON Schema should use Pydantic wherever appropriate.

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
