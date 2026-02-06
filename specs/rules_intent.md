# Agent Behavioral Rules — Project Chimera

Purpose

Define high-level behavioral rules for autonomous agents within Project Chimera. These rules ensure safety, spec-first development, traceability of outputs, and human-in-the-loop (HITL) escalation when ambiguity or risk is detected. The file is intentionally prescriptive so an autonomous agent can generate, validate, and enforce a concrete rules file (e.g., `.github/copilot-instructions.md` or `CLAUDE.md`).

## Project Context
Project Chimera runs autonomous influencer agents that create and publish multimodal content and financial artifacts. Agents operate in a Hierarchical Swarm (Planners, Workers/Skills, Judge) and must follow spec-driven, auditable processes. Rules here govern agent behavior across authoring, execution, and external interactions.

## Rule Document Structure (required for each rule)
Each rule MUST be represented with the following keys. This structure allows agents to programmatically generate rule documents and tests.
- `rule_id` (string): short unique id, e.g., `R-001`.
- `title` (string)
- `description` (string)
- `severity` (enum: `warn` | `block` | `audit`)
- `scope` (enum: `authoring` | `runtime` | `publish` | `developer`)
- `enforcement` (enum: `pre-commit` | `ci-gate` | `runtime-check` | `manual-review`)
- `tests` (array of described test cases)
- `notes` (optional)

Example JSON representation:

```json
{
  "rule_id": "R-001",
  "title": "Spec-First Enforcement",
  "description": "Agents must validate the relevant spec in `specs/` before generating or modifying code.",
  "severity": "block",
  "scope": "authoring",
  "enforcement": "pre-commit",
  "tests": [
    "Fail if no spec link provided in change request",
    "Fail if spec contains 'NEEDS CLARIFICATION' placeholders"
  ]
}
```

## Rule Categories

1. Coding Standards
- File conventions: follow repo layout and naming rules: `src/` for runtime, `specs/` for requirements, `skills/` for skills. Files must include a `Spec §` reference comment when implementing feature-specific logic.
- Naming: use `snake_case` for Python files, `kebab-case` for frontend routes, and `PascalCase` for component names.
- Commit hygiene: Conventional Commits required; PRs must reference spec IDs (e.g., `FR-123`), and include a traceability table in PR description.
- Enforcement: CI `lint` job and pre-commit hooks (black/ruff/isort/ESLint).
- Tests: pre-commit will run simple static checks; CI gate enforces full lint suite.

2. Spec-First Enforcement
- Agents MUST check `specs/` for an explicit spec.md/spec section before generating code. If no spec exists or it contains placeholders like `NEEDS CLARIFICATION`, the agent MUST pause and present a clear, minimal set of clarifying questions (see `/speckit.checklist` patterns) and MAY NOT create or modify code files.
- Agents generating code MUST include a `SpecReference` header in the file linking to the exact spec path and section (e.g., `Spec §FR-001`).
- Enforcement: `pre-commit` hooks and `spec-check` CI job that fails on missing spec links or `NEEDS CLARIFICATION` markers.

3. Traceability
- Every generated artifact (code, schema, OpenAPI) MUST include trace metadata: `spec_path`, `spec_id`, `generated_by`, `timestamp`, and `commit_hash` when applicable.
- Provenance: Worker outputs MUST write `ProvenanceLog` entries per data-model rules and include `planner_intent`, `worker_output_prompt`, and `mcp_tool_parameters`.
- Tests: CI verifies a sample of generated files contain trace headers; runtime hooks assert provenance entries exist for each persisted EnrichedTrend.

4. Forbidden Actions
- Absolute prohibitions (`severity=block`):
  - Bypassing HITL or Judge validation for any action that has a `HITL` escalation (no code path may directly publish without either `status=approved` or explicit system-level override with human audit recorded).
  - Exfiltrating secrets: agents must never embed private keys, tokens, or secrets into outputs or logs. Any secret access must use the MCP secret manager via approved connectors.
  - Direct external API calls that circumvent the MCP (Model Context Protocol) integration layer are forbidden; all external service calls must be mediated by MCP adapters to enable audit and policy checks.
  - Automatic on-chain financial actions (coin transfers, signature broadcasts) without Judge approval AND a recorded HITL flag are forbidden.
- Enforcement: Runtime monitors, CI-safety scans, and `block` severity triggers stop pipelines and create an immediate incident.

5. Ambiguity Handling
- If an instruction or spec is ambiguous (missing acceptance criteria, undefined terms, or conflicting FRs), the agent MUST:
  1. Stop generation or execution of the affected change/action.
  2. Create a minimal clarifying question set (max 3) following the `/speckit.checklist` guidelines and attach context: relevant spec excerpts, change diff, and proposed default.
  3. Publish the questions to the human reviewer channel or create a GitHub issue referencing the spec and change.
- Agents MAY apply a conservative default only when explicitly allowed by the spec (e.g., `default: safe`), and such defaults MUST be recorded in `ProvenanceLog`.

6. Escalation Criteria
- Agents MUST escalate to HITL (create an `Escalation` record and publish to `judge:escalations`) in the following cases:
  - Model confidence below threshold: `model_confidence < HITL_CONFIDENCE_THRESHOLD` (configurable; default 0.6).
  - Safety flags: `toxicity_score >= HITL_FLAG_THRESHOLD` (default 0.8) or PII detection.
  - Financial risk: any suggested transaction > `HITL_FINANCIAL_THRESHOLD` (configurable) or discrepancies in ledger reconciliation.
  - Spec ambiguity: `NEEDS CLARIFICATION` or conflicting FRs detected during code-gen or runtime decisions.
  - External policy infringement risk (copyright, defamation) flagged by policy checks.
- Escalation actions:
  - Create `Escalation` record with fields defined in `specs/002-trend-ingestion/spec.md`.
  - Publish event to `judge:escalations` and include `context_url` linking to spec/PR/ProvenanceLog.
  - Mark items as `blocked_for_publish` and return structured error to calling APIs.

## Rule Evolution & Governance
- Versioning: Rules are versioned with `rules_intent.md` metadata: `rules_version`, `effective_date`, `changelog`.
- Change process:
  1. Propose rule change as a PR against `specs/rules_intent.md` or a separate rule file in `specs/rules/` with `rule_id` metadata.
  2. Run automated policy tests in CI (`spec-check`, `policy-lint`, `simulated-safety-tests`).
  3. Require approval by the Judge maintainers and one human reviewer with `security` or `policy` role.
  4. After merge, new rules get an `effective_date` and are enforced by CI and runtime monitors; older deployments must opt-in or be migrated.
- Deprecation: Rules may be deprecated with a two-stage process: `deprecated` flag then removal after a stabilization period (e.g., 30 days).

## Testability
- Each rule MUST include at least one automated test definition describing how to validate enforcement. Tests must be machine-executable and deterministic.
- Test types:
  - Static checks: linting for prohibited patterns, missing spec-links, secret leakage.
  - Runtime checks: simulate agent behavior to ensure escalation triggers, blocking, and provenance writes.
  - Integration tests: CI runs simulated pipelines with feature toggles to ensure the Judge/HITL workflow operates end-to-end.

Example test case (pseudo):
- Rule: Spec-First Enforcement (`R-001`)
  - Setup: Create PR patch that adds a new `src/` file without a `Spec §` header.
  - Expected: `spec-check` CI job fails with message instructing the agent/author to add a spec reference, and the PR cannot be merged.

## Enforcement Mechanisms & Tooling
- CI gates: `spec-check`, `lint`, `security`, `tests`.
- Pre-commit hooks: check for spec references, run linters.
- Runtime monitors: lightweight policy service that scans outputs for forbidden actions and triggers incidents.
- Secret manager: all secrets accessed via MCP connector; secret leakage detection runs in CI and at runtime.

## Delivery Artifacts (what an autonomous agent should produce)
When implementing or updating rules, agents should generate the following artifacts atomically:
- `specs/rules_intent.md` (updated with changelog)
- Per-rule file under `specs/rules/<rule_id>.md` with JSON metadata and human-readable rationale
- Test stubs under `tests/policies/test_<rule_id>.py` or equivalent
- CI workflow updates (if enforcement requires new jobs)

Example per-rule file structure (`specs/rules/R-001.md`):
```
---
rule_id: R-001
title: Spec-First Enforcement
severity: block
enforcement: pre-commit
---
# Spec-First Enforcement
<full description>

Tests:
- tests/policies/test_R-001.py
```

## Safety & Operational Notes
- Rules must be conservative: when in doubt, require human review.
- Never allow silent bypasses of critical rules; any bypass must be explicit, auditable, and time-limited.
- Monitor enforcement metrics and false-positive rates; adjust thresholds via the governance process.

## Metadata & Version
- `rules_version`: 1.0
- `created`: 2026-02-06
- `maintainers`: Project Chimera Governance Team (see `specs/_meta.md`)

---

This `rules_intent.md` is written to be machine-actionable and precise so an autonomous agent can produce complete rule files, tests, and CI config changes without ambiguity.
