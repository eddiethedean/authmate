# AuthMate MVP

## Objective and fixed scope

Deliver a standalone, single-realm FastAPI identity and credential layer with tested
public consumer contracts. This is a release target, not a claim of implemented
security. All checkboxes below are open until implementation evidence exists.

Include users, operator provisioning/recovery, opaque browser sessions, revocation,
SQL rate limits, service accounts/API tokens, exact RBAC scopes, generic service-account
assumption, credential metadata/exact grants, the read-only environment provider,
durable SQL audit, FastAPI/Python service APIs, and reviewed managed migrations.
Support typed user/service-account metadata, registered providers, and SQLite local /
PostgreSQL production reference backends. One deployment is one security realm.

Exclude self-registration/email flows, JWT/refresh tokens, OIDC/MFA, groups/tenancy,
policy languages, encrypted SQL secrets, writable-provider rotation, generalized
lifecycle hooks, reliable remote audit export, and consumer-specific UI/workflow code.
These are explicit follow-on work, not optional exceptions hidden inside MVP.

## Implementation and release gates

| ID | Required evidence |
| --- | --- |
| G01 | Composition: standalone and embedded FastAPI apps, two isolated instances, lifespan cleanup, direct background calls, host exception-handler preservation |
| G02 | Authentication: Argon2id and bounded hashing; generic failures; password change/reset; concurrent single-use bootstrap; restricted temporary-password session |
| G03 | Sessions/tokens: cookie/CSRF/login-CSRF protections; expiry, logout, epoch invalidation, wrong token type, ambiguous auth, one-time machine-token response |
| G04 | Replica state: two independent instances sharing PostgreSQL observe committed revocations; simultaneous rate-limit reservations, disable versus release, role/grant changes |
| G05 | Authorization: exact/type/realm scope matrix; unknown action/type denial; scope compatibility; forged IDs; reserved-field writes; no implicit owner/admin secret use; list/count visibility |
| G06 | Delegation: actor needs exact account assumption; effective account needs independent permission/grant; disabled actor/account, forged actor IDs at transport boundaries, and transitive assumption denied |
| G07 | Secrets: alias allowlist prevents arbitrary environment access; read-only capability errors; expiry, changed reference/version, unavailable provider, final recheck, bounded plaintext lifetime |
| G08 | Audit: mutation+event atomicity; failed/denied attempt persistence; release-before-return ordering; SQL/provider failure and crash windows; truthful outcomes and bounded volume |
| G09 | Redaction: real password/token/secret values absent from metadata, schema examples/defaults, validation errors, reprs, logging, tracing, audit, and fake-consumer reports; only intended issuance responses reveal new tokens |
| G10 | Persistence: fresh install/upgrade, custom model selection without duplicate tables, reserved schema protection, concurrent migrators, interrupted upgrade, drift checks, unrelated-table preservation |
| G11 | Operations: backup/restore with session/token invalidation and policy reconciliation; maintenance without correctness dependence; readiness failures; bounded lock/hash/login/provider load |
| G12 | Public contract conformance: generic report consumer and background client; provider validation/failure/cancellation; stable error schemas; optional libraries and sibling packages absent |

- [ ] G01–G12 pass with recorded commands, supported versions, and results.
- [ ] SQLite parity and PostgreSQL concurrency tests both run in CI.
- [ ] Release publishes supported Python/FastAPI/Pydantic/SQLModel/SQLAlchemy/database
  versions and minimum/latest dependency test results.
- [ ] An implementation threat-model review resolves critical/high findings; no
  unchecked feature is described as production-ready.
- [ ] Password/rate/size/session defaults are documented and load-tested.
- [ ] Retention, migration lock budgets, recovery, and deployment configuration have
  operator instructions and tested failure paths.

Actual Hedron/ShuETL/ETLantic compatibility is established by consumer-owned adapter
suites. AuthMate's contract fakes do not certify those integrations, and missing
consumer adapters do not block this standalone MVP.

## Dependency and framework gates

- [ ] Public/domain models use Pydantic v2 with explicit input/output boundaries;
  tagged provider/config unions and registry collision validation exist.
- [ ] SQLModel is internal; SQLAlchemy async sessions have explicit service commits.
- [ ] `pwdlib[argon2]`, `pydantic-settings`, and Alembic are configured explicitly.
- [ ] Routers, Depends/Security, yield cleanup, lifespan, and dependency overrides
  compose without installing a second framework or overriding host behavior.
- [ ] JSON media-type behavior and sanitized errors are tested on supported FastAPI
  versions; framework defaults alone are not evidence of CSRF protection.
- [ ] Core requires no Redis, broker, external identity/secret manager, worker fleet,
  or encrypted-provider dependency.
