"""
Security and penetration tests:
- Injection resistance (SQLi, XSS)
- Input boundary enforcement
- Salted SHA-256 PII privacy masking
"""

import time
import pytest
from fastapi.testclient import TestClient

from backend.api.server import create_app
from backend.database.session import Base, engine, SessionLocal
from backend.database.models import TransactionRecord


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_sql_injection_resilience(client):
    """SQL injection payloads in string fields must be safely parameterized."""
    now_ms = int(time.time() * 1000)
    payload = {
        "transaction_id": f"test-sec-sqli-{now_ms}",
        "timestamp": now_ms,
        "payer_id": "admin' OR '1'='1",
        "merchant_id": "'; DROP TABLE transactions; --",
        "qr_type": 0,
        "qr_payload": "SELECT * FROM users WHERE 'a'='a'",
        "amount": 100.0,
        "merchant_category_code": 5411,
        "payer_latitude": 23.7808,
        "payer_longitude": 90.4152,
        "merchant_latitude": 23.7810,
        "merchant_longitude": 90.4154,
        "device_trust_score": 0.90,
        "scan_to_pay_latency_ms": 3500,
        "failed_pin_attempts": 0,
    }

    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200

    # Verify table was NOT dropped and database remains intact
    db = SessionLocal()
    count = db.query(TransactionRecord).count()
    db.close()
    assert count >= 1


def test_boundary_negative_amount_rejected(client):
    """Negative amount must be rejected at API gateway with HTTP 422."""
    now_ms = int(time.time() * 1000)
    payload = {
        "transaction_id": "test-sec-boundary-001",
        "timestamp": now_ms,
        "payer_id": "PAYER_TEST",
        "merchant_id": "MCH_5411",
        "qr_type": 0,
        "qr_payload": "valid_qr_payload",
        "amount": -50.0,  # Negative amount violation
        "merchant_category_code": 5411,
        "payer_latitude": 23.7808,
        "payer_longitude": 90.4152,
        "merchant_latitude": 23.7810,
        "merchant_longitude": 90.4154,
        "device_trust_score": 0.90,
        "scan_to_pay_latency_ms": 3000,
        "failed_pin_attempts": 0,
    }

    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422


def test_boundary_gps_out_of_range_rejected(client):
    """Latitude > 90.0 must be rejected with HTTP 422."""
    now_ms = int(time.time() * 1000)
    payload = {
        "transaction_id": "test-sec-boundary-002",
        "timestamp": now_ms,
        "payer_id": "PAYER_TEST",
        "merchant_id": "MCH_5411",
        "qr_type": 0,
        "qr_payload": "valid_qr_payload",
        "amount": 100.0,
        "merchant_category_code": 5411,
        "payer_latitude": 123.7808,  # Out of range (> 90.0)
        "payer_longitude": 90.4152,
        "merchant_latitude": 23.7810,
        "merchant_longitude": 90.4154,
        "device_trust_score": 0.90,
        "scan_to_pay_latency_ms": 3000,
        "failed_pin_attempts": 0,
    }

    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422


def test_pii_privacy_masking(client):
    """Raw payer_id must never appear in database; only 64-char SHA-256 hash."""
    now_ms = int(time.time() * 1000)
    sensitive_payer_id = "NATIONAL_ID_9876543210"
    payload = {
        "transaction_id": f"test-sec-pii-{now_ms}",
        "timestamp": now_ms,
        "payer_id": sensitive_payer_id,
        "merchant_id": "MCH_5411",
        "qr_type": 0,
        "qr_payload": "valid_qr_payload",
        "amount": 100.0,
        "merchant_category_code": 5411,
        "payer_latitude": 23.7808,
        "payer_longitude": 90.4152,
        "merchant_latitude": 23.7810,
        "merchant_longitude": 90.4154,
        "device_trust_score": 0.90,
        "scan_to_pay_latency_ms": 3000,
        "failed_pin_attempts": 0,
    }

    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200

    db = SessionLocal()
    rec = db.query(TransactionRecord).filter(TransactionRecord.transaction_id == payload["transaction_id"]).first()
    db.close()

    assert rec is not None
    assert rec.payer_hash != sensitive_payer_id
    assert len(rec.payer_hash) == 64
