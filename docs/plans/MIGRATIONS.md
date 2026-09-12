# Persistence and Managed Migrations

## Ownership and schema

AuthMate owns an explicit table allowlist under `authmate_*`, including its own
`authmate_alembic_version` table. Prefix alone is not permission to inspect or drop
host tables. Alembic filters must exclude consumer and other packages' metadata.
A shared database does not transfer schema ownership. No cross-package foreign keys
are required; opaque resource references are validated by consumer services.

MVP relational records include principals and user/service-account subtypes, roles,
role permission entries, scoped role bindings, sessions, API-token digests, credentials,
credential grants, audit events, rate-limit buckets, bootstrap
state, and a security-state revision/lock row. The implementation schema review
must enumerate every foreign key, uniqueness/check constraint, expiry index, and
on-delete behavior before coding routes. Grants/bindings require non-null valid
references; discriminated scope checks prevent contradictory type/ID fields.

Use SQLModel for ordinary persistence and SQLAlchemy 2 async sessions for transaction,
locking, and query mechanics. Public Pydantic models always remain separate. Use
one session per unit of work, never share an AsyncSession across concurrent tasks.
Transactions are explicit in services; `yield` dependency cleanup must not be where
security-sensitive success commits. Fresh SQLite databases enable foreign keys.
SQLite uses serialized writes and bounded busy retries for local parity; PostgreSQL
is required to test real multi-replica behavior and is the production reference.

## Versioned revisions, not runtime schema inference

AuthMate distributes immutable Alembic revisions for core tables. Host extensions
ship reviewed revisions in a separate, named branch/version table with explicit
core-version compatibility. Revisions are source-controlled release artifacts,
including data migrations; a production process never generates revision files.

The programmatic schema API retains the no-Alembic-CLI developer experience:

```python
auth.schema.status()  # installed revisions and compatibility
auth.schema.plan()    # read-only candidate changes for development/review
auth.schema.check()   # verify supported revision heads and model drift
auth.schema.upgrade() # apply already reviewed, packaged revisions
```

Names are proposed contracts, not implemented methods. Production startup performs
`check()` only and fails readiness for incompatible heads, drift, missing revisions,
or mismatched extension models. Runtime database credentials do not need DDL rights.
An operator invokes `upgrade()` in a separate deployment step using migration
credentials. Only one migrator runs: PostgreSQL uses a database advisory lock;
SQLite development uses an exclusive migration workflow. Set bounded lock/statement
timeouts and fail on concurrent migrators instead of racing.

Alembic autogeneration produces candidates requiring review; it cannot reliably
infer renames and all constraint changes.
[Source: Alembic autogenerate limitations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html).
Nullable columns, defaults, indexes, and constraints may still lock tables, rewrite
data, or fail validation. They are not universally safe startup migrations.
`auto_migrate="safe"` is not an MVP setting. An explicit disposable-development mode
may apply packaged revisions, but never infer and execute unreviewed DDL.

## Custom models

User and ServiceAccount support additive metadata through non-table SQLModel bases
and a model factory/registry that selects exactly one mapped class per table before
metadata construction. Default models must not register the same table before a
custom model is selected. Core repositories target the registered model; no global
monkey-patching or inherited mapped table replacement is supported.

Validate required field types, primary/foreign keys, constraints, relationships,
and reserved-field immutability at startup. Custom persistence fields do not become
HTTP input/output automatically; register an explicit metadata schema and field
allowlist. Only trusted deployment code can register models. Prefer a host-owned
extension table for changes needing independent lifecycle or complex relations.

## Upgrade and recovery gates

Test fresh install, upgrade from every supported prior release, extension branch
ordering, drift detection, concurrent migrators, interrupted migration retry, and
preservation of unrelated tables on SQLite and PostgreSQL. PostgreSQL deployment
checks cover realistic data size and lock budgets, not just an empty test database.

Use expand/backfill/contract steps for incompatible changes; release metadata
declares supported schema ranges for mixed-version rollouts. Back up before upgrades
and prove restoration, including matching keys when encrypted storage is used.
Destructive downgrade is never automatic. Document rollback via compatible binaries
or restoration and the resulting security-state/revocation recovery procedure.
A restored snapshot can revive old sessions/grants: invalidate all sessions/API
tokens and reconcile policy changes before serving traffic after a restore.
