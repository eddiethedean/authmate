# AuthMate Planning Pack

AuthMate is a broadly designed FastAPI identity, authorization, service-account,
credential, and secret-resolution package. It owns the contracts consumers implement;
Hedron, ShuETL, and other consumers own their adapters and domain behavior.

Status: plans only. The 2026-09-12 review tightened security contracts, removed
consumer coupling, and made release criteria testable. No implementation gate is
marked complete. See [review findings and fixes](PLAN_REVIEW.md).

## Reading order and authority

| Document | Defines |
| --- | --- |
| [Vision](VISION.md) | Product scope and ownership |
| [Design Decisions](DESIGN_DECISIONS.md) | Selected decisions and remaining Phase 0 questions |
| [MVP](MVP.md) | Fixed scope and required release evidence |
| [Roadmap](ROADMAP.md) | Sequencing and later features |
| [Architecture](ARCHITECTURE.md) | Service boundaries and deployment |
| [Consumer Contracts](CONSUMER_CONTRACTS.md) | AuthMate-owned public integration surface |
| [Authentication](AUTHENTICATION.md) | Sessions, passwords, bootstrap, API tokens, CSRF, rate limits |
| [Identity and Authorization](IDENTITY_AND_AUTHORIZATION.md) | Principal trust, scope matching, admin powers, generic assumption |
| [Credentials and Secrets](CREDENTIALS_AND_SECRETS.md) | Exact grants, allowed providers, secret release, future encryption gate |
| [Security and Audit](SECURITY_AND_AUDIT.md) | Threat model, transactions, failures, recovery, operations |
| [API Design](API_DESIGN.md) | Proposed HTTP paths, permission mapping, errors |
| [Persistence and Managed Migrations](MIGRATIONS.md) | SQL ownership, custom models, reviewed upgrades |
| [Extensibility](EXTENSIBILITY.md) | Supported extension families and invariant enforcement |
| [Dependency Strategy](DEPENDENCY_STRATEGY.md) | Core/optional package boundaries and version evidence |
| [Pydantic Strategy](PYDANTIC_STRATEGY.md) | Public validation and serialization boundaries |
| [FastAPI Strategy](FASTAPI_STRATEGY.md) | Host composition and HTTP adaptation |
| [Hedron Notes](HEDRON_INTEGRATION.md) | Optional consumer-owned adapter guidance |
| [ShuETL Notes](SHUETL_INTEGRATION.md) | Optional consumer-owned adapter guidance |

Design Decisions and MVP govern scope; the dedicated contract documents specify
behavior. Consumer notes are non-normative examples and cannot add requirements to
core. API names/signatures are proposals until the Phase 0 implementation validates
them. Any scope change must update the decision, contract, and corresponding MVP gate.

## Baseline

Production reference: FastAPI processes + PostgreSQL + operator-supplied configuration
and secrets. SQLite is local development. MVP is single-realm and uses opaque SQL
sessions, exact RBAC, generic service-account assumption, environment secret aliases,
and mandatory SQL audit. There is no required Redis, broker, external identity/secret
service, scheduler, worker fleet, or sibling package.

Typed model/provider customization and programmatic migrations remain central.
Production migrations are reviewed artifacts run explicitly; app startup checks
compatibility. Federation, JWT/refresh, encrypted SQL secrets, groups/tenancy, and
general hook/export frameworks are later features with their own security gates.
