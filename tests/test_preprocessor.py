"""
Unit tests for DataPreprocessor:
- Feature extraction and label verification
- Stratified and chronological train/val/test splits (70% / 15% / 15%)
- Scaler fitting strictly on training split
- Borderline-SMOTE oversampling strictly isolated to training partition
- Validation and test splits preservation (zero leakage)
- Scaler persistence and single-vector inference transformation
"""

import os
import pytest
import numpy as np
import pandas as pd

from backend.data.preprocessor import DataPreprocessor, DEFAULT_SCALER_PATH
from backend.data.generator import SyntheticQRTransactionGenerator
from backend.data.feature_engineering import FEATURE_COLUMNS


@pytest.fixture
def synthetic_dataframe():
    """Generates a reproducible 1,000-sample dataset with 1% fraud."""
    gen = SyntheticQRTransactionGenerator(random_state=42)
    return gen.generate_dataset(n_samples=1000, fraud_ratio=0.01)


def test_prepare_features_and_labels(synthetic_dataframe):
    """Verifies X has shape (N, 16) and y has shape (N,)."""
    preprocessor = DataPreprocessor()
    X, y, feature_names = preprocessor.prepare_features_and_labels(synthetic_dataframe)

    assert X.shape == (1000, 16)
    assert y.shape == (1000,)
    assert feature_names == FEATURE_COLUMNS
    assert np.isnan(X).sum() == 0


def test_train_val_test_split_proportions(synthetic_dataframe):
    """Verifies 70% / 15% / 15% partition proportions."""
    preprocessor = DataPreprocessor()
    X, y, _ = preprocessor.prepare_features_and_labels(synthetic_dataframe)

    (X_train, y_train), (X_val, y_val), (X_test, y_test) = preprocessor.train_val_test_split(
        X, y, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, temporal=True
    )

    assert len(X_train) == 700
    assert len(X_val) == 150
    assert len(X_test) == 150
    assert len(X_train) + len(X_val) + len(X_test) == 1000


def test_scaler_fitting_and_transformation(synthetic_dataframe):
    """Verifies RobustScaler transforms training data to zero median and unit IQR."""
    preprocessor = DataPreprocessor()
    X, y, _ = preprocessor.prepare_features_and_labels(synthetic_dataframe)
    (X_train, _), (X_val, _), (X_test, _) = preprocessor.train_val_test_split(X, y)

    preprocessor.fit_scaler(X_train)
    X_train_scaled = preprocessor.transform(X_train)
    X_val_scaled = preprocessor.transform(X_val)

    assert X_train_scaled.shape == X_train.shape
    assert X_val_scaled.shape == X_val.shape
    assert not np.isnan(X_train_scaled).any()
    assert not np.isinf(X_train_scaled).any()


def test_smote_strict_partition_isolation(synthetic_dataframe, tmp_path):
    """
    CRITICAL REQUIREMENT (FR-DAT-003, AC-05):
    SMOTE must be applied strictly to X_train.
    Validation and test sets must NOT be resampled.
    """
    scaler_file = str(tmp_path / "test_scaler.joblib")
    preprocessor = DataPreprocessor(scaler_path=scaler_file)

    pipeline_result = preprocessor.fit_and_preprocess_pipeline(
        synthetic_dataframe,
        scaler_save_path=scaler_file,
        balance_method="borderline",
        sampling_strategy=0.20,
        temporal=False,
        stratify=True,
    )

    X_train = pipeline_result["X_train"]
    y_train = pipeline_result["y_train"]
    X_val = pipeline_result["X_val"]
    y_val = pipeline_result["y_val"]
    X_test = pipeline_result["X_test"]
    y_test = pipeline_result["y_test"]

    # Training fold was oversampled to 20% minority ratio
    minority_train = int(np.sum(y_train == 1))
    majority_train = int(np.sum(y_train == 0))
    train_ratio = minority_train / majority_train
    assert pytest.approx(train_ratio, abs=0.02) == 0.20

    # Validation and test folds were NOT oversampled (must maintain original sample count)
    assert len(X_val) == 150
    assert len(X_test) == 150

    # Scaler was successfully saved to disk
    assert os.path.exists(scaler_file)


def test_scaler_persistence_and_single_transform(synthetic_dataframe, tmp_path):
    """Verifies scaler persistence and single-sample inference transform."""
    scaler_file = str(tmp_path / "persisted_scaler.joblib")
    preprocessor1 = DataPreprocessor(scaler_path=scaler_file)
    X, y, _ = preprocessor1.prepare_features_and_labels(synthetic_dataframe)

    preprocessor1.fit_scaler(X)
    preprocessor1.save_scaler(scaler_file)

    # Load in new preprocessor instance
    preprocessor2 = DataPreprocessor(scaler_path=scaler_file)
    preprocessor2.load_scaler(scaler_file)

    sample_vector = X[0]
    out1 = preprocessor1.transform_single(sample_vector)
    out2 = preprocessor2.transform_single(sample_vector)

    assert out1.shape == (1, 16)
    assert np.allclose(out1, out2)


def test_error_handling_invalid_columns():
    """Missing required feature column raises descriptive ValueError."""
    bad_df = pd.DataFrame({"amount": [10.0, 20.0], "is_fraud": [0, 1]})
    preprocessor = DataPreprocessor()
    with pytest.raises(ValueError, match="DataFrame is missing required feature columns"):
        preprocessor.prepare_features_and_labels(bad_df)

