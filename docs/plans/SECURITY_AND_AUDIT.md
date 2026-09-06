# Security and Audit

AuthMate is security-critical infrastructure.

## Requirements

- modern password hashing;
- secure session/token expiration;
- CSRF protection where cookie authentication applies;
- deny-by-default authorization;
- strict management-route permissions;
- centralized secret/token redaction;
- bounded request/report sizes;
- authentication rate-limit hooks;
- no arbitrary code execution through identity configuration.

## AuditEvent

```text
AuditEvent
- id
- event_type
- actor_principal_id
- subject/resource references
- outcome
- reason_code
- bounded metadata
- created_at
```

Audit login success/failure, identity enable/disable, role/grant changes, service-account changes, credential creation/rotation/disable/resolution, and authorization denials.

Audit records may state that a credential was used but never contain its value.

ShuETL may attach bounded run/pipeline identifiers to credential-use events.

Historical audit records are append-only through normal application APIs and have independently configurable retention.
