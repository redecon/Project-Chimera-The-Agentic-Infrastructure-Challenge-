# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]  
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]

## Constitution Compliance
All functional requirements defined in this specification MUST include a Constitution Check section referencing `constitution.md`. 
This ensures traceability to governance principles and alignment with security, workflow, and HITL rules.

## Technical Specification & Traceability

This section links the canonical technical artifacts that implement and constrain the functional requirements above. Reviewers MUST use these links to validate that API contracts and the data model align with the feature's FR and SC identifiers.

- **API Contract**: The ingestion API schema and request/response contracts are defined in the OpenAPI file: [specs/002-trend-ingestion/contracts/ingestion-openapi.yaml](specs/002-trend-ingestion/contracts/ingestion-openapi.yaml). Map each API endpoint and required field to related FR IDs (e.g., `FR-XXX -> POST /ingest`), and ensure validation/error formats are specified.
- **Data Model / ERD**: The persistence schema and entity relationships are documented in: [specs/002-trend-ingestion/data-model.md](specs/002-trend-ingestion/data-model.md). Ensure each persisted field is traceable to an FR or SC (for example, `last_ingestion_timestamp` → SC-001 / FR-00X).

Traceability checklist for reviewers:

- For each Functional Requirement (`FR-###`), confirm a corresponding API field and/or persisted data field is identified and linked.
- For each Success Criterion (`SC-###`), confirm measurable artifacts (example payloads, retention rules, error formats) are present in either the API contract or data model.
- Note any mismatches or unlinked requirements as traceability gaps and tag them in the PR for resolution.
 - Note any mismatches or unlinked requirements as traceability gaps and tag them in the PR for resolution.

## Human-in-the-Loop Placement & Test Strategies

### HITL Placement (where moderators intervene)

This feature must include explicit, auditable HITL gates that prevent low-confidence or sensitive content from being published without review. Placement points and behaviors:

- Ingestion validation (POST /ingest): the API accepts raw payloads and enqueues them for processing. No publishing decisions are made here, but the API MUST record `received_at` and create a provenance entry for traceability.
- Post-enrichment evaluation (after ETL worker normalizes and enriches): the enrichment worker computes confidence metrics (sentiment confidence, toxicity score, model confidence). If any configured `HITL_CONDITION` is met (e.g., `confidence < HITL_CONFIDENCE_THRESHOLD` OR `toxicity_score > HITL_FLAG_THRESHOLD` OR `contains_sensitive_entity == true`), the worker MUST create an `Escalation` record and emit an escalation message to the Judge/HITL queue rather than marking the item as `ready_for_publish`.
- Pre-publish check (publish / reply endpoints): any endpoint that transitions content to external systems (e.g., publishing to a social API, creating a reply) MUST check the `Escalation` table for unresolved escalations referencing the `enriched_trend.id` and refuse the action with a `409 Conflict` and a structured error explaining the pending HITL review.
- Manual moderator actions: moderators (via internal UI or webhook endpoints) MUST be able to `approve`, `reject`, or `request_changes` on escalations. The resolution action MUST record `resolved_by`, `resolved_at`, `resolution_reason`, and any `judge_validation_score`.

Required Escalation record fields (DB schema guidance):

- `id` (uuid PK)
- `enriched_trend_id` (uuid FK)
- `issue_type` (enum: `low_confidence`, `sensitive_content`, `financial_discrepancy`, `policy_violation`, `other`)
- `reason` (text)
- `metrics` (jsonb) — raw scores that triggered the escalation (confidence, toxicity, model_id, etc.)
- `status` (enum: `open`, `in_review`, `approved`, `rejected`)
- `created_at`, `escalated_to` (string, optional), `resolved_at`, `resolved_by`, `resolution_reason`

Routing & queues:

- Escalations are published to `judge:escalations` (Redis stream or pub/sub topic). The Judge Agent consumes `judge:escalations`, applies automated checks, and may auto-close low-risk items or forward to human moderators via `hitl:notifications` (webhook or notification service).
- Moderator responses are posted to `judge:responses` or via a secure `POST /escalations/{id}/resolve` API which the backend validates and applies to the `Escalation` record.

### Linkage to API endpoints

- `POST /ingest` (specs/002-trend-ingestion/contracts/ingestion-openapi.yaml) — writes to Redis and creates provenance; returns 200 Accepted with an internal `ingest_id`.
- `POST /publish` or `POST /reply` (if present in service) — before performing external publish, the service MUST query the `Escalation` table for any unresolved escalations for the target `enriched_trend_id`. If any `status IN ('open','in_review')` exist, return `409 Conflict` with payload `{ "error": "HITL_PENDING", "escalation_id": "<uuid>" }`.
- `POST /escalations/{id}/resolve` — accepts moderator action: `{ action: "approve" | "reject" | "request_changes", resolved_by: <user>, notes: <text>, judge_validation_score?: number }`. On `approve`, the backend updates `status=approved` and emits a `hitl:resolution` event consumed by downstream publishers.

### Test Strategies (by endpoint)

All tests must be automatable and deterministic. Use fixtures, seeded DB states, and mock queues.

1) Contract validation tests (for every API endpoint)
   - Purpose: ensure API adheres to JSON schema/OpenAPI contract.
   - Implementation:
     - Use the OpenAPI contract in `specs/002-trend-ingestion/contracts/ingestion-openapi.yaml` and a schema validator (e.g., `jsonschema` in Python or `ajv` in Node) to run positive and negative cases.
     - Positive case: valid payload (required fields present) → assert `200 Accepted` and `ingest_id` returned.
     - Negative case: missing `external_id` or malformed `timestamp` → assert `400` and schema validation error structure.

2) HITL escalation tests
   - Purpose: verify that low-confidence or sensitive content is flagged and routed to Judge/HITL; publishing is blocked until resolution.
   - Implementation:
     - Seed a test `EnrichedTrend` or simulate enrichment step returning `{ confidence: 0.42, toxicity: 0.01 }` with `HITL_CONFIDENCE_THRESHOLD=0.6`.
     - Run the worker logic (unit test or integration test) — assert that an `Escalation` record is created with `issue_type='low_confidence'`, `metrics` contains the confidence value, and an event is published to `judge:escalations`.
     - Attempt `POST /publish` for that `enriched_trend.id` — assert `409 Conflict` and response includes `escalation_id`.
     - Simulate moderator approval by calling `POST /escalations/{id}/resolve` with `{ action: 'approve', resolved_by: 'moderator@test' }` — assert escalation status becomes `approved` and a follow-up event `hitl:resolution` is emitted; subsequent `POST /publish` should succeed.

3) Failure mode tests
   - Purpose: verify resilience when dependencies fail (DB, Redis, embedding service) and that escalations and errors are handled safely.
   - Implementation:
     - API timeout: mock the downstream DB or queue to timeout; assert API returns `503 Service Unavailable` or enqueues message for retry (depending on policy) and logs a provenance entry with `status='deferred'`.
     - Invalid payload: ensure `400` with schema error is returned, no enqueue to Redis, and provenance records the rejection.
     - Redis down: emulate Redis connection failure during `POST /ingest` — assert API returns `503` and writes a local fallback (e.g., write to disk or raise alert), and an operator-visible error is generated.

Endpoint coverage matrix (minimum required tests):

- `POST /ingest`: contract-positive, contract-negative, Redis-down fallback, provenance recorded.
- `ETL worker`: idempotent upsert, escalation creation on low-confidence, DLQ routing on repeated failures.
- `POST /publish` / `POST /reply`: block on open escalations, accept after approval, security/auth checks.
- `POST /escalations/{id}/resolve`: validation of moderator identity, audit log creation, and downstream event emission.

### Test harness & automation guidance

- Provide fixtures for: test `EnrichedTrend` rows, mock Redis streams, a fake Judge consumer that records messages, and a test database schema created via Alembic's `--sql` dry-run then applied to a test DB.
- Environment variables to control behavior in tests:
  - `HITL_CONFIDENCE_THRESHOLD` (default 0.6)
  - `HITL_FLAG_THRESHOLD` (toxicity, default 0.8)
  - `ESCALATION_QUEUE` (topic name)

- Example unit test pseudocode (pytest-style):

```python
def test_low_confidence_escalates(db, redis_client, worker):
    # arrange
    enriched = seed_enriched_trend(db, confidence=0.42)
    # act: run worker's evaluation step
    worker.evaluate_and_maybe_escalate(enriched.id)
    # assert escalation created
    esc = db.query(Escalation).filter_by(enriched_trend_id=enriched.id).one()
    assert esc.issue_type == 'low_confidence'
    assert 'confidence' in esc.metrics
    # assert event published to judge queue
    assert redis_client.stream_contains('judge:escalations', esc.id)

    # attempt publish should be blocked
    resp = test_client.post('/publish', json={'enriched_trend_id': enriched.id})
    assert resp.status_code == 409
```

### Auditability & traceability rules

- All moderator actions and judge decisions MUST be recorded in `ProvenanceLog` with `planner_intent`, `worker_output_prompt`, `mcp_tool_parameters`, and an added `hitl_action` object for moderator events.
- Tests must assert that provenance entries exist for each escalation lifecycle transition (created, in_review, resolved).

---

Update status: set TODO `Add implementation stubs and tests` in the feature plan when ready.

