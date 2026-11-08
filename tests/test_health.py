"""
Tests health-check probes and metrics endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client):
    """Verify /api/v1/health returns HTTP 200 and healthy status."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["database_status"] == "CONNECTED"
    assert data["cache_backend"] == "memory"
    assert "timestamp_utc" in data
    assert "X-Response-Time-Ms" in response.headers


@pytest.mark.asyncio
async def test_metrics_endpoint(async_client):
    """Verify /api/v1/metrics returns system scoreboard."""
    response = await async_client.get("/api/v1/metrics")
    assert response.status_code == 200

    data = response.json()
    assert data["system_status"] == "HEALTHY"
    assert "latency_metrics" in data
    assert "accuracy_scoreboard" in data
    assert data["accuracy_scoreboard"]["recall"] >= 0.95
