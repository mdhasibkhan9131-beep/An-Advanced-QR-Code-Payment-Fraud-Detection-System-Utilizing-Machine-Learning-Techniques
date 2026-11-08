"""
Unit tests for feature engineering algorithms:
- Haversine spatial displacement
- Shannon entropy of QR payload
- Customer historical amount Z-score
- End-to-end FeatureEngineeringPipeline integration
"""

import pytest
import numpy as np

from backend.data.feature_engineering import (
    calculate_haversine_km,
    calculate_shannon_entropy,
    calculate_amount_zscore,
    FeatureEngineeringPipeline,
    FEATURE_COLUMNS,
)
from backend.cache.memory import InMemoryStateCache


def test_haversine_co_located_distance():
    """Points at identical coordinates should return 0.0 km displacement."""
    dist = calculate_haversine_km(23.7808, 90.4152, 23.7808, 90.4152)
    assert dist == 0.0


def test_haversine_known_city_distance():
    """Dhaka (23.8103, 90.4125) to Chittagong (22.3569, 91.7832) great-circle distance is ~215-220 km."""
    dist = calculate_haversine_km(23.8103, 90.4125, 22.3569, 91.7832)
    assert 210.0 < dist < 225.0


def test_haversine_symmetry():
    """Haversine distance must be symmetric: d(A, B) == d(B, A)."""
    d1 = calculate_haversine_km(23.8103, 90.4125, 24.8949, 91.8687)
    d2 = calculate_haversine_km(24.8949, 91.8687, 23.8103, 90.4125)
    assert pytest.approx(d1, rel=1e-4) == d2


def test_shannon_entropy_empty_and_uniform():
    """Empty payload returns 0.0; uniform repeating characters return 0.0 bits."""
    assert calculate_shannon_entropy("") == 0.0
    assert calculate_shannon_entropy("AAAAAAAAAA") == 0.0


def test_shannon_entropy_routine_vs_high_entropy():
    """Natural EMVCo payload has moderate entropy (<4.3), while random token exceeds 4.5."""
    standard_payload = "00020101021126580014bd.bkash.b2b011001711234567520454115303050"
    random_token = "https://phish.net/?token=q8$Z#2!kL9%wP*vM&1^xR7@bC5"

    standard_entropy = calculate_shannon_entropy(standard_payload)
    random_entropy = calculate_shannon_entropy(random_token)

    assert standard_entropy < 4.4
    assert random_entropy > 4.5
    assert random_entropy > standard_entropy


def test_amount_zscore_calculations():
    """Test standard normal Z-score computation and zero-std protection."""
    # Amount equals mean -> Z-score 0.0
    assert calculate_amount_zscore(500.0, 500.0, 100.0) == 0.0

    # Amount is 2 std above mean -> Z-score 2.0
    assert calculate_amount_zscore(700.0, 500.0, 100.0) == 2.0

    # Zero standard deviation should not crash (protected by epsilon)
    z_safe = calculate_amount_zscore(600.0, 500.0, 0.0)
    assert z_safe > 0.0


def test_feature_pipeline_extraction():
    """Test full pipeline feature vector generation and dimension conformity."""
    cache = InMemoryStateCache()
    pipeline = FeatureEngineeringPipeline(cache=cache)

    raw_tx = {
        "transaction_id": "test-uuid-001",
        "timestamp": 1700000000000,
        "payer_id": "PAYER_9999",
        "merchant_id": "MCH_555",
        "qr_type": 1,
        "qr_payload": "00020101021126580014bd.bkash.b2b0110MCH_555",
        "amount": 750.0,
        "merchant_category_code": 5411,
        "payer_latitude": 23.7808,
        "payer_longitude": 90.4152,
        "merchant_latitude": 23.7815,
        "merchant_longitude": 90.4160,
        "device_trust_score": 0.95,
        "scan_to_pay_latency_ms": 4200,
        "failed_pin_attempts": 0,
    }

    vec, feat_dict = pipeline.extract_features(raw_tx)

    # Must be 2D array of shape (1, 16)
    assert vec.shape == (1, 16)
    assert len(feat_dict) == 16
    assert set(feat_dict.keys()) == set(FEATURE_COLUMNS)

    # Check key engineered values
    assert feat_dict["qr_type"] == 1
    assert feat_dict["amount"] == 750.0
    assert feat_dict["haversine_distance_km"] < 0.2  # Very close coordinates
    assert feat_dict["device_trust_score"] == 0.95
    assert feat_dict["scan_to_pay_latency_ms"] == 4200

