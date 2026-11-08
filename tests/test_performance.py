"""
Performance and Latency SLA validation tests:
- Verification of Sub-100ms end-to-end inference SLA (NFR-PERF-001)
- Throughput and latency distribution percentiles (P50, P95, P99)
"""

import time
import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.api.server import create_app
from backend.database.session import Base, engine


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_sub_100ms_inference_sla(client):
    """
    CRITICAL PROPOSAL SLA REQUIREMENT (NFR-PERF-001):
    End-to-end inference latency must remain strictly below 100 ms at P95.
    """
    now_ms = int(time.time() * 1000)
    latencies = []

    for i in range(25):
        payload = {
            "transaction_id": f"perf-tx-{i}-{now_ms}",
            "timestamp": now_ms,
            "payer_id": f"PAYER_PERF_{i}",
            "merchant_id": "MCH_5411",
            "qr_type": 0,
            "qr_payload": "00020101021126580014bd.bkash.b2b",
            "amount": 250.0,
            "merchant_category_code": 5411,
            "payer_latitude": 23.7808,
            "payer_longitude": 90.4152,
            "merchant_latitude": 23.7812,
            "merchant_longitude": 90.4156,
            "device_trust_score": 0.95,
            "scan_to_pay_latency_ms": 4000,
            "failed_pin_attempts": 0,
        }

        t0 = time.perf_counter()
        response = client.post("/api/v1/predict", json=payload)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed_ms)
        assert response.status_code == 200

    p50 = float(np.percentile(latencies, 50))
    p95 = float(np.percentile(latencies, 95))
    max_latency = float(np.max(latencies))

    print(f"\n[Performance Test] P50: {p50:.2f}ms | P95: {p95:.2f}ms | Max: {max_latency:.2f}ms")
    assert p95 < 100.0, f"P95 latency exceeded 100ms SLA: {p95:.2f}ms"

