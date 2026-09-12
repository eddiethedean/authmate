# Extensibility

## Principle and scope

AuthMate is customizable through typed contracts without forks. Security gates
remain in AuthMate service wrappers: principal state, token validation, resource
matching, credential grants/delegation, audit-before-release, and redaction cannot
be disabled by a provider returning allow. Custom implementations are trusted code;
conformance tests enforce supported behavior but do not sandbox malicious Python.

MVP extension surfaces are user/service-account metadata, authenticators, an
authorization provider, credential types, secret providers, and typed audit metadata.
Claims/JWT issuance, groups, a general lifecycle hook engine, and reliable remote
audit delivery are later features. Protocols remain versioned/experimental until
implementation proves their lifecycle and failure semantics.

## Persistence metadata and managed migrations

Expose non-table SQLModel bases with fixed security fields. A model factory selects
one effective table model before metadata is built; repositories use that registry.
For example, an application may add `department: str | None` to its user metadata,
but it cannot redefine `id`, principal kind, enabled state, or authentication epoch.
No mapped-table inheritance, duplicate default/custom table registration, or
`extend_existing` workaround is part of the supported contract.

Typed persistence metadata is separate from API metadata. Explicit request/response
schemas select fields callers may write/read; a custom column never automatically
becomes user-editable or public. Groups are future relational concepts, not custom
role-list fields that bypass AuthMate relationships.

AuthMate provides programmatic Alembic status/plan/check/upgrade APIs while production
applies packaged, reviewed revisions in a serialized deployment step. Automatic DDL
inference at app startup is excluded. Details and conformance gates are in
[Persistence and Managed Migrations](MIGRATIONS.md).

## Authentication and authorization

An authenticator consumes a typed mechanism-specific input and returns an
`AuthenticationResult` identifying a validated principal, mechanism, authentication
time, and assurance metadata, or a typed failure. Keep Request parsing in the
FastAPI adapter; domain protocols must work outside HTTP. Missing credentials,
invalid credentials, and provider unavailable are distinct outcomes. Invalid input
must not fall through to a more permissive authenticator. Register accepted mechanisms
and reject ambiguous multiple credentials explicitly at startup/request boundaries.

AuthMate's wrapper rechecks the local principal and revocation/expiry state after
provider authentication. Reverse-proxy or certificate adapters require independently
verified proxy/TLS trust; arbitrary forwarded headers are not authenticators. OIDC
issuers, subjects, linking, audiences, and assurance mapping need their own tested
adapter design before federation ships.

The AuthorizationProvider evaluates a trusted PrincipalRef, exact registered action,
and optional ResourceRef, returning the common AuthorizationDecision. One provider
is selected explicitly per deployment. No OR-composition of multiple providers or
fallback on errors. Service wrappers preserve the invariants in
[Identity and Authorization](IDENTITY_AND_AUTHORIZATION.md).

## Credential/provider registries

Credential configs use discriminated Pydantic models keyed by a namespaced `type`.
A provider registration binds an operator-chosen alias, a typed config, and its
read/write/rotate/version capabilities. Freeze registries before schema generation;
duplicate discriminators or names are configuration errors. Unions are built from
this registry at startup and do not change dynamically per request.

Public callers select only allowed aliases and types. Secret references and provider
endpoints remain operator-controlled. Provider errors map to stable codes without
exception text. Providers cannot bypass the resolver's authorization/audit wrapper.
Blocking SDKs run in bounded off-loop execution; native async adapters have explicit
timeout/cancellation and close/aclose contracts. Cleanup occurs on failed startup,
request failure, cancellation, and shutdown.

## Claims: later adapter capability

Opaque MVP sessions have no client-visible claim payload to subclass. Custom session
metadata is stored server-side, bounded, and never taken as current permission state.
A future JWT adapter can accept a separate custom-claims model/resolver, then merge
it only after checking keys against the reserved registry. Reserved keys include
subject, issuer, audience, issued/expiry/not-before timestamps, token ID/type, and
AuthMate authentication/security version fields. Reject collisions, including model
aliases; do not let Pydantic inheritance redefine reserved fields.

That adapter must own a tested algorithm allowlist, issuer/audience checks, clock
skew, key selection/rotation, expiry, and revocation strategy. A metadata claim such
as `tenant_id` never independently supplies authority. Refresh-token rotation/reuse
detection requires a separate design and is not implied by custom access claims.

## Audit metadata and later hooks

Register bounded, typed audit metadata with explicit field allowlists; AuthMate
owns actor, effective principal, timestamp, event ID, outcome, and redaction. The
SQL audit store remains mandatory. An optional sink observes committed events;
reliable delivery requires the later outbox contract in
[Security and Audit](SECURITY_AND_AUDIT.md).

The MVP supports domain validation through services/providers, not a generalized
security event hook engine. Future `before_*` validators run before mutation under
a defined timeout, cannot broaden authority, and fail closed. External side effects
must not occur inside rollbackable transactions. `after_*` notifications run after
commit; their failure cannot turn a committed operation into an apparent rollback.
Retries, idempotency, cancellation, ordering, and outbox delivery must be specified
before that hook family is advertised as stable. Never pass plaintext secrets to
generic hooks or permit a hook to replace issued security claims.

## Conformance and packaging

Each supported extension family must pass typed-input/output, reserved-field,
failure/timeout, revocation, secret-redaction, transaction, startup/shutdown,
request-isolation, and FastAPI dependency-override tests. Test custom models across
fresh install and upgrade on both databases. Core protocol packages import neither
Hedron nor ShuETL nor optional provider libraries. Missing extras yield safe,
actionable configuration errors; no provider is selected by untrusted import paths.
