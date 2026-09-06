# Hedron Integration

## Requirement

AuthMate must feel native in Hedron while Hedron remains optional. AuthMate core never imports Hedron.

Use an optional extra or adapter such as `authmate[hedron]` or `authmate-hedron`.

## Integration behavior

Hedron pages/components consume the same current principal resolved by FastAPI/AuthMate.

Authorization-aware UI can call:

```python
await authmate.can(
    principal,
    "shuetl.schedule.manage",
    ResourceRef("shuetl.schedule", schedule_id),
)
```

to hide or disable controls. The server operation independently enforces the permission.

An optional Hedron admin surface may provide login/profile, users, roles, service accounts, credentials, and audit pages.

When co-located, UI code should call AuthMate services directly rather than make HTTP requests back into the same process.

## Compatibility gate

CI must cover AuthMate standalone, AuthMate + Hedron, AuthMate + ShuETL, and the full Hedron + AuthMate + ShuETL stack. Representative tests must prove UI visibility and API authorization agree.
