# Architecture

AuthMate is an embeddable FastAPI identity, authorization, and credential package.
It defines its own public contracts independently of consumer applications.

```text
FastAPI routers/dependencies       Trusted Python/background callers
                 \                  /
                  AuthMate service facade
                  /         |          \
           Identity   Authorization   Credentials
                  \         |          /
                   SQL unit of work + audit
                        |         \
                   Persistence    Secret-provider adapters
```

Mandatory checks live in service wrappers, so direct Python calls cannot accidentally
skip rules enforced only by HTTP routes. Providers supply mechanisms behind those
checks. Audit is part of each protected operation, not an asynchronous afterthought.
Secret-provider I/O is bounded and happens outside held SQL write locks; release
requires a final current-state check and committed audit event.

## Composition and contracts

FastAPI dependencies handle current identity, permission enforcement, and resource
lookup. A resource-specific dependency must derive its ResourceRef from a trusted
lookup; `require_permission("myapp.report.read")` without a resource is insufficient
for an exact-resource action. Python `can`, `authorize`, `require`, and credential
resolution use explicit context and do not need HTTP request state.

[Consumer Contracts](CONSUMER_CONTRACTS.md) defines PrincipalRef, AccessContext,
ResourceRef, decisions, provider protocols, and lifecycle/error semantics. Consumers
register generic action/resource namespaces and adapt their own APIs to AuthMate.
Core never imports Hedron, ShuETL, ETLantic, or their ORM/domain models. Their adapters
and compatibility tests are consumer-owned and cannot block a core release.

AuthMate owns identity/security semantics and reuses maintained hashing, validation,
SQL, and optional cryptographic/protocol libraries behind implementation adapters.
Public Pydantic values remain separate from persistence/provider objects. SQLModel
models represent ordinary internal tables; SQLAlchemy handles explicit transactions,
async sessions, locking, and advanced queries.

## Deployment and state

Default production deployment is one or more FastAPI processes plus PostgreSQL.
SQLite is a local-development backend. SQL stores session/token digests, security
state, roles/grants, credential metadata, rate-limit state, and durable audit. Correctness
never relies on process-local positive caches, a cleanup timer, Redis, or a broker.

Environment-backed secret references are the MVP provider. External identity/secret
services and the encrypted SQL provider are optional later capabilities. Process
configuration, TLS, operator-provisioned secrets, backups, and reviewed migrations
remain deployment responsibilities even though no additional service is mandatory.

Each AuthMate instance has its own explicit configuration/provider registry and unit
of work. No module-global current user, service locator, or shared request session.
Host lifespan explicitly enters/closes AuthMate resources; failed startup cleans up
partially opened providers. Async sessions never outlive their operation or cross
concurrent tasks. See [FastAPI Strategy](FASTAPI_STRATEGY.md).

## Schema and isolation

AuthMate owns only its registered `authmate_*` tables and migration history, even
when it shares a database with consumers. User/service-account metadata extensions
use a validated model registry and reviewed migrations. Production startup verifies
schema compatibility; it does not generate or automatically apply DDL. See
[Persistence and Managed Migrations](MIGRATIONS.md).

MVP supports one security realm per deployment. Namespaces partition action names,
not tenants. Generic resource strings or custom claims do not establish tenant
isolation. Strong tenant boundaries require a future schema/contract design or
separate deployments today.
