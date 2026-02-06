"""Core ingestion flow for trend events.

This module implements a small, testable ingestion function that follows the
plan: validate -> enrich -> create ledger record -> enqueue processing.

Database and queue integrations are represented by callouts to pluggable
functions so the implementation can be wired to SQLAlchemy/Redis later.
"""

from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from ..models import EnrichedTrend, FinancialRecord
from .enrichment import enrich_event
from ..tasks import process_enriched_trend


def _now_iso():
    return datetime.utcnow().isoformat() + "Z"


def ingest_event(raw_event: Dict[str, Any], write_financial_record=None, enqueue_task=None) -> Dict[str, Any]:
    """Process a raw event end-to-end (in-memory).

    Parameters:
    - raw_event: incoming payload expected to contain `external_id`, `source`, `text`, and `timestamp`.
    - write_financial_record: callable(FinancialRecord) -> None; optional DB writer.
    - enqueue_task: callable(task_callable, payload) -> None; optional queue enqueuer.

    Returns a dict with keys: `enriched_id`, `financial_id`, `task_status`.
    """
    # Basic validation
    if not isinstance(raw_event, dict):
        raise TypeError("raw_event must be a dict")
    external_id = raw_event.get("external_id")
    source = raw_event.get("source")
    text = raw_event.get("text")
    if not external_id or not source or not text:
        raise ValueError("missing required fields: external_id, source, text")

    # Enrich
    enriched_payload = enrich_event(raw_event)

    enriched_id = str(uuid4())
    created_at = datetime.utcnow()
    enriched = EnrichedTrend(
        id=enriched_id,
        external_id=external_id,
        source=source,
        text=text,
        sentiment=enriched_payload.get("sentiment"),
        topics=enriched_payload.get("topics", []),
        confidence_score=enriched_payload.get("confidence_score"),
        geo=raw_event.get("geo"),
        enrichment_metadata=enriched_payload.get("enrichment_metadata", {}),
        created_at=created_at,
        embedding_status="pending",
    )

    # Create financial record (estimate cost placeholder)
    financial_id = str(uuid4())
    fin = FinancialRecord(
        id=financial_id,
        enriched_trend_id=enriched_id,
        cost_tokens=0.0,
        currency="USD",
        compute_duration_ms=0,
        timestamp=created_at,
        invoice_reference=None,
    )

    # Persist financial record if caller provided a writer
    if write_financial_record:
        write_financial_record(fin)

    # Enqueue processing task
    task_status = "enqueued"
    if enqueue_task:
        enqueue_task(process_enriched_trend, enriched.__dict__)
    else:
        # Synchronous fallback for scaffold/testing
        process_enriched_trend(enriched.__dict__)
        task_status = "processed-sync"

    return {"enriched_id": enriched_id, "financial_id": financial_id, "task_status": task_status}


__all__ = ["ingest_event"]
