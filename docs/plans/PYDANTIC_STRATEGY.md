# Pydantic Strategy

Pydantic v2 defines public/domain values, requests/responses, settings, principal and
resource references, decisions, provider/config unions, audit metadata, and versioned
JSON Schema. SQLModel/SQLAlchemy persistence models never become public responses.
Explicit public schemas also prevent accidental exposure when a custom column is added.

Use immutable reference/context models and strict security-field validation where
coercion is unsafe. Request models reject unknown/reserved fields; PATCH uses explicit
editable-field schemas. Values supplied by clients are never trusted authentication
merely because a Pydantic model accepted their types. SQL uniqueness, foreign keys,
transactional authorization, and concurrency invariants cannot be proved by model
validators alone.

Provider/credential unions use registered discriminators frozen at startup. Duplicate
names/types and aliases colliding with reserved fields are errors. Use TypeAdapter
for boundary validation and version public schemas independently of ORM layout.
Pydantic models/settings are an intentional public dependency; third-party backend
and pagination implementation objects are not part of the public domain contract.

Use SecretStr/SecretBytes for sensitive inputs where helpful, but masking is not a
guarantee against validation errors, custom serializers, tracing, or explicit unwrap.
Use separate response schemas that omit sensitive fields entirely. Sanitize validation
errors before logging or returning them, dropping input/context that may contain a
password or provider configuration. No generated schema example/default includes
real credentials. Resolved SecretValue is a deliberately non-serializable internal
wrapper, not a normal response model with a masked field.

Use pydantic-settings for configuration, origins, proxy trust, SQL connections, session
limits, and operator-controlled provider aliases. Configuration loads no arbitrary
Python import path from HTTP/tenant metadata. Sensitive settings have redacted reprs.

Test request/response/schema snapshots, reserved-field injection, custom model field
exposure, union collision handling, malformed secret-bearing inputs, and serialization
through error/log/audit paths. Only narrow token-issuance/CSRF responses intentionally
contain newly issued secret values; they are no-store and excluded from logging.
