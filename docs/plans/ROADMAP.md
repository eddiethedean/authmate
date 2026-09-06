# AuthMate Roadmap

## Phase 0 — Contract freeze

Freeze principal/resource protocols, authorization decisions, credential/secret-provider contracts, FastAPI dependencies, persistence model, and Hedron/ShuETL compatibility contracts.

## Phase 1 — MVP

Deliver local users/authentication, service accounts, RBAC/scopes, credentials/grants, initial secret provider(s), audit, FastAPI router/dependencies, SQLite/PostgreSQL, and integration CI.

## Phase 2 — Operational security

Add richer session management, revocation, rate-limit hooks, credential expiration/rotation workflows, audit export, and security administration.

## Phase 3 — Federation

Add OIDC/OAuth2/enterprise SSO adapters, external identity linking, reverse-proxy identity, and client-certificate/CAC adapters.

## Phase 4 — Secret ecosystems

Add optional Azure Key Vault, AWS Secrets Manager, HashiCorp Vault, Kubernetes Secrets, and provider health/rotation integrations.

## Phase 5 — Authorization evolution

Add groups, richer scopes, workspace/tenant boundaries, and only then consider a policy language if RBAC cannot express proven requirements.

## Phase 6 — Hedron experience

Ship reusable login/profile/admin components and first-class user/role/service-account/credential/audit pages through an optional integration.

## Phase 7 — ShuETL hardening

Add credential rotation impact views, pipeline-to-credential dependency inspection, service-account health, and security-focused run diagnostics.
