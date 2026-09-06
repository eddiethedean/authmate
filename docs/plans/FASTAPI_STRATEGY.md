# FastAPI Strategy

## Principle

AuthMate should use FastAPI as its runtime integration substrate rather than recreating routing, dependency injection, security-scheme plumbing, lifecycle hooks, OpenAPI, or testing overrides.

## Required FastAPI features

### APIRouter
Expose AuthMate as composable routers with clear prefixes/tags.

### Dependency injection
Use `Depends` and `Annotated` for current principal, database/session access, authorization provider, credential resolver, audit sink, and external authenticator/provider clients.

FastAPI dependency injection is the preferred runtime composition mechanism.

### Security()
Use `Security()` where OAuth/OpenAPI scopes map cleanly to AuthMate permissions. Scopes must not replace AuthMate's resource-scoped authorization model.

### Router-level dependencies
Use router-level dependencies for broad management/security boundaries, then endpoint/service checks for resource-specific permissions.

### yield dependencies
Use `yield` dependencies for request-scoped SQLModel/SQLAlchemy sessions and short-lived provider resources.

### Lifespan
Use FastAPI lifespan for startup/shutdown of long-lived provider clients and AuthMate service resources.

### Security schemes
Reuse FastAPI-native bearer/API-key/OAuth2/OpenID Connect security primitives rather than inventing custom token-extraction middleware.

### Separate input/output models
Security-sensitive APIs use explicit input/output Pydantic models. Passwords, tokens, and secret material are write-only and never appear in response schemas.

### Strict content type
Keep FastAPI strict content-type behavior enabled unless a documented compatibility requirement says otherwise.

### Exception handling
Define a stable AuthMate error envelope and map AuthMate exceptions plus request-validation errors through custom handlers.

### OpenAPI
Treat OpenAPI as a product surface for security requirements, response models, scopes, SDK generation, and carefully scoped `x-authmate-*` metadata where standard OpenAPI is insufficient.

### Testing
Use FastAPI dependency overrides for fake identity providers, credential resolvers, audit sinks, and database/session fixtures.

## Do not misuse

- Do not implement resource authorization in global middleware when DI/service checks are sufficient.
- Do not rely on UI visibility as authorization.
- Do not disable strict content-type checking casually.
- Do not expose provider-specific security objects in response models.
