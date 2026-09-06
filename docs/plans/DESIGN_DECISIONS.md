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

## Open ADRs

- session vs JWT/refresh-token default;
- exact password-hashing library/parameters;
- encrypted database secret-store design;
- resource-scope inheritance rules;
- role/permission registration by consumer packages;
- service-account credential binding representation;
- audit retention/export;
- external authenticator protocol;
- optional Hedron integration packaging;
- migration coordination when AuthMate and ShuETL share a database.

## D14 — Reuse mature security mechanics

AuthMate owns identity/security semantics but delegates commodity mechanics to maintained libraries. Initial choices: `pwdlib[argon2]`, `cryptography`, `itsdangerous`, `pydantic-settings`, optional Authlib, and optional Casbin.

## D15 — Pydantic is the public contract layer

AuthMate uses Pydantic for public/domain contracts, configuration, validation, serialization, and schema generation while SQLAlchemy remains available beneath persistence.

## D16 — Prefer SQLModel for ordinary persisted entities

AuthMate uses SQLModel as the default persistence modeling layer where it cleanly combines Pydantic and SQLAlchemy, retaining direct SQLAlchemy for advanced cases.

## D17 — FastAPI is the runtime integration substrate

AuthMate directly uses FastAPI DI, security primitives, lifespan, OpenAPI, exception handling, and dependency overrides instead of duplicating those mechanisms.

## D18 — SQL-only infrastructure baseline

AuthMate's default production deployment requires only the FastAPI application process and a relational SQL database. External identity providers, secret managers, caches, and messaging systems may extend AuthMate but cannot become baseline requirements.
