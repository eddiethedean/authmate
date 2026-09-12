# AuthMate Vision

AuthMate prevents FastAPI applications from rebuilding identity, authorization,
service accounts, delegated identity, credential access, and audit from scratch.
Its primary product is a standalone embeddable security package with broadly useful
public contracts, not an identity subsystem specialized for another project.

## Ownership

AuthMate owns principals, authentication, role/scope semantics, generic service-account
assumption, credential metadata/grants, secret-provider abstraction, audit, and
FastAPI/Python enforcement services. Consumers own their resources, business rules,
workflows, execution, presentation, and adapter mappings. They adapt to AuthMate's
contracts; core does not need to know what those consumers do.

Hedron and ShuETL are possible consumers alongside custom APIs, automation, and
background services. Their optional integrations demonstrate composition without
becoming a prerequisite or design authority for AuthMate core.

## Principles

1. Compose into an existing FastAPI app and work through Python outside HTTP.
2. Use exact generic principal/resource values and explicit registered permissions.
3. Separate authentication, authorization, delegation, and credential use.
4. Resolve secrets only after current checks and durable audit; persist references.
5. Keep consumer-domain approval/execution and UI rules with the consumer.
6. Preserve mandatory security checks across every supported extension.
7. Require only application processes plus SQL for baseline correctness.
8. Earn compatibility and production claims through implementation evidence.
