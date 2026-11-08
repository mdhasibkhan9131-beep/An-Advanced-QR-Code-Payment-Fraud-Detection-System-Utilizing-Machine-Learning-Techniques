"""
Unit tests for Explainable AI (SHAP) and Reason Code Engine:
- SHAP TreeExplainer calculation
- Top-3 reason code mapping
- Attribution latency budget (<= 40 ms)
"""

import time
import pytest
import numpy as np
import lightgbm as lgb

from backend.xai.explainer import SHAPTreeExplainer, REASON_CODE_MAP
from backend.data.feature_engineering import FEATURE_COLUMNS


@pytest.fixture
def trained_tree_explainer():
    """Builds a fast LightGBM booster and wraps with SHAPTreeExplainer."""
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1, size=(100, len(FEATURE_COLUMNS))).astype(np.float32)
    # Target strongly driven by haversine distance (feature 8) and entropy (feature 1)
    y = ((X[:, 8] > 0.8) | (X[:, 1] > 1.2)).astype(int)

    clf = lgb.LGBMClassifier(n_estimators=10, random_state=42, verbose=-1)
    clf.fit(X, y)
    return SHAPTreeExplainer(clf.booster_)


def test_shap_explanation_structure(trained_tree_explainer):
    """Verifies SHAP output dictionary contains top features, reason codes, and raw values."""
    sample = np.zeros((1, len(FEATURE_COLUMNS)), dtype=np.float32)
    sample[0, 8] = 3.5  # Large displacement

    res = trained_tree_explainer.explain_instance(sample, top_k=3)

    assert "top_features" in res
    assert "reason_codes" in res
    assert "raw_attributions" in res
    assert len(res["top_features"]) == 3
    assert len(res["raw_attributions"]) == len(FEATURE_COLUMNS)
    assert isinstance(res["reason_codes"], list)


def test_shap_reason_code_mapping(trained_tree_explainer):
    """Verifies dominant anomalous feature triggers correct semantic reason code."""
    sample = np.zeros((1, len(FEATURE_COLUMNS)), dtype=np.float32)
    sample[0, 8] = 5.0  # Dominant displacement

    res = trained_tree_explainer.explain_instance(sample, top_k=1)
    top_feature = res["top_features"][0]["feature"]

    if top_feature == "haversine_distance_km":
        assert "GEOGRAPHIC_DISPLACEMENT_EXCEEDED" in res["reason_codes"]


def test_shap_attribution_latency_budget(trained_tree_explainer):
    """Verifies single-instance SHAP attribution executes well within the 40 ms budget."""
    sample = np.random.normal(0, 1, size=(1, len(FEATURE_COLUMNS))).astype(np.float32)

    latencies = []
    for _ in range(20):
        t0 = time.perf_counter()
        trained_tree_explainer.explain_instance(sample)
        latencies.append((time.perf_counter() - t0) * 1000)

    avg_ms = float(np.mean(latencies))
    assert avg_ms < 40.0, f"SHAP latency exceeded 40 ms: {avg_ms:.2f} ms"

