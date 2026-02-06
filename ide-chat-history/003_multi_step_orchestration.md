# 003 — Multi-Step Orchestration Maturity

Date: 2026-02-06

Overview:
- Moved from single-worker proofs to a Planner → Worker → Judge swarm with HITL escalation.
- Demonstrates a full orchestration example and the mental model for failures and human interventions.

Run narrative (successful orchestration):

1) Planner issues intent: "Detect emerging trend from source X and prepare summary + embed for semantic recall." (planner_intent logged)
2) Ingestion API receives payload and writes to Redis stream `trend:ingest:stream`.
3) Worker A (ETL) claims stream entry, normalizes payload, computes sentiment & topics, writes `EnrichedTrend` in Postgres (id=uuid-aaa), writes `ProvenanceLog`.
4) Worker A enqueues embedding job `trend:embedding:jobs` with `enriched_trend_id=uuid-aaa`.
5) Embedding Worker B consumes job, computes vector, upserts to Weaviate with vector_id=`uuid-aaa`, creates `EmbeddingRecord` and sets `embedding_status = succeeded` in Postgres.
6) Judge evaluates enrichment: if `confidence < 0.6` or `toxicity_score > 0.8`, create `Escalation` and publish to `judge:escalations`; else mark ready.
7) If escalated, HITL Moderator receives notification, reviews `ContentReviewPanel`, resolves via `POST /escalations/{id}/resolve`.
8) On `approve`, `hitl:resolution` event triggers Publisher to resume and call external publish adapter via MCP.

Edge handling during orchestration:
- If Embedding Worker fails (network to Weaviate): retry with backoff; after N attempts, write to `trend:embedding:dlq` and mark `embedding_status = failed`.
- If Judge auto-rejects (policy violation): create incident, block publish, and attach provenance to incident.
- If budget exceeded mid-job: worker pauses, creates `Escalation(issue_type="budget_overrun")`, alerts operators.

Observability & traceability:
- Each step logs `trace_id`, `enriched_trend_id`, `planner_intent`, and `worker_output_prompt`. Logs are correlated in tracing UI.
- ProvenanceLog entries provide a complete chain of the planner's prompts, tool outputs, and judge decisions for audit and later model analysis.

Maturity notes:
- Orchestration now supports parallel workers for enrichment, each idempotent.
- Added consumer-group monitoring and automatic rebalancing to reduce single-point failures.
- HITL flow is integrated end-to-end: moderator decisions are authoritative and emitted back into event streams.

Next evolution:
- Add simulated load tests for the orchestration to exercise backpressure and auto-scaling.
- Include a replay tool to re-run failed items from DLQ with new code.

Reflection:
- The project moved from exploratory specs to robust, testable orchestration with clear escalation and human oversight.
- Emphasis on invariant: never publish without either approved status or explicit audit trace when override used.
