# 002 — Debugging Attempts

Date: 2026-02-04

Context:
- After scaffolding ingestion and worker code, observed non-deterministic failures during integration tests.

Log excerpts:

2026-02-04T09:12:03Z - Run: `pytest tests/test_ingest.py`
- Failure: intermittent `503` from ingestion handler when Redis briefly unreachable.
- Action: added retry/backoff for Redis writes and fallbacks: if Redis unavailable, write to local `./tmp/ingest-fallback.json` and alert.

2026-02-04T10:07:21Z - Symptom: schema mismatch causing worker to crash when `topics` arrived as string instead of JSON array.
- Investigation: real-world source occasionally sends `topics: "tag1,tag2"`.
- Fix: normalize step in ETL: if `topics` is string, split on `,` and trim; add robust schema validation and DLQ routing.

2026-02-04T11:54:12Z - Symptom: race condition when embedding worker upserts `EmbeddingRecord` while ETL upsert still in-flight caused FK constraint failure.
- Diagnosis: ETL transaction committed but worker attempted to read before primary key returned. Root cause: non-serial ordering of background tasks.
- Mitigation: change to two-step: commit EnrichedTrend first, then publish embedding job referencing persisted `enriched_trend.id`; embedding worker requires verify existence before embedding.

2026-02-04T13:02:00Z - Observed: flaky test due to time-based assertions (timestamps close to now causing occasional off-by-one failures).
- Fix: switch to fixed test timestamps and seeded clocks in tests.

Lessons learned:
- Add idempotent upsert patterns (INSERT ... ON CONFLICT DO UPDATE) across ETL to handle retries.
- Normalize third-party data aggressively and document expected shapes in `specs/data-model.md`.
- Use DLQ for malformed or repeatedly failing messages and ensure alerts for DLQ entries.

Next steps:
- Harden schema validators and add contract tests for variations of `topics` and `metadata` formats.
- Add consumer-group monitoring for Redis to detect stalled consumers (XPENDING alerting).
