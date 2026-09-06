# API Design

Recommended prefix: `/api/auth`.

## Authentication

```http
POST /auth/login
POST /auth/logout
POST /auth/refresh
GET  /auth/me
```

## Users and roles

```http
POST  /auth/users
GET   /auth/users
GET   /auth/users/{id}
PATCH /auth/users/{id}
POST  /auth/users/{id}/disable

POST   /auth/roles
GET    /auth/roles
PATCH  /auth/roles/{id}
POST   /auth/role-bindings
DELETE /auth/role-bindings/{id}
```

## Service accounts

```http
POST  /auth/service-accounts
GET   /auth/service-accounts
GET   /auth/service-accounts/{id}
PATCH /auth/service-accounts/{id}
POST  /auth/service-accounts/{id}/disable
```

## Credentials

```http
POST  /auth/credentials
GET   /auth/credentials
GET   /auth/credentials/{id}
PATCH /auth/credentials/{id}
POST  /auth/credentials/{id}/rotate
POST  /auth/credentials/{id}/disable

POST   /auth/credentials/{id}/grants
GET    /auth/credentials/{id}/grants
DELETE /auth/credentials/{id}/grants/{grant_id}
```

Secret material is write-only where creation/update requires it and never appears in normal response schemas.

## Audit

```http
GET /auth/audit-events
```

All management routes require server-side authorization, bounded pagination, Pydantic schemas, structured errors, and OpenAPI documentation.

## FastAPI-specific API requirements

- Use `APIRouter` for authentication, users, roles, service accounts, credentials, and audit.
- Use router-level dependencies for broad management boundaries.
- Reuse FastAPI-native bearer/API-key/OAuth2/OIDC security helpers.
- Keep strict content-type validation enabled.
- Define explicit normal/error response models.
- Use separate Pydantic request/response models for secret-bearing operations.
- Add OpenAPI scopes/security requirements where they faithfully represent AuthMate behavior.
