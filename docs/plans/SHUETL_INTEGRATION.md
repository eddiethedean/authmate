# ShuETL Consumer Integration Notes

## Direction of dependency

AuthMate defines general identity, authorization, delegation, and credential
contracts. ShuETL or a separately maintained consumer adapter implements those
contracts. AuthMate core does not import ShuETL/ETLantic, model their operations,
query their records, require callbacks into them, or wait for their release cycle.
[Consumer Contracts](CONSUMER_CONTRACTS.md) is the normative AuthMate surface;
this document is optional guidance for the consumer, not a core requirement.

## Current consumer observation

The sibling ShuETL checkout inspected on 2026-09-12 (`f5806be`) uses ETLantic's
`Authorizer` and `etlantic_fastapi.auth.ContextFactory` / `PrincipalDependency`
in `src/shuetl/providers.py`; its identity plan says ETLantic owns canonical
control-plane and execution records. Its pyproject pins ETLantic packages to
`0.51.0`. This explains why the old AuthMate plan's ShuETL-owned pipeline/run model
was misplaced. It does not constrain AuthMate's public contracts or certify any
released integration.

The ShuETL-side adapter is responsible for translating authenticated AuthMate
principals and decisions into its chosen upstream interfaces. It owns an explicit,
versioned action/resource mapping and preserves consumer denial semantics. AuthMate
accepts generic registered actions and ResourceRefs and need not know their origin.

## Responsibilities that stay with the consumer

ShuETL/ETLantic must decide who may create/edit/trigger work, which execution account
an approved workload can select, how immutable versions and input constraints bind
that approval, how queued work is revalidated, and how schedules are revoked.
A user with run permission must not be able to substitute an arbitrary account,
credential, connector, or destination. These checks belong at the consumer's own
submission/execution boundary, not in AuthMate workload tables or callbacks.

At execution the consumer supplies a verified AccessContext. For example, a dedicated
executor principal may have `authmate.service_account.assume` on selected accounts;
AuthMate checks that assumption and the effective account's exact credential grant.
The consumer must restrict each job's account and credentials further according to
its own approval records. AuthMate's assumption permission alone does not prove a
job is approved. A triggering human can be separate audit context; the consumer
owns whether later changes to that human's authority cancel queued/scheduled work.

The consumer owns job transport authentication, trusted record loading, cancellation,
external I/O, and redaction of its definitions/reports. It never stores resolved
secrets or silently substitutes global credentials. AuthMate rechecks current
identity/grant state at each resolution and documents that revocation cannot retract
plaintext already released.

## Consumer-owned compatibility testing

ShuETL or its adapter package should pin AuthMate and upstream versions and test
identity mapping, denial propagation, account/credential substitution, stale queued
work, schedule policy, secret redaction, and actor/effective-principal audit fields.
AuthMate provides a provider-neutral conformance kit and standalone examples. It
publishes no ShuETL compatibility claim until an adapter demonstrates it, but core
AuthMate releases are never gated on ShuETL or ETLantic implementation changes.
