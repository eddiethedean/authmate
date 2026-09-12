# FastAPI Strategy

Use FastAPI's routers, dependency injection, security extraction, lifespan, OpenAPI,
and test overrides while keeping AuthMate usable through explicit Python services.

## Integration contract

Expose APIRouter modules under one configurable prefix. The host includes them and
explicitly enters AuthMate's async lifespan/context manager from its own lifespan.
Do not assume mounting a subapplication automatically executes its lifespan; FastAPI
documents lifespan execution for the main app.
[Source: FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/).
Test two AuthMate instances, shared host lifespan, failed initialization, and shutdown
cleanup. Avoid global registry/session state and replacing host exception handlers.

Use Depends/Annotated for authenticated actor, AccessContext, resource lookup,
services, and request unit-of-work access. Dependencies adapt HTTP to domain services;
security enforcement also runs inside services. Background operations receive
explicit context and fresh sessions, never a captured request/session object.

`yield` closes request resources, but protected writes and audit commit before the
service returns success. Long-lived provider clients belong to lifespan. Blocking
password hashes/SDK calls run off the event loop with bounded concurrency. ORM
sessions are never reused by concurrent tasks.

## Security and schemas

Document browser cookies and machine HTTP bearer authentication as separate schemes.
Use Security() and FastAPI extraction helpers where useful; declaring a scheme or
OAuth scope does not implement token validation or exact-resource authorization.
Resource-specific dependencies build references from trusted consumer lookups.

Keep strict JSON Content-Type validation; explicitly enforce/test the expected media
types and 415 error contract for supported versions instead of relying only on a
host setting. FastAPI documents strict JSON handling as its current default.
[Source: FastAPI strict content type](https://fastapi.tiangolo.com/advanced/strict-content-type/).
This does not replace origin/CSRF/session checks in [Authentication](AUTHENTICATION.md).

Separate input/output Pydantic models. Passwords and credential values are write-only;
new service-account tokens and CSRF values have narrow intentional response schemas
with no-store headers. No ordinary metadata/validation/error schema contains them.
Configure AuthMate-route validation/error translation to strip raw rejected input
and provider errors. Preserve the host's handling for unrelated routes; integration
may use a scoped route wrapper rather than a global validation-handler replacement.

OpenAPI publishes truthful schemes, errors, bounded pagination, and response models.
AuthMate's resource/grant semantics stay authoritative when OpenAPI cannot express
them. Schema generation never invokes providers or claims resolvers with real secrets.

## Verification

Use dependency overrides for fake identities, providers, sessions, and audit faults.
Test authorization inside direct service calls as well as through routes. Test
cookie/origin/CSRF behavior, wrong/ambiguous mechanisms, validation redaction, host
handler isolation, cancellation, and proper commits before responses.
