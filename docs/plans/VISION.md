# AuthMate Vision

## Purpose

AuthMate prevents every FastAPI application from independently rebuilding users, RBAC, service accounts, credential delegation, secret storage, and authorization dependencies.

The primary compatibility target is one deployable app:

```text
FastAPI
├── Hedron UI
├── AuthMate
├── ShuETL
└── custom APIs
```

while every package remains independently useful.

## Responsibilities

AuthMate owns principals, users, authentication, roles, permissions, resource grants, service accounts, credential metadata/grants, secret-provider abstraction, optional encrypted local secret storage, audit events, and FastAPI security dependencies.

It does not own Hedron pages, ShuETL pipelines/runs, ETLantic execution, or consumer resource models.

## Principles

1. **Composition first** — mount into an existing FastAPI app.
2. **Generic resources** — authorize resources such as `shuetl.pipeline`, `hedron.page`, or `myapp.report`.
3. **Human and workload identity** — users and service accounts share a principal model.
4. **Explicit delegation** — permission to trigger work is separate from a workload's permission to use credentials.
5. **Late secret resolution** — persistent records store references, not resolved secrets.
6. **Shared authorization** — Hedron visibility and FastAPI enforcement consume the same engine; server enforcement remains authoritative.
7. **Standalone usefulness** — AuthMate works without Hedron or ShuETL.
