"""
Data preprocessing, feature scaling, and class-imbalance rebalancing pipeline.
Enforces strict split isolation: RobustScaler is fitted strictly on the training partition,
and Borderline-SMOTE / SMOTE oversampling is applied strictly to training folds.
Validation and test sets remain un-oversampled and pristine to preserve evaluation fidelity.
"""

import os
from typing import Tuple, List, Optional, Dict, Any, Union
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import BorderlineSMOTE, SMOTE

from backend.data.feature_engineering import FEATURE_COLUMNS


DEFAULT_SCALER_PATH = "backend/models/scaler.joblib"


class DataPreprocessor:
    """
    Manages end-to-end dataset preparation:
    1. Feature matrix and label separation.
    2. Chronological / stratified train/val/test splitting (70% / 15% / 15%).
    3. RobustScaler fitting and serializing on training partition only.
    4. Borderline-SMOTE / SMOTE rebalancing on training partition only.
    """

    def __init__(self, scaler_path: Optional[str] = DEFAULT_SCALER_PATH):
        self.scaler_path = scaler_path
        self.scaler: Optional[RobustScaler] = None
        self.feature_columns: List[str] = list(FEATURE_COLUMNS)

    def prepare_features_and_labels(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Extracts 16-dimensional feature matrix X and binary target vector y from DataFrame.
        """
        missing_cols = [c for c in self.feature_columns if c not in df.columns]
        if missing_cols:
            raise ValueError(f"DataFrame is missing required feature columns: {missing_cols}")

        if "is_fraud" not in df.columns:
            raise ValueError("DataFrame is missing required target label column 'is_fraud'.")

        X = df[self.feature_columns].to_numpy(dtype=np.float32)
        y = df["is_fraud"].to_numpy(dtype=np.int32)
        return X, y, self.feature_columns

    def train_val_test_split(
        self,
        X: np.ndarray,
        y: np.ndarray,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        temporal: bool = True,
        stratify: bool = False,
        random_state: int = 42,
    ) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
        """
        Splits data into train (70%), validation (15%), and test (15%) partitions.
        Preserves chronological ordering when temporal=True.
        """
        total_ratio = train_ratio + val_ratio + test_ratio
        if not np.isclose(total_ratio, 1.0):
            raise ValueError(f"Partition ratios must sum to 1.0, got {total_ratio:.4f}")

        n_samples = len(X)
        if n_samples < 20:
            raise ValueError(f"Insufficient samples for 3-way split: {n_samples}")

        if temporal:
            # Chronological contiguous slice
            train_end = int(n_samples * train_ratio)
            val_end = train_end + int(n_samples * val_ratio)

            X_train, y_train = X[:train_end], y[:train_end]
            X_val, y_val = X[train_end:val_end], y[train_end:val_end]
            X_test, y_test = X[val_end:], y[val_end:]
        else:
            # Random split (stratified if requested)
            strat_first = y if stratify else None
            val_plus_test_ratio = val_ratio + test_ratio
            X_train, X_temp, y_train, y_temp = train_test_split(
                X,
                y,
                test_size=val_plus_test_ratio,
                random_state=random_state,
                stratify=strat_first,
            )

            relative_test_ratio = test_ratio / val_plus_test_ratio
            strat_second = y_temp if stratify else None
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp,
                y_temp,
                test_size=relative_test_ratio,
                random_state=random_state,
                stratify=strat_second,
            )

        return (X_train, y_train), (X_val, y_val), (X_test, y_test)

    def fit_scaler(self, X_train: np.ndarray) -> RobustScaler:
        """
        Fits a RobustScaler strictly on the training partition to avoid data leakage.
        """
        self.scaler = RobustScaler()
        self.scaler.fit(X_train)
        return self.scaler

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Applies pre-fitted RobustScaler normalization to feature matrix X.
        """
        if self.scaler is None:
            raise RuntimeError("Scaler has not been fitted or loaded yet. Call fit_scaler or load_scaler.")
        return self.scaler.transform(X)

    def save_scaler(self, filepath: Optional[str] = None) -> str:
        """
        Serializes fitted RobustScaler to disk using joblib.
        """
        if self.scaler is None:
            raise RuntimeError("No fitted scaler available to save.")
        target_path = filepath or self.scaler_path
        if not target_path:
            raise ValueError("No filepath specified for saving scaler.")

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        joblib.dump(self.scaler, target_path)
        return target_path

    def load_scaler(self, filepath: Optional[str] = None) -> RobustScaler:
        """
        Loads pre-fitted RobustScaler from disk using joblib.
        """
        target_path = filepath or self.scaler_path
        if not target_path or not os.path.exists(target_path):
            raise FileNotFoundError(f"Scaler file not found at: {target_path}")

        self.scaler = joblib.load(target_path)
        return self.scaler

    def apply_smote(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        method: str = "borderline",
        sampling_strategy: float = 0.20,
        k_neighbors: int = 5,
        random_state: int = 42,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Applies Borderline-SMOTE or SMOTE strictly to the training fold.
        Automatically checks and clips k_neighbors if minority class count is small.
        """
        minority_count = int(np.sum(y_train == 1))
        if minority_count <= 1:
            raise ValueError(
                f"Cannot apply SMOTE with fewer than 2 minority samples. Found {minority_count}."
            )

        safe_k = min(k_neighbors, max(1, minority_count - 1))

        if method == "borderline":
            oversampler = BorderlineSMOTE(
                kind="borderline-1",
                sampling_strategy=sampling_strategy,
                k_neighbors=safe_k,
                random_state=random_state,
            )
        elif method == "smote":
            oversampler = SMOTE(
                sampling_strategy=sampling_strategy,
                k_neighbors=safe_k,
                random_state=random_state,
            )
        else:
            raise ValueError(f"Unsupported oversampling method '{method}'. Choose 'borderline' or 'smote'.")

        X_resampled, y_resampled = oversampler.fit_resample(X_train, y_train)
        return X_resampled, y_resampled

    def fit_and_preprocess_pipeline(
        self,
        df: pd.DataFrame,
        scaler_save_path: Optional[str] = DEFAULT_SCALER_PATH,
        balance_method: str = "borderline",
        sampling_strategy: float = 0.20,
        temporal: bool = True,
        stratify: bool = False,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end preprocessing:
        1. Separates features and labels.
        2. Splits into Train (70%), Val (15%), Test (15%).
        3. Fits RobustScaler on Train fold only.
        4. Normalizes Train, Val, and Test folds.
        5. Rebalances Train fold with Borderline-SMOTE.
        6. Keeps Val and Test folds strictly un-oversampled.
        7. Serializes scaler to disk.
        """
        X, y, feature_names = self.prepare_features_and_labels(df)
        (X_train, y_train), (X_val, y_val), (X_test, y_test) = self.train_val_test_split(
            X, y,
            train_ratio=0.70,
            val_ratio=0.15,
            test_ratio=0.15,
            temporal=temporal,
            stratify=stratify,
            random_state=random_state,
        )

        # Fit RobustScaler on training fold strictly
        self.fit_scaler(X_train)
        if scaler_save_path:
            self.save_scaler(scaler_save_path)

        # Normalize features
        X_train_scaled = self.transform(X_train)
        X_val_scaled = self.transform(X_val)
        X_test_scaled = self.transform(X_test)

        # Apply SMOTE strictly to training fold
        X_train_resampled, y_train_resampled = self.apply_smote(
            X_train_scaled,
            y_train,
            method=balance_method,
            sampling_strategy=sampling_strategy,
            random_state=random_state,
        )

        return {
            "X_train": X_train_resampled,
            "y_train": y_train_resampled,
            "X_val": X_val_scaled,
            "y_val": y_val,
            "X_test": X_test_scaled,
            "y_test": y_test,
            "raw_train_samples": len(X_train),
            "resampled_train_samples": len(X_train_resampled),
            "val_samples": len(X_val),
            "test_samples": len(X_test),
            "scaler": self.scaler,
            "feature_names": feature_names,
        }

    def transform_single(self, feature_vector: Union[np.ndarray, List[float]]) -> np.ndarray:
        """
        Scales a single 16-element feature vector for live model inference.
        """
        if self.scaler is None:
            raise RuntimeError("Scaler is not loaded. Call load_scaler() before single-sample inference.")

        arr = np.asarray(feature_vector, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.shape[1] != len(self.feature_columns):
            raise ValueError(
                f"Expected feature vector of length {len(self.feature_columns)}, got {arr.shape[1]}"
            )

        return self.scaler.transform(arr)

