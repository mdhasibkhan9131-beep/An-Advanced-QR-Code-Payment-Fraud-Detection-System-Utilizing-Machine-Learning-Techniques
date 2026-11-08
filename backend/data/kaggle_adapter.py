"""
Kaggle Dataset Adapter Module.
Enables seamless ingestion and adaptation of standard Kaggle financial fraud benchmarks
(specifically the PaySim Mobile Money Fraud dataset: 'Synthetic Financial Datasets For Fraud Detection')
into the specialized QR Code Payment Fraud schema defined in source/PROJECT_SPEC.md.
"""

import os
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from backend.data.feature_engineering import calculate_haversine_km, calculate_shannon_entropy


class KagglePaySimAdapter:
    """
    Adapts Kaggle PaySim and standard tabular financial datasets into the
    16-dimensional QR-augmented payment fraud schema specified in source/PROJECT_SPEC.md.
    """

    MCC_MAPPING = {
        "PAYMENT": 5411,    # Retail grocery / routine payment
        "TRANSFER": 4814,   # Wire transfer / P2P money movement
        "CASH_OUT": 6011,   # Agent ATM / cash withdrawal
        "DEBIT": 5311,      # Department store debit
        "CASH_IN": 6012,    # Bank branch deposit
    }

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.rng = np.random.default_rng(seed=random_state)

    def adapt_paysim_dataframe(
        self,
        df: pd.DataFrame,
        sample_size: Optional[int] = 10000,
    ) -> pd.DataFrame:
        """
        Transforms raw Kaggle PaySim rows into schema-compliant QR transaction records.
        Preserves authentic financial amounts, customer identifiers, and ground-truth fraud labels.
        """
        working_df = df.copy()

        # If sample_size specified and dataset is larger, sample preserving fraud ratio
        if sample_size and len(working_df) > sample_size:
            fraud_df = working_df[working_df["isFraud"] == 1]
            legit_df = working_df[working_df["isFraud"] == 0]

            fraud_sample_count = min(len(fraud_df), int(sample_size * 0.01))
            legit_sample_count = sample_size - fraud_sample_count

            sampled_fraud = fraud_df.sample(n=fraud_sample_count, random_state=self.random_state)
            sampled_legit = legit_df.sample(n=legit_sample_count, random_state=self.random_state)
            working_df = pd.concat([sampled_fraud, sampled_legit]).sample(frac=1.0, random_state=self.random_state).reset_index(drop=True)

        n = len(working_df)
        records = []
        base_time_ms = int(1731102000000)

        for idx, row in working_df.iterrows():
            is_fraud = int(row.get("isFraud", 0))
            amount = float(row.get("amount", 100.0))
            raw_type = str(row.get("type", "PAYMENT")).upper()
            mcc = self.MCC_MAPPING.get(raw_type, 5411)
            payer_id = str(row.get("nameOrig", f"CUST_{idx:05d}"))
            merchant_id = str(row.get("nameDest", f"MCH_{idx:05d}"))

            # Synthesize QR contextual features based on fraud status conforming to PROJECT_SPEC.md
            if is_fraud:
                qr_type = int(self.rng.choice([0, 1], p=[0.70, 0.30]))
                if qr_type == 0:
                    # Sticker replacement quishing payload
                    rand_token = "".join(self.rng.choice(list("abcdef0123456789"), size=32))
                    qr_payload = f"https://secure-qr.bkash-auth.net/pay/v2?session={rand_token}"
                    disp_km = float(self.rng.uniform(35.0, 180.0))
                    latency_ms = int(self.rng.uniform(4000, 12000))
                    trust = float(self.rng.uniform(0.70, 0.90))
                    pin_fails = int(self.rng.choice([0, 1], p=[0.85, 0.15]))
                else:
                    # Dynamic MITM or Bot Probing
                    qr_payload = f"00020101021226580014bd.bkash.b2b0110{merchant_id[:10]}"
                    disp_km = float(self.rng.uniform(0.1, 4.0))
                    latency_ms = int(self.rng.uniform(150, 450))
                    trust = float(self.rng.uniform(0.10, 0.35))
                    pin_fails = int(self.rng.choice([1, 2, 3], p=[0.3, 0.5, 0.2]))
            else:
                qr_type = int(self.rng.choice([0, 1], p=[0.75, 0.25]))
                qr_payload = f"00020101021126580014bd.bkash.b2b0110{merchant_id[:10]}5204{mcc}5303050"
                disp_km = float(self.rng.uniform(0.05, 3.5))
                latency_ms = int(self.rng.uniform(1500, 7500))
                trust = float(self.rng.uniform(0.85, 0.99))
                pin_fails = 0

            entropy = calculate_shannon_entropy(qr_payload)
            v5m = float(self.rng.choice([0, 1, 2], p=[0.7, 0.2, 0.1]) if not is_fraud else self.rng.choice([5, 8, 12], p=[0.3, 0.4, 0.3]))
            v1h = v5m + float(self.rng.integers(0, 3))
            v_ratio = round(v1h / (v1h + 2.0), 4)
            zscore = round((amount - 300.0) / 150.0, 4)

            # Coordinates centered in Dhaka metropolitan financial district
            p_lat = 23.7808 + float(self.rng.uniform(-0.05, 0.05))
            p_lon = 90.4152 + float(self.rng.uniform(-0.05, 0.05))
            m_lat = p_lat + (disp_km / 111.0)
            m_lon = p_lon

            records.append({
                "transaction_id": f"kaggle-paysim-{idx:06d}",
                "timestamp": base_time_ms + (idx * 500),
                "payer_id": payer_id,
                "merchant_id": merchant_id,
                "qr_type": qr_type,
                "qr_payload": qr_payload,
                "amount": round(amount, 2),
                "merchant_category_code": mcc,
                "payer_latitude": round(p_lat, 6),
                "payer_longitude": round(p_lon, 6),
                "merchant_latitude": round(m_lat, 6),
                "merchant_longitude": round(m_lon, 6),
                "device_trust_score": round(trust, 4),
                "scan_to_pay_latency_ms": latency_ms,
                "failed_pin_attempts": pin_fails,
                "haversine_distance_km": round(disp_km, 4),
                "qr_payload_entropy": round(entropy, 4),
                "velocity_5m": v5m,
                "velocity_1h": v1h,
                "velocity_ratio": v_ratio,
                "amount_zscore": zscore,
                "is_fraud": is_fraud,
                "fraud_type": "KAGGLE_PAYSIM_ADAPTED" if is_fraud else "NONE",
            })

        return pd.DataFrame(records)

    def export_adapted_dataset(
        self,
        source_csv_path: str,
        output_csv_path: str = "data/kaggle_paysim_adapted.csv",
        sample_size: int = 10000,
    ) -> str:
        """Loads Kaggle CSV, transforms it, and saves schema-compliant dataset."""
        df_raw = pd.read_csv(source_csv_path)
        df_adapted = self.adapt_paysim_dataframe(df_raw, sample_size=sample_size)
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        df_adapted.to_csv(output_csv_path, index=False)
        return output_csv_path
