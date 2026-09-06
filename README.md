# AuthMate

**AuthMate** is a FastAPI-native identity, authorization, service-account, credential, and secret-resolution layer.

> **AuthMate gives FastAPI applications a composable security control plane for users, permissions, service identities, and delegated credentials.**

AuthMate is designed to work standalone and to compose cleanly with other FastAPI-native applications such as Hedron and ShuETL.

## Architecture principles

- **Independent by default, composable by contract.**
- **Own the contracts; reuse the mechanics.**
- **Pydantic-first public contracts.**
- **SQLModel where it cleanly fits; SQLAlchemy for advanced persistence mechanics.**
- **FastAPI-native dependency injection, security, lifespan, and OpenAPI.**
- **SQL-only infrastructure baseline** — core production functionality requires only the FastAPI application process and a relational SQL database.

A reference composition is:

```text
FastAPI
├── Hedron
├── AuthMate
├── ShuETL
└── custom APIs
```

AuthMate core does not depend on Hedron or ShuETL and does not contain their domain logic.

## Status

AuthMate is currently in the architecture and planning phase.

The complete design pack is in [`docs/plans/`](docs/plans/README.md).

## Planned capabilities

- users and local authentication;
- service accounts;
- RBAC and resource-scoped permissions;
- FastAPI `Depends` / `Security()` integration;
- generic principal and resource references;
- credential metadata and delegated credential use;
- encrypted SQL-backed secret storage;
- optional external secret providers and OIDC adapters;
- audit events;
- optional Hedron UI integration;
- ShuETL execution-identity and credential integration.

## Default deployment goal

```text
FastAPI application
+
PostgreSQL
```

SQLite should remain sufficient for local development.

No Redis, message broker, external secret manager, or external identity service is required for core functionality.
