# ShuETL Integration

ShuETL uses AuthMate for human authorization, service-account execution identity, credential delegation, secret resolution, and security auditing without depending on AuthMate ORM internals.

## Execution chain

```text
User
  ↓ authorized to trigger
ShuETL Pipeline
  ↓ executes as
ServiceAccount
  ↓ authorized to use
Credential
  ↓ resolved through
SecretProvider
  ↓
ETLantic connector/runtime
```

A ShuETL pipeline version may persist service-account and credential references, never resolved secrets.

## Manual runs

1. Authenticate the human.
2. Authorize `shuetl.pipeline.run`.
3. Create the durable run with triggering-principal metadata.
4. Executor resolves the pipeline service account.
5. Authorize that service account for each required credential.
6. Resolve secrets just in time.
7. Execute ETLantic.
8. Persist only redacted reports/artifact references.
9. Audit security-sensitive actions.

## Scheduled runs

Scheduled runs execute as the pipeline's explicit service account. A schedule never implicitly gains credential access.

If a service account is disabled, credential revoked, or grant removed, the run blocks/fails before unsafe external I/O. Never silently fall back to application-global credentials.

ShuETL should consume `AuthorizationProvider`, `ServiceAccountProvider`, `CredentialResolver`, and `AuditSink` protocols.
