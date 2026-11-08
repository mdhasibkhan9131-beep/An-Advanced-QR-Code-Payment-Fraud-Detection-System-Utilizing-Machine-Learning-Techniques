"""
Model training, benchmarking, and evaluation harness.
Conforms to docs/05_System_Design/LOW_LEVEL_DESIGN.md and FR-MOD-001, FR-MOD-002, FR-MOD-003.
Runs empirical benchmarking on all candidate algorithms and exports reproducible results.
"""

import time
import os
import json
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
)

from backend.models.supervised import (
    LightGBMClassifierWrapper,
    RandomForestWrapper,
    SVMWrapper,
    LogisticRegressionWrapper,
    PyTorchMLPWrapper,
)
from backend.models.unsupervised import IsolationForestDetector
from backend.models.ensemble import HybridScorer, DecisionGatingEngine
from backend.data.generator import SyntheticQRTransactionGenerator
from backend.data.preprocessor import DataPreprocessor, DEFAULT_SCALER_PATH


DEFAULT_LIGHTGBM_PATH = "backend/models/lightgbm_model.joblib"
DEFAULT_IFOREST_PATH = "backend/models/isolation_forest.joblib"
DEFAULT_BENCHMARK_PATH = "research/benchmarks/benchmark_results.json"


class ModelTrainer:
    """
    Executes training and comparative evaluation across all candidate algorithms.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.preprocessor = DataPreprocessor()
        self.hybrid_scorer = HybridScorer()
        self.gating_engine = DecisionGatingEngine()

    def calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_scores: np.ndarray,
        latency_ms: float,
    ) -> Dict[str, float]:
        """Calculates standard classification metrics and latency."""
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

        try:
            auc = float(roc_auc_score(y_true, y_scores))
        except Exception:
            auc = 0.5

        return {
            "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
            "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
            "specificity": round(specificity, 4),
            "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
            "false_positive_rate": round(fpr, 4),
            "roc_auc": round(auc, 4),
            "latency_ms": round(float(latency_ms), 3),
        }

    def run_benchmark(
        self,
        n_samples: int = 10000,
        fraud_ratio: float = 0.008,
        save_production_models: bool = True,
        output_results_path: Optional[str] = DEFAULT_BENCHMARK_PATH,
    ) -> Dict[str, Any]:
        """
        Runs the full comparative benchmark pipeline.
        """
        print(f"[Trainer] Generating {n_samples} synthetic QR transactions (fraud_ratio={fraud_ratio})...")
        generator = SyntheticQRTransactionGenerator(random_state=self.random_state)
        df = generator.generate_dataset(n_samples=n_samples, fraud_ratio=fraud_ratio)

        print("[Trainer] Preprocessing dataset with strict split isolation & Borderline-SMOTE...")
        prep_data = self.preprocessor.fit_and_preprocess_pipeline(
            df=df,
            scaler_save_path=DEFAULT_SCALER_PATH,
            balance_method="borderline",
            sampling_strategy=0.20,
            temporal=True,
            random_state=self.random_state,
        )

        X_train = prep_data["X_train"]
        y_train = prep_data["y_train"]
        X_val = prep_data["X_val"]
        y_val = prep_data["y_val"]
        X_test = prep_data["X_test"]
        y_test = prep_data["y_test"]

        # Models dictionary
        models: Dict[str, Any] = {
            "Logistic Regression": LogisticRegressionWrapper(random_state=self.random_state),
            "Support Vector Machine": SVMWrapper(random_state=self.random_state),
            "Random Forest": RandomForestWrapper(random_state=self.random_state),
            "PyTorch MLP": PyTorchMLPWrapper(input_dim=16, epochs=15),
            "LightGBM": LightGBMClassifierWrapper(random_state=self.random_state),
        }

        results: Dict[str, Any] = {}

        # 1. Train and evaluate supervised classifiers
        for name, clf in models.items():
            print(f"[Trainer] Training {name}...")
            t0 = time.time()
            clf.fit(X_train, y_train)
            train_time = time.time() - t0

            # Measure inference latency over 100 iterations on test set single samples
            latencies = []
            for i in range(min(100, len(X_test))):
                sample = X_test[i:i+1]
                t_inf = time.perf_counter()
                clf.predict_proba(sample)
                latencies.append((time.perf_counter() - t_inf) * 1000)

            avg_latency = float(np.mean(latencies))
            probas = clf.predict_proba(X_test)[:, 1]
            preds = (probas >= 0.5).astype(int)

            metrics = self.calculate_metrics(y_test, preds, probas, avg_latency)
            metrics["train_time_sec"] = round(train_time, 2)
            results[name] = metrics
            print(f"[Trainer] {name} -> Recall: {metrics['recall']:.2%}, Precision: {metrics['precision']:.2%}, Latency: {metrics['latency_ms']:.2f}ms")

        # 2. Train and evaluate Isolation Forest
        print("[Trainer] Training Unsupervised Isolation Forest on legitimate instances...")
        X_train_legit = X_train[y_train == 0]
        iforest = IsolationForestDetector(random_state=self.random_state)
        t0 = time.time()
        iforest.fit(X_train_legit)
        iforest_train_time = time.time() - t0

        latencies_iforest = []
        for i in range(min(100, len(X_test))):
            sample = X_test[i:i+1]
            t_inf = time.perf_counter()
            iforest.score_anomaly(sample)
            latencies_iforest.append((time.perf_counter() - t_inf) * 1000)

        avg_latency_iforest = float(np.mean(latencies_iforest))
        anomaly_scores = iforest.score_anomaly(X_test)
        iforest_preds = (anomaly_scores >= 0.70).astype(int)
        iforest_metrics = self.calculate_metrics(y_test, iforest_preds, anomaly_scores, avg_latency_iforest)
        iforest_metrics["train_time_sec"] = round(iforest_train_time, 2)
        results["Isolation Forest"] = iforest_metrics
        print(f"[Trainer] Isolation Forest -> Recall: {iforest_metrics['recall']:.2%}, ROC-AUC: {iforest_metrics['roc_auc']:.4f}")

        # 3. Evaluate Hybrid Engine (LightGBM + Isolation Forest)
        print("[Trainer] Evaluating Hybrid Composite Engine (LightGBM + Isolation Forest)...")
        lgbm = models["LightGBM"]
        lgbm_scores = lgbm.predict_proba(X_test)[:, 1]

        hybrid_scores = np.array([
            self.hybrid_scorer.calculate_composite_score(lgbm_scores[i], anomaly_scores[i])
            for i in range(len(X_test))
        ])

        hybrid_verdicts = []
        for i in range(len(X_test)):
            verdict, _, _ = self.gating_engine.evaluate_verdict(
                lgbm_scores[i], anomaly_scores[i], hybrid_scores[i]
            )
            hybrid_verdicts.append(1 if verdict in ["BLOCK", "CHALLENGE_MFA"] else 0)

        hybrid_preds = np.array(hybrid_verdicts)
        hybrid_latency = results["LightGBM"]["latency_ms"] + avg_latency_iforest + 0.05
        hybrid_metrics = self.calculate_metrics(y_test, hybrid_preds, hybrid_scores, hybrid_latency)
        results["Hybrid Model (Proposed)"] = hybrid_metrics
        print(f"[Trainer] Hybrid Model -> Recall: {hybrid_metrics['recall']:.2%}, Precision: {hybrid_metrics['precision']:.2%}, FPR: {hybrid_metrics['false_positive_rate']:.2%}")

        # 4. Save production models
        if save_production_models:
            print("[Trainer] Serializing production models to disk...")
            models["LightGBM"].save(DEFAULT_LIGHTGBM_PATH)
            iforest.save(DEFAULT_IFOREST_PATH)
            print(f"[Trainer] Saved LightGBM to {DEFAULT_LIGHTGBM_PATH}")
            print(f"[Trainer] Saved Isolation Forest to {DEFAULT_IFOREST_PATH}")

        # 5. Export benchmark results
        if output_results_path:
            os.makedirs(os.path.dirname(output_results_path), exist_ok=True)
            with open(output_results_path, "w") as f:
                json.dump(results, f, indent=2)
            print(f"[Trainer] Benchmark report exported to {output_results_path}")

        return results


def main():
    trainer = ModelTrainer(random_state=42)
    results = trainer.run_benchmark(n_samples=10000, fraud_ratio=0.008)
    print("\n--- FINAL BENCHMARK SCOREBOARD ---")
    summary_df = pd.DataFrame(results).T
    print(summary_df.to_string())


if __name__ == "__main__":
    main()

