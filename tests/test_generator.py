"""
Unit tests for SyntheticQRTransactionGenerator:
- Imbalance preservation (<= 1.0% fraud)
- Representation of all 4 fraud archetypes
- Vector domain constraints (Quishing displacement, Dynamic MITM Z-score, Bot latency)
- Reproducibility and throughput
"""

import time
import pytest
import pandas as pd
import numpy as np

from backend.data.generator import SyntheticQRTransactionGenerator
from backend.data.feature_engineering import FEATURE_COLUMNS


def test_generator_sample_count_and_columns():
    """Verifies generated sample count and presence of raw + engineered columns."""
    gen = SyntheticQRTransactionGenerator(random_state=42)
    df = gen.generate_dataset(n_samples=500, fraud_ratio=0.01)

    assert len(df) == 500
    for col in FEATURE_COLUMNS:
        assert col in df.columns, f"Missing feature column {col}"
    assert "is_fraud" in df.columns
    assert "fraud_type" in df.columns
    assert "transaction_id" in df.columns
    assert "timestamp" in df.columns


def test_generator_fraud_ratio_imbalance():
    """Verifies acute class imbalance stays at or below requested fraud ratio."""
    gen = SyntheticQRTransactionGenerator(random_state=42)
    df = gen.generate_dataset(n_samples=2000, fraud_ratio=0.008)

    fraud_count = int(df["is_fraud"].sum())
    fraud_rate = fraud_count / len(df)

    assert 0.005 <= fraud_rate <= 0.010
    assert fraud_count == 16  # Exactly 0.8% of 2000


def test_generator_all_archetypes_present():
    """Verifies all 4 archetypes (NONE, QUISHING, DYNAMIC_MITM, VELOCITY_PROBE) are generated."""
    gen = SyntheticQRTransactionGenerator(random_state=42)
    df = gen.generate_dataset(n_samples=2500, fraud_ratio=0.01)

    archetypes = set(df["fraud_type"].unique())
    expected = {"NONE", "QUISHING", "DYNAMIC_MITM", "VELOCITY_PROBE"}
    assert expected.issubset(archetypes)


def test_generator_quishing_characteristics():
    """Quishing cases must be static QR (qr_type=0) and exhibit large spatial displacement."""
    gen = SyntheticQRTransactionGenerator(random_state=42)
    df = gen.generate_dataset(n_samples=2000, fraud_ratio=0.02)

    quishing_df = df[df["fraud_type"] == "QUISHING"]
    assert len(quishing_df) > 0
    assert (quishing_df["qr_type"] == 0).all()
    assert (quishing_df["haversine_distance_km"] > 50.0).all()
    assert (quishing_df["qr_payload_entropy"] >= 4.4).all()


def test_generator_dynamic_mitm_characteristics():
    """Dynamic MITM cases must have dynamic QR (qr_type=1) and extreme amount Z-scores."""
    gen = SyntheticQRTransactionGenerator(random_state=42)
    df = gen.generate_dataset(n_samples=2000, fraud_ratio=0.02)

    mitm_df = df[df["fraud_type"] == "DYNAMIC_MITM"]
    assert len(mitm_df) > 0
    assert (mitm_df["qr_type"] == 1).all()
    assert (mitm_df["amount_zscore"] > 3.5).all()
    assert (mitm_df["amount"] > 3000.0).all()


def test_generator_velocity_probe_characteristics():
    """Bot probing cases must have sub-second latency and elevated 5m velocity."""
    gen = SyntheticQRTransactionGenerator(random_state=42)
    df = gen.generate_dataset(n_samples=2000, fraud_ratio=0.02)

    probe_df = df[df["fraud_type"] == "VELOCITY_PROBE"]
    assert len(probe_df) > 0
    assert (probe_df["scan_to_pay_latency_ms"] < 800).all()
    assert (probe_df["velocity_5m"] >= 5.0).all()
    assert (probe_df["device_trust_score"] < 0.40).all()


def test_generator_reproducibility():
    """Identical seeds must yield identical transaction IDs and features."""
    gen1 = SyntheticQRTransactionGenerator(random_state=123)
    gen2 = SyntheticQRTransactionGenerator(random_state=123)

    df1 = gen1.generate_dataset(n_samples=200, fraud_ratio=0.01)
    df2 = gen2.generate_dataset(n_samples=200, fraud_ratio=0.01)

    assert df1["amount"].equals(df2["amount"])
    assert df1["is_fraud"].equals(df2["is_fraud"])
    assert df1["haversine_distance_km"].equals(df2["haversine_distance_km"])


def test_generator_throughput():
    """Generating 1,000 records should take well under 1.0 second."""
    gen = SyntheticQRTransactionGenerator(random_state=42)
    t0 = time.time()
    df = gen.generate_dataset(n_samples=1000, fraud_ratio=0.008)
    elapsed = time.time() - t0

    assert len(df) == 1000
    assert elapsed < 1.0  # Fast generation performance
