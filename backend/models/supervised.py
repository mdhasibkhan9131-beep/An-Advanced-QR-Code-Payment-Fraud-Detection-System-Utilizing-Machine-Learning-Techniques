"""
Concrete supervised classification model implementations.
Conforms to docs/05_System_Design/LOW_LEVEL_DESIGN.md.
Includes LightGBM, Random Forest, SVM, Logistic Regression, and PyTorch Tabular Deep MLP.
"""

import os
from typing import Optional
import numpy as np
import joblib

import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from backend.models.base import BaseClassifier


DEFAULT_LIGHTGBM_PATH = "backend/models/lightgbm_model.joblib"


class LightGBMClassifierWrapper(BaseClassifier):
    """
    LightGBM Gradient Boosted Decision Tree classifier.
    Primary production classifier engine.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        learning_rate: float = 0.05,
        num_leaves: int = 31,
        scale_pos_weight: float = 5.0,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.num_leaves = num_leaves
        self.scale_pos_weight = scale_pos_weight
        self.random_state = random_state
        self.model = lgb.LGBMClassifier(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            num_leaves=self.num_leaves,
            scale_pos_weight=self.scale_pos_weight,
            random_state=self.random_state,
            n_jobs=4,
            verbose=-1,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LightGBMClassifierWrapper":
        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def get_booster(self):
        """Returns underlying booster required for SHAP TreeExplainer."""
        return self.model.booster_

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.model, filepath)

    def load(self, filepath: str) -> "LightGBMClassifierWrapper":
        self.model = joblib.load(filepath)
        return self


class RandomForestWrapper(BaseClassifier):
    """Random Forest baseline classifier."""

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=4,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestWrapper":
        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.model, filepath)

    def load(self, filepath: str) -> "RandomForestWrapper":
        self.model = joblib.load(filepath)
        return self


class SVMWrapper(BaseClassifier):
    """Support Vector Machine with RBF kernel."""

    def __init__(self, random_state: int = 42):
        self.model = SVC(
            kernel="rbf",
            probability=True,
            class_weight="balanced",
            random_state=random_state,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SVMWrapper":
        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.model, filepath)

    def load(self, filepath: str) -> "SVMWrapper":
        self.model = joblib.load(filepath)
        return self


class LogisticRegressionWrapper(BaseClassifier):
    """Logistic Regression linear baseline classifier."""

    def __init__(self, random_state: int = 42):
        self.model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=random_state,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LogisticRegressionWrapper":
        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.model, filepath)

    def load(self, filepath: str) -> "LogisticRegressionWrapper":
        self.model = joblib.load(filepath)
        return self


class _TorchMLPModule(nn.Module):
    """Internal PyTorch 3-layer tabular neural network."""

    def __init__(self, input_dim: int = 16, hidden_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class PyTorchMLPWrapper(BaseClassifier):
    """PyTorch Deep Multi-Layer Perceptron tabular classifier executing on CPU."""

    def __init__(self, input_dim: int = 16, epochs: int = 15, batch_size: int = 64, lr: float = 0.003):
        self.input_dim = input_dim
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.module = _TorchMLPModule(input_dim=input_dim)
        self.device = torch.device("cpu")
        self.module.to(self.device)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "PyTorchMLPWrapper":
        self.module.train()
        tensor_x = torch.tensor(X, dtype=torch.float32)
        tensor_y = torch.tensor(y, dtype=torch.long)
        dataset = TensorDataset(tensor_x, tensor_y)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.module.parameters(), lr=self.lr)

        for _ in range(self.epochs):
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                logits = self.module(batch_x)
                loss = criterion(logits, batch_y)
                loss.backward()
                optimizer.step()

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        probas = self.predict_proba(X)
        return np.argmax(probas, axis=1)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        self.module.eval()
        with torch.no_grad():
            tensor_x = torch.tensor(X, dtype=torch.float32).to(self.device)
            logits = self.module(tensor_x)
            probas = torch.softmax(logits, dim=1).cpu().numpy()
        return probas

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save({
            "input_dim": self.input_dim,
            "state_dict": self.module.state_dict(),
        }, filepath)

    def load(self, filepath: str) -> "PyTorchMLPWrapper":
        checkpoint = torch.load(filepath, map_location=self.device)
        self.input_dim = checkpoint["input_dim"]
        self.module = _TorchMLPModule(input_dim=self.input_dim)
        self.module.load_state_dict(checkpoint["state_dict"])
        self.module.to(self.device)
        self.module.eval()
        return self
