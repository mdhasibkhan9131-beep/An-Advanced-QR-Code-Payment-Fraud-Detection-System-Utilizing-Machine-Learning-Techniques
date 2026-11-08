"""
Machine learning models, anomaly detectors, and hybrid decision gating package.
"""

from backend.models.base import BaseClassifier, BaseAnomalyDetector
from backend.models.supervised import (
    LightGBMClassifierWrapper,
    RandomForestWrapper,
    SVMWrapper,
    LogisticRegressionWrapper,
    PyTorchMLPWrapper,
)
from backend.models.unsupervised import IsolationForestDetector
from backend.models.ensemble import HybridScorer, DecisionGatingEngine
from backend.models.trainer import (
    ModelTrainer,
    DEFAULT_LIGHTGBM_PATH,
    DEFAULT_IFOREST_PATH,
)

__all__ = [
    "BaseClassifier",
    "BaseAnomalyDetector",
    "LightGBMClassifierWrapper",
    "RandomForestWrapper",
    "SVMWrapper",
    "LogisticRegressionWrapper",
    "PyTorchMLPWrapper",
    "IsolationForestDetector",
    "HybridScorer",
    "DecisionGatingEngine",
    "ModelTrainer",
    "DEFAULT_LIGHTGBM_PATH",
    "DEFAULT_IFOREST_PATH",
]
