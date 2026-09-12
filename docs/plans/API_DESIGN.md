# API Design

Status: proposed MVP surface, not an implemented API. The configurable router
prefix defaults to `/api/auth`; all paths below include that prefix exactly once.
All body-bearing mutations use explicit JSON schemas. No OAuth2 password-grant or
refresh endpoint is implied by local session login.

## Authentication and sessions

| Method and path | Authority / behavior |
| --- | --- |
| `POST /api/auth/login` | Public but origin-checked and rate-limited; sets opaque session cookie |
| `GET /api/auth/me` | Current authenticated principal; redacted response |
| `GET /api/auth/csrf` | Browser session; returns session-bound CSRF value, no-store |
| `POST /api/auth/logout` | Browser session + CSRF; SQL revocation then cookie clear |
| `POST /api/auth/password/change` | User session + CSRF + current password; revokes sessions |
| `GET /api/auth/sessions` | User's own session metadata |
| `DELETE /api/auth/sessions/{id}` | User's own session only; revoke, never disclose token |

Expired/invalid sessions return 401. A restricted temporary-password session can
only obtain its CSRF value, change its password, or log out. Login, logout, and CSRF behavior is defined in
[Authentication](AUTHENTICATION.md). No public registration, recovery, or bootstrap
route is included in MVP.

## Management routes and permission matrix

Each listed permission has the `authmate.` prefix. User/service-account/credential
creation and top-level listing use realm-level `.create` / `.list` actions; `.manage`
applies to existing-object read/edit. Roles and role bindings use realm-level
management actions for all their routes. Nested token/grant operations use their
parent resource. These are distinct registered actions, not implied suffix matching.

| Paths and methods | Permission | Resource type |
| --- | --- | --- |
| `POST, GET /api/auth/users` | `user.create`, `user.list` respectively | realm-level actions |
| `GET, PATCH /api/auth/users/{id}` | `user.manage` | `authmate.user` |
| `POST /api/auth/users/{id}/disable`, `/enable` | `user.disable` | `authmate.user` |
| `POST /api/auth/users/{id}/password-reset` | `user.password.reset` | `authmate.user` |
| `POST, GET /api/auth/roles`; `GET, PATCH /api/auth/roles/{id}` | `role.manage` | realm-level actions |
| `POST, GET /api/auth/role-bindings`; `DELETE /api/auth/role-bindings/{id}` | `role_binding.manage` | realm-level actions |
| `POST, GET /api/auth/service-accounts` | `service_account.create`, `service_account.list` respectively | realm-level actions |
| `GET, PATCH /api/auth/service-accounts/{id}` | `service_account.manage` | `authmate.service_account` |
| `POST /api/auth/service-accounts/{id}/disable`, `/enable` | `service_account.disable` | `authmate.service_account` |
| `POST, GET /api/auth/service-accounts/{id}/tokens`; `DELETE /api/auth/service-accounts/{id}/tokens/{token_id}` | `service_account.token.manage` | `authmate.service_account` |
| `POST, GET /api/auth/credentials` | `credential.create`, `credential.list` respectively | realm-level actions |
| `GET, PATCH /api/auth/credentials/{id}`; `POST /api/auth/credentials/{id}/disable`, `/enable` | `credential.manage` | `authmate.credential` |
| `GET /api/auth/credentials/{id}` (alternative read-only authority) | `credential.read_metadata` | `authmate.credential` |
| `POST, GET /api/auth/credentials/{id}/grants`; `DELETE /api/auth/credentials/{id}/grants/{grant_id}` | `credential.grant.manage` | `authmate.credential` |
| `GET /api/auth/audit-events` | `audit.read` | realm-level action |

A management role explicitly includes all required create/list/manage entries;
there is no implicit permission hierarchy. Do not overload `resource=None` to
authorize a resource action. Credential detail can use either listed authority;
that OR is explicit and grants no secret access. Grant deletion also checks that
the supplied grant ID belongs to the authorized parent credential.

`authmate.service_account.assume` is a resource permission assigned through ordinary
role bindings. It governs generic delegated service calls, not a workload binding
API. Consumer workflow/approval records never become AuthMate management endpoints.

The environment provider is read-only. No secret upload, secret read, or rotation
route ships in MVP. A later writable-provider API requires capability-specific
schemas and the encrypted-provider release gate. Service-account token creation
is a deliberate one-time secret response; all other reads return metadata only.

## Enforcement and error contract

Use APIRouter, explicit Pydantic request/response models, and server-side service
checks even for in-process callers. PATCH schemas allowlist editable fields and
reject unknown/reserved fields. Require version/If-Match on concurrent metadata,
role, and grant-policy edits; stale writes return 409. DELETE/revocation operations
are idempotent within caller authority; nested IDs must belong to the parent object.

Collection routes require the corresponding realm list/management/audit authority;
credential grants and tokens are scoped to their parent. Authorize/filter in SQL before
pagination/counts. Own a bounded Page schema: default 50, maximum 100, deterministic
sort with ID tie-breaker, and opaque cursor where supported. Audit paging uses a
stable time/ID cursor. A cursor is an untrusted input, never authorization evidence.

Errors use `{ "code": "...", "message": "...", "request_id": "..." }`.
Return 401 for invalid/missing identity, 403 for known prohibited operations, 404
for missing or undiscoverable detail resources, 409 for stale/conflicting writes,
422 for sanitized validation failures, 429 for throttling, and 503 for security
state/provider/audit unavailability. Reject unsupported JSON media types before
service invocation (415). Use WWW-Authenticate on bearer 401 responses. Do not expose
SQL/provider exceptions, raw rejected input, hashes, tokens, or permission internals.

Document cookie/CSRF and HTTP bearer schemes truthfully in OpenAPI. Resource RBAC
is checked by services; OAuth scopes do not encode it. Auth/session/token responses
use Cache-Control: no-store. AuthMate-scoped error handling must not overwrite the
host application's handlers globally; see [FastAPI Strategy](FASTAPI_STRATEGY.md).
