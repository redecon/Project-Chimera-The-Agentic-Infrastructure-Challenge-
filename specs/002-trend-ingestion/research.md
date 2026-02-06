# Research: Trend Ingestion Pipeline

**Created**: 2026-02-06
**Feature**: Trend Ingestion Pipeline (002-trend-ingestion)

## Decisions & Rationale

### Vector DB / Embedding Store
Decision: Use Weaviate (self-hosted) or Pinecone (managed) as options; default to Weaviate for initial development (open-source, easy local dev via Docker) and evaluate Pinecone for production if team prefers managed service.

Rationale: Weaviate provides local emulators and schema flexibility. Pinecone reduces operational overhead but adds vendor lock-in and cost.

Alternatives considered: FAISS (local only, requires custom orchestration), Milvus (heavyweight), Pinecone (managed).

### Embedding Model
Decision: Start with OpenAI/embedding-3-small (or open alternative like SentenceTransformers in local dev). Marked as configurable.

Rationale: Managed embeddings provide quality and maintenance; open models reduce cost and dependency.

### Task Queue
Decision: Redis + RQ for lightweight background task processing; Celery optional if distributed scheduling features needed.

Rationale: Redis is already required by constitution for ephemeral state; RQ is simple and fits Python stack.

### Enrichment Libraries
Decision: Use a mix of lightweight NLP (spaCy for tokenization + rule-based topic extraction) and a model-backed sentiment/topic classifier (configurable via service calls to model provider).

Rationale: spaCy gives deterministic behavior and speed; model-based classifiers improve quality.

### Financial Ledger Pattern
Decision: Ledger writes performed in PostgreSQL within a transaction when possible. If embedding write is external and cannot be transactional, persist EnrichedTrend + FinancialRecord first, then attempt embedding and update EmbeddingRecord status. Compensating reconciliation required if embedding fails permanently.

Rationale: Ensures financial accountability; accepts eventual consistency for semantic store.

## Open Questions (NEEDS CLARIFICATION)

- Production embedding vendor selection (Weaviate vs Pinecone vs managed FAISS) — ACTION: ops decision.
- SLA targets for burst capacity and retry windows — ACTION: product/ops to specify.

## Alternatives & Tradeoffs

- Managed embeddings reduce maintenance but increase cost and lock-in.
- Attempting a two-phase commit across SQL + external vector DB is complex; prefer write-ahead ledger + retry/upsert pattern.

## Outcome

- Resolved: vendor options and embedding model approach.
- Outstanding: final production vendor choice and SLA burst targets (deferred to ops). 
