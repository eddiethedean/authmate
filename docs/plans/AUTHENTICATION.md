# Authentication and Sessions

Status: selected MVP design; implementation and security gates remain open.

## Default transport and state

MVP uses opaque, SQL-backed sessions, not self-contained JWTs or refresh tokens.
Browser login sets a cookie; it does not return a bearer token in JSON. Machine
clients use separately issued service-account API tokens. JWT/OIDC adapters and
custom token claims are later features, not prerequisites for local login.

Generate authentication tokens with 32 bytes from a CSPRNG. Store a SHA-256 digest of the random
secret, never the raw token. This fast digest is for high-entropy tokens only;
passwords use Argon2id. Use token-type prefixes and separate lookup/state tables
so a machine token cannot be accepted as a browser session. Never accept tokens
in query parameters. Multiple supplied authentication mechanisms are rejected
rather than resolved by implicit precedence.

Each session stores principal ID, creation/last-activity times, idle/absolute
expiry, revocation time, and the principal's authentication epoch at issuance.
Create a fresh session ID on every successful login; never adopt a supplied ID.
Every authenticated operation checks current SQL state, principal enabled state,
epoch, and expiry. Baseline has no process-local positive authorization cache.
Use database time for expiry and atomic conditional activity updates so races
cannot resurrect revoked or expired sessions. Proposed defaults: 30-minute idle
and 12-hour absolute lifetime; operators can shorten both. No sliding update
extends absolute expiry. OWASP motivates server-side state, unpredictable IDs,
and server-enforced expiry; these exact defaults are AuthMate design choices.
[Source: OWASP session guidance](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html).

Logout revokes the session in SQL before reporting success and clears the cookie.
Password change/reset and principal disable atomically increment the authentication
epoch and revoke all sessions/tokens for that principal. Re-enabling never revives
old tokens. Role/grant removal affects the next authorization check through fresh
SQL evaluation, without requiring logout. See the concurrency boundary in
[Identity and Authorization](IDENTITY_AND_AUTHORIZATION.md).

## Browser protection

Use a deployment-unique `__Host-` cookie name, `Secure`, `HttpOnly`, `SameSite=Lax`,
`Path=/`, and no Domain attribute. Plain HTTP cookies require an explicit local
development profile rejected by production readiness. Cookie paths do not isolate
mutually untrusted apps on one origin; those apps need separate origins.

For unsafe cookie-authenticated requests, require both an exact configured Origin
(or validated Referer origin fallback) and a session-bound CSRF token in a custom
header. Obtain that token through authenticated `GET /api/auth/csrf`, with no-store
responses and no permissive credentialed CORS. The CSRF value is an independent
random per-session value stored in the session row and compared in constant time;
it cannot authenticate a request and never substitutes for the opaque session cookie. Login itself requires an allowed
origin and JSON content type, including before a session exists. Logout and login
are never GET operations. Reject missing/invalid origin evidence for browser
mutations; machine bearer endpoints do not use cookie authentication. Strict JSON
content type supplements CSRF checks; it does not replace them.

Cookies, CSRF values, password inputs, and token responses are excluded from
access logs, tracing, validation error input, and caches. TLS termination and
forwarded client IP headers are trusted only from explicitly configured proxies.

## Local users and password lifecycle

MVP login uses a unique normalized username; email is optional metadata, not an
alternate unverified login identifier. Normalize usernames once (NFKC + casefold),
store a separate display name, and enforce canonical uniqueness in SQL on both
backends. Never normalize, trim, or silently truncate passwords.

Use `pwdlib[argon2]` with explicitly configured Argon2id parameters, unique salts,
and rehash-on-success. Start at 64 MiB, 3 iterations, parallelism 1; benchmark under
bounded login concurrency before release. Never configure below the reviewed
minimum of 19 MiB, 2 iterations, parallelism 1.
[Source: OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
Accept 15–128 Unicode characters and at most 1024 UTF-8 bytes; allow spaces and
password managers, reject a shipped common-password list, and impose no composition
rules or routine forced rotation. Password policy and hashing cost are versioned
settings, not whatever a library changes its defaults to.

Unknown users perform dummy hash verification. Unknown, disabled, and incorrect
password cases share a generic 401 response. Hash work runs off the event loop
with bounded concurrency. A SQL rate limiter reserves attempts atomically before
hashing, using independent account-name and source-IP windows. Initial defaults:
5 attempts/account/5 minutes and 50 attempts/IP/5 minutes, including failures and
unknown users; return generic 429 with Retry-After. Bound key cardinality with a
global attempt budget and expire buckets. Tune these defaults with documented
load/abuse tests; process-local hooks are insufficient across replicas. SQL failure
denies login. Rate limiting reduces guessing but can be abused to deny service.

Self-registration, email verification, email-based recovery, MFA, and invitation
flows are deferred. Provisioning and recovery use an operator command or an
explicitly privileged management operation; never a public bootstrap endpoint.
Initial bootstrap uses a single-use SQL guard in the same transaction as the
first administrator binding and audit event, so concurrent processes cannot both
bootstrap. Input passwords through a hidden prompt/secure input, not CLI arguments
or logs. Provide an audited operator recovery procedure using database access.
An administrator can set a temporary password with a `must_change_password` flag;
that login yields only a password-change capability (plus CSRF retrieval and logout)
until successful replacement.
Self password change requires the current password and revokes existing sessions.
Hash verification happens outside SQL locks; login and password changes then acquire
the security-state guard and recheck the hash/epoch, enabled state, and restriction
flag before committing. A concurrent reset/disable invalidates the pending issuance.
Rehash-on-login uses a conditional update so it cannot overwrite a concurrent reset.

## Service-account API tokens

A trusted co-located executor need not mint a bearer token to use a service account;
its authority comes from the generic AccessContext and assumption permission in
[Consumer Contracts](CONSUMER_CONTRACTS.md). An arbitrary principal ID is not proof
of authority at an HTTP or job boundary.

Remote clients may receive an opaque API token only through a caller with
`authmate.service_account.token.manage` on that account. This permission permits
impersonation and is distinct from metadata editing. Reveal the token exactly once
in the creation response, with Cache-Control: no-store. Store its digest, account
ID, creation/expiry/revocation timestamps, authentication epoch, and display prefix.
Default expiry is 24 hours with a configurable finite maximum of 30 days. Tokens
inherit the account's current permissions; narrower token scopes are deferred and
must not be implied. Use separate accounts for distinct privilege sets.

API-token rotation creates a new token and explicitly revokes the old one; any
overlap must be bounded by an explicit expiry. Do not retry issuance automatically
after an ambiguous response; list token metadata, revoke an uncertain token, and
issue another. Token values are never recoverable from read/list endpoints.
