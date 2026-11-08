# Low-Level Software Design (LLD)

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 05)  
**Parent Document:** `docs/05_System_Design/HIGH_LEVEL_DESIGN.md`  
**Reference Standards:** PEP 8, PEP 484, Gang of Four (GoF) Design Patterns

---

## 1. Class Hierarchy & Interface Specifications

### 1.1 Machine Learning Base Interfaces (`backend/models/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
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
        pass

    @abstractmethod
    def load(self, filepath: str) -> "BaseAnomalyDetector":
        pass
```

---

### 1.2 Concrete Model Implementations (`backend/models/supervised.py`, `unsupervised.py`)

- **`LightGBMClassifierWrapper(BaseClassifier)`**:
  - Encapsulates `lightgbm.LGBMClassifier`.
  - Hyperparameters: `n_estimators=100`, `learning_rate=0.05`, `num_leaves=31`, `scale_pos_weight=12.5`, `n_jobs=4`.
  - Provides direct access to the underlying `booster_` object required by SHAP TreeExplainer.
- **`RandomForestWrapper(BaseClassifier)`**:
  - Encapsulates `sklearn.ensemble.RandomForestClassifier(n_estimators=100, class_weight='balanced')`.
- **`PyTorchMLPWrapper(BaseClassifier)`**:
  - Implements a 3-layer tabular Multi-Layer Perceptron in PyTorch (`Linear(16, 64) -> ReLU -> BatchNorm -> Dropout(0.2) -> Linear(64, 32) -> ReLU -> Linear(32, 2) -> Softmax`).
  - Executes exclusively on CPU device tensors.
- **`IsolationForestDetector(BaseAnomalyDetector)`**:
  - Encapsulates `sklearn.ensemble.IsolationForest(n_estimators=100, contamination=0.01, random_state=42)`.
  - Converts raw `decision_function` outputs to a normalized $[0, 1]$ interval via min-max calibration.

---

### 1.3 State Caching Architecture (`backend/cache/base.py`, `memory.py`, `redis_adapter.py`)

```python
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict
import time

class StateCacheInterface(ABC):
    """Abstract interface for sliding window frequency and velocity lookups."""

    @abstractmethod
    def record_transaction(self, payer_hash: str, timestamp_ms: int, amount: float) -> None:
        """Record transaction timestamp and amount for sliding window tracking."""
        pass

    @abstractmethod
    def get_velocities(self, payer_hash: str, current_time_ms: int) -> Tuple[int, int, int]:
        """Return rolling transaction counts for (5min, 1hour, 24hour) windows."""
        pass

    @abstractmethod
    def get_historical_stats(self, payer_hash: str) -> Tuple[float, float]:
        """Return (mean_amount, std_amount) for payer historical baseline."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Reset cache state (primarily for test isolation)."""
        pass
```

- **`InMemoryTTLCache(StateCacheInterface)`**:
  - Thread-safe implementation utilizing Python's `threading.Lock` and collections `deque`.
  - Stores sliding records in a dictionary indexed by `payer_hash`.
  - Evicts entries older than 24 hours automatically on lookup.
- **`RedisCacheAdapter(StateCacheInterface)`**:
  - Connects to Redis via `redis.asyncio.Redis` utilizing sorted sets (`ZADD`, `ZREMRANGEBYSCORE`, `ZCARD`) for cluster deployments.

---

### 1.4 Feature Engineering Engine (`backend/data/feature_engineering.py`)

```python
class FeatureEngineeringPipeline:
    """Transforms raw transaction dictionaries into normalized numerical feature vectors."""

    def __init__(self, cache: StateCacheInterface, scaler_path: str):
        self.cache = cache
        self.scaler = self._load_scaler(scaler_path)

    @staticmethod
    def calculate_haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate spatial distance in kilometers between two GPS coordinates."""
        pass

    @staticmethod
    def calculate_shannon_entropy(payload_str: str) -> float:
        """Calculate Shannon entropy in bits per character for decoded QR payload."""
        pass

    def transform(self, raw_tx: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Extracts Haversine distance, QR entropy, stateful velocities, Z-scores,
        applies RobustScaler, and returns (normalized_vector, unscaled_features_dict).
        """
        pass
```

---

### 1.5 Hybrid Risk Ensemble & Gating (`backend/models/ensemble.py`)

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class DecisionVerdict(str, Enum):
    APPROVE = "APPROVE"
    CHALLENGE_MFA = "CHALLENGE_MFA"
    BLOCK = "BLOCK"

@dataclass
class HybridScoringResult:
    supervised_prob: float
    anomaly_score: float
    composite_score: float
    verdict: DecisionVerdict
    is_zero_day_escalation: bool
    reason_codes: List[str]
    is_fallback: bool = False

class HybridRiskEnsemble:
    def __init__(self, weight_supervised: float = 0.70, weight_anomaly: float = 0.30):
        self.w1 = weight_supervised
        self.w2 = weight_anomaly

    def compute_composite_score(self, p_sup: float, s_anomaly: float) -> float:
        return float(self.w1 * p_sup + self.w2 * s_anomaly)

    def arbitrate(self, p_sup: float, s_anomaly: float) -> Tuple[DecisionVerdict, bool]:
        composite = self.compute_composite_score(p_sup, s_anomaly)

        # Zero-Day Anomaly Escalation Override
        if 0.25 <= p_sup <= 0.45 and s_anomaly > 0.80:
            return DecisionVerdict.CHALLENGE_MFA, True

        if composite < 0.30:
            return DecisionVerdict.APPROVE, False
        elif composite <= 0.70:
            return DecisionVerdict.CHALLENGE_MFA, False
        else:
            return DecisionVerdict.BLOCK, False
```

---

### 1.6 Explainable AI Module (`backend/xai/explainer.py`)

```python
import shap
import numpy as np
from typing import List, Tuple

class SHAPExplainerService:
    """Manages pre-computed TreeExplainer and extracts standardized human-readable reason codes."""

    def __init__(self, lgbm_model, background_data: np.ndarray, feature_names: List[str]):
        self.explainer = shap.TreeExplainer(lgbm_model, data=background_data)
        self.feature_names = feature_names

    def get_top_reasons(self, feature_vector: np.ndarray, top_k: int = 3) -> List[str]:
        """
        Computes local Shapley values for vector and formats top positive drivers
        into standardized strings (e.g., 'AmountDeviation (+0.38)').
        """
        pass
```

---

### 1.7 Cryptographic Ledger & Audit Chain (`backend/ledger/audit_chain.py`)

```python
import hashlib
from typing import Optional, Dict, Any

class CryptographicLedgerService:
    """Maintains sequential SHA-256 block hash chaining for auditability."""

    GENESIS_HASH: str = "0" * 64

    def compute_block_hash(self, prev_hash: str, tx_id: str, score: float, verdict: str, timestamp_ms: int) -> str:
        payload = f"{prev_hash}|{tx_id}|{score:.4f}|{verdict}|{timestamp_ms}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def append_record(self, db_session, tx_id: str, score: float, verdict: str, timestamp_ms: int, reasons: str) -> str:
        """Fetches last block hash, computes new block hash, and commits to SQLite."""
        pass

    def verify_integrity(self, db_session) -> Tuple[bool, int, Optional[str]]:
        """
        Sequentially iterates through ledger records, recalculating expected hashes.
        Returns (is_valid, total_blocks_checked, first_corrupted_tx_id).
        """
        pass
```

---

## 2. Directory Tree & Concrete Module Mapping

```
advanced-qr-code-payment-fraud-detection-system/
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Pydantic BaseSettings, environment variables
│   ├── api/
│   │   ├── __init__.py
│   │   ├── server.py            # FastAPI app initialization, middleware, routes
│   │   ├── routes.py            # /predict, /batch-predict, /explain, /metrics, /health
│   │   ├── schema.py            # Pydantic v2 Ingestion and Response schemas
│   │   └── fallback.py          # Deterministic Heuristic Fallback Circuit Breaker
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── base.py              # StateCacheInterface ABC
│   │   ├── memory.py            # Thread-safe in-memory sliding window cache
│   │   └── redis_adapter.py     # Optional Redis client adapter
│   ├── data/
│   │   ├── __init__.py
│   │   ├── generator.py         # Synthetic QR transaction generator (Realistic vectors)
│   │   ├── feature_engineering.py # Haversine, Shannon entropy, Z-scores
│   │   └── preprocessor.py      # Masking, scaling, SMOTE balance pipeline
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py              # BaseClassifier, BaseAnomalyDetector ABCs
│   │   ├── supervised.py        # LightGBM, Random Forest, SVM, PyTorch MLP
│   │   ├── unsupervised.py      # Isolation Forest anomaly detector
│   │   ├── ensemble.py          # HybridRiskEnsemble fusion & 3-tier gating
│   │   └── trainer.py           # Training orchestration, cross-validation, evaluation
│   ├── xai/
│   │   ├── __init__.py
│   │   └── explainer.py         # SHAP TreeExplainer & reason code generator
│   ├── ledger/
│   │   ├── __init__.py
│   │   └── audit_chain.py       # SHA-256 block-chained ledger manager
│   └── database/
│       ├── __init__.py
│       ├── session.py           # SQLAlchemy engine, session maker, WAL pragmas
│       └── models.py            # ORM tables: TransactionRecord, LedgerBlock, AuditEvent
├── frontend/
│   ├── app.py                   # Streamlit live telemetry & simulator dashboard
│   └── components/              # Gauges, transaction table, SHAP charts
├── research/
│   ├── federation/              # Federated Learning (FedAvg) simulation
│   └── benchmarks/              # Jupyter notebooks / exploratory scripts
├── tests/                       # Unit, integration, latency benchmarks
└── scripts/                     # Standalone CLI tools for training and evaluation
```

