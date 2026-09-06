# AuthMate MVP

## Objective

Provide a production-credible FastAPI identity and credential layer that works standalone and composes cleanly with Hedron and ShuETL.

## Scope

- users and service accounts;
- secure local authentication;
- roles, permissions, resource-scoped bindings;
- Python authorization API and FastAPI dependencies;
- credential metadata and grants;
- environment secret provider;
- encrypted DB provider only if its crypto design is approved before freeze;
- audit events;
- SQLModel/SQLAlchemy + Alembic;
- SQLite development and PostgreSQL production reference;
- stable consumer protocols;
- Hedron/ShuETL/full-stack compatibility CI.

## Acceptance criteria

- [ ] Mounts into an existing FastAPI app.
- [ ] Users authenticate securely.
- [ ] Disabled principals cannot authenticate or perform newly authorized work.
- [ ] Generic resource refs support scoped RBAC.
- [ ] FastAPI endpoints enforce permissions declaratively.
- [ ] Background services authorize without HTTP request state.
- [ ] Service accounts receive resource and credential permissions.
- [ ] Secret resolution requires explicit authorization and is audited.
- [ ] ShuETL can execute a pipeline as a service account using AuthMate credential references.
- [ ] Hedron consumes principal/authorization APIs without AuthMate core importing Hedron.
- [ ] One FastAPI app can mount Hedron + AuthMate + ShuETL.
- [ ] PostgreSQL tests cover multi-replica security state.
- [ ] OpenAPI/log/audit redaction tests prove secrets are not exposed.

## Dependency requirements

- [ ] `pwdlib[argon2]` handles password hashing.
- [ ] `cryptography` handles local encrypted-secret implementation.
- [ ] `itsdangerous` or an ADR-approved equivalent handles bounded signed tokens.
- [ ] `pydantic-settings` handles application configuration.
- [ ] OAuth/OIDC remains optional behind an Authlib adapter.
- [ ] Advanced authorization remains optional behind the provider contract.

## Pydantic requirements

- [ ] Public API/domain models use Pydantic rather than ORM objects.
- [ ] Credential/provider configurations use discriminated unions.
- [ ] Sensitive inputs use secret-safe Pydantic types/serialization rules.
- [ ] Cross-field security invariants use model validation where appropriate.
- [ ] Public JSON Schema/OpenAPI comes from the same Pydantic contracts.

## SQLModel requirements

- [ ] Persisted core entities use SQLModel where it improves clarity and avoids duplicate Pydantic/ORM models.
- [ ] Sensitive API models remain separate when persistence models would expose fields that should not be serialized.
- [ ] Direct SQLAlchemy is used for advanced transaction/locking/query cases.

## FastAPI requirements

- [ ] Routers compose cleanly into an existing FastAPI app.
- [ ] DI is the primary runtime composition mechanism.
- [ ] `Security()`/FastAPI security schemes are used where appropriate.
- [ ] Request-scoped DB/provider resources use `yield` dependencies.
- [ ] Long-lived resources use lifespan.
- [ ] Strict content-type behavior remains enabled.
- [ ] Stable custom exception handlers/error envelopes exist.
- [ ] Dependency overrides support integration/security tests.

## SQL-only infrastructure acceptance

- [ ] Core production functionality requires only FastAPI + relational SQL.
- [ ] SQLite supports local development.
- [ ] PostgreSQL is the production reference backend.
- [ ] Local authentication/RBAC/service accounts/audit require no external service.
- [ ] Credential metadata and optional encrypted secret storage require no external secret manager.
- [ ] External OIDC/secret-manager systems remain optional integrations.
- [ ] No Redis/message broker/cache is required for correctness.
