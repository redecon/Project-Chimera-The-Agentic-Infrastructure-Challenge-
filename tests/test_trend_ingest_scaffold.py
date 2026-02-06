"""Sanity tests for trend_ingest scaffold.

These tests avoid external dependencies by invoking the factory which defers
importing FastAPI until runtime.
"""

from src.services.trend_ingest.api.main import create_app


def test_create_app_returns_object():
    app = create_app()
    assert app is not None


def test_enrich_event_basic():
    from src.services.trend_ingest.services.enrichment import enrich_event

    raw = {"external_id": "evt-1", "source": "twitter", "text": "AI is awesome"}
    enriched = enrich_event(raw)
    assert enriched["external_id"] == "evt-1"
    assert "ai" in enriched.get("topics", [])
