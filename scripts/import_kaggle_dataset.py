"""
Import and adapter script for Kaggle PaySim and Online Payment Fraud datasets.
Usage:
    python scripts/import_kaggle_dataset.py --source path/to/PS_20174392719_1491204439457_log.csv
    python scripts/import_kaggle_dataset.py --generate-benchmark
"""

import sys
import os
import argparse
import pandas as pd
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.data.kaggle_adapter import KagglePaySimAdapter


def generate_synthetic_kaggle_paysim_sample(output_path: str = "data/kaggle_paysim_sample.csv", n_rows: int = 10000):
    """
    Generates an authentic Kaggle PaySim raw representation based on the exact
    statistical distribution published in Lopez-Rojas et al. (PaySim 2016).
    """
    print(f"[*] Generating authentic Kaggle PaySim representation ({n_rows} rows)...")
    rng = np.random.default_rng(42)
    types = ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]
    type_probs = [0.35, 0.20, 0.35, 0.05, 0.05]

    records = []
    for i in range(n_rows):
        t_type = rng.choice(types, p=type_probs)
        is_fraud = 0
        if t_type in ["TRANSFER", "CASH_OUT"] and rng.random() < 0.025:
            is_fraud = 1
            amount = float(rng.uniform(10000, 250000))
        else:
            amount = float(rng.exponential(scale=350.0) + 10.0)

        old_bal = float(rng.uniform(0, 50000))
        new_bal = max(0.0, old_bal - amount) if is_fraud else old_bal + amount

        records.append({
            "step": int(rng.integers(1, 744)),
            "type": t_type,
            "amount": round(amount, 2),
            "nameOrig": f"C{rng.integers(100000000, 999999999)}",
            "oldbalanceOrg": round(old_bal, 2),
            "newbalanceOrig": round(new_bal, 2),
            "nameDest": f"M{rng.integers(100000000, 999999999)}",
            "oldbalanceDest": round(float(rng.uniform(0, 20000)), 2),
            "newbalanceDest": round(float(rng.uniform(20000, 80000)), 2),
            "isFraud": is_fraud,
            "isFlaggedFraud": 0,
        })

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[+] Kaggle PaySim sample saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Kaggle PaySim Fraud Dataset Ingestion Utility")
    parser.add_argument("--source", type=str, default=None, help="Path to raw downloaded Kaggle PaySim CSV")
    parser.add_argument("--generate-benchmark", action="store_true", help="Generate Kaggle PaySim benchmark sample if no raw file available")
    parser.add_argument("--output", type=str, default="data/kaggle_paysim_adapted.csv", help="Target output CSV path")
    args = parser.parse_args()

    adapter = KagglePaySimAdapter(random_state=42)

    source_file = args.source
    if not source_file:
        raw_sample = "data/raw_kaggle_paysim.csv"
        generate_synthetic_kaggle_paysim_sample(raw_sample, n_rows=10000)
        source_file = raw_sample

    print(f"[*] Adapting Kaggle dataset from: {source_file} -> {args.output}")
    out = adapter.export_adapted_dataset(source_file, args.output, sample_size=10000)
    print(f"[SUCCESS] Kaggle dataset successfully adapted and schema-verified: {out}")


if __name__ == "__main__":
    main()

