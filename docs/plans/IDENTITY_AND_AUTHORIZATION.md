# Identity and Authorization

## Principal model

```text
Principal
├── User
└── ServiceAccount
```

A principal has an ID, type, display name, enabled state, and timestamps. Users add username/email and authentication metadata. Service accounts add name, owner, description, and optional expiration.

## Extensible principal models

AuthMate should expose non-table SQLModel bases for supported extensible entities. Applications may add typed fields without forking AuthMate:

```python
class User(AuthMateUserBase, table=True):
    __tablename__ = "authmate_users"

    department: str | None = None
    employee_id: str | None = Field(default=None, index=True)
```

AuthMate supplies a default table model when no custom user model is configured.

The same controlled pattern may support ServiceAccount and Group metadata. Not every internal table must be extensible.

Roles, groups, permissions, memberships, and bindings remain first-class AuthMate relational concepts rather than application-defined scalar fields.

Schema changes from supported model extensions are handled through AuthMate's managed Alembic layer. Safe additions may auto-migrate; destructive or ambiguous changes require explicit review/action.

See `EXTENSIBILITY.md`.

## Generic resources

AuthMate must not require knowledge of consumer ORM classes.

```python
ResourceRef(type="shuetl.pipeline", id="pipe_123")
```

## Roles and permissions

Permissions use package-owned namespaces:

```text
authmate.user.manage
authmate.credential.use
shuetl.pipeline.read
shuetl.pipeline.run
shuetl.schedule.manage
hedron.admin.access
```

MVP uses RBAC plus resource-scoped bindings. Unknown authorization evidence defaults to deny.

Authorization itself is provider-extensible through a typed `AuthorizationProvider` contract. AuthMate's default provider remains authoritative unless explicitly replaced/configured.

## Authorization API

```python
decision = await authmate.authorize(
    principal=principal,
    action="shuetl.pipeline.run",
    resource=ResourceRef("shuetl.pipeline", "customers"),
)
```

The service API must work outside HTTP requests so schedulers and workers can authorize background actions.

## Authentication

MVP supports secure local username/email + password authentication, modern password hashing, current-principal resolution, and a short-lived token/session model selected by ADR.

External/custom authentication is adapter-based through a stable authenticator contract for OIDC, enterprise SSO, reverse-proxy identity, client certificates/CAC, API-specific mechanisms, and application-supplied identity.

Authentication answers *who are you?* Authorization answers *may you do this?*

## Extensible token claims

JWT/token claims use Pydantic extension models and typed claim resolvers.

```python
class ApplicationClaims(AccessTokenClaims):
    department: str | None = None
    tenant_id: UUID | None = None
```

Applications may add claims, but AuthMate retains authority over reserved security-critical claims such as subject, issuer, audience, issued/expiry/not-before timestamps, token identifier, and token type.

Custom claims cannot silently overwrite reserved claims.

Token issuance hooks/providers must preserve validation, signing, expiry, audience/issuer, revocation/session, and redaction invariants defined by AuthMate.
