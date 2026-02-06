from src.services.trend_ingest.services.ingest import ingest_event


def test_ingest_event_happy_path():
    raw = {"external_id": "evt-42", "source": "twitter", "text": "I love AI"}

    persister = []

    def write_financial_record(fr):
        # simple in-memory capture
        persister.append(fr)

    result = ingest_event(raw, write_financial_record=write_financial_record)
    assert "enriched_id" in result
    assert "financial_id" in result
    assert result["task_status"] in ("enqueued", "processed-sync")
    assert len(persister) == 1


def test_ingest_event_missing_field():
    raw = {"source": "twitter", "text": "no id"}
    try:
        ingest_event(raw)
        assert False, "ingest_event should have raised ValueError"
    except ValueError:
        pass
