# Credentials and Secrets

## Separation and permissions

A Credential is metadata and access policy pointing to a SecretProvider reference.
It stores ID, type, provider alias, opaque reference, enabled state, version,
expiry/rotation metadata, and description. A secret value is sensitive material.
MVP ships an API-key credential type and an operator-managed environment provider;
other typed bundles can use the registered extension contract.

Use one permission namespace everywhere:

| Permission | Authority |
| --- | --- |
| `authmate.credential.read_metadata` | Read redacted metadata for a credential |
| `authmate.credential.create` / `.list` | Realm-level creation/listing of metadata using approved aliases |
| `authmate.credential.manage` | Read/edit/disable existing metadata and authorized provider references |
| `authmate.credential.grant.manage` | Add/remove exact credential-use grants |
| `authmate.credential.use` | Use secret material through the resolver, via an exact grant |

A CredentialGrant links an existing principal to one credential, with optional
expiry. It is the single source of credential-use authority; RBAC role entries
cannot contain `authmate.credential.use`. A grant is not an authentication token.
Metadata/management permissions do not imply use, and use does not imply broad
metadata discovery. Grant managers can confer access, including to themselves;
metadata managers can change what existing grants resolve. Both are privileged
security administrators, not ordinary metadata editors. Changes are audited.

No raw-secret HTTP read/resolve endpoint is exposed in MVP. Trusted in-process
runtime consumers use `CredentialResolver`. Arbitrary plugins running in the same
process can access process memory; this API is not a sandbox for untrusted code.

## Provider contract and environment baseline

Providers implement async resolution returning a non-serializable `SecretValue`
with redacted repr and an explicit narrow unwrap method. Provider registration,
configuration, allowed reference aliases, and credentials are controlled by trusted
host code. An API caller selects only an allowed alias; it cannot request arbitrary
environment variable names, URLs, file paths, cloud identities, or provider config.
Otherwise creating a credential could expose AuthMate's own database or signing key.

The environment provider maps approved aliases to injected process secrets. It is
read-only: secret creation/rotation through the API returns an explicit unsupported
capability error. Metadata reference changes use version checks and preserve audit.
Operators roll updated secrets to every replica; this provider offers no atomic
cross-replica rotation. Hosts requiring that guarantee must use a versioned provider.
Externally supplied values must never be interpolated into executable code.

Provider capabilities (read/write/rotate/version support) are declared and checked
before any mutation. External adapters additionally define timeouts, response-size
limits, TLS verification, retry behavior, and an operator-controlled endpoint allowlist.
No fallback to environment/global credentials on failure.

## Resolution and revocation boundary

1. Validate the trusted AccessContext and load current principal,
   credential, expiry, exact grant, and any actor-to-service-account assumption
   permission from SQL.
2. Commit an audit attempt before contacting the provider. Resolve using the captured
   credential reference and version, with bounded timeout/size and no SQL lock held
   across remote I/O.
3. Under the security-state guard, recheck current authorization, enabled/expiry
   state, and unchanged credential version. Reject/discard if anything changed.
4. Commit a `credential.release_authorized` audit event before returning the value.
   If this commit fails, return no value. Crashes after commit may mean the consumer
   never received it; this event does not assert successful external use.
5. Release the value only to the requesting runtime consumer. Do not persist/cache
   resolved values. Shorten their lifetime and close handles on exit; Python cannot
   promise reliable zeroization of all string/bytes copies.

Audit failures and provider failures return safe reason codes. Best-effort outcome
events supplement the durable attempt; an unfinished attempt is visible after a
crash. Revocation prevents subsequent authorized releases, but cannot retract
already released values or stop an external operation in progress.

Secrets must not appear in metadata, errors, reprs, traces, metrics labels, audit,
pipeline definitions, reports, or OpenAPI examples. Hidden provider references may
also disclose infrastructure; public metadata returns only approved display fields.
`SecretStr` alone does not enforce these boundaries; explicit schemas and tests do.

## Optional encrypted SQL provider: separate release gate

Environment references satisfy the MVP without an external secret service.
Encrypted SQL storage is a follow-on capability, not a conditional MVP dependency
or a promised default. `cryptography` is installed only with that provider.

Before release, approve an ADR and test a versioned authenticated-encryption format
binding ciphertext to deployment, credential ID, secret version, and provider
purpose through authenticated data. Specify algorithm/key sizes, nonce allocation
and uniqueness under concurrent writes, size limits, key IDs, and corruption errors.
AEAD libraries require correct nonce handling and authenticated-data verification.
[Source: cryptography AEAD documentation](https://cryptography.io/en/stable/hazmat/primitives/aead/).

Keep encryption keys outside SQL and database backups. All replicas must share an
operator-managed active key and decrypt-only old keys during rotation. Never create
a new master key implicitly at startup. Key absence/mismatch fails readiness for
this provider. Define resumable re-encryption, bounded key overlap, rollback, and
backup/restore tests before removing old keys. Distinguish encryption-key rotation
from rotating a downstream API password/token. Database encryption does not protect
against a compromised process holding the key or a fully privileged database writer.
