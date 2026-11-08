"""
Abstract Base Classes for Supervised and Unsupervised Machine Learning Models.
Conforms to docs/05_System_Design/LOW_LEVEL_DESIGN.md.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class BaseClassifier(ABC):
    """Abstract Base Class for all supervised tabular classifiers."""

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseClassifier":
        """Fit model to training feature matrix X and target labels y."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict binary classification labels {0, 1}."""
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities; returns array of shape (N, 2)."""
        pass

    @abstractmethod
    def save(self, filepath: str) -> None:
        """Serialize model weights and metadata to disk."""
        pass

    @abstractmethod
    def load(self, filepath: str) -> "BaseClassifier":
        """Load serialized model weights from disk."""
        pass


class BaseAnomalyDetector(ABC):
    """Abstract Base Class for unsupervised outlier and anomaly detectors."""

    @abstractmethod
    def fit(self, X: np.ndarray) -> "BaseAnomalyDetector":
        """Fit detector strictly on legitimate baseline feature vectors."""
        pass

    @abstractmethod
    def score_anomaly(self, X: np.ndarray) -> np.ndarray:
        """Compute normalized anomaly score S_anomaly in range [0.0, 1.0]."""
        pass

    @abstractmethod
    def save(self, filepath: str) -> None:
        """Serialize detector weights to disk."""
        pass

    @abstractmethod
    def load(self, filepath: str) -> "BaseAnomalyDetector":
        """Load serialized detector weights from disk."""
        pass
