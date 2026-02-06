# Implementation Plan: Trend Ingestion Pipeline

**Branch**: `002-trend-ingestion` | **Date**: 2026-02-06 | **Spec**: `specs/001-trend-ingestion/spec.md`
**Input**: Feature specification from `specs/001-trend-ingestion/spec.md`

## Summary

Implement a backend ingestion pipeline that collects social media trend events, validates and enriches them (sentiment, topics, confidence), persists authoritative records and financial ledger entries to PostgreSQL, stores semantic embeddings in a vector store, and enqueues follow-up tasks in Redis for downstream Workers. All external publishes or economic actions must pass the Judge HITL approval gate.

## Technical Context

**Language/Version**: Python 3.11 (recommended)
**Primary Dependencies**: FastAPI (ingestion API), SQLAlchemy + psycopg2 (PostgreSQL), redis-py (Redis), RQ or Celery (task execution), a lightweight embedding client (vendor-specific; see Research), and an HTTP client for integrations.
**Storage**: PostgreSQL for System of Record (enriched records, financial ledger, audit logs). Vector DB (Weaviate/Pinecone/FAISS-hosted) for semantic memory. Redis for ephemeral task queues and idempotency markers.
**Testing**: pytest for unit tests, contract tests for API payloads, integration tests for end-to-end ingestion → persistence; local test harness for vector DB can use an in-memory alternative during CI.
**Target Platform**: Linux server or container platforms (Docker). Service packaged as a small backend microservice.
**Project Type**: Backend service (single project layout under `src/services/trend_ingest`).
**Performance Goals**: p95 processing latency < 200ms for validation/enrichment under normal loads; end-to-end processing (including embedding + ledger write) within 10s for typical events. Support bursty inputs using queue backpressure.
**Constraints**: Must enforce data separation per constitution; financial records cannot be stored in NoSQL/semantic store. HITL gate must be enforced for publishes.
**Scale/Scope**: Initial scope: handle 100 events/sec sustained with burst capacity; plan for horizontal scaling.

## Constitution Check

Spec-First: PASS — This plan is derived from `specs/001-trend-ingestion/spec.md` which contains user stories and acceptance criteria.

Agent Architecture: PASS — Planner will subscribe to trend summaries; Workers will process enrichment and draft artifacts; Judge will evaluate publishable artifacts and set `hitl_approved` flag. Task envelopes will include `task_id`, `persona_ref`, `enriched_trend_id`, and `reasoning_trace`.

Traceability: PASS — Enriched records and FinancialRecords in PostgreSQL include `task_id`, `reasoning_trace`, `model_metadata` and `audit_created_at`. Provenance recorded in `provenance` table and `generation_log` for assets.

Data Separation: PASS — Transactional & financial data → PostgreSQL. Semantic embeddings → Vector DB. Redis → ephemeral queue only. No financial data will be stored in vector DB or Redis.

HITL / Judge Gate: PASS — Publish/transaction actions remain in `pending` state until Judge returns `approve` and `hitl_approved=true`. The Judge API will be invoked synchronously by the orchestration workflow prior to any external call; an explicit human action is required to flip the flag.

Security & Secrets: PASS (requires infra) — Secrets managed via external secret manager (Vault/Cloud KMS). DB credentials, signing keys, and API tokens will not be checked into source control. Access control enforced via service accounts and RBAC.

Testing & Observability: PASS — Unit tests, contract tests, integration tests required. Observability: structured logs, distributed tracing (OpenTelemetry), and metrics (Prometheus) for ingestion rate, processing latency, failed enrichments, pending embeddings.

## Project Structure

```text
src/services/trend_ingest/
├── api/                  # FastAPI ingestion endpoints
├── services/             # enrichment, embedding, ledger writers
├── models/               # SQLAlchemy models (EnrichedTrend, FinancialRecord, Provenance)
├── tasks/                # background workers (RQ/Celery tasks)
├── db/                   # migrations + schema
└── tests/

docker/
├── Dockerfile
└── compose.yml            # local dev with Postgres, Redis, vector-store emulator
```

**Structure Decision**: Single backend service under `src/services/trend_ingest` to keep ingestion, enrichment, and ledger writes co-located for transactional integrity. Worker tasks are separate modules invoked via Redis queues.

## Complexity Tracking

No constitution violations detected; all gates have affirmative statements. If the team chooses a managed vector DB (e.g., Pinecone), add a short risk note in `research.md` addressing vendor lock-in and privacy.

## Phase 0: Research (Deliverable: research.md)

- Resolve vendor choices for vector DB and embedding models.
- Best-practice patterns for transactional ledger + embedding eventual consistency.
- Recommended enrichment libraries (sentiment, topic classification) and trade-offs.

## Phase 1: Design (Deliverables: data-model.md, contracts/, quickstart.md)

- Data model: SQL schema for EnrichedTrend, FinancialRecord, Provenance.
- API contracts: ingestion endpoint and webhook schema (OpenAPI).
- Quickstart: local dev steps (Docker Compose), env vars, and test payloads.

## Phase 1 Action: Update Agent Context

Run `.specify/scripts/bash/update-agent-context.sh copilot` to add the new technology choices (`FastAPI`, `PostgreSQL`, `Redis`, `VectorDB`) to the agent context files.

## Phase 2: Implementation (high level tasks)

- Implement ingestion API and validation layer.
- Implement enrichment pipeline and embedding writer with retry semantics.
- Implement financial ledger writer with transactional guarantees or compensating reconciliation path.
- Implement Judge integration and HITL workflow for publishes.
- Add tests: unit, contract, integration; CI pipelines.

---

**Next step**: Phase 0 — generate `research.md` and resolve any remaining clarification items (embedding vendor selection and enrichment library).  
