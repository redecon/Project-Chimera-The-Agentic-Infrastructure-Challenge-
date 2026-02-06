# Project Chimera  Autonomous Influencer Network

## Project Overview & Mission
Project Chimera is an Autonomous Influencer Network that composes agentic workflows to create, validate, and publish multimodal content and on-chain proofs of outcome. Chimera coordinates a Hierarchical Swarm of planners, workers (skills), and a Judge agent to maintain brand safety, traceability, and human-in-the-loop (HITL) oversight.

## Role & Context
This repository is part of the FDE Trainee Challenge: a hands-on exercise in designing spec-driven, auditable agentic systems. Use this workspace to experiment with feature specs, skills, and the integration surfaces required for safe autonomous publication and financial reconciliation.

## Business Objective & Core Philosophies
- Spec-Driven Development: All implementation must be traceable to `specs/` artifacts. Never implement features without first updating the spec.
- Traceability: Requirements, API contracts, and data models must be cross-linked and reviewable by auditors and reviewers.
- Skills vs Tools: Small, composable `skills/` encapsulate single-purpose actions (download, transcribe, reconcile). Skills are decoupled from orchestration logic in `src/services`.
- Git Hygiene: Use feature branches, atomic commits with Conventional Commit messages, and document design decisions in `specs/`.

## Repository Structure
- `specs/` — Feature specs, plans, contracts, and checklists (source of truth).
- `src/` — Application code and microservices (ingest pipeline, services, tasks).
- `skills/` — Small, versionable skill modules with `schema.json` and `SKILL.md` for traceability.
- `tests/` — Unit and integration tests.
- `research/`, `docs/` — Architecture notes, research, and strategy artifacts.
- `Makefile`, `pyproject.toml` — Build, test, and lint orchestration.

## Getting Started
Prerequisites: Python 3.10+ (see `pyproject.toml`), Docker optional for services.

Quick commands (run from repo root):

```bash
# create virtualenv and install deps
make setup

# run tests
make test

# run linters / formatters
make lint

# run security checks (safety, bandit, etc.)
make security
```

If `make` targets are missing on your platform, inspect `Makefile` for equivalent commands or use `python -m pip install -r requirements.txt` then `pytest`.

## Governance Pipeline
All changes intended for mainline must flow through the governance pipeline:

1. Update or create spec(s) in `specs/` describing Feature, FR/SC, and traceability links.
2. Open a feature branch named `###-feature-name` and reference spec IDs in your PR.
3. CI gates run the following checks:
   - `spec-check` (validate presence and basic format of `specs/` artifacts)
   - `lint` (code style and static analysis)
   - `security` (SAST/dependency checks such as Bandit/safety)
   - `tests` (unit & integration tests)
4. Reviewers verify traceability: every FR/SC must point to API/data-model artifacts (OpenAPI, `data-model.md`) and skills used.
5. After approval, merge and tag. Post-merge: optionally run on-chain attestation steps if the feature publishes proofs.

## Links & Traceability
- Feature specs: `specs/` (start here for requirements)
- API contracts: `specs/**/contracts/*.yaml`
- Data models: `specs/**/data-model.md`
- Skills: `skills/*/schema.json` and `skills/*/SKILL.md`
 - Architectural Decisions (ADRs): `docs/adr/adr-001-db-choice.md`, `docs/adr/adr-002-orchestration-pattern.md`, `docs/adr/adr-003-security-strategy.md`

## Contact
For questions about governance, reach out to the project owner or the Judge Agent maintainers listed in `specs/_meta.md`.

---
Generated/updated by automation to provide a clear onboarding and governance summary. Ensure `specs/` remains the source of truth.
