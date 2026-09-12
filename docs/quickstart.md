# AuthMate 0.1.0 quickstart

AuthMate 0.1.0 defines a small, provider-neutral contract. A host application owns authentication and resource lookup; AuthMate receives a verified `AccessContext`, loads current principal state, and asks an `AuthorizationProvider` for one decision.

```python
from authmate import AccessContext, AuthMateSecurity

security = AuthMateSecurity(authmate, context_dependency=current_context)
require_report = security.require("report.read", resource_dependency=current_report)
```

Use `require_report` with `fastapi.Depends` on a route. An allow result is returned to the route. A policy denial becomes HTTP 403 with `{"detail": {"code": "authorization_denied"}}`; a provider failure or contract violation becomes HTTP 503 with `{"detail": {"code": "authmate_unavailable"}}`. Authentication failures, resource-not-found responses, and other host concerns remain owned by the dependencies.

The service is intentionally stateless. It does not create sessions or tokens, call an identity provider, persist principals, resolve credentials, emit audit events, or provide a default policy. `effective` delegation is rejected with a typed denial in this preview. Provider exceptions are sanitized into a deny decision, and `AuthMate.aclose()` drains active checks before closing providers in reverse construction order.

Implement all provider `aclose()` methods. Provider objects may be shared; AuthMate closes an object only once. Call `aclose()` from the host application's shutdown lifecycle.

The public models are immutable Pydantic v2 values with extra fields forbidden. Action names use dotted lower-case segments such as `report.read`; resource references carry a dotted type and an exact opaque id. Timestamps must be timezone-aware and are normalized to UTC.
