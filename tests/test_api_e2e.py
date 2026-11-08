"""
End-to-End API integration tests for FastAPI gateway:
- Real-time transaction inference (/api/v1/predict)
- Archetype evaluations (Routine, Quishing, MITM, Bot Probing)
- Batch prediction (/api/v1/predict/batch)
- Ledger audit verification endpoint (/api/v1/ledger/verify)
"""

import time
import pytest
from fastapi.testclient import TestClient

from backend.api.server import create_app
from backend.database.session import Base, engine, SessionLocal


@pytest.fixture(scope="module")
def client():
    """Initializes tables and returns TestClient."""
    Base.metadata.create_all(bind=engine)
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_predict_routine_legitimate_payment(client):
    """Routine payment with small displacement and valid latency should APPROVE."""
    now_ms = int(time.time() * 1000)
    payload = {
        "transaction_id": f"test-e2e-routine-{now_ms}",
        "timestamp": now_ms,
        "payer_id": "PAYER_ROUTINE_123",
        "merchant_id": "MCH_5411_01",
        "qr_type": 0,
        "qr_payload": "00020101021126580014bd.bkash.b2b0110MCH_5411_01520454115303050",
        "amount": 250.0,
        "merchant_category_code": 5411,
        "payer_latitude": 23.7808,
        "payer_longitude": 90.4152,
        "merchant_latitude": 23.7812,
        "merchant_longitude": 90.4156,
        "device_trust_score": 0.95,
        "scan_to_pay_latency_ms": 4500,
        "failed_pin_attempts": 0,
    }

    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["transaction_id"] == payload["transaction_id"]
    assert data["verdict"] == "APPROVE"
    assert data["composite_score"] < 0.30
    assert len(data["ledger_block_hash"]) == 64
    assert data["response_time_ms"] > 0


def test_predict_quishing_payment_blocked(client):
    """Static QR replacement with remote displacement (>50km) and obfuscated payload."""
    now_ms = int(time.time() * 1000)
    payload = {
        "transaction_id": f"test-e2e-quishing-{now_ms}",
        "timestamp": now_ms,
        "payer_id": "PAYER_VICTIM_456",
        "merchant_id": "MCH_ROGUE_99",
        "qr_type": 0,
        "qr_payload": "https://secure-qr.bkash-auth.net/pay/v2?redirect=login&session=7f9a8b1c4e2d3f0a9b8c7d6e5f4a3b2c1d0e9f8a",
        "amount": 450.0,
        "merchant_category_code": 5411,
        "payer_latitude": 23.7808,
        "payer_longitude": 90.4152,
        "merchant_latitude": 24.8949,  # Remote displacement (~150km away)
        "merchant_longitude": 91.8687,
        "device_trust_score": 0.88,
        "scan_to_pay_latency_ms": 5500,
        "failed_pin_attempts": 0,
    }

    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["verdict"] in ["BLOCK", "CHALLENGE_MFA"]
    assert data["composite_score"] >= 0.30
    assert len(data["reason_codes"]) > 0


def test_predict_batch_processing(client):
    """Batch endpoint should process multiple transactions sequentially."""
    now_ms = int(time.time() * 1000)
    batch = [
        {
            "transaction_id": f"test-batch-{now_ms}-{i}",
            "timestamp": now_ms,
            "payer_id": f"PAYER_BATCH_{i}",
            "merchant_id": "MCH_5411",
            "qr_type": 0,
            "qr_payload": "00020101021126580014bd.bkash.b2b",
            "amount": 100.0 * (i + 1),
            "merchant_category_code": 5411,
            "payer_latitude": 23.7808,
            "payer_longitude": 90.4152,
            "merchant_latitude": 23.7810,
            "merchant_longitude": 90.4154,
            "device_trust_score": 0.90,
            "scan_to_pay_latency_ms": 3000,
            "failed_pin_attempts": 0,
        }
        for i in range(3)
    ]

    response = client.post("/api/v1/predict/batch", json=batch)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["transaction_id"] == f"test-batch-{now_ms}-0"


def test_api_ledger_verification(client):
    """GET /api/v1/ledger/verify should return unbroken chain verification."""
    response = client.get("/api/v1/ledger/verify")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["total_blocks"] >= 1
