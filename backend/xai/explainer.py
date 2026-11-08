"""
Explainable AI (XAI) engine using SHAP TreeExplainer.
Conforms to docs/05_System_Design/LOW_LEVEL_DESIGN.md and FR-XAI-001, FR-XAI-002, FR-XAI-003.
Generates local feature attributions and standardized human-readable reason codes.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import shap

from backend.data.feature_engineering import FEATURE_COLUMNS


# Standardized Human-Readable Reason Codes Mapping (FR-XAI-002)
REASON_CODE_MAP: Dict[str, str] = {
    "haversine_distance_km": "GEOGRAPHIC_DISPLACEMENT_EXCEEDED",
    "qr_payload_entropy": "ANOMALOUS_QR_PAYLOAD_ENTROPY",
    "amount_zscore": "AMOUNT_EXCEEDS_HISTORICAL_BASELINE",
    "amount": "ELEVATED_TRANSACTION_VALUE",
    "scan_to_pay_latency_ms": "SUB_SECOND_SCAN_LATENCY",
    "velocity_5m": "HIGH_FREQUENCY_VELOCITY_5M",
    "velocity_1h": "HIGH_FREQUENCY_VELOCITY_1H",
    "velocity_ratio": "ANOMALOUS_VELOCITY_SURGE_RATIO",
    "device_trust_score": "DEGRADED_DEVICE_TRUST_FINGERPRINT",
    "failed_pin_attempts": "MULTIPLE_FAILED_PIN_ATTEMPTS",
    "qr_type": "SUSPICIOUS_STATIC_QR_DISPLACEMENT",
    "merchant_category_code": "ATYPICAL_MERCHANT_CATEGORY",
}


class SHAPTreeExplainer:
    """
    Computes local SHAP feature attributions using TreeExplainer on LightGBM.
    Translates top contributing positive SHAP values into compliance reason codes.
    """

    def __init__(self, lightgbm_booster):
        self.booster = lightgbm_booster
        self.feature_names = list(FEATURE_COLUMNS)
        self.explainer = shap.TreeExplainer(self.booster)

    def explain_instance(
        self,
        feature_vector: np.ndarray,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        Calculates local feature attribution for a single 16-element feature vector.
        
        Args:
            feature_vector: 2D numpy array of shape (1, 16).
            top_k: Number of primary contributing factors to extract.

        Returns:
            Dictionary containing raw SHAP values, base value, and top reason codes.
        """
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)

        shap_values = self.explainer.shap_values(feature_vector)

        # Handle binary classification output formats (single array or list [class0, class1])
        if isinstance(shap_values, list):
            sv = shap_values[1][0]  # Positive fraud class attributions
        elif shap_values.ndim == 3:
            sv = shap_values[0, :, 1]
        else:
            sv = shap_values[0]

        # Extract features that positively drive the fraud prediction (sv > 0)
        sorted_indices = np.argsort(sv)[::-1]
        top_features = []
        reason_codes = []

        for idx in sorted_indices[:top_k]:
            val = float(sv[idx])
            col_name = self.feature_names[idx]
            top_features.append({
                "feature": col_name,
                "attribution": round(val, 4),
            })
            if val > 0.05:  # Significance cutoff
                reason_codes.append(REASON_CODE_MAP.get(col_name, f"ANOMALOUS_{col_name.upper()}"))

        return {
            "top_features": top_features,
            "reason_codes": reason_codes if reason_codes else ["GENERAL_RISK_ELEVATION"],
            "raw_attributions": [round(float(v), 4) for v in sv],
        }
