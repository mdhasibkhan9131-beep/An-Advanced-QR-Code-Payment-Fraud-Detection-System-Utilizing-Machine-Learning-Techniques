"""
Unsupervised anomaly detection implementations.
Conforms to docs/05_System_Design/LOW_LEVEL_DESIGN.md.
Includes Isolation Forest anomaly scoring calibrated to [0.0, 1.0].
"""

import os
from typing import Optional
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest

from backend.models.base import BaseAnomalyDetector


DEFAULT_IFOREST_PATH = "backend/models/isolation_forest.joblib"


class IsolationForestDetector(BaseAnomalyDetector):
    """
    Unsupervised Isolation Forest anomaly detector.
    Trained strictly on legitimate baseline feature vectors.
    Converts raw decision scores to normalized anomaly probability S_anomaly in [0.0, 1.0].
    """

    def __init__(
        self,
        n_estimators: int = 100,
        contamination: float = 0.01,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=4,
        )
        self.min_score: float = -0.5
        self.max_score: float = 0.5

    def fit(self, X: np.ndarray) -> "IsolationForestDetector":
        """Fit detector strictly on legitimate baseline vectors."""
        self.model.fit(X)
        raw_scores = self.model.decision_function(X)
        self.min_score = float(np.min(raw_scores))
        self.max_score = float(np.max(raw_scores))
        return self

    def score_anomaly(self, X: np.ndarray) -> np.ndarray:
        """
        Calculates normalized anomaly score S_anomaly in [0.0, 1.0].
        In IsolationForest: lower raw score -> more anomalous.
        Inverted so 0.0 is routine inlier and 1.0 is extreme out-of-distribution anomaly.
        """
        raw_scores = self.model.decision_function(X)
        # Avoid division by zero
        score_range = max(self.max_score - self.min_score, 1e-5)
        # Invert: normalized = (max - raw) / range
        normalized = (self.max_score - raw_scores) / score_range
        return np.clip(normalized, 0.0, 1.0).astype(np.float32)

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "n_estimators": self.n_estimators,
            "contamination": self.contamination,
        }, filepath)

    def load(self, filepath: str) -> "IsolationForestDetector":
        data = joblib.load(filepath)
        self.model = data["model"]
        self.min_score = data["min_score"]
        self.max_score = data["max_score"]
        self.n_estimators = data["n_estimators"]
        self.contamination = data["contamination"]
        return self
