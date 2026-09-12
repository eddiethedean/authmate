# Critical Plan Review — 2026-09-12

## Basis and limits

Reviewed every planning document and the root README. The repository contains no
runtime implementation, package manifest, or executable tests, so this review fixes
specifications and identifies future evidence; it does not certify working security.
Read-only inspection of sibling repositories informed the optional integration notes.
No sibling files were changed. AuthMate's broad contracts remain independent of them.

## Findings and fixes

Severity describes the risk if the original wording were implemented literally.

| Severity | Finding in the original plan | Applied correction | Evidence gate |
| --- | --- | --- | --- |
| Critical | A pipeline could select a powerful service account without a defined authority boundary. | Generic actor-to-account assumption plus independent effective-principal grants; consumer owns job approval and selection constraints. | G06 |
| High | Session/JWT choice was open, while revocation and rate limits were deferred after MVP. | Opaque SQL sessions/API tokens; expiry, SQL revocation/rate limits, CSRF, and password recovery in MVP. | G02–G04 |
| High | Resource-scoped RBAC lacked matching, inheritance, and privilege-administration rules. | Exact/type/realm matching, unknown-action denial, no inheritance, explicit elevation powers and list visibility. | G05 |
| High | Credential grants and role permissions could disagree; references could expose arbitrary process secrets. | One exact use-grant authority, canonical names, operator-controlled environment aliases, no raw-secret HTTP endpoint. | G05, G07 |
| High | “Every resolution is audited” lacked transaction/failure/crash semantics. | Durable attempt and release authorization, final state/version recheck, fail closed before release, truthful crash outcomes. | G07–G08 |
| High | Additive DDL was described as safe to auto-apply, with unresolved revision and replica coordination. | Packaged reviewed revisions, check-only production startup, separate migration identity, serialized upgrades and recovery. | G10–G11 |
| High | Custom authenticators/providers/hooks could transfer or implicitly override security invariants. | Mandatory service wrappers, distinct trusted identity provenance, constrained providers, deferred general hooks. | G05–G06, G12 |
| High | Revocation was promised to stop unsafe external I/O without a realizable atomic boundary. | Guarantee fresh subsequent checks; explicitly leave cancellation/retraction of already released secrets to consumers. | G04, G07 |
| Medium | Encrypted SQL storage was both a baseline promise and conditional MVP work. | Read-only environment provider is fixed MVP; encryption has a separate format/key/rotation/restore gate. | G07, future provider gate |
| Medium | Core/consumer responsibilities and mandatory full-stack CI created coupling to evolving siblings. | AuthMate owns general contracts; consumer adapters own domain translation and compatibility tests. | G12 |
| Medium | Custom table inheritance could register default and replacement tables; new fields might become public. | One model registry before mapping, fixed reserved fields, separate public metadata schemas and reviewed extension revisions. | G09–G10 |
| Medium | API prefix, permission names, refresh route, and “no token responses” conflicted. | One `/api/auth` prefix, canonical names, no refresh endpoint, explicit one-time machine-token/CSRF responses. | G03, G05, G09 |
| Medium | FastAPI/SecretStr behavior was treated as sufficient protection. | Explicit host lifespan, scoped handlers, service commits, CSRF, sanitized validation errors, and output-boundary tests. | G01, G03, G09 |
| Medium | Tenant claims implied isolation without keys, lookups, or policies enforcing it. | Explicit single-realm MVP; custom tenant metadata grants no isolation. | G05 |
| Medium | Bootstrap, account recovery, cleanup, audit retention, and restore effects were missing. | Operator provisioning/recovery, bounded SQL maintenance, mandatory retention choice, restored-token invalidation and policy reconciliation. | G02, G11 |

## Remaining work

The revised plans select design defaults, but Phase 0 must still validate the exact
SQL schema/lock ordering, protocol signatures, permission catalog, model registry,
dependency support matrix, and operational budgets. Every MVP gate remains open.
Encrypted storage, federation, tenancy, and hooks need separate future ADRs; no
unfinished feature is silently included in the standalone MVP.

## Source checks

Primary documentation informed specific mechanics, not a security certification:

- [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
  supports unpredictable opaque IDs and server-enforced expiration.
- [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
  supplies the Argon2id configuration floor; AuthMate's proposed operational defaults need benchmarks.
- [OWASP authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
  supports deny-by-default checks at each operation.
- [Alembic autogeneration](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
  documents candidate-review requirements and incomplete change detection.
- [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/) and
  [strict content type](https://fastapi.tiangolo.com/advanced/strict-content-type/)
  inform composition and HTTP checks, without replacing CSRF enforcement.
- [cryptography AEAD](https://cryptography.io/en/stable/hazmat/primitives/aead/)
  informs the future encrypted-provider nonce/authenticated-data gate.
