# Hedron Integration

This is non-normative consumer-owned adapter guidance. Hedron remains optional; AuthMate core never imports it. Start with a separately
versioned adapter/example; select extra/package naming when a tested adapter exists.
Reusable login/profile/admin pages are later work.

## Existing integration surface

The sibling Hedron checkout at `a747271a`, inspected 2026-09-12, exposes
`hedron.auth.session.mark_authenticated(request, value=...)` and
`hedron_core.security_context.SecurityContext`. Its session helper explicitly sets
a cache/Explorer signal and does not own authorization. Validate exports and behavior
against a pinned package release before committing to an adapter.

The adapter maps AuthMate's verified request identity into the host's supported
Hedron context. Marking a request authenticated is not evidence of authentication,
and copying `request.session['user']` is not a substitute for validating the current
AuthMate SQL session. Do not install a second independent login/session authority.
Mapping custom metadata into tenant/scopes fields does not create tenant isolation.

UI code may use the same AuthMate `can()` service to hide/disable controls. This
advisory decision is not cached as an execution capability; every form, action,
HTMX endpoint, and API independently enforces current server authorization. Keep
identity and response caches request-scoped or explicitly partitioned; test that
a different user cannot receive previously rendered privileged UI.

When co-located, UI code calls services directly with the trusted request context.
Browser mutations still require CSRF protection. Avoid leaking session/API tokens
through page state, client-visible props, browser storage, URLs, or logs.

## Compatibility gate

Test a pinned Hedron adapter for login/logout/expiry, identity propagation, matching
visibility and server permissions, cache isolation, CSRF, and disable/revocation.
Add the full Hedron + AuthMate + ShuETL + ETLantic composition only when all required
public adapters exist. Core CI uses a small fake UI consumer; that is contract
coverage, not evidence of real Hedron compatibility. Publish tested versions and
known limitations with each adapter release.
