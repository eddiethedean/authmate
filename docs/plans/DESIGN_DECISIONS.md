# Initial Design Decisions

1. **Separate package** — AuthMate is not embedded in Hedron or ShuETL.
2. **FastAPI-native** — FastAPI dependencies and routers are first-class public surfaces.
3. **Generic resources** — consumer packages define resource namespaces without AuthMate domain knowledge.
4. **Unified principals** — users and service accounts share the authorization model.
5. **RBAC first** — roles + permissions + scopes before any general policy language.
6. **Credential/secret separation** — persistent credentials reference secret providers.
7. **Late resolution** — secrets resolve only when an authorized operation needs them.
8. **No UI authority** — Hedron visibility never replaces server authorization.
9. **Protocol-based ShuETL integration** — ShuETL depends on public interfaces, not ORM models.
10. **Shared DB allowed, ownership separate** — AuthMate owns `authmate_*` tables/migrations.
11. **SQLite local, PostgreSQL reference production backend.**
12. **Compatibility is a release gate** — Hedron + AuthMate + ShuETL is tested as a supported composition.
13. **Secure defaults, extensible by contract** — major capabilities expose typed extension surfaces without requiring forks.
14. **Security invariants remain authoritative** — extension hooks cannot implicitly weaken reserved security semantics.

## Open ADRs

- session vs JWT/refresh-token default;
- exact password-hashing parameters;
- encrypted database secret-store design;
- resource-scope inheritance rules;
- role/permission registration by consumer packages;
- service-account credential binding representation;
- audit retention/export;
- external authenticator protocol;
- optional Hedron integration packaging;
- migration coordination when AuthMate and ShuETL share a database;
- exact supported set of extensible persistence models;
- managed migration revision storage/versioning;
- safe-vs-unsafe automatic DDL classification;
- lifecycle hook ordering/transaction semantics;
- reserved token claim registry and custom-claim collision policy.

## D14 — Reuse mature security mechanics

AuthMate owns identity/security semantics but delegates commodity mechanics to maintained libraries. Initial choices: `pwdlib[argon2]`, `cryptography`, `itsdangerous`, `pydantic-settings`, optional Authlib, and optional Casbin.

## D15 — Pydantic is the public contract layer

AuthMate uses Pydantic for public/domain contracts, configuration, validation, serialization, extension payloads, and schema generation while SQLAlchemy remains available beneath persistence.

## D16 — Prefer SQLModel for ordinary persisted entities

AuthMate uses SQLModel as the default persistence modeling layer where it cleanly combines Pydantic and SQLAlchemy, retaining direct SQLAlchemy for advanced cases.

Developer-extensible persisted entities should normally inherit from AuthMate non-table SQLModel base models and define the effective table model themselves. Avoid relying on accidental SQLAlchemy mapped-table inheritance semantics.

## D17 — FastAPI is the runtime integration substrate

AuthMate directly uses FastAPI DI, security primitives, lifespan, OpenAPI, exception handling, and dependency overrides instead of duplicating those mechanisms.

## D18 — SQL-only infrastructure baseline

AuthMate's default production deployment requires only the FastAPI application process and a relational SQL database. External identity providers, secret managers, caches, and messaging systems may extend AuthMate but cannot become baseline requirements.

## D19 — Secure defaults, extensible by contract

**Decision:** Every major AuthMate subsystem should expose a stable typed extension surface where practical, including persisted model metadata, authentication, authorization, token claims, credential types, secret providers, audit metadata, and lifecycle behavior.

**Reason:** AuthMate is an embeddable application capability and must adapt to host-application domain needs without forks or monkey-patching.

**Constraint:** Extensions may not silently override AuthMate security-critical invariants.

## D20 — Managed Alembic migrations for supported model extensions

**Decision:** AuthMate invokes Alembic programmatically and provides a schema-management API so developers normally do not need the Alembic CLI for AuthMate-owned/customized tables.

A safe automatic migration mode may apply validated additive changes. Destructive or ambiguous changes are blocked and surfaced as an explicit migration plan/error.

**Reason:** developer-extensible SQLModel entities are substantially more useful when schema evolution remains part of the AuthMate developer experience.

## D21 — Token claims are extensible but reserved claims are protected

**Decision:** Access/session token payloads support Pydantic-derived custom claim models and typed resolvers.

AuthMate retains authority over reserved claims and signing/expiry/audience/issuer/token-type invariants unless responsibility is explicitly transferred through a low-level provider contract.
