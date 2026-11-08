# Project Overview

The Advanced Quick Response (QR) Code Payment Fraud Detection System is a high-throughput, low-latency machine learning framework designed to detect and intercept fraudulent financial transactions within digital and contactless payment infrastructures. As peer-to-peer (P2P) and point-of-sale (POS) QR payment adoption accelerates, existing static, rule-based fraud detection mechanisms fail to counter non-linear, multi-layered fraud vectors such as QR payload tampering, dynamic QR injection, malicious merchant redirection, rapid velocity scanning, and credential hijacking. These legacy systems suffer from prohibitive false-positive rates and delayed post-facto audit workflows.

This project delivers an autonomous, end-to-end predictive defense engine that processes real-time transaction streams, extracts specialized spatial-temporal and QR payload features, handles acute class imbalance, and executes hybrid inference (combining supervised classification and unsupervised anomaly detection). Operating at sub-100ms inference latency, the system incorporates Explainable AI (XAI) for real-time auditability, cryptographic ledger-based tamper-evident logging, and federated learning architectural abstractions for financial privacy compliance.

---

# System Architecture & Data Flow

The system processes transaction payloads from point of presentation to final risk authorization through a serialized, fail-safe pipeline:

```
[ QR Code Scan / Payment Client ]
               │
               ▼ (Raw JSON Transaction Payload)
┌────────────────────────────────────────────────────────┐
│ 1. Ingestion & Validation Gateway (FastAPI)            │
│    - Schema validation via Pydantic v2                 │
│    - Timestamp, signature & cryptographic hash check   │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────┐
│ 2. Feature Extraction & State Pipeline                 │
│    - QR context analysis (Static vs Dynamic, URL/ID)   │
│    - In-memory state lookup (Velocity, 1h/24h totals)  │
│    - Spatial delta computation (Haversine distance)    │
│    - Online scaler transformation                      │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────┐
│ 3. Hybrid ML Inference Engine                          │
│    ├─ Supervised Model (LightGBM / Random Forest / NN) │ ──> P(Fraud)
│    └─ Unsupervised Model (Isolation Forest / Autoenc.) │ ──> Anomaly Score
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────┐
│ 4. Decision & Gating Module                            │
│    - Weighted risk aggregation: S_composite            │
│    - Multi-tier classification:                        │
│        • Low Risk (< 0.30): APPROVE                    │
│        • Medium Risk (0.30 - 0.70): CHALLENGE / 2FA    │
│        • High Risk (> 0.70): BLOCK                     │
└──────────────────────┬─────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
┌───────────────────┐       ┌────────────────────────────┐
│ 5. XAI Explainer  │       │ 6. Audit & Storage Service │
│    - SHAP values  │       │    - Hash-chained Ledger   │
│    - Top features │       │    - SQLite/PostgreSQL Log │
└────────┬──────────┘       └────────────┬───────────────┘
         │                               │
         └─────────────┬─────────────────┘
                       ▼
[ Client Response: Status, Risk Score, Reason Codes ]
```

### Detailed Pipeline Flow:
1. **Payload Ingestion**: The client application (POS or consumer wallet) submits a JSON payload containing transaction parameters, payer metadata, and decoded QR payload strings.
2. **Preprocessing & Feature Augmentation**: The transaction is validated, normalized, and augmented with stateful rolling velocity counters (e.g., number of scans within the last 5 minutes, 1 hour, and 24 hours) and spatial displacement calculations.
3. **Dual-Model Inference**:
   - The primary supervised classifier calculates the probability of known fraudulent patterns: $P(\text{Fraud} \mid X)$.
   - The unsupervised anomaly detector evaluates deviation from normative baseline behavior: $A(X) \in [0, 1]$.
4. **Risk Arbitration**: The scores are blended into a composite index $S_{\text{composite}}$ using calibrated decision thresholds.
5. **Explainability Generation**: For transactions flagged as Medium or High Risk, local SHAP attributions are generated to provide human-readable reason codes for regulatory compliance.
6. **Immutable Ledger Logging**: The transaction record, prediction score, and SHA-256 state hash are committed to an append-only cryptographic ledger.

---

# Technical Stack & Dependencies

| Layer | Component / Technology | Specification & Version | Justification |
| :--- | :--- | :--- | :--- |
| **Language** | Python | `>= 3.10, < 3.12` | Strong ecosystem for ML/DL, asynchronous API support, and production runtime stability. |
| **Data Processing** | NumPy & Pandas | `numpy >= 1.24.0`, `pandas >= 2.0.0` | Matrix operations, rolling window transformations, and dataset curation. |
| **Imbalance Handling** | Imbalanced-Learn | `imbalanced-learn >= 0.11.0` | Implementation of SMOTE, Borderline-SMOTE, and ADASYN oversampling. |
| **Supervised ML** | LightGBM & Scikit-Learn | `lightgbm >= 4.1.0`, `scikit-learn >= 1.3.0` | Fast gradient boosted trees and benchmark ensembles (Random Forest, SVM, Logistic Regression). |
| **Deep Learning** | PyTorch | `torch >= 2.1.0` (CPU/CUDA) | Deep Neural Network (MLP / Tabular ResNet / Autoencoder architectures). |
| **Anomaly Detection** | PyOD / Scikit-Learn | `pyod >= 1.1.0`, `scikit-learn` | Isolation Forest, Local Outlier Factor (LOF), and One-Class SVM for zero-day fraud. |
| **Explainability (XAI)** | SHAP & LIME | `shap >= 0.43.0`, `lime >= 0.2.0` | TreeExplainer for instantaneous feature importance attribution. |
| **Serving API** | FastAPI & Uvicorn | `fastapi >= 0.104.0`, `uvicorn >= 0.24.0` | Asynchronous, OpenAPI-compliant microservice with sub-10ms overhead. |
| **Validation** | Pydantic | `pydantic >= 2.5.0` | Strict type enforcement and deserialization of incoming transaction payloads. |
| **State & In-Memory Store** | Redis / In-Memory Mock | `redis >= 5.0.0` or local TTL cache | Real-time sliding window aggregation (velocity checks, rapid successive scans). |
| **Relational Storage** | SQLite / SQLAlchemy | `SQLAlchemy >= 2.0.0` | Transaction logs, historical benchmarks, and audit trail storage. |
| **Dashboard & UI** | Streamlit | `streamlit >= 1.28.0` | Real-time transaction simulation, fraud telemetry, and XAI visual analytics. |

### Runtime & Hardware Constraints:
- **Execution Mode**: Online real-time inference (REST endpoint) with asynchronous background logging; offline batch capability for training/benchmarking.
- **Inference Latency Budget**: $\le 100\text{ ms}$ total round-trip time (Pre-processing: $< 15\text{ ms}$, Model Inference: $< 35\text{ ms}$, XAI calculation: $< 40\text{ ms}$, Storage: $< 10\text{ ms}$).
- **Memory Footprint**: Designed to run efficiently within a 4 GB RAM container (CPU-only capable) without GPU dependency during inference.

---

# Data Specifications

### Transaction Schema

The system ingests and processes structured transaction vectors represented by the following schema:

| Field Name | Type | Range / Format | Description |
| :--- | :--- | :--- | :--- |
| `transaction_id` | String | UUIDv4 | Unique transaction reference. |
| `timestamp` | Integer | Epoch milliseconds | Time of transaction initialization. |
| `payer_id` | String | Alphanumeric (16 chars) | Unique identifier for paying customer account. |
| `merchant_id` | String | Alphanumeric (16 chars) | Registered identifier of the receiving merchant. |
| `qr_type` | Integer | `0` (Static), `1` (Dynamic) | QR operational paradigm; static codes carry higher physical spoof risk. |
| `qr_payload_entropy` | Float | `0.0 - 8.0` | Shannon entropy of raw QR content string; detects obfuscated/malicious URLs. |
| `amount` | Float | `> 0.00` | Transaction monetary value in standard currency units. |
| `merchant_category_code` | Integer | `1000 - 9999` (ISO 18245) | Merchant classification sector (e.g., retail, dining, transfer). |
| `payer_latitude` | Float | `-90.0` to `+90.0` | Geolocation latitude coordinate of payer mobile device. |
| `payer_longitude` | Float | `-180.0` to `+180.0` | Geolocation longitude coordinate of payer mobile device. |
| `merchant_latitude` | Float | `-90.0` to `+90.0` | Registered latitude coordinate of merchant POS terminal. |
| `merchant_longitude` | Float | `-180.0` to `+180.0` | Registered longitude coordinate of merchant POS terminal. |
| `device_trust_score` | Float | `0.0 - 1.0` | Hardware fingerprint integrity score (jailbreak, emulator, rooted status). |
| `scan_to_pay_latency_ms` | Integer | `0 - 600000` | Elapsed duration between optical QR code scan and payment submit. |
| `failed_pin_attempts` | Integer | `0 - 5` | Number of incorrect authorization attempts preceding submission. |
| `is_fraud` | Integer | `0` (Legitimate), `1` (Fraudulent) | Binary ground truth label (used during training/evaluation). |

### Mathematical Transformations & Feature Engineering

1. **Spatial Displacement (Haversine Distance)**:
   Measures geographic distance ($d$) between payer device and merchant terminal:
   $$\Delta\phi = \phi_{\text{merchant}} - \phi_{\text{payer}}, \quad \Delta\lambda = \lambda_{\text{merchant}} - \lambda_{\text{payer}}$$
   $$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_{\text{payer}}) \cos(\phi_{\text{merchant}}) \sin^2\left(\frac{\Delta\lambda}{2}\right)$$
   $$d = 2 R \cdot \arcsin\left(\sqrt{a}\right) \quad \text{where } R = 6371\text{ km}$$

2. **Amount Z-Score Relative to Payer Baseline**:
   Normalizes transaction value against payer historical mean ($\mu_p$) and standard deviation ($\sigma_p$):
   $$Z_{\text{amount}} = \frac{\text{amount} - \mu_p}{\sigma_p + \epsilon}$$

3. **Temporal Velocity Features**:
   Rolling aggregate metrics computed over window durations $T \in \{5\text{ min}, 1\text{ hr}, 24\text{ hr}\}$:
   $$V_{T} = \sum_{i=1}^{N} \mathbb{I}(t_i \ge t_{\text{current}} - T)$$
   $$\text{Ratio}_{\text{velocity}} = \frac{V_{1\text{ hr}}}{V_{24\text{ hr}} + 1}$$

4. **Class Imbalance Resolution**:
   Given high imbalance ratio (fraud $\le 1\%$), training sets are synthesized using Synthetic Minority Over-sampling Technique (SMOTE):
   $$x_{\text{new}} = x_i + \lambda \cdot (x_{zi} - x_i), \quad \lambda \sim U(0, 1)$$
   where $x_i$ is a minority class instance and $x_{zi}$ is one of its $k$-nearest minority neighbors ($k=5$).

---

# Core Modules & Responsibilities

```
qr_fraud_detection/
├── config/
│   └── settings.py              # Environment variables, model paths, risk thresholds
├── data/
│   ├── generator.py             # Synthetic QR transaction generator with realistic fraud archetypes
│   ├── preprocessor.py          # Scaling, imputation, categorical encoding, and vector normalization
│   └── feature_engineering.py   # Haversine distance, velocities, entropy, and ratios
├── models/
│   ├── base.py                  # Abstract Base Class for classification models
│   ├── supervised.py            # LightGBM, Random Forest, SVM, MLP implementations
│   ├── unsupervised.py          # Isolation Forest & Autoencoder anomaly detectors
│   ├── ensemble.py              # Hybrid risk scoring aggregator and threshold calibrator
│   └── trainer.py               # Cross-validation, hyperparameter tuning, and SMOTE pipeline
├── xai/
│   └── explainer.py             # SHAP TreeExplainer & local attribution generator
├── ledger/
│   └── audit_chain.py           # Cryptographic hash-chained immutable audit log
├── api/
│   ├── schema.py                # Pydantic input/output contracts
│   ├── routes.py                # REST endpoints: /predict, /simulate, /metrics
│   └── server.py                # FastAPI application entrypoint
├── federation/
│   └── mock_federated.py        # Federated averaging (FedAvg) architectural simulation
└── ui/
    └── app.py                   # Streamlit live monitoring & interactive simulation dashboard
```

### Module Responsibilities:

- **`data.generator`**: Synthesizes structured datasets reflecting real-world QR vulnerabilities (e.g., sticker replacement attacks, fast-paced phishing redirect, man-in-the-middle dynamic amount modifications).
- **`data.feature_engineering`**: Converts raw transaction attributes into normalized tensor vectors, calculating spatial anomalies and behavioral velocity spikes.
- **`models.supervised`**: Trains and evaluates candidate models (Logistic Regression, Decision Trees, Random Forest, SVM, LightGBM, Deep MLP).
- **`models.unsupervised`**: Computes an anomaly isolation index to flag transactions that do not conform to known fraudulent or legitimate archetypes.
- **`models.ensemble`**: Computes composite risk score:
  $$S_{\text{composite}} = w_1 \cdot P_{\text{supervised}}(\text{Fraud}) + w_2 \cdot S_{\text{unsupervised}}(\text{Anomaly})$$
  Default parameters: $w_1 = 0.70$, $w_2 = 0.30$.
- **`xai.explainer`**: Calculates Shapley feature contributions ($f(x) = \phi_0 + \sum_{j=1}^{M} \phi_j$) for high-risk flags, returning top-3 explanatory drivers (e.g., `["AmountDeviation > 3.8 sigma", "GeoDistance > 450 km", "ScanLatency < 800 ms"]`).
- **`ledger.audit_chain`**: Computes SHA-256 block hash chaining:
  $$H_k = \text{SHA256}(H_{k-1} \,\|\, \text{TxID}_k \,\|\, S_{\text{composite}} \,\|\, \text{Decision}_k \,\|\, \text{Timestamp}_k)$$
  Guarantees non-repudiation and auditability for financial regulatory compliance.
- **`federation.mock_federated`**: Demonstrates privacy-preserving multi-institution training using Federated Averaging (FedAvg):
  $$W_{t+1} = \sum_{k=1}^{K} \frac{n_k}{n} W_{t+1}^k$$

---

# Functional & Non-Functional Requirements

### Functional Requirements (FR)

- **FR-01: Multi-Vector Ingestion**: System must accept structured JSON payloads encompassing transaction details, QR metadata, payer state, and device telemetry.
- **FR-02: Real-Time Fraud Classification**: System must evaluate incoming transactions and assign an actionable verdict:
  - `APPROVE` ($S_{\text{composite}} < 0.30$)
  - `CHALLENGE_MFA` ($0.30 \le S_{\text{composite}} \le 0.70$)
  - `BLOCK` ($S_{\text{composite}} > 0.70$)
- **FR-03: Anomaly Fallback Detection**: If supervised probability is ambiguous ($0.25 - 0.45$), an anomaly score exceeding $0.80$ must escalate the verdict to `CHALLENGE_MFA`.
- **FR-04: Automated Explainability**: Every flagged or rejected transaction must be annotated with local SHAP feature attributions indicating the root reason for intervention.
- **FR-05: Immutable Audit Chaining**: Every inference verdict must be appended to the local cryptographic hash ledger with parent block linking.
- **FR-06: Batch Evaluation & Benchmarking**: System CLI must provide automated training and benchmarking across all implemented algorithms, outputting comparative performance tables.

### Non-Functional Requirements (NFR)

- **NFR-01: Latency Threshold**: Single transaction end-to-end inference (including preprocessing and scoring) must execute in $\le 100\text{ ms}$ on standard x86 CPU hardware.
- **NFR-02: Throughput Capacity**: System must sustain at least $200\text{ requests/second}$ under concurrent stress testing without memory leaks.
- **NFR-03: High Fraud Recall**: The target operational model must achieve $\ge 95.0\%$ recall on fraudulent transactions while capping False Positive Rate (FPR) at $\le 1.5\%$.
- **NFR-04: Deterministic Fallback**: In the event of model failure or timeout ($> 120\text{ ms}$), the system must degrade safely to a baseline heuristic rule set (e.g., velocity check + amount cap) rather than dropping transactions.
- **NFR-05: Privacy & Zero PII Leakage**: Plaintext PII (account numbers, names) must never enter feature tensors or persistent logs; all identifiers must be salted and hashed.

---

# Evaluation & Validation Metrics

The system performance is evaluated across classification fidelity, economic cost mitigation, and computational efficiency:

### 1. Classification Metrics

- **Recall (Sensitivity / Detection Rate)**:
  $$\text{Recall} = \frac{TP}{TP + FN}$$
  *Target*: $\ge 0.95$ (ensures minimal undetected fraud).

- **Precision (Positive Predictive Value)**:
  $$\text{Precision} = \frac{TP}{TP + FP}$$
  *Target*: $\ge 0.90$ (prevents consumer friction due to erroneous blocks).

- **F1-Score & F2-Score**:
  $$F_\beta = (1 + \beta^2) \frac{\text{Precision} \cdot \text{Recall}}{(\beta^2 \cdot \text{Precision}) + \text{Recall}}$$
  $F_2$ is prioritized ($\beta = 2$) to weight Recall higher than Precision in financial fraud detection.

- **Precision-Recall Area Under Curve (PR-AUC)**:
  Preferred over standard ROC-AUC due to acute class imbalance ($< 1\%$ fraud rate).

### 2. Financial Cost Optimization Metric

To mirror production commercial viability, models are scored against an asymmetric financial utility function:
$$\text{Total Cost} = C_{\text{fraud}} \cdot FN + C_{\text{friction}} \cdot FP + C_{\text{review}} \cdot (\text{Challenged Cases})$$
Where:
- $C_{\text{fraud}} = \text{Average fraud monetary loss}$ (highest weight, e.g., \$150.00).
- $C_{\text{friction}} = \text{Customer churn / dissatisfaction cost per false flag}$ (e.g., \$5.00).
- $C_{\text{review}} = \text{Operational MFA / manual inspection overhead}$ (e.g., \$0.50).

### 3. Computational Benchmark Metrics

| Metric | Target Specification |
| :--- | :--- |
| **Inference Latency (p50)** | $< 35\text{ ms}$ |
| **Inference Latency (p95)** | $< 75\text{ ms}$ |
| **Inference Latency (p99)** | $< 100\text{ ms}$ |
| **Model In-Memory Footprint** | $< 250\text{ MB}$ |
| **SMOTE Preprocessing Speed** | $> 10,000\text{ records/sec}$ |

