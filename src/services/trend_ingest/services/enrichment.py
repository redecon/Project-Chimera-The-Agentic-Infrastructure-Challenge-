"""Enrichment utilities for trend ingestion.

This module provides pure-Python enrichment stubs suitable for local testing.
Real model-backed enrichment can be swapped in later.
"""

from typing import Dict, Any


def enrich_event(raw_event: Dict[str, Any]) -> Dict[str, Any]:
    """Return an enriched event dict with basic computed fields.

    This is intentionally lightweight and deterministic for testing.
    """
    text = raw_event.get("text", "")
    # Naive sentiment: positive if contains 'good' or 'great', negative if 'bad'
    sentiment = 0.0
    if any(tok in text.lower() for tok in ("good", "great", "love", "awesome")):
        sentiment = 0.8
    elif any(tok in text.lower() for tok in ("bad", "hate", "terrible")):
        sentiment = -0.6

    topics = []
    if "ai" in text.lower() or "artificial intelligence" in text.lower():
        topics.append("ai")

    enriched = {
        "external_id": raw_event.get("external_id"),
        "source": raw_event.get("source"),
        "text": text,
        "sentiment": sentiment,
        "topics": topics,
        "confidence_score": 0.9,
        "enrichment_metadata": {"enr_version": "0.1"},
    }
    return enriched
