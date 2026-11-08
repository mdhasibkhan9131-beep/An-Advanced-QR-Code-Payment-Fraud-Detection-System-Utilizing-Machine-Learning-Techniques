# High-Level Architecture Design (HLD)

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 05)  
**Author:** Principal Software Architect  
**Parent Document:** `docs/02_Requirements/SRS.md` | `docs/04_Technical_Research/TECHNICAL_RECOMMENDATIONS.md`

---

## 1. Architectural Paradigm & System Overview

The system implements a **High-Throughput, Low-Latency Layered Pipeline Architecture** organized into asynchronous, decoupled micro-components. The architecture is engineered to evaluate incoming payment transaction payloads in real time ($\le 100\text{ ms}$ round-trip), extract specialized spatial-temporal features, synthesize risk across supervised and unsupervised machine learning models, generate human-interpretable explanations, and enforce mathematical non-repudiation via an append-only cryptographic ledger.

```mermaid
graph TD
    subgraph ClientLayer["Client & Ingestion Tier"]
        ClientApp["Mobile Wallet / POS Scanner"]
        FastAPIGateway["FastAPI Gateway (/api/v1/predict)"]
        PydanticValidator["Pydantic v2 Schema & Boundary Validator"]
    end

    subgraph StateAndFeatures["Feature Engineering & State Tier"]
        SaltPII["PII Salted Hash (SHA-256)"]
        GeoEngine["Haversine Spatial Distance Calculator"]
        EntropyEngine["Shannon Entropy Analyzer"]
        VelocityEngine["Stateful Velocity Engine (5m, 1h, 24h)"]
        InMemoryCache[("Thread-Safe In-Memory TTL Cache / Redis")]
        ScalerEngine["RobustScaler Online Normalizer"]
    end

    subgraph ModelEngine["Dual-Model Hybrid Inference Tier"]
        SupervisedModel["Supervised Classifier (LightGBM Engine)"]
        AnomalyModel["Unsupervised Anomaly Detector (Isolation Forest)"]
        HybridEnsemble["Calibrated Ensemble Fusion (S_comp = 0.70*P + 0.30*A)"]
        DecisionGating["3-Tier Policy Gating (Approve / Challenge / Block)"]
        FallbackEngine["Heuristic Fallback Circuit Breaker (Timeout > 120ms)"]
    end

    subgraph GovernanceTier["Explainability & Governance Tier"]
        SHAPEngine["SHAP TreeExplainer (Local Attributions)"]
        ReasonCodes["Human-Readable Reason Code Generator"]
        AuditLedger["Cryptographic Audit Ledger (SHA-256 Chained)"]
        SQLiteDB[("SQLite WAL Persistent Store")]
    end

    subgraph PresentationTier["Presentation & Monitoring Tier"]
        StreamlitUI["Streamlit Real-Time Monitoring Dashboard"]
        Simulator["Interactive Fraud Vector Simulator"]
        FedSim["Federated Learning (FedAvg) Research Module"]
    end

    ClientApp -->|HTTP POST JSON Payload| FastAPIGateway
    FastAPIGateway --> PydanticValidator
    PydanticValidator --> SaltPII
    SaltPII --> GeoEngine
    SaltPII --> EntropyEngine
    SaltPII --> VelocityEngine
    VelocityEngine <-->|Read / Write Rolling Counters| InMemoryCache
    GeoEngine & EntropyEngine & VelocityEngine --> ScalerEngine

    ScalerEngine -->|Feature Vector X| SupervisedModel
    ScalerEngine -->|Feature Vector X| AnomalyModel
    SupervisedModel -->|P_fraud| HybridEnsemble
    AnomalyModel -->|S_anomaly| HybridEnsemble
    HybridEnsemble --> DecisionGating

    FastAPIGateway -.->|Async Timeout Interceptor| FallbackEngine
    FallbackEngine -.->|Fallback Verdict| DecisionGating

    DecisionGating -->|If Challenge or Block| SHAPEngine
    SHAPEngine --> ReasonCodes
    DecisionGating -->|All Decisions & Vectors| AuditLedger
    AuditLedger --> SQLiteDB

    SQLiteDB -.-> StreamlitUI
    Simulator -.->|Simulated Payloads| FastAPIGateway
    SQLiteDB -.-> FedSim

    DecisionGating -->|JSON Verdict + Reason Codes| FastAPIGateway
    FastAPIGateway -->|HTTP 200 Response <= 100ms| ClientApp
```

---

## 2. Subsystem Decomposition & Component Responsibilities

```mermaid
graph LR
    subgraph APISubsystem["Subsystem: api"]
        direction TB
        Server["api.server\n(FastAPI / Uvicorn)"]
        Routes["api.routes\n(REST Handlers)"]
        Schema["api.schema\n(Pydantic Contracts)"]
        Fallback["api.fallback\n(Heuristic Circuit Breaker)"]
    end

    subgraph DataSubsystem["Subsystem: data"]
        direction TB
        Generator["data.generator\n(Synthetic QR Stream)"]
        FeatureEng["data.feature_engineering\n(Haversine & Entropy)"]
        Preprocessor["data.preprocessor\n(Scaling & Masking)"]
    end

    subgraph CacheSubsystem["Subsystem: cache"]
        direction TB
        CacheInterface["cache.base\n(StateCache ABC)"]
        MemCache["cache.memory\n(Thread-Safe TTL)"]
        RedisCache["cache.redis\n(Redis Adapter)"]
    end

    subgraph ModelSubsystem["Subsystem: models"]
        direction TB
        ModelBase["models.base\n(Classifier ABC)"]
        LightGBMMod["models.supervised\n(LightGBM / RF / MLP)"]
        IsoForest["models.unsupervised\n(Isolation Forest)"]
        Ensemble["models.ensemble\n(Hybrid Gating)"]
        Trainer["models.trainer\n(SMOTE & CV)"]
    end

    subgraph XAISubsystem["Subsystem: xai"]
        direction TB
        Explainer["xai.explainer\n(SHAP TreeExplainer)"]
    end

    subgraph LedgerSubsystem["Subsystem: ledger"]
        direction TB
        AuditChain["ledger.audit_chain\n(SHA-256 Chained Blocks)"]
        DBStore["database.session\n(SQLAlchemy / SQLite)"]
    end

    subgraph UISubsystem["Subsystem: ui"]
        direction TB
        Dashboard["ui.app\n(Streamlit Dashboard)"]
        SimView["ui.simulator\n(Interactive Vector Sliders)"]
    end

    Routes --> Schema
    Routes --> Fallback
    Routes --> FeatureEng
    FeatureEng --> Preprocessor
    FeatureEng --> CacheInterface
    CacheInterface --> MemCache
    CacheInterface --> RedisCache

    Routes --> Ensemble
    Ensemble --> LightGBMMod
    Ensemble --> IsoForest
    LightGBMMod --> ModelBase
    Trainer --> Generator
    Trainer --> LightGBMMod

    Routes --> Explainer
    Routes --> AuditChain
    AuditChain --> DBStore
    Dashboard --> Routes
    SimView --> Routes
```

### 2.1 Subsystem 1: Ingestion & Validation Gateway (`api`)
- **Protocol:** HTTP/REST JSON over asynchronous ASGI (Uvicorn).
- **Core Function:** Enforces strict boundary verification via Pydantic v2 models. Checks timestamp freshness ($\pm 300\text{s}$) and immediately masks/salts customer identifiers (`payer_id`) using SHA-256 before downstream propagation.
- **Circuit Breaker:** Manages an asynchronous timeout watchdog ($120\text{ ms}$). If ML models fail to respond in time, routes the request to the deterministic fallback engine.

### 2.2 Subsystem 2: Contextual Feature & State Pipeline (`data`, `cache`)
- **Spatial Engine:** Computes Haversine spherical distance ($d$) between payer device coordinates and merchant terminal location.
- **Payload Engine:** Computes Shannon entropy ($H(X)$) of decoded QR text strings to flag obfuscated phishing redirects.
- **Velocity Engine:** Interacts with `cache.memory` (or `cache.redis`) to retrieve and increment rolling scan frequencies ($V_{5\text{m}}, V_{1\text{h}}, V_{24\text{h}}$) and compute historical spending Z-scores.
- **Normalization:** Transforms features through pre-fitted `RobustScaler` transformation matrices.

### 2.3 Subsystem 3: Dual-Model Hybrid Inference Tier (`models`)
- **Supervised Classifier Ensemble:** LightGBM gradient-boosted decision tree outputs known fraud probability: $P_{\text{supervised}}(\text{Fraud} \mid X) \in [0, 1]$.
- **Unsupervised Anomaly Detector:** Isolation Forest computes structural deviation score: $S_{\text{anomaly}}(X) \in [0, 1]$.
- **Hybrid Fusion Engine:** Combines scores into composite risk index $S_{\text{composite}} = 0.70 P_{\text{sup}} + 0.30 S_{\text{unsup}}$ and applies the three-tier decision gating policy (`APPROVE`, `CHALLENGE_MFA`, `BLOCK`) with zero-day anomaly escalation.

### 2.4 Subsystem 4: Explainability & Governance Tier (`xai`, `ledger`)
- **XAI Explainer:** Executes SHAP TreeExplainer local attribution for transactions resulting in `CHALLENGE_MFA` or `BLOCK`, extracting top-3 human-readable reason codes (bypassed for low-risk approvals).
- **Cryptographic Audit Ledger:** Computes SHA-256 block digest chaining linking transaction metadata to the preceding block hash ($H_k = \text{SHA256}(H_{k-1} \,\|\, \dots)$), persisting to SQLite with Write-Ahead Logging (WAL).

### 2.5 Subsystem 5: Presentation & Research Simulation Tier (`ui`, `research`)
- **Streamlit Dashboard:** Displays real-time transaction telemetry, risk dials, historical audit tables, and visual SHAP waterfall plots.
- **Fraud Simulator:** Interactive parameter sliders to simulate Quishing, MITM, and velocity attacks.
- **Federated Simulation:** Demonstrates multi-institutional model aggregation via FedAvg.

---

## 3. High-Level Inter-Module Interface Contracts

```
[ Client JSON ] ──> [ api.schema.TransactionRequest ]
                          │
                          ▼
                    [ data.feature_engineering.ExtractedFeatures ]
                          │
                          ▼
                    [ numpy.ndarray X (Normalized Vector, Shape: (1, 16)) ]
                          │
                          ├───────────────┬───────────────┐
                          ▼                               ▼
     [ LightGBM.predict_proba ]             [ IsolationForest.score_samples ]
                          │                               │
                          ▼                               ▼
                 [ float P_fraud ]               [ float S_anomaly ]
                          │                               │
                          └───────────────┬───────────────┘
                                          ▼
                         [ models.ensemble.DecisionResult ]
                           ├── composite_score: float
                           ├── verdict: DecisionVerdictEnum
                           └── reason_codes: List[str]
                                          │
                                          ▼
                         [ api.schema.TransactionResponse ]
```

---

## 4. Performance, Scalability & Availability Architecture

1. **Sub-100ms Latency Enforcement:**
   - Pre-compiled model weights loaded into memory on server startup (zero cold-start lag per request).
   - In-memory thread-safe state cache ensures velocity lookup overhead is $< 0.5\text{ ms}$.
   - Selective synchronous SHAP calculation ensures $> 95\%$ of transactions (`APPROVE`) execute in $< 50\text{ ms}$.
2. **High Availability via Heuristic Fallback:**
   - In the event of thread lock or timeout ($> 120\text{ ms}$), the system engages a deterministic heuristic fallback (amount cap + velocity check) within $10\text{ ms}$, ensuring checkout lanes never stall.
3. **Storage Concurrency via SQLite WAL:**
   - The SQLite database operates with `PRAGMA journal_mode=WAL` (Write-Ahead Logging), allowing concurrent reader connections from the Streamlit UI without locking incoming transaction ledger writes.

