# Design Decisions

Status: planning decisions, not implemented guarantees. This register supersedes
contradictory wording in earlier drafts. [MVP](MVP.md) defines release evidence.

| ID | Decision |
| --- | --- |
| D01 | AuthMate is a standalone embeddable package, independent of consumers. |
| D02 | FastAPI adapters are first-class; domain services also work without HTTP. |
| D03 | Consumers register generic action/resource contracts; core owns no consumer domain. |
| D04 | Users/service accounts share immutable principal identities and authorization. |
| D05 | RBAC uses explicit realm/type/exact scopes; no MVP inheritance, groups, or wildcard strings. |
| D06 | Credential policy and secret material are separate; use requires one exact grant. |
| D07 | Resolve late, recheck state, commit release audit, and never persist resolved values. |
| D08 | UI visibility is advisory; server services enforce current authority. |
| D09 | Consumers adapt to AuthMate's public protocols; core does not adapt to their internals. |
| D10 | Shared databases retain explicit table and migration ownership. |
| D11 | SQLite is for local development; PostgreSQL is the production reference. |
| D12 | Core releases require generic conformance tests; real integration gates belong to consumer adapters. |
| D13 | Typed extensions support customization without forks within a stated release scope. |
| D14 | Reuse maintained security mechanics; optional features bring optional dependencies. |
| D15 | Pydantic public contracts are separate from ORM and provider objects. |
| D16 | SQLModel handles ordinary internal tables; SQLAlchemy handles advanced persistence and transactions. |
| D17 | FastAPI DI/lifespan/OpenAPI compose explicitly without taking over the host app. |
| D18 | SQL-only infrastructure is the baseline; operational configuration and keys are still required. |
| D19 | Mandatory service checks remain authoritative with every configured provider. |
| D20 | Programmatic Alembic manages reviewed revisions; production startup checks and does not infer/apply DDL. |
| D21 | Custom claims are a later token-adapter feature; separate metadata cannot override reserved fields. |
| D22 | MVP uses opaque SQL browser sessions and separate revocable service-account API tokens. |
| D23 | Revocation, rate limits, CSRF, bootstrap/recovery, and audit failure behavior are MVP gates. |
| D24 | Environment aliases are the read-only MVP secret provider; encrypted SQL has a separate later release gate. |
| D25 | MVP is single-realm; arbitrary tenant metadata does not establish isolation. |
| D26 | Delegation is generic actor/effective-principal assumption; consumers own workload approvals and execution constraints. |
| D27 | No check can retract an already released secret or atomically cancel external I/O. |

## Rationale for revised decisions

D09/D12/D26 preserve AuthMate's broad purpose: ShuETL/Hedron and other consumers
implement its contracts and own their domain constraints. A conformance kit proves
AuthMate independently; actual adapter compatibility needs separate versioned evidence.
There are no core workload version records, schedule rules, or consumer callbacks.

D20 retains managed migrations and custom models while removing the assumption that
nullable additions/indexes/constraints are universally safe to execute at startup.
Migrations are reviewed release artifacts applied by one migrator. See [Migrations](MIGRATIONS.md).

D21/D22 resolve the open session-versus-JWT decision in favor of current SQL state
and straightforward revocation. Custom token signing/refresh machinery is deferred;
server-side typed metadata remains available without exposing claims to clients.

D23/D24 make MVP scope unconditional. Baseline protections cannot wait for an
operational-security phase, and a crypto review cannot silently change what ships.
The environment provider supports a useful standalone release while encrypted storage
gets a separate format/key-lifecycle design and test gate.

## Implementation decisions to resolve in Phase 0

These are concrete engineering gates, not permission to weaken the decisions above:

- Exact SQL constraints/indexes and guard-lock query ordering; prove concurrency on
  PostgreSQL and local serialized-write behavior on SQLite.
- Versioned public protocol signatures, full registered permission catalog, and
  immutable/custom model registry construction.
- Tested Python/library/database support matrix and selected async driver versions.
- Benchmarked password hash/rate/lock/size budgets and startup error behavior.
- Packaged core/extension revision layout and supported upgrade/schema ranges.
- Operator retention/storage policy, recovery drill, and release evidence format.

Future features need their own ADRs: encrypted secret format/key lifecycle, federation
identity linking, JWT/refresh validation, tenant isolation, generalized hooks, and
reliable audit export. No approval of those features is implied by this plan.
