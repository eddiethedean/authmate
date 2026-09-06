# Identity and Authorization

## Principal model

```text
Principal
├── User
└── ServiceAccount
```

A principal has an ID, type, display name, enabled state, and timestamps. Users add username/email and authentication metadata. Service accounts add name, owner, description, and optional expiration.

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

External authentication is adapter-based for future OIDC, enterprise SSO, reverse-proxy identity, client certificates/CAC, and application-supplied identity.

Authentication answers *who are you?* Authorization answers *may you do this?*
