"""
Feature engineering pipeline for QR payment transactions.
Computes Haversine spatial distance, Shannon entropy, stateful rolling velocities,
and customer spending baseline Z-scores.
"""

import math
from typing import Dict, Any, Tuple, List
import numpy as np
from backend.cache.base import StateCacheInterface
from backend.utils.security import hash_sensitive_identifier


FEATURE_COLUMNS: List[str] = [
    "qr_type",
    "qr_payload_entropy",
    "amount",
    "merchant_category_code",
    "payer_latitude",
    "payer_longitude",
    "merchant_latitude",
    "merchant_longitude",
    "haversine_distance_km",
    "device_trust_score",
    "scan_to_pay_latency_ms",
    "failed_pin_attempts",
    "velocity_5m",
    "velocity_1h",
    "velocity_ratio",
    "amount_zscore",
]


def calculate_haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance in kilometers between two GPS coordinates
    using the Haversine trigonometric formula.
    """
    R = 6371.0  # Earth's mean radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    # Clamp 'a' to [0, 1] to prevent domain errors in sqrt due to floating-point rounding
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(R * c, 4)


def calculate_shannon_entropy(payload_str: str) -> float:
    """
    Computes Shannon entropy in bits per character for decoded QR payload text.
    Detects high-entropy random tokens, obfuscated redirects, or encrypted injection payloads.
    """
    if not payload_str:
        return 0.0

    length = len(payload_str)
    char_counts: Dict[str, int] = {}
    for char in payload_str:
        char_counts[char] = char_counts.get(char, 0) + 1

    entropy = 0.0
    for count in char_counts.values():
        p = count / length
        entropy -= p * math.log2(p)

    return round(entropy, 4)


def calculate_amount_zscore(
    amount: float, mean_amount: float, std_amount: float, epsilon: float = 1e-5
) -> float:
    """
    Normalizes transaction amount against payer historical baseline spending profile.
    """
    std_safe = max(std_amount, epsilon)
    z_score = (amount - mean_amount) / std_safe
    return round(z_score, 4)


class FeatureEngineeringPipeline:
    """
    Orchestrates full feature extraction from raw transaction payloads,
    enriching with rolling cache velocity metrics and spatial calculations.
    """

    def __init__(self, cache: StateCacheInterface):
        self.cache = cache

    def extract_features(
        self, raw_tx: Dict[str, Any]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Converts raw transaction dictionary into an ordered 16-element numpy vector
        and an unscaled feature dictionary.
        """
        payer_id = raw_tx["payer_id"]
        payer_hash = hash_sensitive_identifier(payer_id)
        timestamp_ms = int(raw_tx["timestamp"])
        amount = float(raw_tx["amount"])

        # Spatial Haversine Distance
        haversine_dist = calculate_haversine_km(
            lat1=float(raw_tx["payer_latitude"]),
            lon1=float(raw_tx["payer_longitude"]),
            lat2=float(raw_tx["merchant_latitude"]),
            lon2=float(raw_tx["merchant_longitude"]),
        )

        # Shannon Entropy of QR Payload
        qr_entropy = calculate_shannon_entropy(str(raw_tx.get("qr_payload", "")))

        # Stateful Velocity Counters from Cache
        v5m, v1h, v24h = self.cache.get_velocities(payer_hash, timestamp_ms)
        velocity_ratio = round(v1h / (v24h + 1.0), 4)

        # Historical Amount Baseline Z-Score
        hist_mean, hist_std = self.cache.get_historical_stats(payer_hash)
        amount_zscore = calculate_amount_zscore(amount, hist_mean, hist_std)

        # Assemble Feature Dictionary
        features_dict: Dict[str, Any] = {
            "qr_type": int(raw_tx["qr_type"]),
            "qr_payload_entropy": float(qr_entropy),
            "amount": float(amount),
            "merchant_category_code": int(raw_tx["merchant_category_code"]),
            "payer_latitude": float(raw_tx["payer_latitude"]),
            "payer_longitude": float(raw_tx["payer_longitude"]),
            "merchant_latitude": float(raw_tx["merchant_latitude"]),
            "merchant_longitude": float(raw_tx["merchant_longitude"]),
            "haversine_distance_km": float(haversine_dist),
            "device_trust_score": float(raw_tx["device_trust_score"]),
            "scan_to_pay_latency_ms": int(raw_tx["scan_to_pay_latency_ms"]),
            "failed_pin_attempts": int(raw_tx.get("failed_pin_attempts", 0)),
            "velocity_5m": float(v5m),
            "velocity_1h": float(v1h),
            "velocity_ratio": float(velocity_ratio),
            "amount_zscore": float(amount_zscore),
        }

        # Construct Ordered Vector
        feature_vector = np.array(
            [features_dict[col] for col in FEATURE_COLUMNS], dtype=np.float32
        ).reshape(1, -1)

        return feature_vector, features_dict

