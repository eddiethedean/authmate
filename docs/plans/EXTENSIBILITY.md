# Extensibility

## Principle

> **Secure defaults, extensible by contract.**

Every major AuthMate capability should expose a stable, typed extension surface where practical. Applications may extend models, token claims, providers, policies, credential types, secret backends, audit metadata, and lifecycle behavior without modifying AuthMate internals.

A companion invariant applies:

> **Extensibility must never weaken security invariants implicitly.**

Extensions may add behavior and metadata, but reserved security semantics remain AuthMate-authoritative unless an explicit low-level provider contract transfers that responsibility.

## Extensible persistence models

AuthMate should expose non-table SQLModel bases for developer-extensible persisted entities where safe.

Conceptually:

```python
class AuthMateUserBase(SQLModel):
    id: UUID
    username: str
    email: str
    enabled: bool = True

class User(AuthMateUserBase, table=True):
    __tablename__ = "authmate_users"

    department: str | None = None
    employee_id: str | None = Field(default=None, index=True)
```

AuthMate supplies a default table model when no custom model is configured.

Initial extension candidates:

- User;
- ServiceAccount;
- Group;
- selected credential/audit metadata models.

Not every internal table must be subclassable. Extensibility should be intentional and conformance-tested.

### Roles and groups

Roles, groups, permissions, memberships, and bindings remain first-class AuthMate relational concepts rather than application-defined scalar columns.

Applications may extend role/group metadata, but AuthMate owns relationship semantics.

## Managed schema migrations

Developers should not need the Alembic CLI for normal AuthMate model extension.

AuthMate should invoke Alembic programmatically against the effective SQLModel metadata and expose a schema manager such as:

```python
auth.schema.status()
auth.schema.plan()
auth.schema.check()
auth.schema.upgrade()
```

Normal configuration may support:

```python
AuthMate(
    user_model=User,
    auto_migrate="safe",
)
```

### Safe automatic migration policy

Automatically applicable changes may include, after validation:

- add nullable columns;
- add columns with safe server defaults;
- add indexes;
- create AuthMate-owned extension tables;
- add constraints only when existing data is proven compatible.

Potentially destructive/ambiguous changes must not be blindly applied:

- drop/rename columns;
- incompatible type changes;
- nullable to non-nullable without migration data/defaults;
- primary-key changes;
- destructive foreign-key/constraint changes.

Unsafe changes produce a migration plan/error requiring explicit developer action or an approved migration hook.

Alembic autogeneration is evidence for a candidate migration, not permission to execute arbitrary DDL.

## Extensible JWT/token claims

Token payloads should use Pydantic extension models.

```python
class ApplicationClaims(AccessTokenClaims):
    department: str | None = None
    tenant_id: UUID | None = None
```

Applications provide a typed claims resolver:

```python
async def claims(ctx: TokenContext) -> ApplicationClaims:
    ...
```

Reserved AuthMate claims remain authoritative, including security-critical fields such as subject, issuer, audience, issued/expiry/not-before timestamps, token identifier, and token type.

Custom claims may not silently override reserved claims.

AuthMate should support separate extension contracts for access-token and refresh/session token payloads where their semantics differ.

## Authentication providers

Define a stable authenticator protocol so applications can add authentication mechanisms without patching AuthMate:

```python
class Authenticator(Protocol):
    async def authenticate(self, request: Request) -> PrincipalRef | None: ...
```

AuthMate may ship password/bearer/API-key mechanisms and optional OIDC adapters. Applications can add mechanisms such as enterprise proxy identity or CAC/client-certificate authentication.

## Authorization providers

Authorization remains behind a provider contract:

```python
class AuthorizationProvider(Protocol):
    async def authorize(
        self,
        principal: PrincipalRef,
        action: str,
        resource: ResourceRef | None,
    ) -> AuthorizationDecision: ...
```

AuthMate ships understandable RBAC/resource bindings. Optional/custom providers may implement Casbin, ABAC, OPA-style remote adapters, or organization-specific policy while returning the same typed decision.

## Credential types and resolvers

Credential types should be extensible through discriminated Pydantic models and resolvers.

```python
class SnowflakeCredential(CredentialConfig):
    type: Literal["snowflake"]
    account: str
    warehouse: str
    username: str
```

Conceptual registration:

```python
auth.credentials.register_type(
    "snowflake",
    SnowflakeCredential,
    resolver=resolve_snowflake,
)
```

Resolved secret material must still obey AuthMate redaction, authorization, audit, and late-resolution invariants.

## Secret providers

External/local secret storage is provider-based:

```python
auth.secrets.register_provider("company", CompanySecretProvider())
```

Custom providers must conform to AuthMate's secret-resolution/redaction contract and cannot leak secret values into ordinary Pydantic response models or audit metadata.

## Audit extensions

Applications may define typed audit metadata/event extensions while AuthMate owns common event identity, actor, timestamp, correlation, and redaction semantics.

Avoid arbitrary unbounded dictionaries as the primary extension mechanism; prefer registered Pydantic metadata/event models.

## Lifecycle hooks

Provide typed hooks/events for bounded behavioral customization, for example:

```text
before_user_create
after_user_create
before_login
after_login
login_failed
before_token_issue
after_token_issue
before_credential_resolve
after_credential_resolve
authorization_denied
user_disabled
service_account_disabled
```

Hooks must have documented ordering, error semantics, timeout/cancellation behavior, and whether they execute inside or outside database transactions.

Security-sensitive `before_*` hooks should fail closed unless explicitly documented otherwise.

## Registration surface

Prefer explicit registration over monkey-patching:

```python
auth.register_authenticator(...)
auth.register_authorization_provider(...)
auth.register_claims_resolver(...)
auth.register_credential_type(...)
auth.register_secret_provider(...)
auth.register_audit_sink(...)
auth.register_hook(...)
```

Exact names may evolve, but the pattern should remain consistent.

## Extension conformance

Each extension family should have a conformance test kit so third-party implementations can verify behavior independently.

Tests should cover:

- typed input/output validation;
- async behavior;
- error mapping;
- security invariant preservation;
- secret redaction;
- lifecycle cleanup;
- compatibility with FastAPI dependency overrides;
- OpenAPI behavior where relevant.

## Packaging

AuthMate core contains extension protocols and default implementations. Heavy integrations remain optional extras or separate adapter packages.

Sibling packages such as Hedron and ShuETL must integrate through these public contracts rather than importing extension implementation internals.
