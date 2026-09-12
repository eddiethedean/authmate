# Phase 0.1 — Architecture & Implementation Plan

Status: ready implementation contract

Target release: `0.1.0` contract preview

This document is authoritative for phase `0.1`. Later roadmap phases and broader
planning documents provide context but do not expand this change. If they conflict
with this document, implementation must follow this bounded contract and record the
broader conflict for later planning.

## Repository ground truth

The repository was inspected at commit `94fb867` on 2026-09-12.

- The repository contains 21 Markdown planning documents and no production package,
  tests, examples, dependency manifest, lockfile, migrations, or CI workflows.
- There is no existing public Python API or persisted data to preserve.
- The default branch is `main`; the remote is `eddiethedean/authmate`.
- GitHub reports no open implementation issues and no status checks on the inspected
  commit.
- The roadmap defines `0.1` as a contract preview, followed by persistence in `0.2`,
  local authentication in `0.3`, and full authorization semantics in `0.4`.
- Existing plans require Pydantic v2 contracts, FastAPI composition, provider-neutral
  services, deny-by-default behavior, explicit lifecycle handling, and no imports
  from consumer projects.
- Existing plans do not select a Python version range or concrete phase `0.1`
  dependency versions. This plan selects them below.
- The repository now carries the MIT License in `LICENSE` and matching PEP 639
  metadata; issue [#1](https://github.com/eddiethedean/authmate/issues/1) is resolved.

Current upstream package metadata supports the selected runtime range:
[FastAPI](https://pypi.org/project/fastapi/) `0.140+` supports Python 3.10+, and
[Pydantic](https://pypi.org/project/pydantic/) `2.12+` includes Python 3.14
support. Phase `0.1` intentionally supports CPython 3.11 through 3.14.

## Architecture summary

Phase `0.1` establishes a typed authorization seam and proves that the same service
enforcement works from Python and FastAPI. It does not establish an identity system.

```text
Trusted host context dependency       Trusted background caller
                |                              |
                +-------- AccessContext -------+
                               |
                         AuthMate facade
                               |
                +--------------+---------------+
                |                              |
        PrincipalProvider             AuthorizationProvider
                |                              |
         current principal              allow/deny decision
```

The host authenticates a caller and supplies `AccessContext`; AuthMate does not read
an identity from request headers, bodies, query parameters, or cookies in this
release. The facade reloads current principal state, rejects unsupported delegation,
invokes one authorization provider, validates the provider response, and exposes
`authorize()`, `can()`, and `require()`.

Credential, secret-provider, and audit interfaces are defined and exercised with
test fakes so later features have a concrete extension shape. They are not wired to
the service facade and cannot resolve or persist real credentials in `0.1`.

The package uses a `src/` layout with these module responsibilities:

```text
src/authmate/
├── __init__.py       stable convenience exports and __version__
├── errors.py         sanitized domain exception hierarchy
├── models.py         immutable public Pydantic values
├── protocols.py      provider Protocol definitions
├── secrets.py        non-serializable SecretValue lease value
├── service.py        AuthMate authorization facade
├── fastapi.py        host-supplied context/resource dependency adapter
└── py.typed           PEP 561 marker
```

No module in `authmate` may import an example, test fake, consumer package, ORM,
database driver, password library, cryptography library, or migration library.

## Change boundary

### Problem

AuthMate currently exists only as broad planning. There is no installable package
or executable contract proving that consumer-neutral identity references,
authorization providers, direct Python calls, and FastAPI dependencies can compose
without bypassing service checks.

### Desired outcome

After `0.1`, another application can install the preview package, provide trusted
principal and authorization providers, authorize a direct or FastAPI operation, and
receive predictable typed decisions and sanitized failures. Maintainers can run one
documented command set to validate all supported Python versions and build artifacts.

The release documentation clearly states that `0.1` does not authenticate users,
persist policy, implement RBAC, or manage credentials.

### In scope

- Initial PEP 621 package, lockfile, build configuration, and typed `src/` layout.
- CPython 3.11, 3.12, 3.13, and 3.14 support.
- Pydantic v2 public models and stable JSON-mode serialization.
- Principal, authorization, credential-resolver, secret-provider, and audit protocols.
- An async `AuthMate` facade for direct authorization.
- A FastAPI dependency factory using a host-owned trusted context dependency.
- Provider timeout, exception normalization, response validation, and cleanup.
- A redacted, explicitly closed `SecretValue` used only by protocol tests.
- Unit, contract, property, FastAPI integration, packaging, and import-boundary tests.
- One generic report-resource example and one direct background-call example.
- GitHub Actions quality and supported-runtime matrices.
- Documentation describing the preview API, trust boundary, and limitations.

## Explicit non-scope

- Users, passwords, login, sessions, bearer-token parsing, API-token issuance, CSRF,
  rate limiting, bootstrap, account recovery, or any authenticator.
- SQLModel, SQLAlchemy, Alembic, database drivers, tables, repositories, migrations,
  transactions, or durable audit.
- RBAC roles, permissions, bindings, action/resource registries, groups, tenancy,
  policy caching, or service-account assumption grants.
- Support for an effective principal different from the actor. The model can express
  it, but the `0.1` facade must deny it as unsupported before provider authorization.
- Credential metadata, grants, environment access, secret resolution through the
  facade, real secret values, encryption, or external secret managers.
- Management routers, the planned `/api/auth` HTTP API, OpenAPI security schemes,
  custom application-wide exception handlers, or middleware.
- Hedron, ShuETL, ETLantic, or any other consumer-specific adapter or test dependency.
- Stable `1.0` compatibility, PyPI publication, release automation, benchmarks, or
  production-readiness claims.
- Fixing unrelated repository governance or documentation concerns.

## Touched surface

The implementation is expected to create or update only:

```text
pyproject.toml
uv.lock
.gitignore
.github/workflows/ci.yml
src/authmate/**
tests/unit/**
tests/contract/**
tests/integration/**
tests/property/**
tests/packaging/**
examples/report_consumer.py
examples/background_authorization.py
README.md
docs/quickstart.md
docs/plans/PHASE_0_1_IMPLEMENTATION_PLAN.md
docs/plans/README.md
```

An implementer may split modules or tests differently if the public imports and
observable behavior below remain identical. No persistence or consumer repository
should change.

## Public contract

### Required behavior

#### Packaging and runtime

- Distribution name: `authmate`.
- Initial version: `0.1.0`.
- Import package: `authmate`.
- `requires-python`: `>=3.11,<3.15`.
- Supported interpreter: CPython only for `0.1`; PyPy is unclaimed.
- Runtime dependencies: `pydantic>=2.12,<3` and `fastapi>=0.140,<1`.
- Build backend: Hatchling with a `src/` package layout.
- The wheel includes `authmate/py.typed` and no tests or examples.
- `authmate.__version__` is the literal package version `0.1.0` and equals the
  installed distribution metadata in the built artifact without reading project
  files at import time.
- Importing `authmate`, `authmate.models`, `authmate.protocols`, or
  `authmate.service` performs no I/O and creates no global provider/service instance.

The committed development lockfile is authoritative for contributor and CI runs.
Declared runtime ranges remain the installation contract. CI must separately test
the declared lower bounds so the lockfile does not conceal an invalid minimum.

Development dependencies live in a non-runtime `dev` dependency group and use these
major-version bounds: pytest `>=9,<10`, pytest-asyncio `>=1,<2`, pytest-cov `>=7,<8`,
Hypothesis `>=6,<7`, HTTPX `>=0.28,<1`, mypy `>=1.17,<2`, Ruff `>=0.16,<1`, build
`>=1.3,<2`, and Twine `>=6,<7`. Hatchling is `>=1.27,<2` in `build-system.requires`.
Exact resolved versions are committed in `uv.lock`.

The required local and CI commands are:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run mypy --strict src/authmate tests
uv run pytest --cov=authmate --cov-branch --cov-fail-under=95
uv build
uv run twine check dist/*
```

GitHub Actions contains four required jobs: `quality` on CPython 3.14 with the locked
environment; `tests` on Ubuntu with CPython 3.11, 3.12, 3.13, and 3.14; `lower-bounds`
on CPython 3.11 with the declared FastAPI/Pydantic minima; and `package` on CPython
3.14, which builds, inspects, installs, and smoke-tests the wheel and sdist in clean
environments. Actions and the `uv` installer are pinned to immutable revisions. No
publish job is added in `0.1`.

#### Common model behavior

All public Pydantic models use `extra="forbid"`, are frozen after construction, and
produce only JSON-compatible values from `model_dump(mode="json")`. They never trim
security-relevant strings silently. Unknown fields, wrong primitive types, naive
datetimes, nil UUIDs, leading/trailing whitespace, ASCII control characters, and
values beyond stated bounds are rejected with `ValidationError`.

JSON input may express UUIDs and aware datetimes as strings. Serialization uses
lowercase hyphenated UUID strings, enum values, and RFC 3339 timestamps normalized
to UTC with a `Z` suffix. Serialization never emits Python enum objects or UUIDs.

The following names and fields are public:

| Type | Required fields and validation |
| --- | --- |
| `PrincipalKind` | String enum: `user`, `service_account` |
| `PrincipalRef` | `id: UUID` (non-nil), `kind: PrincipalKind` |
| `PrincipalRecord` | `ref`, `display_name` (1–200 characters), `enabled: bool`, `expires_at: aware datetime | None = None`, `version: int >= 0 = 0` |
| `ResourceRef` | `type` is a 3–100 character lowercase dotted name; `id` is an exact 1–255 character consumer ID |
| `AccessContext` | `actor: PrincipalRef`, `effective: PrincipalRef | None = None`, `correlation_id: str | None = None` |
| `DecisionReason` | String enum listed below |
| `AuthorizationDecision` | `allowed`, `reason`, `action`, `resource`, `policy_revision: str | None = None` |
| `CredentialRef` | `id: UUID` (non-nil) |
| `SecretReference` | `provider` is a lowercase 1–63 character alias matching `^[a-z][a-z0-9_-]{0,62}$`; `key` is an opaque 1–255 character exact reference |
| `AuditOutcome` | String enum: `succeeded`, `denied`, `failed` |
| `AuditEvent` | Required `id: UUID`, dotted `event_type: str`, aware `occurred_at: datetime`, and `outcome: AuditOutcome`; optional `actor`, `effective`, `action`, `resource`, `reason_code`, and `correlation_id` default to `None`; no free-form metadata in `0.1` |

Dotted names, including actions, resource types, and event types, match:

```text
^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$
```

Actions and event types are at most 200 characters. Resource types are at most 100.
`ResourceRef.id`, `SecretReference.key`, display names, policy revisions, and
correlation IDs reject leading/trailing whitespace and ASCII control characters.
Correlation IDs are at most 128 characters and contain only ASCII letters, digits,
period, underscore, colon, and hyphen. `AccessContext.effective` must be omitted for
a direct actor; setting it equal to `actor` is invalid rather than normalized.
Audit reason codes are 1–100 lowercase characters matching
`^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$` when present.

`DecisionReason` has exactly these `0.1` values:

```text
allowed
denied
principal_not_found
principal_disabled
principal_expired
delegation_not_supported
provider_unavailable
provider_contract_violation
```

An allowed decision must use reason `allowed`; a denied decision must use any other
reason. `policy_revision`, when present, is 1–128 characters. A principal is expired
when `expires_at <= now`.

#### Provider protocols

`authmate.protocols` exports structural, async-first typing protocols. Protocols are
not marked `runtime_checkable`; conformance is established by static checks and the
test suite rather than a misleading `isinstance()` check.

```python
class PrincipalProvider(Protocol):
    async def get_principal(self, ref: PrincipalRef) -> PrincipalRecord | None: ...

    async def aclose(self) -> None: ...


class AuthorizationProvider(Protocol):
    async def authorize(
        self,
        *,
        principal: PrincipalRecord,
        action: str,
        resource: ResourceRef | None,
    ) -> AuthorizationDecision: ...

    async def aclose(self) -> None: ...


class CredentialResolver(Protocol):
    def resolve(
        self,
        *,
        context: AccessContext,
        credential: CredentialRef,
    ) -> AsyncContextManager[SecretValue[Any]]: ...

    async def aclose(self) -> None: ...


class SecretProvider(Protocol):
    def resolve(self, reference: SecretReference) -> AsyncContextManager[SecretValue[Any]]: ...

    async def aclose(self) -> None: ...


class AuditSink(Protocol):
    async def record(self, event: AuditEvent) -> None: ...

    async def aclose(self) -> None: ...
```

`get_principal()` returning `None` means the principal is not known. Providers raise
`ProviderUnavailableError` for expected operational unavailability. An unexpected
ordinary exception is treated the same at the facade boundary. Cancellation is
never converted to a decision.

`CredentialResolver`, `SecretProvider`, and `AuditSink` are type contracts only in
this release. No production implementation, registry, facade method, network call,
or filesystem/environment access is provided.

#### SecretValue

`SecretValue[T]` is a final, non-Pydantic value used to make protocol lifecycle and
redaction testable. It has `reveal() -> T`, `close() -> None`, and context-manager
cleanup through the resolver/provider protocols.

- `str(value)` and `repr(value)` return a constant redacted marker without type,
  length, hash, or content information.
- `close()` is idempotent and drops AuthMate's reference to the wrapped object.
- `reveal()` after close raises `SecretClosedError` with a constant safe message.
- Pickling and Pydantic/JSON serialization raise a safe error rather than revealing
  the value.
- AuthMate makes no claim that arbitrary Python object copies can be zeroized.

Only synthetic test values may be used in phase `0.1` examples and tests.

#### Error contract

`authmate.errors` exports:

```text
AuthMateError
├── InvalidAuthorizationRequestError
├── AuthorizationDeniedError
├── AuthMateUnavailableError
│   ├── ProviderUnavailableError
│   └── ProviderContractError
├── AuthMateConfigurationError
├── AuthMateClosedError
└── SecretClosedError
```

Every `AuthMateError` has a stable string `code`. Its `str()` contains a constant,
human-readable message and never includes model input, provider exception text,
principal/resource IDs, or secret values. `AuthorizationDeniedError` exposes its
typed `decision` attribute. `AuthMateUnavailableError` also exposes a typed
`decision` when `require()` raises it for an unavailable or contract-violation
result; its public annotation is `AuthorizationDecision | None` for direct provider
use. The facade discards normalized provider exception text and does not attach it to
a public decision or raised `require()` error. Providers may implement their own safe
observability outside this contract.

| Exception | `code` | Constant `str()` message |
| --- | --- | --- |
| `InvalidAuthorizationRequestError` | `invalid_authorization_request` | `invalid authorization request` |
| `AuthorizationDeniedError` | `authorization_denied` | `authorization denied` |
| `AuthMateUnavailableError` | `authmate_unavailable` | `authorization service unavailable` |
| `ProviderUnavailableError` | `provider_unavailable` | `provider unavailable` |
| `ProviderContractError` | `provider_contract_violation` | `provider contract violation` |
| `AuthMateConfigurationError` | `authmate_configuration_error` | `invalid AuthMate integration configuration` |
| `AuthMateClosedError` | `authmate_closed` | `AuthMate is closed` |
| `SecretClosedError` | `secret_closed` | `secret value is closed` |

`ProviderUnavailableError` is available for provider implementations to signal an
operational failure. `ProviderContractError` represents a provider response that
violates the required type or request echo. Neither is a normal policy denial.

#### AuthMate facade

The public constructor and methods are:

```python
class AuthMate:
    def __init__(
        self,
        *,
        principal_provider: PrincipalProvider,
        authorization_provider: AuthorizationProvider,
        provider_timeout_seconds: float = 5.0,
    ) -> None: ...

    async def authorize(
        self,
        *,
        context: AccessContext,
        action: str,
        resource: ResourceRef | None = None,
    ) -> AuthorizationDecision: ...

    async def can(...same keyword arguments...) -> bool: ...
    async def require(...same keyword arguments...) -> AuthorizationDecision: ...
    async def aclose(self) -> None: ...
```

The timeout must be finite and between 0.01 and 60 seconds inclusive; invalid values
raise `ValueError` during construction. It applies independently to principal and
authorization-provider calls.

`authorize()` performs exactly this observable sequence:

1. Reject a call after closure with `AuthMateClosedError`.
2. Validate the action without trimming or case conversion. Invalid input raises
   `InvalidAuthorizationRequestError`; no provider is called.
3. If `context.effective` is present, return a denied decision with
   `delegation_not_supported`; no provider is called.
4. Load the actor from `PrincipalProvider` under the timeout.
5. Return `principal_not_found`, `principal_disabled`, or `principal_expired` as
   applicable. The authorization provider is not called for these states.
6. Treat a returned `PrincipalRecord.ref` different from the requested actor as
   `provider_contract_violation`.
7. Invoke `AuthorizationProvider.authorize()` once, with the current record and exact
   action/resource, under the timeout.
8. Validate that the result is an `AuthorizationDecision` and exactly echoes the
   action and resource. A mismatch becomes `provider_contract_violation`.
9. Return the validated decision. The facade never turns a deny into an allow.

Provider timeouts, declared unavailability, and unexpected ordinary exceptions
produce a denied `AuthorizationDecision` with `provider_unavailable`. Provider
response violations produce a denied decision with `provider_contract_violation`.
Those decisions echo the requested action/resource and omit policy revision.
`asyncio.CancelledError`, `KeyboardInterrupt`, and `SystemExit` propagate.

`can()` calls `authorize()` exactly once and returns only `decision.allowed`. It is
`False` for every deny and unavailable result. `require()` calls `authorize()`
exactly once and returns the allowed decision. It raises `AuthorizationDeniedError`
for policy, missing/disabled/expired-principal, and unsupported-delegation decisions;
it raises `AuthMateUnavailableError` for unavailable or contract-violation decisions.

The facade owns the two providers passed to it. The first `aclose()` atomically marks
the facade closing, rejects new operations, waits for every operation that entered
before that transition to finish, then closes authorization followed by principal
provider. It de-duplicates the same object by identity and attempts every distinct
close after ordinary close failures. Multiple ordinary failures are raised as an
`ExceptionGroup`.

Exactly one internal shutdown task performs cleanup. Concurrent and later `aclose()`
calls await that same task and observe the same success or stored exception; providers
are never closed twice. Awaiting the task is shielded so cancelling one caller
propagates `CancelledError` to that caller without cancelling shared cleanup. Every
service method after closing begins raises `AuthMateClosedError`.

#### FastAPI adapter

`authmate.fastapi` exports `AuthMateSecurity` and dependency type aliases.

```python
security = AuthMateSecurity(
    authmate,
    context_dependency=host_current_access_context,
)


@router.get("/reports/{report_id}")
async def read_report(
    decision: Annotated[
        AuthorizationDecision,
        Depends(
            security.require(
                "example.report.read",
                resource_dependency=current_report_resource,
            )
        ),
    ],
): ...
```

The host dependency is the authentication trust boundary. AuthMate does not provide
a default context dependency. The adapter must not inspect headers, cookies, query
parameters, request bodies, or session state to construct an identity.

`security.require(action, resource_dependency=None)` validates the action when the
dependency is created. With no resource dependency it authorizes `resource=None`.
With one, FastAPI resolves that callable and it must return a `ResourceRef` derived
from the consumer's trusted resource lookup. Wrong context/resource return types
raise `AuthMateConfigurationError`, a subclass of `AuthMateError`, and are not
reported as caller validation errors.

The dependency calls `AuthMate.require()`; it does not duplicate authorization.
It maps `AuthorizationDeniedError` to HTTP 403 with exactly
`{"detail": {"code": "authorization_denied"}}`, and
`AuthMateUnavailableError` to HTTP 503 with exactly
`{"detail": {"code": "authmate_unavailable"}}`. It does not serialize the
underlying reason, IDs, exception cause, or provider text. HTTP exceptions raised by
the host context/resource dependencies propagate unchanged. The adapter installs no
router, middleware, global exception handler, lifespan, or OpenAPI security scheme.

#### Imports and versioned surface

`authmate` exports `AuthMate`, all public models/enums, the documented errors, and
`__version__`. Provider protocols remain under `authmate.protocols`, `SecretValue`
under `authmate.secrets`, and FastAPI helpers under `authmate.fastapi`. All modules
are covered by `py.typed` and strict static analysis.

Names not listed in this document are internal in `0.1`. JSON schema snapshots and
the documented import paths are compatibility artifacts for patch releases within
the `0.1` line.

### Recommended implementation

The implementer may adapt these internal choices while preserving required behavior:

- Use Pydantic field/model validators plus reusable annotated string aliases for
  bounded names and exact identifiers.
- Inject an internal UTC clock callable into `AuthMate` for deterministic expiry
  tests without exposing it as a documented public argument.
- Use `asyncio.timeout()` for provider deadlines and an identity-keyed ordered list
  for lifecycle de-duplication.
- Use private helper functions to create facade-owned deny decisions so providers
  cannot influence reason normalization.
- Use Hatchling, `uv`, Ruff, mypy strict mode, pytest, pytest-asyncio, HTTPX, and
  Hypothesis. Lock exact development versions in `uv.lock`; keep public dependency
  ranges in `pyproject.toml`.
- Keep test fakes under `tests/contract/fakes.py`; do not ship them as public helpers
  until the conformance kit is designed for `0.6`.

## Invariants

- **INV-001 — References are not identity proof.** A model supplied by an HTTP caller
  is never accepted as authenticated context by AuthMate itself.
- **INV-002 — Current state precedes policy.** AuthorizationProvider is never called
  for an absent, disabled, expired, mismatched, or delegated principal in `0.1`.
- **INV-003 — Deny is monotonic.** No wrapper or adapter converts a denied/unavailable
  result into allow.
- **INV-004 — Request echo is exact.** An allowed provider result applies only to the
  exact action and resource passed to that invocation.
- **INV-005 — Provider failure fails closed.** Timeouts and ordinary exceptions
  cannot escape as allow or expose provider text to HTTP clients.
- **INV-006 — Cancellation remains cancellation.** Cancellation is not converted to
  denial or unavailability.
- **INV-007 — Models are immutable and bounded.** Public contract values reject
  extras and invalid bounds and have deterministic JSON-mode serialization.
- **INV-008 — Secrets do not serialize.** `SecretValue` never reveals content through
  stringification, representation, pickling, JSON, or Pydantic serialization.
- **INV-009 — Direct and HTTP enforcement agree.** The FastAPI dependency delegates
  to the same facade and cannot maintain separate policy logic.
- **INV-010 — Lifecycle has one owner.** Each distinct injected provider is closed at
  most once by a successful/idempotent shutdown and cannot be used afterward.
- **INV-011 — Core is consumer-neutral.** Production and test-collection imports do
  not require or conditionally import consumer packages.
- **INV-012 — Phase boundary is explicit.** No `0.1` artifact claims authentication,
  persistence, RBAC, credential management, or production readiness.

## Edge cases and failure modes

| Case | Required outcome |
| --- | --- |
| Empty/malformed action | Safe `InvalidAuthorizationRequestError`; zero provider calls |
| Nil UUID or invalid enum/model field | Pydantic `ValidationError` before service use |
| Unknown actor | Denied `principal_not_found`; no authorization-provider call |
| Disabled actor | Denied `principal_disabled`; no authorization-provider call |
| Expiry equal to current instant | Denied `principal_expired` |
| Effective principal supplied | Denied `delegation_not_supported`; no provider call |
| Principal provider returns a different ref | Denied `provider_contract_violation` |
| Provider returns wrong object, action, or resource | Denied `provider_contract_violation` |
| Provider returns inconsistent allowed/reason pair | Model validation or contract violation; never allow |
| Provider returns `None` instead of a decision | Denied `provider_contract_violation` |
| Either provider times out or raises `Exception` | Denied `provider_unavailable`; no exception text in decision/HTTP |
| Provider call is cancelled | `CancelledError` propagates |
| Repeated `can()` / `require()` | Fresh provider evaluation each time; no cache |
| Concurrent authorization calls | No shared mutable request state or cross-call decisions |
| Facade close during/around use | Calls begun after close starts fail; close waits for already-entered calls before provider cleanup |
| Same object supplies both providers | It is closed once |
| One provider close fails | Remaining distinct provider close is attempted; error reported after cleanup |
| Repeated/concurrent close | All callers await one shielded cleanup task; providers close once and callers observe its stored outcome |
| SecretValue is empty or wraps mutable data | Redaction and close rules remain identical; no truthiness/content disclosure in repr |
| FastAPI host dependency raises 401 | The host's 401 propagates unchanged |
| FastAPI resource does not exist | Consumer dependency owns 404; AuthMate is not called |
| FastAPI dependency returns the wrong type | Configuration error; never a caller 422 or authorization allow |
| Wheel installed without repository checkout | Imports, typing marker, version, and examples documented for users still work |

There is no existing data, schema, or migration path in this phase. Upgrade and
migration behavior begins in `0.2`.

## Security and reliability requirements

- Trust only the host-supplied context dependency or direct trusted Python caller;
  never derive a principal from unchecked transport fields.
- Validate every provider result after the await boundary. Structural typing helps
  development but is not runtime trust.
- Bound each provider await independently with the configured timeout.
- Do not catch `BaseException`; cancellation and process-control exceptions propagate.
- Do not log provider exception messages, model input, or identifiers in the package.
  Phase `0.1` introduces no package logging API.
- Do not cache principal records or authorization decisions.
- Keep the service stateless except for provider references and lifecycle state.
- Use constant public HTTP error bodies and no global exception handler.
- Keep synthetic secret values out of assertion failure messages by comparing only
  safe sentinels and redacted representations.
- Ensure cleanup tests cover in-flight draining, normal completion, partial ordinary
  failure, duplicate provider identity, repeat/concurrent close, and cancellation of
  one close waiter.
- Examples must carry a conspicuous comment that their fixed context dependency is
  trusted test/demo wiring and is not an authentication method.

## Compatibility requirements

There is no prior code API, persisted format, or user behavior to preserve. The
following become patch-level compatibility promises for `0.1.x`:

- documented import paths and call signatures;
- enum string values and error `code` values;
- Pydantic field names, validation bounds, and JSON-mode serialization;
- 403/503 FastAPI response bodies produced by `AuthMateSecurity`;
- CPython 3.11–3.14 and the declared FastAPI/Pydantic dependency ranges;
- async-only provider and service semantics;
- consumer-neutral imports and the absence of mandatory infrastructure.

Breaking changes may occur in `0.2` because the project is pre-1.0, but they require
release notes and updates to contract tests/examples. Phase `0.1` must not introduce
persisted data whose compatibility would constrain `0.2` migrations.

## Acceptance criteria

- **AC-001:** A wheel and source distribution named `authmate` version `0.1.0` build
  successfully, and a clean environment can import every documented module on
  CPython 3.11, 3.12, 3.13, and 3.14.
- **AC-002:** The built wheel contains `py.typed`, excludes tests/examples, and
  `authmate.__version__` reports `0.1.0` without reading project files or using the
  network at import time.
- **AC-003:** Every public Pydantic model accepts its documented valid JSON form,
  rejects extras and every documented invalid boundary, is immutable, and emits the
  specified JSON-compatible form.
- **AC-004:** `AuthorizationDecision` rejects inconsistent `allowed`/`reason` pairs,
  and all documented enum values and error codes match this plan exactly.
- **AC-005:** Provider protocols pass strict static typing with conforming async fakes,
  while deliberately malformed fakes fail the dedicated static contract fixture.
- **AC-006:** An active direct actor and an exact matching allow decision cause
  `authorize()` to return that allowed decision after one principal lookup and one
  authorization-provider call.
- **AC-007:** Unknown, disabled, and expired actors produce their documented denied
  decisions without invoking AuthorizationProvider.
- **AC-008:** A supplied effective principal is denied as
  `delegation_not_supported` without invoking either policy authorization or secret
  interfaces.
- **AC-009:** Provider timeout or ordinary exception yields `provider_unavailable`;
  cancellation propagates; no failure path returns allowed.
- **AC-010:** Wrong principal refs and malformed/mismatched authorization-provider
  results yield `provider_contract_violation` and echo the original request.
- **AC-011:** `can()` returns only the allowed bit from one fresh `authorize()` call;
  `require()` returns the allowed decision or raises the documented sanitized denied
  versus unavailable exception with its decision attached where specified.
- **AC-012:** Invalid actions and invalid timeout settings fail before provider work
  with the documented error types.
- **AC-013:** Concurrent calls through one facade retain independent contexts,
  resources, decisions, and provider call records with no cross-request state.
- **AC-014:** `aclose()` rejects new work, drains already-entered operations, uses
  reverse order, closes duplicate provider objects once, attempts remaining providers
  after ordinary failures, shares one shielded cleanup result across callers, and
  prevents later service use.
- **AC-015:** `SecretValue` returns its synthetic value only through `reveal()` before
  close, is redacted through all specified representation/serialization paths, and
  raises `SecretClosedError` after idempotent close.
- **AC-016:** A FastAPI endpoint protected by `AuthMateSecurity.require()` obtains its
  context and resource only from the supplied dependencies and reaches the same
  `AuthMate.require()` behavior as a direct call.
- **AC-017:** The FastAPI adapter maps denial to the exact 403 body, unavailability to
  the exact 503 body, preserves host/resource HTTP exceptions, and installs no global
  application behavior.
- **AC-018:** The generic report example denies an unknown report and unauthorized
  actor, allows its configured actor/resource, and accepts no caller-controlled
  principal field; the background example exercises the same facade without FastAPI.
- **AC-019:** Import-boundary tests prove production modules do not import consumer,
  persistence, migration, password, crypto, or database packages, and the package
  runs with only its declared runtime dependencies.
- **AC-020:** CI runs formatting, lint, strict typing, unit/contract/property/FastAPI
  tests, lower-bound dependency tests, distribution build checks, and clean-wheel
  smoke tests; all required jobs pass before `0.1.0` is tagged.
- **AC-021:** README and quickstart describe the exact public contract and state that
  `0.1` provides no authentication, persistence, RBAC, credential management, or
  production-readiness guarantee; documentation snippets execute in CI.

## Verification matrix

| AC | Preferred proof | Primary target |
| --- | --- | --- |
| AC-001 | Compatibility + packaging | Python matrix build/install/import test |
| AC-002 | Packaging + static gate | Wheel content and installed metadata test |
| AC-003 | Unit + property | Model boundary and JSON round-trip suites |
| AC-004 | Unit + contract | Decision/enumeration/error snapshot tests |
| AC-005 | Static gate + contract | mypy strict valid and expected-failure fixtures |
| AC-006 | Unit | Facade allowed-path call-count test |
| AC-007 | Unit/property | Principal-state table and expiry-boundary test |
| AC-008 | Unit | Delegation-not-supported short-circuit test |
| AC-009 | Unit + async integration | Exception, timeout, and cancellation tests |
| AC-010 | Contract + property | Provider-response mutation/mismatch tests |
| AC-011 | Unit | Facade method semantics and exception assertions |
| AC-012 | Unit/property | Invalid action and finite timeout boundaries |
| AC-013 | Integration/property | Coordinated concurrent request isolation test |
| AC-014 | Unit + integration | Ordered lifecycle, failure, duplicate, repeat tests |
| AC-015 | Unit + property | Repr/str/pickle/Pydantic/JSON/close leakage suite |
| AC-016 | FastAPI integration | HTTPX ASGI app with dependency overrides |
| AC-017 | FastAPI contract | Exact response snapshot and host-error propagation |
| AC-018 | Contract + example smoke | Execute/import examples as tests |
| AC-019 | Static gate + clean install | Import graph scan and minimal-environment smoke |
| AC-020 | Static gate + compatibility | Required GitHub Actions checks |
| AC-021 | Manual + documentation test | README/quickstart snippets executed in CI |

Every AC has an automated primary proof except the accuracy/readability portion of
AC-021, which requires review in addition to executable snippets.

## Implementation phases

### Phase A — Package and quality scaffold

Goal: create an installable empty typed package before defining behavior.

Relevant files: `pyproject.toml`, `uv.lock`, `.gitignore`, `src/authmate/__init__.py`,
`src/authmate/py.typed`, initial packaging tests, and `.github/workflows/ci.yml`.

Required behavior: AC-001, AC-002, and the framework for AC-019/AC-020. Configure
CPython 3.11–3.14, the selected runtime dependency ranges, Hatchling, Ruff, mypy
strict mode, pytest, and build verification. Do not add future runtime dependencies.

Dependencies: none.

### Phase B — Public values and errors

Goal: establish validation, serialization, reason codes, and sanitized exceptions.

Relevant modules: `models.py`, `errors.py`, model/error unit and property tests, JSON
schema snapshots.

Required behavior: AC-003, AC-004, and AC-012 model/action portions. Tests cover every
boundary and forbid accidental coercion, whitespace normalization, extra fields, and
naive time.

Dependencies: Phase A.

### Phase C — Protocol and secret-lifecycle contracts

Goal: make extension shapes type-check and exercise safe secret lifecycle without
wiring any real provider.

Relevant modules: `protocols.py`, `secrets.py`, contract fakes, static contract
fixtures, redaction/property tests.

Required behavior: AC-005 and AC-015. Documentation must label resolver/provider/audit
interfaces as unwired previews.

Dependencies: Phases A–B.

### Phase D — Authorization facade

Goal: implement the one authoritative service path and lifecycle owner.

Relevant modules: `service.py`, facade unit/async/property tests.

Required behavior: AC-006 through AC-014. Exercise call counts and short-circuit order,
not only final return values. Use deterministic time and controlled async providers.

Dependencies: Phases B–C.

### Phase E — FastAPI adapter

Goal: prove transport composition without introducing authentication or global app
behavior.

Relevant modules: `fastapi.py`, `tests/integration/test_fastapi_security.py`.

Required behavior: AC-016 and AC-017. Test host 401 and resource 404 propagation,
exact 403/503 bodies, dependency overrides, and absence of middleware/handlers.

Dependencies: Phase D.

### Phase F — Consumer-neutral examples and import boundaries

Goal: demonstrate intended adoption from HTTP and background code while proving core
independence.

Relevant files: `examples/report_consumer.py`,
`examples/background_authorization.py`, example smoke tests, import graph tests.

Required behavior: AC-018 and AC-019. Use only `example.report.*` resources and
synthetic values. Never import or mention sibling project APIs in executable code.

Dependencies: Phases D–E.

### Phase G — Documentation and release evidence

Goal: align user-facing statements with the implemented preview and run every gate.

Relevant files: root README, `docs/quickstart.md`, planning index, CI workflow, build
configuration, and release notes/changelog if introduced.

Required behavior: AC-020 and AC-021. Run the full locked suite, declared dependency
floors, every supported Python, distribution inspection, and clean install smoke.
Do not publish to PyPI while issue #1 remains unresolved.

Dependencies: all earlier phases.

## Risks

| Risk | Control in this plan |
| --- | --- |
| Preview protocols prematurely constrain later persistence/security work | Keep `0.1` pre-stable, prohibit persisted formats, and cover changes with contract snapshots/release notes |
| AccessContext is mistaken for authentication | No default context extraction; docs/examples label the host dependency as the trust boundary |
| Effective principal field creates an early privilege path | Facade rejects every non-null effective principal before policy evaluation |
| A provider fabricates a decision for another request | Exact action/resource echo validation and contract-violation denial |
| Error handling hides cancellation | Catch ordinary exceptions only and test cancellation propagation |
| Timeout creates flaky tests | Deterministic controlled providers and generous test coordination; no wall-clock sleeps |
| Secret wrapper implies zeroization Python cannot provide | Promise reference dropping and redaction only; document copy limitations |
| Broad dependency plans leak into the initial package | Import and clean-environment gates; only FastAPI and Pydantic at runtime |
| Four-version Python matrix increases initial work | Build the matrix at scaffold time so incompatibility is found before API implementation |
| Users infer production readiness from package availability | Explicit pre-alpha metadata and repeated README/quickstart limitation statement |

## Known pre-existing problems

No production defects can be identified because there is no implementation. Missing
package, tests, examples, dependency metadata, and CI are direct phase `0.1` scope,
not pre-existing failures exempt from the definition of done.

The repository license was a pre-existing governance gap. It is now resolved by the
root MIT License and matching package metadata.

## Known follow-up candidates

- `0.2`: SQL persistence, repositories, migrations, model extension registry, and
  PostgreSQL/SQLite behavior.
- `0.3`: authenticators, local users/passwords, opaque sessions, CSRF, and rate limits.
- `0.4`: action/resource registry, RBAC, service-account assumption, and list scoping.
- `0.5`: credential metadata/grants, actual resolver integration, environment provider,
  API tokens, and durable audit.
- `0.6`: stable HTTP management surface, public conformance kit, and operational MVP
  evidence.

These candidates are not required for any `0.1` acceptance criterion.

## Definition of done

Phase `0.1` is done when AC-001 through AC-021 are satisfied, all stated compatibility
and invariants are preserved, required automated and manual verification passes,
the repository's new quality gates pass, examples and docs match behavior, and no
critical/high issue attributable to this phase remains.

Failures independently confirmed outside this boundary may be documented and tracked
without expanding the release. Absence of persistence, authentication, RBAC, real
secret management, consumer adapters, or global repository perfection does not make
this bounded contract incomplete.

## READY FOR IMPLEMENTATION
