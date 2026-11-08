"""
Unit tests for Machine Learning model suite:
- Supervised classifiers (LightGBM, Random Forest, SVM, PyTorch MLP)
- Unsupervised Isolation Forest anomaly detector
- Hybrid composite risk scorer
- Three-tier decision gating and zero-day anomaly escalation
"""

import pytest
import numpy as np

from backend.models.supervised import (
    LightGBMClassifierWrapper,
    RandomForestWrapper,
    SVMWrapper,
    LogisticRegressionWrapper,
    PyTorchMLPWrapper,
)
from backend.models.unsupervised import IsolationForestDetector
from backend.models.ensemble import HybridScorer, DecisionGatingEngine


@pytest.fixture
def dummy_train_data():
    """Generates synthetic 16D training data for testing."""
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1, size=(200, 16)).astype(np.float32)
    # Fraud condition: feature 0 > 0.5 or feature 8 > 1.0
    y = ((X[:, 0] > 0.5) | (X[:, 8] > 1.0)).astype(int)
    return X, y


def test_lightgbm_classifier(dummy_train_data, tmp_path):
    """Verifies LightGBM training, prediction probability shape, and serialization."""
    X, y = dummy_train_data
    clf = LightGBMClassifierWrapper(n_estimators=20, random_state=42)
    clf.fit(X, y)

    preds = clf.predict(X[:10])
    probas = clf.predict_proba(X[:10])

    assert len(preds) == 10
    assert probas.shape == (10, 2)
    assert np.all((probas >= 0.0) & (probas <= 1.0))
    assert clf.get_booster() is not None

    # Test serialization
    model_path = str(tmp_path / "test_lgbm.joblib")
    clf.save(model_path)
    loaded_clf = LightGBMClassifierWrapper()
    loaded_clf.load(model_path)
    loaded_probas = loaded_clf.predict_proba(X[:10])
    assert np.allclose(probas, loaded_probas)


def test_pytorch_mlp_classifier(dummy_train_data, tmp_path):
    """Verifies PyTorch MLP CPU execution, prediction shapes, and serialization."""
    X, y = dummy_train_data
    mlp = PyTorchMLPWrapper(input_dim=16, epochs=5, batch_size=32)
    mlp.fit(X, y)

    probas = mlp.predict_proba(X[:10])
    preds = mlp.predict(X[:10])

    assert probas.shape == (10, 2)
    assert len(preds) == 10
    assert np.allclose(np.sum(probas, axis=1), 1.0, atol=1e-5)

    # Test serialization
    save_path = str(tmp_path / "test_mlp.pt")
    mlp.save(save_path)
    loaded_mlp = PyTorchMLPWrapper(input_dim=16)
    loaded_mlp.load(save_path)
    loaded_probas = loaded_mlp.predict_proba(X[:10])
    assert np.allclose(probas, loaded_probas, atol=1e-4)


def test_isolation_forest_detector(dummy_train_data, tmp_path):
    """Verifies Isolation Forest training on inliers and calibrated [0, 1] output."""
    X, y = dummy_train_data
    X_legit = X[y == 0]
    detector = IsolationForestDetector(n_estimators=20, random_state=42)
    detector.fit(X_legit)

    scores = detector.score_anomaly(X[:15])
    assert len(scores) == 15
    assert np.all((scores >= 0.0) & (scores <= 1.0))

    # Test serialization
    if_path = str(tmp_path / "test_if.joblib")
    detector.save(if_path)
    loaded_det = IsolationForestDetector()
    loaded_det.load(if_path)
    loaded_scores = loaded_det.score_anomaly(X[:15])
    assert np.allclose(scores, loaded_scores)


def test_hybrid_scorer():
    """Verifies composite scoring formula S_comp = alpha*S_sup + (1-alpha)*S_ano."""
    scorer = HybridScorer(alpha=0.70)
    score = scorer.calculate_composite_score(supervised_score=0.80, anomaly_score=0.40)
    expected = (0.70 * 0.80) + (0.30 * 0.40)  # 0.56 + 0.12 = 0.68
    assert pytest.approx(score, abs=1e-4) == expected

    # Test clipping boundaries
    assert scorer.calculate_composite_score(1.5, 0.0) == 0.70
    assert scorer.calculate_composite_score(0.0, -0.5) == 0.0


def test_decision_gating_engine():
    """Verifies 3-tier gating (APPROVE, CHALLENGE_MFA, BLOCK) and Zero-Day Escalation."""
    gating = DecisionGatingEngine(
        threshold_approve=0.30,
        threshold_challenge=0.70,
        threshold_escalation=0.80,
    )

    # 1. Routine approve
    v1, z1, _ = gating.evaluate_verdict(supervised_score=0.10, anomaly_score=0.10, composite_score=0.10)
    assert v1 == "APPROVE"
    assert not z1

    # 2. Ambiguous MFA
    v2, z2, _ = gating.evaluate_verdict(supervised_score=0.50, anomaly_score=0.40, composite_score=0.47)
    assert v2 == "CHALLENGE_MFA"
    assert not z2

    # 3. High risk block
    v3, z3, _ = gating.evaluate_verdict(supervised_score=0.90, anomaly_score=0.80, composite_score=0.87)
    assert v3 == "BLOCK"
    assert not z3

    # 4. Zero-Day Anomaly Escalation Override:
    # Supervised score is low (0.05) -> composite is 0.29 (below 0.30 approve threshold),
    # but Anomaly score is extreme (0.85 >= 0.80) -> MUST escalate to CHALLENGE_MFA!
    v4, z4, _ = gating.evaluate_verdict(supervised_score=0.05, anomaly_score=0.85, composite_score=0.29)
    assert v4 == "CHALLENGE_MFA"
    assert z4 is True

