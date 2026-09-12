# AuthMate Roadmap

## Phase 0 — Validate contracts and security design

Implement a small end-to-end spike: session authentication, generic resource
permission, actor/effective-account validation, environment credential resolution,
and transactional audit. Use standalone generic consumers; do not freeze protocols
before proving them. Specify SQL constraints, permission catalog, lifecycle, error,
and migration contracts. Exit when design review and threat cases are concrete
and implementable; this phase is not a production release.

## Phase 1 — Standalone MVP

Complete [MVP gates G01–G12](MVP.md), including revocation, rate limiting, CSRF,
bootstrap/recovery, multi-replica SQL state, redaction, migrations, and operational
recovery. Publish tested public contracts and a consumer conformance kit. No sibling
project, UI, or unreleased adapter is a dependency of this phase.

## Phase 2 — Operational extensions

Add operator-facing session administration, audit retention/export tooling with a
SQL outbox, richer diagnostics, and optional encrypted SQL storage only after its
crypto/key-rotation/restore release gate. These extend a secure MVP; baseline
revocation and abuse prevention are already required in Phase 1.

## Phase 3 — Federation and authentication options

Add optional OIDC/OAuth2 adapters, MFA, identity linking, and recovery/verification
flows with explicit threat models. Custom signed-token claims, JWT access tokens,
refresh rotation/reuse detection, proxy identity, and client certificates each
require conformance tests before support is advertised.

## Phase 4 — Provider ecosystem

Add optional external secret-manager adapters and writable-provider rotation/health
workflows. All conform to AuthMate-owned capability, authorization, audit, and
redaction contracts. No external backend becomes a baseline requirement.

## Phase 5 — Authorization evolution

Add groups, richer scopes, and tenant/workspace isolation only with explicit schema,
lookup, token, grant, and migration semantics. Consider a policy language when
real requirements exceed RBAC. Custom lifecycle hooks need transaction and delivery
contracts before becoming a stable extension family.

## Independent consumer tracks

Hedron, ShuETL, and any other consumer may build adapters against published AuthMate
contracts whenever useful. Their packages own mapping, UI/workflow behavior, version
pins, and real compatibility CI. AuthMate can provide generic examples and review
contract feedback without incorporating consumer-domain logic or release gates.
