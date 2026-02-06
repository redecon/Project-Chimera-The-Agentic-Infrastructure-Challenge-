# Quickstart: Trend Ingestion Pipeline (local dev)

Prerequisites:
- Docker & Docker Compose
- Python 3.11

1. Start local dev stack (Postgres, Redis, Weaviate emulator):

```bash
docker-compose -f docker/compose.yml up -d
```

2. Create virtualenv and install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Apply migrations and start service:

```bash
alembic upgrade head
uvicorn src.services.trend_ingest.api.main:app --reload
```

4. Test ingestion endpoint with sample payload:

```bash
curl -X POST http://localhost:8000/ingest -H 'Content-Type: application/json' -d '{"external_id":"evt-123","source":"twitter","text":"AI is trending","timestamp":"2026-02-06T12:00:00Z"}'
```

5. Verify:
- EnrichedTrend row in Postgres
- FinancialRecord in Postgres
- EmbeddingRecord status pending/succeeded
- Task enqueued in Redis

