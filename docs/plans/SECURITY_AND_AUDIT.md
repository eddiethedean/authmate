# Security and Audit

## Threat model and deployment boundary

Protect against unauthenticated callers, compromised low-privilege accounts,
forged resource/principal references, CSRF, credential substitution, stale work,
malicious input, and replicas observing inconsistent security state. SQL, trusted
host code, and registered in-process extensions are inside the trust boundary.
AuthMate does not sandbox hostile Python plugins or arbitrary pipeline code and
does not protect plaintext from a compromised application process.

A copied database should not reveal passwords or raw bearer tokens; encrypted
secret storage additionally requires keys absent from that copy. A database writer
can change grants/state, so SQL administration remains security-critical. SQL-only
means no mandatory remote service, not no TLS, operator secrets, backups, migration
step, or maintenance. Production is PostgreSQL; SQLite support is local development.

## Required MVP controls

- SQL-backed session/token revocation and bounded expiry; password lifecycle and
  administrator bootstrap/recovery from [Authentication](AUTHENTICATION.md).
- SQL-coordinated rate limits, bounded hash concurrency, trusted proxy configuration,
  explicit allowed origins, CSRF checks, TLS, and no-store authentication responses.
- Exact authorization scopes, separate secret-use grants, and generic actor/effective-principal validation.
- Schema allowlists preventing mass assignment, bounded input/page/provider sizes,
  and centralized redaction for logs, errors, traces, and serialization.
- Fail closed on unavailable authentication/authorization state or required audit.
- No startup-generated DDL; reviewed upgrades and restore drills.

Initial bounds are 64 KiB per AuthMate JSON request, 64 KiB per resolved secret,
4 KiB per audit metadata object, and page size at most 100. Validate before allocation
where possible, including requests without Content-Length. Hosts can lower these;
raising them requires load tests and an explicit configuration change.

## Audit contract and transaction semantics

AuditEvent contains an immutable ID, schema version, event type, server timestamp,
actor principal (nullable for failed login/system events), effective execution
principal when different, resource/subject refs, request/correlation ID, outcome,
reason code, and registered bounded metadata. Unauthenticated caller-supplied names
are not recorded as authenticated actors. Never put credentials, passwords, tokens,
authorization headers, raw provider exceptions, or request bodies in events.

Security mutations and their success audit row commit in the same SQL transaction.
If insertion fails, roll back the mutation. Authentication issuance commits its
session/token and event before returning the cookie/secret. Login failures and
authorization denials use a separate bounded audit transaction so rolling back a
request does not silently erase them. If SQL audit is unavailable, access remains
denied; emit only a redacted operational signal. Never report that an event was
persisted when it was not.

Credential resolution uses durable attempt plus release-authorization events and
rechecks state before releasing plaintext; see
[Credentials and Secrets](CREDENTIALS_AND_SECRETS.md). No distributed transaction
with an external secret manager or external API is implied. Retries carry correlation
and attempt IDs so repeated attempts are distinguishable; events do not claim
exactly-once external execution.

Audit login success/failure, session/token issue/revoke, password changes/resets,
identity enable/disable, role/binding changes, assumption-permission changes, credential/grant
changes/resolution, and enforced authorization denials. A UI `can()` check is advisory
and does not generate an enforced-denial event on every render. Rate-limited repeated
unauthenticated failures may be aggregated into bounded window events; security
mutations and credential releases are never sampled. Define bucket retention and
size controls to resist audit-volume abuse.

## Durability, retention, and availability

The SQL audit store is mandatory. Optional sinks receive committed events afterwards;
sink failure cannot undo a successful operation. Reliable delivery requires a SQL
outbox, at-least-once dispatch, and idempotent event-ID handling, and is deferred
until export is implemented. In-process callbacks alone cannot promise delivery.

Normal APIs cannot edit/delete historical events. Use restricted database roles
where practical. Append-only application behavior is not cryptographic tamper
proofing against database administrators. MVP retains audit rows until an operator
runs an explicit retention/purge operation; deployment must choose retention and
storage budgets before release. Purges record policy, cutoff, actor, and row counts.
An SQL-full condition fails security-sensitive operations closed and raises readiness
alerts; it must never silently discard mandatory audit events.

No external scheduler/worker is required. Provide idempotent bounded maintenance
commands for expired sessions, tokens, rate buckets, and approved audit retention;
operators may run them directly or through the host lifespan with SQL lease election
across replicas. Correct expiry/revocation does not depend on cleanup running.

Readiness checks verify supported schema, SQL access, required provider/key config,
trusted origins/proxy settings, and availability of required audit writes. Liveness
must not disclose secrets or mutate security policy. Restore operations must revoke
restored authentication state and reconcile policy before reopening traffic.

## Evidence required before a release

Use adversarial tests for cross-resource access, forged principals, reserved-field
writes, CSRF/login CSRF, wrong token types, concurrency, stale grants, provider/audit
failure, secret-reference substitution, and redaction across every output boundary.
Run PostgreSQL integration tests with multiple independent service instances;
SQLite tests alone cannot establish replica correctness. All implementation and
release gates are listed in [MVP](MVP.md); a planning review is not a security audit
of working software.
