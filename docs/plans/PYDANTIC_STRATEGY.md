# Pydantic Strategy

## Principle

AuthMate should fully exploit Pydantic as the public modeling and validation layer already aligned with FastAPI.

> **Pydantic is the contract layer; SQLAlchemy is the persistence layer.**

## Use Pydantic for

- request and response models;
- public domain records;
- provider configuration;
- principal/resource references;
- authorization decisions;
- credential metadata;
- discriminated unions for credential/provider types;
- secret-safe serialization;
- validation constraints;
- JSON Schema/OpenAPI generation;
- settings through `pydantic-settings`;
- serialization boundaries between adapters/providers;
- versioned event/audit payloads.

## Model boundaries

SQLAlchemy ORM models must not leak directly through FastAPI responses. Use explicit Pydantic models between persistence and public APIs.

## Discriminated unions

Use tagged unions for extensible credential, secret-provider, and external-authenticator configurations with stable discriminator fields.

## Secret handling

Use Pydantic secret types where appropriate for write-only sensitive inputs, while ensuring secrets are never serialized into normal responses, reprs, logs, audit metadata, or OpenAPI examples.

## Validation

Use `Field`, `Annotated`, constrained metadata, field validators, and model validators for cross-field invariants. Prefer declarative Pydantic constraints over ad-hoc endpoint validation.

## Settings

Use `BaseSettings` from `pydantic-settings` for database configuration, token/session configuration, cryptographic key references, external provider configuration, and environment-specific policy.

## JSON Schema

Treat generated JSON Schema as a supported artifact for OpenAPI, configuration tooling, admin UI generation, compatibility checks, and documentation.

## TypeAdapter

Use `TypeAdapter` at adapter/plugin boundaries when validating arbitrary Pydantic-compatible payloads without inventing wrapper models.

## Stability rule

Public Pydantic models should be versioned carefully. Persistence/internal models may evolve independently.

## SQLModel relationship

For persisted AuthMate entities such as users, principals, roles, bindings, service accounts, credentials, and audit records, prefer SQLModel when one model can safely serve typed persistence and internal domain needs.

Keep separate Pydantic request/response models when security or API-shape concerns require stricter separation, especially write-only password/secret inputs, public credential metadata, redacted audit output, administrator-only fields, and external provider payloads.
