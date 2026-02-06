"""Data model placeholders for trend ingestion.

These use simple dataclasses to avoid heavy ORMs at scaffold time. SQLAlchemy
models can be added later in `src/services/trend_ingest/models_sqlalchemy.py`.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class EnrichedTrend:
    id: str
    external_id: str
    source: str
    text: str
    sentiment: Optional[float]
    topics: List[str]
    confidence_score: Optional[float]
    geo: Optional[Dict[str, Any]]
    enrichment_metadata: Dict[str, Any]
    created_at: datetime
    embedding_status: str = "pending"


@dataclass
class FinancialRecord:
    id: str
    enriched_trend_id: str
    cost_tokens: float
    currency: str
    compute_duration_ms: int
    timestamp: datetime
    invoice_reference: Optional[str] = None


@dataclass
class EmbeddingRecord:
    id: str
    enriched_trend_id: str
    vector_id: Optional[str]
    embedding_status: str
    created_at: datetime
