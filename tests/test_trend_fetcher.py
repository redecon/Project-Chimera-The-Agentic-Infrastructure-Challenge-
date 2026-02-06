import pytest
from skills import trend_fetcher



# Assuming trend_fetcher.py will expose a function called fetch_trends
from skills import trend_fetcher

def test_trend_data_structure():
    """
    Test that the trend data returned matches the API contract.
    Expected contract (example from technical.md):
    {
        "trend_id": str,
        "name": str,
        "popularity_score": float,
        "timestamp": str (ISO 8601)
    }
    """
    trends = trend_fetcher.fetch_trends()

    # Assert that we got a list
    assert isinstance(trends, list), "Expected a list of trends"

    # Assert that each trend matches the contract
    for trend in trends:
        assert "trend_id" in trend, "Missing trend_id"
        assert isinstance(trend["trend_id"], str)

        assert "name" in trend, "Missing name"
        assert isinstance(trend["name"], str)

        assert "popularity_score" in trend, "Missing popularity_score"
        assert isinstance(trend["popularity_score"], (int, float))

        assert "timestamp" in trend, "Missing timestamp"
        assert isinstance(trend["timestamp"], str)
