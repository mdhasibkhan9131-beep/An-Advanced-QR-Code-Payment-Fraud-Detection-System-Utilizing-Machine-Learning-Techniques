"""
Tests schema validation, error handling, and baseline predict endpoint.
"""

import pytest


@pytest.mark.asyncio
async def test_predict_valid_payload(async_client):
    """Verify valid payload receives HTTP 200 and structured response."""
    payload = {
        "transaction_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": 1731102000000,
        "payer_id": "ACC_PAYER_884920",
        "merchant_id": "MERCH_POS_104829",
        "qr_type": 1,
        "qr_payload": "https://secure.paygate.com/qr?m=MERCH_POS_104829",
        "amount": 145.50,
        "merchant_category_code": 5411,
        "payer_latitude": 23.8103,
        "payer_longitude": 90.4125,
        "merchant_latitude": 23.8110,
        "merchant_longitude": 90.4132,
        "device_trust_score": 0.95,
        "scan_to_pay_latency_ms": 3200,
        "failed_pin_attempts": 0
    }
    response = await async_client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["transaction_id"] == payload["transaction_id"]
    assert data["verdict"] in ["APPROVE", "CHALLENGE_MFA", "BLOCK"]
    assert 0.0 <= data["composite_score"] <= 1.0
    assert "response_time_ms" in data
    assert "X-Response-Time-Ms" in response.headers


@pytest.mark.asyncio
async def test_predict_negative_amount_rejection(async_client):
    """Verify negative monetary amount returns HTTP 422 with diagnostic error."""
    payload = {
        "transaction_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": 1731102000000,
        "payer_id": "ACC_PAYER_884920",
        "merchant_id": "MERCH_POS_104829",
        "qr_type": 1,
        "qr_payload": "https://secure.paygate.com/qr?m=104829",
        "amount": -50.00,  # Invalid negative
        "merchant_category_code": 5411,
        "payer_latitude": 23.8103,
        "payer_longitude": 90.4125,
        "merchant_latitude": 23.8110,
        "merchant_longitude": 90.4132,
        "device_trust_score": 0.95,
        "scan_to_pay_latency_ms": 3200,
        "failed_pin_attempts": 0
    }
    response = await async_client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422

    data = response.json()
    assert data["error_code"] == "UNPROCESSABLE_ENTITY"
    assert any("amount" in str(d["field"]) for d in data["details"])


@pytest.mark.asyncio
async def test_predict_invalid_latitude_rejection(async_client):
    """Verify out-of-bound latitude returns HTTP 422."""
    payload = {
        "transaction_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": 1731102000000,
        "payer_id": "ACC_PAYER_884920",
        "merchant_id": "MERCH_POS_104829",
        "qr_type": 1,
        "qr_payload": "https://secure.paygate.com/qr?m=104829",
        "amount": 100.00,
        "merchant_category_code": 5411,
        "payer_latitude": 195.4,  # Invalid latitude > 90
        "payer_longitude": 90.4125,
        "merchant_latitude": 23.8110,
        "merchant_longitude": 90.4132,
        "device_trust_score": 0.95,
        "scan_to_pay_latency_ms": 3200,
        "failed_pin_attempts": 0
    }
    response = await async_client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422

    data = response.json()
    assert data["error_code"] == "UNPROCESSABLE_ENTITY"
    assert any("payer_latitude" in str(d["field"]) for d in data["details"])

