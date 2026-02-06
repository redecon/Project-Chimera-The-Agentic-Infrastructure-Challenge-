<!--
Sync Impact Report

- Version change: template → 1.0.0
- Modified principles: (none previously defined in template) → Added: Spec-First Governance; Hierarchical Swarm Architecture; Traceability & Auditability; Polyglot Persistence & Data Separation; Safety & Human-in-the-Loop (HITL) Gatekeeping
- Added sections: Security & Compliance; Development Workflow
- Removed sections: none
- Templates requiring updates: ✅ .specify/templates/plan-template.md
- Templates pending manual review: ⚠ .specify/templates/spec-template.md (ensure FRs reference constitution checks)
- Follow-up TODOs: RATIFICATION_DATE (deferred — requires project ratification date)
-->

# Project Chimera Constitution

## Core Principles

### Spec-First Governance
All implementation work MUST be traceable to a corresponding specification in `/specs/` and MUST NOT be implemented without an approved spec. The repository's `specs/` directory is the single source of truth for feature intent, acceptance criteria, and compliance requirements. Rationale: prevents ad-hoc coding, preserves alignment with Strategic Planner objectives, and enforces the Prime Directive: consult `specs/` before coding.

### Hierarchical Swarm Architecture
All agent design and execution patterns MUST follow the Planner → Worker → Judge hierarchy. Workflows MUST expose explicit task envelopes (task ID, persona reference, tool requirements) and preserve reasoning traces across transitions. Rationale: ensures modular delegation, auditability of decisions, and predictable orchestration between strategic and execution agents.

### Traceability & Auditability
Every state-changing action (asset creation, publication, transaction) MUST include an auditable record: unique identifiers, reasoning trace, model/tool metadata, and cryptographic provenance where applicable. Logs and ledgers MUST be sufficient for end-to-end reconstruction of decisions. Rationale: enables human Super-Orchestrator review, forensics, and regulatory compliance.

### Polyglot Persistence & Data Separation
Storage responsibilities are strictly separated:
- PostgreSQL: authoritative System of Record for financial ledgers, transactional history, and audit logs (ACID guarantees required).
- Vector/NoSQL DB: semantic memory and unstructured content metadata only (no financial or transactional record storage).
- Redis (or equivalent): ephemeral state and task queuing only — never persist long-term financial data here.
Designs that conflate these responsibilities are prohibited unless explicitly justified and approved by governance. Rationale: reduces risk of data leakage, preserves integrity of financial records, and matches the system architecture in `specs/technical.md`.

### Safety & Human-in-the-Loop (HITL) Gatekeeping
All actions that affect external systems of record (on‑chain transactions via Coinbase AgentKit, public posting via Social APIs, or any action with financial/legal exposure) MUST include a Judge evaluation and an explicit HITL approval flag before execution. Automated suggestions MAY be produced, but the Judge (or designated human approver) MUST authorize final commits and publishes. Rationale: prevents unauthorized economic actions and protects brand/legal safety.

## Security & Compliance
Project Chimera enforces data governance and security controls aligned with its principles:
- Financial and ledger data MUST be stored in PostgreSQL with strong access controls and audit logging.
- All content assets MUST include provenance metadata and cryptographic signatures when published.
- Secrets and keys MUST be managed via approved secret stores; private keys for signing/publishing MUST never be checked into source control.
- External integrations that execute transactions or publish content MUST include Judge verification and HITL approval workflows.
- Any deviation from these controls requires a documented risk assessment and explicit sign-off from the Super-Orchestrator.

## Development Workflow
- All work MUST start from a spec in `/specs/` and a corresponding plan created from `.specify/templates/plan-template.md`.
- Tests are mandatory: for each user story, tests (unit/contract/integration) SHOULD be written before implementation and MUST be included in the PR when applicable.
- Commit messages MUST follow Conventional Commits. PRs must reference the related spec and include a Constitution Check section describing how the change complies with this constitution.
- Versioning: follow semantic versioning for governance documents and public APIs; see Governance section for rules on bumping MAJOR/MINOR/PATCH.

## Governance
Amendments and governance rules:
- Amendments to this constitution MUST be proposed via a pull request that includes: (1) a migration/compatibility plan, (2) a testing strategy, and (3) an explicit version bump per the rules below.
- Approval: constitutional amendments require approval from the Super-Orchestrator (or a designated governance group) and a Judge review demonstrating no safety regressions.
- Versioning policy:
	- MAJOR: Backward-incompatible governance or principle removals/redefinitions.
	- MINOR: Addition of a new principle or material expansion of guidance.
	- PATCH: Clarifications, wording fixes, and non-semantic edits.
- Compliance reviews: every PR that changes runtime behavior or external integrations MUST include a Constitution Check and a compliance checklist referencing this document.

**Version**: 1.0.0 | **Ratified**: 2/5/2026  | **Last Amended**: 2026-02-06
