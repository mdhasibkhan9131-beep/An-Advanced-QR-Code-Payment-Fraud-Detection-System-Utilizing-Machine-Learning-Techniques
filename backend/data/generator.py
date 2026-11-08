"""
Synthetic QR transaction generator module.
Simulates realistic mobile QR payment transactions reproducing acute financial
class imbalance (<= 1.0% fraud) and 4 distinct fraud archetypes:
1. Legitimate Baseline (99.2%)
2. Sticker Replacement / Quishing (0.3%)
3. Dynamic QR Injection / MITM (0.25%)
4. High-Velocity Credential Probing Bot (0.25%)
"""

import argparse
import os
import uuid
import time
import math
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import pandas as pd

from backend.data.feature_engineering import (
    calculate_haversine_km,
    calculate_shannon_entropy,
    calculate_amount_zscore,
    FEATURE_COLUMNS,
)


# ISO 18245 Merchant Category Codes (Retail, Groceries, Dining, Utilities)
MCC_LIST = [5411, 5812, 5311, 5912, 4814, 5541, 5999]

# Metro Center baseline (Dhaka Metropolitan Area)
BASE_LAT = 23.7808
BASE_LON = 90.4152


class SyntheticQRTransactionGenerator:
    """
    Synthesizes realistic payment streams with acute class imbalance and
    proposal-specified domain fraud vectors.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.rng = np.random.default_rng(seed=random_state)

    def _generate_legitimate_payload(self, merchant_id: str, amount: float, mcc: int) -> str:
        """Constructs a compliant EMVCo-like merchant QR string with normal entropy."""
        return (
            f"00020101021126580014bd.bkash.b2b0110{merchant_id}"
            f"5204{mcc}5303050540{int(amount):04d}5802BD5910MerchantHub6005Dhaka6304ABCD"
        )

    def _generate_quishing_payload(self) -> str:
        """Constructs an obfuscated high-entropy redirect phishing URL."""
        rand_token = "".join(self.rng.choice(list("abcdef0123456789!@#$%^&*="), size=36))
        return f"https://secure-qr.bkash-auth.net/pay/v2?redirect=login&session={rand_token}&ref=x7k"

    def generate_dataset(
        self,
        n_samples: int = 10000,
        fraud_ratio: float = 0.008,
        random_state: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Generates a synthetic dataset of n_samples with fraud_ratio minority instances.
        
        Args:
            n_samples: Total number of records to generate.
            fraud_ratio: Fraction of fraudulent transactions (default 0.008 = 0.8%).
            random_state: Optional seed override.

        Returns:
            pd.DataFrame containing raw transaction attributes, engineered features, and labels.
        """
        rng = np.random.default_rng(seed=random_state if random_state is not None else self.random_state)

        n_fraud = int(round(n_samples * fraud_ratio))
        n_legit = n_samples - n_fraud

        # Partition fraud archetypes among the minority cases:
        # ~38% Quishing, ~31% Dynamic MITM, ~31% Velocity Probe
        n_quishing = int(round(n_fraud * 0.38))
        n_mitm = int(round(n_fraud * 0.31))
        n_probe = n_fraud - n_quishing - n_mitm

        records: List[Dict[str, Any]] = []
        base_time_ms = int(time.time() * 1000) - (n_samples * 1200)  # staggered back in time

        # -------------------------------------------------------------
        # 1. Legitimate Transactions (n_legit)
        # -------------------------------------------------------------
        for i in range(n_legit):
            t_ms = base_time_ms + int(i * 1200 + rng.integers(0, 800))
            payer_num = rng.integers(1000, 9999)
            payer_id = f"PAYER_{payer_num}"
            merchant_id = f"MCH_{rng.integers(100, 999)}"
            mcc = int(rng.choice(MCC_LIST))
            qr_type = int(rng.choice([0, 1], p=[0.70, 0.30]))

            # Routine Dhaka coordinates with close proximity (< 3km)
            payer_lat = BASE_LAT + rng.normal(0, 0.03)
            payer_lon = BASE_LON + rng.normal(0, 0.03)
            merchant_lat = payer_lat + rng.normal(0, 0.005)
            merchant_lon = payer_lon + rng.normal(0, 0.005)

            # Spending: lognormal centered at ~300 BDT
            amount = float(np.clip(rng.lognormal(mean=5.7, sigma=0.8), 20.0, 5000.0))
            payer_mean = float(rng.uniform(250.0, 450.0))
            payer_std = float(rng.uniform(80.0, 150.0))

            latency = int(rng.normal(5500, 1800))
            latency = int(np.clip(latency, 2000, 25000))
            device_trust = float(np.clip(rng.uniform(0.85, 1.0), 0.0, 1.0))
            pin_fails = int(rng.choice([0, 1], p=[0.97, 0.03]))

            # Realistic low-to-moderate velocity
            v5m = float(rng.choice([0, 1, 2], p=[0.75, 0.20, 0.05]))
            v1h = float(v5m + rng.choice([0, 1, 2, 3], p=[0.50, 0.30, 0.15, 0.05]))
            v24h = float(v1h + rng.choice([1, 2, 4, 6], p=[0.40, 0.30, 0.20, 0.10]))
            vel_ratio = round(v1h / (v24h + 1.0), 4)

            payload = self._generate_legitimate_payload(merchant_id, amount, mcc)
            haversine = calculate_haversine_km(payer_lat, payer_lon, merchant_lat, merchant_lon)
            entropy = calculate_shannon_entropy(payload)
            zscore = calculate_amount_zscore(amount, payer_mean, payer_std)

            records.append({
                "transaction_id": str(uuid.UUID(int=int(rng.integers(1, 2**63)))),
                "timestamp": t_ms,
                "payer_id": payer_id,
                "merchant_id": merchant_id,
                "qr_type": qr_type,
                "qr_payload": payload,
                "amount": round(amount, 2),
                "merchant_category_code": mcc,
                "payer_latitude": round(payer_lat, 6),
                "payer_longitude": round(payer_lon, 6),
                "merchant_latitude": round(merchant_lat, 6),
                "merchant_longitude": round(merchant_lon, 6),
                "device_trust_score": round(device_trust, 4),
                "scan_to_pay_latency_ms": latency,
                "failed_pin_attempts": pin_fails,
                "haversine_distance_km": round(haversine, 4),
                "qr_payload_entropy": round(entropy, 4),
                "velocity_5m": v5m,
                "velocity_1h": v1h,
                "velocity_ratio": vel_ratio,
                "amount_zscore": round(zscore, 4),
                "is_fraud": 0,
                "fraud_type": "NONE",
            })

        # -------------------------------------------------------------
        # 2. Quishing / Sticker Replacement (n_quishing)
        # -------------------------------------------------------------
        for j in range(n_quishing):
            t_ms = base_time_ms + int(rng.integers(0, n_samples * 1200))
            payer_id = f"PAYER_{rng.integers(1000, 9999)}"
            merchant_id = f"MCH_ROUGE_{rng.integers(10, 99)}"
            mcc = int(rng.choice(MCC_LIST))
            qr_type = 0  # Static QR replacement

            payer_lat = BASE_LAT + rng.normal(0, 0.02)
            payer_lon = BASE_LON + rng.normal(0, 0.02)
            # Remote malicious displacement (> 50 km, e.g. 80-250 km away)
            merchant_lat = payer_lat + float(rng.uniform(0.6, 2.2))
            merchant_lon = payer_lon + float(rng.uniform(0.6, 2.2))

            amount = float(np.clip(rng.lognormal(mean=6.0, sigma=0.7), 50.0, 3000.0))
            payer_mean = 350.0
            payer_std = 120.0

            latency = int(rng.normal(6000, 1500))
            device_trust = float(np.clip(rng.uniform(0.70, 0.95), 0.0, 1.0))
            pin_fails = 0

            v5m = 0.0
            v1h = 1.0
            vel_ratio = 0.33

            payload = self._generate_quishing_payload()
            haversine = calculate_haversine_km(payer_lat, payer_lon, merchant_lat, merchant_lon)
            entropy = calculate_shannon_entropy(payload)
            zscore = calculate_amount_zscore(amount, payer_mean, payer_std)

            records.append({
                "transaction_id": str(uuid.UUID(int=int(rng.integers(1, 2**63)))),
                "timestamp": t_ms,
                "payer_id": payer_id,
                "merchant_id": merchant_id,
                "qr_type": qr_type,
                "qr_payload": payload,
                "amount": round(amount, 2),
                "merchant_category_code": mcc,
                "payer_latitude": round(payer_lat, 6),
                "payer_longitude": round(payer_lon, 6),
                "merchant_latitude": round(merchant_lat, 6),
                "merchant_longitude": round(merchant_lon, 6),
                "device_trust_score": round(device_trust, 4),
                "scan_to_pay_latency_ms": max(latency, 2500),
                "failed_pin_attempts": pin_fails,
                "haversine_distance_km": round(haversine, 4),
                "qr_payload_entropy": round(entropy, 4),
                "velocity_5m": v5m,
                "velocity_1h": v1h,
                "velocity_ratio": vel_ratio,
                "amount_zscore": round(zscore, 4),
                "is_fraud": 1,
                "fraud_type": "QUISHING",
            })

        # -------------------------------------------------------------
        # 3. Dynamic MITM / Amount Tampering (n_mitm)
        # -------------------------------------------------------------
        for k in range(n_mitm):
            t_ms = base_time_ms + int(rng.integers(0, n_samples * 1200))
            payer_id = f"PAYER_{rng.integers(1000, 9999)}"
            merchant_id = f"MCH_{rng.integers(100, 999)}"
            mcc = int(rng.choice(MCC_LIST))
            qr_type = 1  # Dynamic QR injection

            payer_lat = BASE_LAT + rng.normal(0, 0.02)
            payer_lon = BASE_LON + rng.normal(0, 0.02)
            merchant_lat = payer_lat + rng.normal(0, 0.02)
            merchant_lon = payer_lon + rng.normal(0, 0.02)

            # Massive amount surge (Z-score > 3.5)
            payer_mean = 300.0
            payer_std = 100.0
            amount = float(rng.uniform(4500.0, 35000.0))

            latency = int(rng.normal(3500, 1000))
            device_trust = float(np.clip(rng.uniform(0.35, 0.75), 0.0, 1.0))
            pin_fails = int(rng.choice([0, 1, 2], p=[0.70, 0.20, 0.10]))

            v5m = 1.0
            v1h = 2.0
            vel_ratio = 0.50

            payload = self._generate_legitimate_payload(merchant_id, amount, mcc) + "_tampered_sig"
            haversine = calculate_haversine_km(payer_lat, payer_lon, merchant_lat, merchant_lon)
            entropy = calculate_shannon_entropy(payload)
            zscore = calculate_amount_zscore(amount, payer_mean, payer_std)

            records.append({
                "transaction_id": str(uuid.UUID(int=int(rng.integers(1, 2**63)))),
                "timestamp": t_ms,
                "payer_id": payer_id,
                "merchant_id": merchant_id,
                "qr_type": qr_type,
                "qr_payload": payload,
                "amount": round(amount, 2),
                "merchant_category_code": mcc,
                "payer_latitude": round(payer_lat, 6),
                "payer_longitude": round(payer_lon, 6),
                "merchant_latitude": round(merchant_lat, 6),
                "merchant_longitude": round(merchant_lon, 6),
                "device_trust_score": round(device_trust, 4),
                "scan_to_pay_latency_ms": max(latency, 1200),
                "failed_pin_attempts": pin_fails,
                "haversine_distance_km": round(haversine, 4),
                "qr_payload_entropy": round(entropy, 4),
                "velocity_5m": v5m,
                "velocity_1h": v1h,
                "velocity_ratio": vel_ratio,
                "amount_zscore": round(zscore, 4),
                "is_fraud": 1,
                "fraud_type": "DYNAMIC_MITM",
            })

        # -------------------------------------------------------------
        # 4. High-Velocity Credential / Micro-Probing Bot (n_probe)
        # -------------------------------------------------------------
        for m in range(n_probe):
            t_ms = base_time_ms + int(rng.integers(0, n_samples * 1200))
            payer_id = f"PAYER_{rng.integers(1000, 9999)}"
            merchant_id = f"MCH_{rng.integers(100, 999)}"
            mcc = 4814  # Telecom / Micro-utility probe
            qr_type = int(rng.choice([0, 1]))

            payer_lat = BASE_LAT + rng.normal(0, 0.05)
            payer_lon = BASE_LON + rng.normal(0, 0.05)
            merchant_lat = payer_lat + rng.normal(0, 0.05)
            merchant_lon = payer_lon + rng.normal(0, 0.05)

            # Micro-probing amount
            amount = float(rng.uniform(1.0, 45.0))
            payer_mean = 350.0
            payer_std = 120.0

            # Sub-second automated bot latency (< 800 ms)
            latency = int(rng.uniform(120, 750))
            device_trust = float(np.clip(rng.uniform(0.05, 0.35), 0.0, 1.0))
            pin_fails = int(rng.integers(1, 5))

            v5m = float(rng.integers(6, 16))
            v1h = float(v5m + rng.integers(5, 20))
            v24h = float(v1h + 2.0)
            vel_ratio = round(v1h / (v24h + 1.0), 4)

            payload = f"000201010211probe_rapid_stream_{rng.integers(10000, 99999)}"
            haversine = calculate_haversine_km(payer_lat, payer_lon, merchant_lat, merchant_lon)
            entropy = calculate_shannon_entropy(payload)
            zscore = calculate_amount_zscore(amount, payer_mean, payer_std)

            records.append({
                "transaction_id": str(uuid.UUID(int=int(rng.integers(1, 2**63)))),
                "timestamp": t_ms,
                "payer_id": payer_id,
                "merchant_id": merchant_id,
                "qr_type": qr_type,
                "qr_payload": payload,
                "amount": round(amount, 2),
                "merchant_category_code": mcc,
                "payer_latitude": round(payer_lat, 6),
                "payer_longitude": round(payer_lon, 6),
                "merchant_latitude": round(merchant_lat, 6),
                "merchant_longitude": round(merchant_lon, 6),
                "device_trust_score": round(device_trust, 4),
                "scan_to_pay_latency_ms": latency,
                "failed_pin_attempts": pin_fails,
                "haversine_distance_km": round(haversine, 4),
                "qr_payload_entropy": round(entropy, 4),
                "velocity_5m": v5m,
                "velocity_1h": v1h,
                "velocity_ratio": vel_ratio,
                "amount_zscore": round(zscore, 4),
                "is_fraud": 1,
                "fraud_type": "VELOCITY_PROBE",
            })

        df = pd.DataFrame(records)
        # Sort chronologically by timestamp to preserve temporal validity
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df


def main():
    parser = argparse.ArgumentParser(description="Synthetic QR Transaction Dataset Generator")
    parser.add_argument("--samples", type=int, default=10000, help="Number of records to generate")
    parser.add_argument("--fraud-ratio", type=float, default=0.008, help="Fraud class ratio (e.g. 0.008 = 0.8%)")
    parser.add_argument("--output", type=str, default="data/synthetic_transactions.csv", help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    start_time = time.time()
    generator = SyntheticQRTransactionGenerator(random_state=args.seed)
    df = generator.generate_dataset(n_samples=args.samples, fraud_ratio=args.fraud_ratio)
    elapsed = time.time() - start_time

    df.to_csv(args.output, index=False)
    fraud_count = int(df["is_fraud"].sum())
    print(
        f"[Generator] Synthesized {len(df):,} transactions in {elapsed:.3f}s "
        f"({len(df)/max(elapsed, 0.001):.0f} rec/s) -> {args.output}"
    )
    print(
        f"[Generator] Fraud distribution: {fraud_count} cases "
        f"({fraud_count / len(df) * 100:.2f}%)"
    )
    print("[Generator] Breakdown by archetype:")
    print(df["fraud_type"].value_counts())


if __name__ == "__main__":
    main()
