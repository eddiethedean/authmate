# Credentials and Secrets

## Separation

A credential is metadata and policy. A secret is sensitive material.

```text
Credential
  ↓ secret_ref
SecretProvider
  ↓
SecretValue
```

Credential metadata includes ID, name, type, provider, secret reference, enabled state, rotation/expiration metadata, and description.

Potential types include username/password, API key, bearer token, database credential, OAuth client, SSH key, cloud credential, and secret bundle.

## Permissions

```text
credential.read_metadata
credential.use
credential.manage
```

Metadata access never implies access to secret material.

## Secret providers

Define a stable async provider protocol. Initial/future implementations may include environment variables, encrypted AuthMate DB storage, AWS Secrets Manager, Azure Key Vault, HashiCorp Vault, and Kubernetes Secrets.

## Resolution rules

Resolution requires an enabled requesting principal, enabled credential, `credential.use` authorization, an available provider, and a valid reference. Every resolution is audited.

Resolved values must never be logged, returned by metadata APIs, written to audit events, serialized into ShuETL pipeline definitions, or included in ETLantic reports.

If encrypted DB storage is supported, its master key must live outside the database and the format must support rotation/versioning.

## SQL-only baseline for secrets

AuthMate's default production deployment must not require Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, or another external secret service.

Baseline secret-provider options are environment/configuration references and encrypted SQL-backed secret storage.

If encrypted SQL-backed storage is enabled, the encryption master key must remain outside the database, typically in process environment/configuration.

External secret managers remain optional provider integrations.
