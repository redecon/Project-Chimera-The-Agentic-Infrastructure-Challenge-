# Acceptance Criteria — Project Chimera

This file contains formal acceptance criteria expressed in Gherkin (Given/When/Then). Each scenario is precise and machine-executable; tests can be generated directly from these scenarios.

Feature: Trend Ingestion
  In order to reliably capture trends
  As an API consumer
  The ingestion endpoint must accept valid JSON payloads and reject invalid ones

  Background:
    Given the ingestion service is running
    And the test database and Redis are reachable

  Scenario: Accept valid trend ingestion payload
    Given a POST /ingest endpoint
    When I submit a JSON payload with:
      | trend_id        | name            | popularity_score | timestamp                 |
      | "trend-123"    | "CoolTopic"    |  42.7            | "2026-02-06T14:22:03Z"  |
    Then the response status SHOULD be 200
    And the response body SHOULD contain an `ingest_id`
    And a Redis stream entry SHOULD be created with `external_id` = "trend-123"
    And a ProvenanceLog entry SHOULD be created referencing the ingest event

  Scenario Outline: Reject invalid ingestion payloads
    Given a POST /ingest endpoint
    When I submit a JSON payload with missing or invalid field
      | field           | value            |
      | trend_id        | <trend_id>       |
      | name            | <name>           |
      | popularity_score| <popularity>     |
      | timestamp       | <timestamp>      |
    Then the response status SHOULD be 400
    And the response body SHOULD include a JSON schema validation error for <field>

    Examples:
      | trend_id | name     | popularity | timestamp         |
      |          | TopicA   | 10.0       | 2026-02-06T00:00Z |
      | trend-1  |          | 10.0       | 2026-02-06T00:00Z |
      | trend-1  | TopicA   | "high"    | 2026-02-06T00:00Z |
      | trend-1  | TopicA   | 10.0       | "not-a-date"     |

Feature: Skills Interfaces
  In order for skills to be composable and testable
  Each skill must accept its schema-defined inputs and return expected outputs or structured errors

  Background:
    Given skill services are registered and reachable in the test harness

  Scenario: skill-download-video success
    Given the `skill-download-video` schema is available
    When I call the skill with input:
      | url                                 | filename        |
      | "https://cdn.test/video.mp4"        | "video.mp4"    |
    Then the skill SHOULD return `success: true`
    And `file_path` SHOULD be present and point to an accessible file
    And `content_type` SHOULD be a valid MIME type starting with "video/"

  Scenario: skill-download-video failure (404)
    Given the remote URL returns 404
    When I call `skill-download-video` with that URL
    Then the skill SHOULD return `success: false`
    And `error` SHOULD describe the HTTP 404 response

  Scenario: skill-transcribe-audio success
    Given an audio asset is available at `audio_file_path`
    When I call `skill-transcribe-audio` with `{ audio_file_path: "/tmp/test.wav", language: "en-US" }`
    Then the skill SHOULD return `success: true`
    And `transcript` SHOULD be a non-empty string
    And `segments` MAY be present with `start_seconds`, `end_seconds`, and `text`

  Scenario: skill-transcribe-audio error (unsupported format)
    Given an audio file in unsupported format
    When I call `skill-transcribe-audio`
    Then the skill SHOULD return `success: false`
    And `error` SHOULD describe the unsupported format

  Scenario: skill-reconcile-ledger success
    Given a list of `transactions` and a `ledger_snapshot` with matching entries
    When I call `skill-reconcile-ledger` with those inputs
    Then the skill SHOULD return `success: true`
    And `summary.matched` SHOULD equal the number of matched pairs
    And `unmatched_transactions` SHOULD be empty

  Scenario: skill-reconcile-ledger tolerance mismatch
    Given a transaction amount slightly off within `tolerance_cents`
    When I call `skill-reconcile-ledger` with `tolerance_cents=50`
    Then the transaction SHOULD match if difference <= 50 cents
    Else it SHOULD appear in `unmatched_transactions`

Feature: OpenClaw Integration
  In order to support agent discovery and monitoring
  Agents must publish well-formed status updates and consumers must reject malformed messages

  Background:
    Given the OpenClaw status topic is available for subscription

  Scenario: Valid status publish
    Given an agent with id `did:chimera:1234abcd`
    When it publishes a status payload containing fields `agent_id`, `status`, `last_ingestion_timestamp`
      And `status` is one of ["available","negotiating","busy","maintenance","offline"]
      And `last_ingestion_timestamp` is a valid ISO8601 timestamp
    Then consumers subscribed to `openclaw/status/did:chimera:1234abcd` SHOULD accept the message
    And the message signature (if present) SHOULD validate against the agent's JWKS

  Scenario: Reject malformed status publish
    Given a status message missing `agent_id` or `status`
    When it is published to the OpenClaw topic
    Then consumers SHOULD reject the message and log a validation error

Feature: Human-in-the-Loop (HITL) behavior
  HITL ensures low-confidence or sensitive outputs are reviewed before publish

  Background:
    Given HITL thresholds: HITL_CONFIDENCE_THRESHOLD=0.6, TOXICITY_ESCALATE_THRESHOLD=0.8

  Scenario: Low-confidence output is escalated
    Given an enrichment worker produces an `EnrichedTrend` with `confidence` = 0.42
    When the worker evaluates HITL rules
    Then an `Escalation` record SHOULD be created with `issue_type = "low_confidence"`
    And an event SHOULD be published to `judge:escalations`
    And attempts to `POST /publish` for that `enriched_trend.id` SHOULD return 409 with `{ "error": "HITL_PENDING", "escalation_id": "<uuid>" }`

  Scenario: Moderator approves escalated item
    Given an open escalation exists for `enriched_trend.id`
    When a moderator calls `POST /escalations/{id}/resolve` with `{ action: "approve", resolved_by: "mod@test" }`
    Then the escalation status SHOULD become `approved`
    And a `hitl:resolution` event SHOULD be emitted
    And subsequent `POST /publish` attempts SHOULD succeed (subject to other checks)

  Scenario: Moderator rejects escalated item
    Given an open escalation exists
    When a moderator resolves with `{ action: "reject", resolved_by: "mod@test" }`
    Then the escalation status SHOULD become `rejected`
    And the enriched content SHOULD be marked `blocked_for_publish`
    And `POST /publish` SHOULD return 403 or a domain-specific error indicating rejection

Feature: Failure Modes & Edge Cases
  The system must handle timeouts, schema errors, and budget overruns in a predictable manner

  Scenario: API downstream timeout during ingest
    Given the database or Redis times out during /ingest processing
    When the ingestion handler attempts to enqueue or persist
    Then the handler SHOULD return 503 Service Unavailable
    And the response SHOULD include a Retry-After header
    And a ProvenanceLog entry SHOULD note `status = "deferred"` and error details

  Scenario: Invalid schema detected during processing
    Given a worker reads a payload that fails internal schema validation during ETL
    When validation fails
    Then the worker SHOULD route the item to DLQ `trend:ingest:dlq` with diagnostic payload
    And an alert SHOULD be emitted to operators

  Scenario: Budget overrun triggers escalation
    Given a single ingestion job exceeds its token/compute budget
    When the job detects budget overrun
    Then it SHOULD pause further processing, create an `Escalation` with `issue_type = "budget_overrun"`, and notify operators
    And the job SHOULD not publish or perform on-chain actions until resolution

  Scenario: Repeated transient failures route to DLQ
    Given a message fails processing 5 times due to transient DB deadlocks
    When retry count exceeds threshold
    Then the message SHOULD be moved to DLQ and an incident opened

# Notes for test runners
- All scenarios require deterministic fixtures and seeded DB state. Use explicit timestamps and fixed random seeds.
- Use mock adapters for external services (Weaviate, embedding models, social APIs) and make them assert on received calls where applicable.
- Use unique test prefixes for created resources to avoid collisions and ensure cleanup after tests.

Generated: 2026-02-06
