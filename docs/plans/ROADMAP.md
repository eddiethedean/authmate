# AuthMate Roadmap

AuthMate is planned as a sequence of small `0.x` releases. Each release should
leave a usable, testable foundation for the next one. A release may change public
contracts while the major version is `0`; consumers should pin a minor release and
use the conformance suite when upgrading.

The release numbers describe implementation milestones, not calendar dates. Phase
0.1 is released; later milestones are planned. No release is production-ready until
its stated exit checks and the applicable [MVP gates](MVP.md) have passing evidence.

## 0.1 — Contract preview (released)

Released as [`v0.1.0`](https://github.com/eddiethedean/authmate/tree/v0.1.0) on
2026-09-12 and published on [PyPI](https://pypi.org/project/authmate/0.1.0/).

Define and exercise the smallest end-to-end AuthMate service without promising API
stability.

Implementation contract: [Phase 0.1 Architecture & Implementation Plan](PHASE_0_1_IMPLEMENTATION_PLAN.md).

Scope:

- Pydantic `PrincipalRef`, `ResourceRef`, `AccessContext`, and
  `AuthorizationDecision` models;
- generic `PrincipalProvider`, `AuthorizationProvider`, `CredentialResolver`,
  `SecretProvider`, and `AuditSink` protocols;
- a standalone service facade with `can()`, `authorize()`, and `require()`;
- one fake resource consumer and one background caller;
- explicit error categories, redaction rules, and provider lifecycle behavior;
- package layout, supported Python range, and dependency test matrix.

Exit checks:

- direct Python calls and FastAPI dependency calls use the same service checks;
- forged principal/resource references and provider failures fail closed;
- no protocol imports Hedron, ShuETL, ETLantic, or another consumer;
- contract examples run as tests and the initial conformance fixture exists.

This release is a design and implementation spike. It is not a usable identity
system and should not manage real credentials.

## 0.2 — Persistence preview

Add the SQL foundation without exposing an incomplete authentication surface.

Scope:

- principals, users, service accounts, roles, permissions, bindings, and audit
  tables;
- SQLModel ordinary entities with SQLAlchemy transaction and locking paths;
- SQLite development and PostgreSQL reference backends;
- explicit `authmate_*` ownership and migration history;
- reviewed Alembic revisions, schema status/check/plan/upgrade APIs, and model
  registry validation;
- bounded pagination, optimistic version checks, and database-time handling.

Exit checks:

- fresh install, upgrade, drift detection, interrupted upgrade, and concurrent
  migrator tests pass on both databases;
- custom user/service-account metadata cannot replace reserved security fields or
  register duplicate tables;
- production startup checks schema compatibility but does not infer or apply DDL;
- unrelated consumer tables remain untouched in a shared database.

No login or secret-resolution endpoint is advertised in `0.2`.

## 0.3 — Local authentication preview

Deliver local users and server-side browser sessions.

Scope:

- operator bootstrap and recovery procedure;
- normalized usernames and Argon2id password hashing;
- opaque SQL-backed sessions with idle and absolute expiry;
- logout, authentication-epoch invalidation, password change, and temporary
  password restriction;
- cookie security, origin validation, CSRF tokens, login-CSRF protection, and
  sanitized authentication errors;
- SQL-backed login rate limits and bounded password-hash concurrency.

Exit checks:

- unknown, disabled, and incorrect credentials have indistinguishable responses;
- concurrent bootstrap can create only one initial administrator;
- revocation is observed by independent application instances sharing PostgreSQL;
- session, CSRF, origin, rate-limit, password-policy, and redaction tests pass;
- session behavior is covered by G02–G04 where applicable.

This release supports local browser authentication only. It does not include JWT,
refresh tokens, OIDC, self-registration, email recovery, or MFA.

## 0.4 — Authorization preview

Make AuthMate useful to protected application endpoints and background services.

Scope:

- exact registered actions and resource types;
- realm, resource-type, and exact-resource RBAC scopes;
- resource lookup boundaries and SQL-filtered list visibility;
- generic actor/effective-principal service-account assumption;
- explicit administrative permissions for roles, bindings, identity state, and
  account assumption;
- FastAPI `Depends` / `Security` adapters and direct service enforcement.

Exit checks:

- unknown actions/types, incompatible scopes, disabled principals, expired grants,
  forged IDs, transitive assumption, and reserved-field writes are denied;
- authorization decisions are snapshots and cannot be reused as capabilities;
- custom authorization providers cannot bypass principal-state, assumption, or
  error handling invariants;
- the exact scope matrix and G05–G06 tests pass.

Consumers register their own resource namespaces. AuthMate does not add workflow,
pipeline, schedule, or UI records to support this release.

## 0.5 — Credentials and audit preview

Add controlled credential use while keeping secret providers narrow.

Scope:

- credential metadata and exact principal-to-credential grants;
- API-key metadata as the first credential type;
- read-only, operator-controlled environment secret aliases;
- service-account API tokens with one-time reveal, digest storage, expiry, and
  revocation;
- durable audit for identity, authorization, token, grant, and credential events;
- final authorization/version checks around provider I/O;
- no raw-secret HTTP read endpoint.

Exit checks:

- callers cannot select arbitrary environment variables, paths, URLs, or provider
  configuration;
- metadata, roles, and token possession never imply secret use without an exact
  grant;
- release audit commits before a secret is returned, and audit/provider failure
  fails closed;
- resolved values are absent from logs, errors, traces, responses, reports, and
  audit metadata;
- G07–G09 tests pass, including crash and revocation boundaries.

Encrypted SQL storage is deliberately outside this release. It needs its own
format, key-rotation, nonce, restore, and corruption tests.

## 0.6 — Standalone MVP

Combine the `0.1`–`0.5` capabilities into a supported standalone package.

Scope:

- complete proposed HTTP surface under `/api/auth`;
- stable error envelope, bounded cursor/page behavior, and OpenAPI contracts;
- operator documentation for deployment, bootstrap, migrations, backup/restore,
  retention, readiness, and maintenance;
- full SQLite local and PostgreSQL multi-instance CI;
- public consumer conformance kit and generic integration example;
- host-lifespan composition, cleanup, dependency overrides, and scoped exception
  handling.

Exit checks:

- all [MVP gates G01–G12](MVP.md) pass with recorded evidence;
- security review resolves critical and high findings;
- supported dependency versions, migration compatibility, resource bounds, and
  operational recovery are documented;
- the package remains usable without Hedron, ShuETL, ETLantic, Redis, a broker,
  an external identity service, or an external secret manager.

`0.6` is the first release that may be evaluated as a standalone MVP. It is still
pre-1.0 and may require breaking contract changes.

## 0.7 — Operational hardening

Improve the standalone MVP for sustained operation without changing the baseline
security model.

Scope:

- operator session/token administration and safer bulk revocation;
- audit retention and export with a SQL outbox and idempotent delivery;
- richer readiness, migration, lock, rate-limit, and provider diagnostics;
- documented load limits, maintenance leases, and backup/restore drills;
- optional encrypted SQL secret provider after its separate crypto release gate.

Exit checks:

- audit export is at-least-once and consumers can deduplicate event IDs;
- restoration invalidates authentication state and reconciles policy before traffic
  resumes;
- maintenance is bounded and correctness does not depend on a cleanup process;
- encrypted storage, if included, passes its own key lifecycle and corruption gates.

## 0.8 — Optional authentication and provider ecosystem

Add integrations that remain optional and cannot become core infrastructure.

Scope may include:

- OIDC/OAuth2 federation and identity linking;
- MFA, verification, and recovery flows;
- external secret-manager adapters;
- writable-provider rotation and health workflows;
- proxy identity, client-certificate, or workload-identity adapters;
- a carefully scoped custom-claims/token adapter.

Each integration ships separately where practical, has an explicit threat model,
versioned configuration, provider conformance tests, and failure/timeout behavior.
`0.8` does not make any external identity or secret service a baseline dependency.

## 0.9 — Release candidate

Freeze the `1.0` contract candidates and prove upgradeability.

Scope:

- API, Pydantic schema, protocol, permission-catalog, and migration review;
- deprecation notes and one documented upgrade path from the supported `0.8` line;
- performance and failure testing at published limits;
- security review, dependency/advisory review, and threat-model refresh;
- final standalone examples and release documentation.

Exit checks:

- no unresolved critical/high security findings;
- all public contract changes are documented and the conformance kit passes;
- upgrade, rollback/recovery, redaction, replica, and provider-failure suites pass;
- supported combinations and known limitations are published.

## 1.0 — Stable core

Declare the standalone AuthMate core contracts stable: local authentication,
opaque sessions, service accounts, exact RBAC, generic delegated identity,
credential grants, approved secret-provider interfaces, durable SQL audit, and
FastAPI/Python integration.

`1.0` does not freeze optional federation, policy languages, tenancy, consumer
adapters, or UI components. Those remain separately versioned extensions. Hedron,
ShuETL, and any other consumer own their adapters, domain rules, version pins, and
compatibility CI; their behavior is evidence about an adapter, not a prerequisite
for the AuthMate core release.

## Consumer tracks

Consumers may build against any published contract preview. Their adapter work runs
in their repositories or separate integration packages and should pin both AuthMate
and the consumer/upstream versions. A consumer compatibility failure can block that
adapter release, but it does not block an AuthMate core release unless the failure
reveals a defect in an AuthMate-owned contract.
