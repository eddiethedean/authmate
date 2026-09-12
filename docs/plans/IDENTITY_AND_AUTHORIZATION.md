# Identity and Authorization

## Principal and trust boundary

A Principal has an immutable UUID, kind (`user` or `service_account`), enabled
state, authentication epoch, and timestamps. User and ServiceAccount are one-to-one
subtypes sharing the principal key. A service account additionally has an owner
reference, description, and optional expiry. Ownership is metadata and grants no
permissions by itself. Disable is preferred to deletion so references and audit
history remain meaningful; IDs are never reused.

`PrincipalRef` and `ResourceRef` are immutable Pydantic values. A reference identifies
an object; it is not an authenticated capability. HTTP identity comes from AuthMate
session/token validation. Trusted in-process callers supply an authenticated or
validated execution context. Reconstructing a caller from a body-supplied ID, custom
claim, or unsigned job payload is forbidden. Services re-read current principal
state instead of trusting caller-provided roles or enabled flags.

MVP has one security realm per deployment. It does not claim tenant isolation.
A metadata or token field named `tenant_id` supplies no tenancy enforcement.
Multi-tenant hosts require separate deployments/databases until a tenant-aware
contract covers every key, lookup, grant, token, cache, and provider boundary.

## Resource and permission registration

```python
ResourceRef(type="myapp.report", id="report_123")
```

Resource types and actions are explicitly registered at startup by trusted code.
Action definitions declare the owning namespace and either one resource type or
that the action is realm-level. Unknown actions/types and conflicting registrations
fail closed. Names are exact, case-sensitive strings; no prefix or glob matching.
Registering a permission never grants it. AuthMate owns `authmate.*`; adapters own
mappings to consumer namespaces, which must follow the consumer's actual contract.

Resource IDs are nonempty, bounded canonical strings defined by the owning package.
Authorization does not prove a resource exists. Consumer handlers resolve the
resource through a server-authoritative lookup and build the reference from that
object. Resource existence/visibility checks remain in the consumer service.

## RBAC matching rules

A Role has an immutable ID and registered permission entries. A RoleBinding links
one principal, one role, optional expiry, and a discriminated scope:

| Scope | Matching rule |
| --- | --- |
| `realm` | All valid resources for each action in the role, plus realm-level actions |
| `resource_type(type)` | Only resource actions declared for that exact type |
| `resource(type, id)` | Only that exact resource and its declared actions |

`resource=None` means a realm-level operation. It never requests an implicit
wildcard or a list of every resource. There is no hierarchy, inheritance, explicit
deny rule, or group membership in MVP. Grants from matching active bindings are
unioned; absence of a match denies. Incompatible binding/action scopes are rejected
on writes, including role updates. Disabled or expired principals always deny.

`AuthorizationDecision` contains `allowed`, a stable reason code, evaluated action
and resource, and policy revision for diagnostics. A decision is a snapshot, not
a reusable permission token. `can()` returns a bool; `authorize()` returns this
record; `require()` raises a domain denial. Provider exceptions/timeouts fail closed
and map to unavailable, never to an allow or a fallback provider.

```python
decision = await authmate.authorize(
    context=context,  # verified AccessContext supplied by the host adapter
    action="myapp.report.read",
    resource=ResourceRef(type="myapp.report", id="report_123"),
)
```

Background services use the same contracts without a FastAPI Request. The service
wrapper always checks principal state and registered action/resource compatibility,
including when a custom AuthorizationProvider replaces RBAC. A provider cannot
bypass credential grants, delegation checks, audit, or disabled-principal rules.
Deny-by-default and checking every operation follow
[OWASP authorization guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

## Administrative authority

`authmate.role.manage` and `authmate.role_binding.manage` are realm-level security
administrator powers; they can elevate privileges and must be documented as such.
MVP has no partially delegated role administrator. Ordinary user/service-account
metadata writes cannot change principal kind, roles, enabled state, authentication
epoch, password hashes, or reserved fields. Separate operations govern password
reset, disable/enable, token issuance, and credential grants.

`authmate.credential.use` is granted only by the exact credential grants described
in [Credentials and Secrets](CREDENTIALS_AND_SECRETS.md), not by a role permission
entry. Credential grant management is a separate authority that can confer secret
access and must be treated as privileged. No built-in administrator bypass resolves
secrets automatically. Bootstrap creates explicit management bindings only.

List routes apply discoverability filters in SQL before pagination/counting.
MVP permits a realm-wide list only with its matching list/management/audit-read permission;
exact read permissions permit detail access. Per-user discovery lists are deferred.
A scoped detail route returns 404 for missing and non-discoverable resources alike.

## Generic delegated identity

An `AccessContext` carries a verified actor PrincipalRef and an optional effective
PrincipalRef. Both identify AuthMate principals. Normally they are the same. If
they differ, the actor needs `authmate.service_account.assume` on the exact effective
service account; both principals must be enabled/unexpired. The effective principal
then needs the requested permission or exact credential grant. There is no transitive
assumption or automatic role union. Assuming an account permits exercising its
current authority and is explicitly privileged. It does not implicitly mint a token.

The public service wrapper validates this relationship on every operation. A caller
cannot turn an arbitrary ID into a verified actor by constructing a Pydantic model;
HTTP adapters authenticate the actor and trusted Python callers are responsible for
preserving that provenance. An authenticator result and an AccessContext are distinct
contracts. Generic purpose/correlation metadata is bounded and supplies no authority.

A consumer may authenticate a dedicated executor as actor and use an authorized
service account as effective principal. Any human initiator is separate audit context,
not silently treated as the executor's authentication. The consumer owns whether a
job is approved, which account it may select, its resource versions, and when to
cancel it. AuthMate stores no workload approval/version/schedule records and requires
no consumer validation callback. See [Consumer Contracts](CONSUMER_CONTRACTS.md).

## Revocation and concurrent work

SQL is authoritative. Checks starting after a committed disable, revocation, or
grant removal must observe it on every replica; do not use long-lived transaction
snapshots or positive caches. AuthMate-owned security mutations authorize and write
within one transaction, using a common SQL security-state revision row locked by
both authorization-sensitive writers and competing policy changes. This deliberately
serializes MVP security writes; benchmark contention before release. Credential
release uses the same guard for its final check/audit, after provider I/O.

For consumer/external actions the guarantee is narrower: recheck at execution and
before each new credential acquisition or consequential operation. Revocation
cannot retract plaintext already returned or cancel external I/O atomically. A
consumer needing stronger cancellation must implement it at its own execution
boundary. Do not promise that disabling an account instantly halts running work.

## Extension boundary

User and service-account metadata may use configured non-table SQLModel bases;
core identity columns, relationships, and constraints remain fixed. Groups, custom
token claims, and richer scopes are later features. See [Extensibility](EXTENSIBILITY.md)
and [Authentication](AUTHENTICATION.md) for their distinct contracts.
