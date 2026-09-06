# Architecture

```text
FastAPI
  ├── AuthMate router
  └── Consumer routers
          │
          ▼
     AuthMate services
  ┌────────┼───────────┐
Identity  Authorization Credentials
  └────────┼───────────┘
           ▼
         Audit
           ▼
      Persistence
           │
      Secret Providers
```

## Public integration surfaces

### FastAPI dependencies

```python
Depends(authmate.current_principal)
Depends(authmate.require_authenticated())
Depends(authmate.require_permission("shuetl.pipeline.run"))
```

### Python services

```python
await authmate.authorize(...)
await authmate.require(...)
await authmate.credentials.resolve(...)
await authmate.audit.record(...)
```

### Stable protocols

Consumers should type against interfaces such as `AuthorizationProvider`, `CredentialResolver`, `PrincipalProvider`, and `AuditSink`, not AuthMate ORM models.

## Dependency direction

AuthMate core never imports Hedron or ShuETL. Optional integration packages/extras may depend on both public APIs.

## Persistence

A combined deployment may share PostgreSQL while preserving table/migration ownership:

```text
authmate_*
shuetl_*
application_*
```

SQLite is supported for development; PostgreSQL is the production reference. Security correctness must not depend on process-local state.

## Ecosystem composition principle

> **Independent by default, composable by contract.**

AuthMate is independently deployable. Cross-package interoperability uses public FastAPI routers/DI, stable Python protocols, generic principal/resource references, optional adapters/extras, and documented integration contracts.

A feature is an architectural smell if AuthMate core must understand Hedron components, ShuETL pipelines, ETLantic plans, or another consumer-domain object where a generic contract would suffice.

## Dependency boundary

```text
AuthMate API / protocols
        ↓
AuthMate services
        ↓
implementation adapters
├── pwdlib
├── cryptography
├── Authlib
└── optional Casbin
```

Consumers never depend on those implementation libraries through AuthMate's public API.

## Pydantic contract layer

```text
FastAPI
  ↓
Pydantic public/domain contracts
  ↓
AuthMate services
  ↓
SQLAlchemy persistence / provider adapters
```

Pydantic models are the stable integration surface. ORM and provider-specific objects stay internal.

## SQLModel-first persistence strategy

Use **SQLModel** by default where it cleanly unifies Pydantic domain models with relational persistence.

> **Prefer SQLModel for ordinary persisted domain entities; use SQLAlchemy directly for advanced persistence mechanics.**

SQLAlchemy remains available for complex joins/window queries, explicit transaction control, advisory locks/`SELECT ... FOR UPDATE`, bulk operations, engine/session configuration, backend-specific features, migrations, and performance-critical paths.

Alembic remains the migration tool. Do not force SQLModel where plain Pydantic or direct SQLAlchemy is clearer.

## FastAPI runtime composition

Prefer FastAPI dependency injection over global state or service locators. Use `Security()` when OpenAPI scopes add value while provider-neutral resource authorization remains authoritative. Long-lived provider resources initialize through lifespan; request-scoped sessions/resources use `yield` dependencies.

## Infrastructure baseline

The default deployment is:

```text
FastAPI application
        +
relational SQL database
```

No other service is required for core functionality. Redis/RabbitMQ, Kafka, OpenSearch/Elasticsearch, object stores, Vault/cloud secret managers, external schedulers, and separate worker fleets are optional extensions only.
