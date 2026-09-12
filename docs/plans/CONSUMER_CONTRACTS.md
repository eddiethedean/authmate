# Consumer Contracts

Status: proposed AuthMate-owned contracts to validate through implementation.
Consumers adapt to these interfaces; consumer release schedules and domain models
do not define AuthMate core. Method names below are planned, not currently callable.

## Public values and protocols

| Contract | Meaning and boundary |
| --- | --- |
| `PrincipalRef` / `PrincipalRecord` | Immutable ID/kind and explicitly public identity metadata; never ORM objects or authentication proof |
| `AuthenticationResult` | Validated actor identity plus mechanism/time/assurance from a trusted authenticator |
| `AccessContext` | Verified actor and optional effective service account; generic delegation is validated by AuthMate |
| `ResourceRef` | Exact registered type and canonical ID supplied by a trusted consumer lookup |
| `AuthorizationDecision` | Allow/deny with safe reason and diagnostic policy revision; a snapshot, not a capability |
| `PrincipalProvider` | Fetch current principal state through authorized service access; a returned ID does not authorize impersonation |
| `AuthorizationProvider` | Evaluate default RBAC or a selected custom policy inside mandatory AuthMate checks |
| `CredentialResolver` | Resolve an exact credential for AccessContext after current-state checks and durable audit |
| `SecretProvider` | Low-level backend mechanics behind CredentialResolver; not a public authorization bypass |
| `AuditSink` | Optional delivery target for already committed typed events; SQL audit remains authoritative |

Public service operations take explicit context and parameters, use async contracts,
and raise typed AuthMate domain errors. `can()` is advisory; `authorize()` returns a
decision; `require()` enforces or raises. FastAPI dependencies adapt transport to
these services. Background callers use the same services without constructing an
HTTP Request or depending on a request-scoped database session.

## Delegation and credentials

For direct use, actor equals effective principal. For delegated use, the authenticated
actor must hold `authmate.service_account.assume` on the effective account, and that
account must independently hold the requested permission or exact credential-use
grant. AuthMate checks both principals' current state. Assumption does not union
roles, authorize arbitrary token issuance, or recursively assume another account.

An executor, automation, or administrative tool can use this generic contract.
AuthMate does not require a pipeline, job, schedule, approved-version field, or
consumer callback. The consumer owns constraints tying its operation to the chosen
account/resource/credential. Correlation and initiating-user metadata are audit
context only and cannot authenticate an actor or broaden its authority.

## Ownership

AuthMate owns authentication, current principal state, role/scope semantics, generic
assumption permission, credential grants, secret release, and its audit/SQL schema.
Consumers own their resource existence, action registration/mapping, workflow
approval, domain data, execution lifecycle, output redaction, and any additional
business rules. They must enforce their rules before external effects and cannot
turn UI visibility or a prior decision into durable authorization.

An adapter belongs with the consumer or in a separate package depending on both
published APIs. No consumer-specific imports, schema, feature checks, validation
callbacks, or release gates belong in core. AuthMate's conformance tests use generic
report resources and a fake background client, proving the contract without sibling
repositories. Consumer adapters run their own real-version compatibility suites.

## Errors, lifecycle, and versioning

Distinguish unauthenticated, denied, not-found/hidden, invalid reference/config,
conflict, unsupported capability, and unavailable errors. No provider failure means
allow. Metadata and error objects must never contain resolved secrets or raw tokens.
Providers define timeout/cancellation/cleanup, and services commit mandatory audit
before acknowledging protected mutations or releasing secret material.

Registries freeze at startup; duplicate/conflicting registrations fail. Publish a
contract/schema version and a compatibility policy before stable release. Pre-1.0
changes must include migration notes and conformance updates; no promise of a frozen
protocol before the first end-to-end implementation. Adapter authors receive typed
examples and the same conformance suite used by default providers.
