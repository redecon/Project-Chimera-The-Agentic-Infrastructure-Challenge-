# ADR 001 — Data Storage Choice: PostgreSQL + Weaviate + Redis

Date: 2026-02-06
Status: Accepted

## Context
Project Chimera must store structured ingestion records, support high-velocity buffering, and enable semantic search over embeddings for recall and similarity. Requirements include:
- ACID-compliant ledger and auditability for financial records
- High-throughput ingest buffering with at-least-once delivery
- Vector search for semantic recall over enriched text
- Clear traceability and audit trails for provenance and financial integrity

## Decision
Adopt a polyglot persistence approach:
- PostgreSQL as the system-of-record for structured data (EnrichedTrend, FinancialRecord, ProvenanceLog). Use WAL, strong FK constraints, ACID transactions, and read replicas for reporting.
- Redis (Streams and consumer groups) as the high-velocity buffer for ingestion and job queues to enable scalable consumers and bounded latency.
- Weaviate (or compatible vector store) for storing vectors and enabling semantic similarity queries.

## Alternatives Considered
- MongoDB: considered for flexible JSON storage; rejected because it lacks the same transactional guarantees and ledger-quality audit tooling required for financial records.
- MySQL: considered as relational alternative; rejected in favor of Postgres due to richer JSONB, indexing, and extension ecosystem (e.g., pgcrypto, logical replication) and better tooling for migrations and audit patterns.
- Single monolithic DB (e.g., Postgres only): considered, but vector search performance and scaling concerns for embedding stores make a separate vector store preferable.

## Consequences
- Pros:
  - Each system is used for its strengths (transactions & relational integrity, streaming & buffering, semantic vector search).
  - Improved resilience and scale by decoupling components.
- Cons:
  - Operational overhead to manage three systems and ensure consistency (backups, monitoring, migrations across stores).
  - Need for careful orchestration and idempotency patterns to maintain eventual consistency between Postgres and Weaviate.

## Non-Goals
- Avoid making this a single monolithic database design. We do not aim to consolidate all data into one store.

---
References: specs/002-trend-ingestion/data-model.md
