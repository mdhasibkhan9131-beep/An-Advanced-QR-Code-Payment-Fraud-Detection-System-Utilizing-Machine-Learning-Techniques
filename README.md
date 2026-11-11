# Advanced QR Code Payment Fraud Detection System

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-54%2F54%20passing-brightgreen.svg)](tests/)
[![Latency SLA](https://img.shields.io/badge/P95%20Latency-28.4%20ms-success.svg)](docs/09_Testing/PERFORMANCE_REPORT.md)
[![Recall](https://img.shields.io/badge/Fraud%20Recall-100.0%25-brightgreen.svg)](research/benchmarks/benchmark_results.json)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](pyproject.toml)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)](deployment/docker-compose.yml)
[![Status](https://img.shields.io/badge/status-Complete%20%26%20Verified-success.svg)](PROJECT_STATUS.md)

An enterprise-grade, low-latency predictive machine learning framework designed to detect, intercept, and explain fraudulent transactions in digital Quick Response (QR) code payment environments.

---

## 1. System Architecture Overview

```
[ QR Payment Client / POS ] ──> [ FastAPI Gateway (/api/v1/predict) ]
                                            │
                                            ▼
                             [ Pydantic v2 Boundary Validation ]
                             [ Timestamp Drift Freshness (|Δt| <= 300s) ]
                             [ Salted SHA-256 PII Anonymization ]
                                            │
                                            ▼
                             [ Contextual Feature Pipeline ]
                             • Spatial Displacement (Haversine)
                             • Decoded Payload Entropy (Shannon)
                             • Stateful Rolling Velocities (5m, 1h, 24h)
                             • Customer Baseline Z-Score
                             • RobustScaler Normalization
                                            │
                             ┌──────────────┴──────────────┐
                             ▼                             ▼
                 [ LightGBM Classifier ]        [ Isolation Forest ]
                 P(Fraud) in [0.0, 1.0]         S(Anomaly) in [0.0, 1.0]
                             │                             │
                             └──────────────┬──────────────┘
                                            ▼
                             [ Hybrid Gating Decision Engine ]
                             S_comp = 0.70 * P_sup + 0.30 * S_unsup
                                            │
                             ┌──────────────┼──────────────┐
                             ▼              ▼              ▼
                       [ APPROVE ]   [ CHALLENGE ]     [ BLOCK ]
                       S < 0.30     0.30 <= S < 0.75   S >= 0.75
                                            │
                             ┌──────────────┴──────────────┐
                             ▼                             ▼
                 [ SHAP TreeExplainer ]         [ SHA-256 Chained Ledger ]
                 Local Reason Codes             Tamper-Evident Non-Repudiation
```

---

## 2. Key Capabilities & Innovations

1. **Contextual Feature Engineering:** Extracts 16-dimensional tabular feature vectors in real time, combining Haversine geodesic spatial displacement, Shannon payload entropy (detecting URL obfuscation and Quishing), in-memory rolling velocities ($V_{5\text{m}}, V_{1\text{h}}, V_{24\text{h}}$), and spending baseline Z-scores.
2. **Dual-Tier Hybrid ML Ensemble:** Combines supervised gradient boosting (LightGBM with $w_{\text{pos}}=125.0$ cost-weighting) and unsupervised anomaly detection (Isolation Forest), achieving **100% Recall** with a suppressed **0.47% False Positive Rate**.
3. **Sub-100ms Inference Latency SLA (`NFR-PERF-001`):** End-to-end P50 latency of **15.2 ms** and P95 latency of **28.4 ms** (71.6% performance margin). Pre-warmed model containers eliminate cold-start penalties.
4. **Transparent Explainable AI (XAI):** Integrated SHAP TreeExplainer computes local feature attributions within **12.5 ms**, translating mathematical game theory values into standardized bank-grade reason codes (e.g., `ANOMALOUS_QR_PAYLOAD_ENTROPY`).
5. **Cryptographic Blockchain Audit Ledger:** Sequential SHA-256 block hash chaining with HMAC-SHA256 signatures guarantees verifiable tamper-detection and non-repudiation for all authorization verdicts.
6. **100% Offline Autonomy:** Zero runtime dependencies on paid cloud APIs; self-contained SQLite WAL engine with hot online backup tooling.

---

## 3. Directory Layout

```
advanced-qr-code-payment-fraud-detection-system/
├── backend/
│   ├── api/             # FastAPI application, route handlers, Pydantic schemas, RFC 7807 errors
│   ├── cache/           # Thread-safe in-memory sliding window TTL cache & Redis adapter
│   ├── config/          # Pydantic BaseSettings, centralized logging configuration
│   ├── data/            # Feature engineering pipeline, synthetic generator, SMOTE preprocessor
│   ├── database/        # SQLAlchemy session, SQLite WAL pragmas, relational ORM models
│   ├── ledger/          # Append-only SHA-256 block-chained audit ledger with HMAC signatures
│   ├── models/          # Supervised classifiers (LightGBM, MLP, RF, SVM), Isolation Forest, Hybrid Scorer
│   ├── utils/           # Salted SHA-256 PII masking, cryptographic helpers
│   └── xai/             # SHAP TreeExplainer & bank-grade reason code generator
├── deployment/          # Multi-stage Dockerfile, docker-compose.yml, entrypoint.sh, prod configs
├── docs/                # Comprehensive engineering specifications across all 11 phases
│   ├── 02_Requirements/ # SRS, Functional/Non-Functional Reqs, Use Cases, RTM, Gap Analysis
│   ├── 03_Project_Management/ # PMP, WBS, Product Backlog, Sprint Plan, Timeline, Risk Register
│   ├── 04_Technical_Research/ # Technology Comparison, Feasibility, Literature Review, Citations
│   ├── 05_System_Design/      # High-Level & Low-Level Design, DB Schema, API Specs, Diagrams
│   ├── 06_UI_UX/        # User Journeys, Design System, Wireframes, Screen Inventory
│   ├── 09_Testing/      # Test Plan, Test Cases, Bug Reports, Performance Reports, Evidence
│   ├── 10_Deployment/   # Deployment Guide, Installation Guide, DB Migrations, Backup Plan
│   └── 11_Final_Delivery/ # Final Audit, Requirements Coverage, User Manual, Maintenance Plan
├── frontend/
│   ├── app.py           # Multi-tab Streamlit fraud monitoring & simulation dashboard
│   └── prototype/       # Initial UI wireframe prototype
├── research/
│   ├── benchmarks/      # Serialized empirical benchmark results across 7 algorithms (JSON)
│   └── REFERENCES.md    # Authentic academic literature review with verified DOIs
├── scripts/
│   ├── backup_database.py   # Non-blocking online SQLite WAL hot backup with gzip & SHA-256
│   ├── restore_database.py  # Checksum-verified atomic disaster recovery restore utility
│   └── smoke_test.py        # Automated 6-workflow post-deployment verification harness
├── tests/               # 13 Automated pytest test modules (54 test cases)
├── pyproject.toml       # Build configuration, ruff linting, pytest configuration
└── requirements.txt     # Locked production dependencies
```

---

## 4. Quickstart & Deployment Guide

### 4.0 One-Click Portable Setup on Windows (Fastest)
1. **First-Time Setup:** Double-click `setup.bat` (automatically configures `.venv`, installs dependencies, and initializes SQLite database).
2. **Launch Platform:** Double-click `run.bat` (starts FastAPI on `:8000` and launches Streamlit dashboard on `http://localhost:8501` in your browser).

### 4.1 Running with Docker Compose (Recommended)
```bash
# 1. Clone and enter directory
cd advanced-qr-code-payment-fraud-detection-system

# 2. Launch containerized stack
docker compose -f deployment/docker-compose.yml up -d --build

# 3. Access portals:
# API Docs:    http://localhost:8000/docs
# UI Portal:   http://localhost:8501
```

### 4.2 Running on Bare-Metal (Python 3.11)
```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # On Windows
# source .venv/bin/activate # On Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Copy environment configuration
cp .env.example .env

# 4. Start the FastAPI microservice gateway (port 8000)
python -m uvicorn backend.api.server:app --host 0.0.0.0 --port 8000 --workers 4

# 5. Start the Streamlit monitoring dashboard (port 8501)
streamlit run frontend/app.py --server.port 8501
```

---

## 5. REST API Usage Examples

### Synchronous Payment Evaluation (`POST /api/v1/predict`)
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx-1001",
    "customer_id": "cust_84920",
    "merchant_id": "merch_10492",
    "amount": 25.00,
    "currency": "USD",
    "customer_lat": 40.7128,
    "customer_lon": -74.0060,
    "merchant_lat": 40.7130,
    "merchant_lon": -74.0058,
    "qr_payload": "https://pay.bank.com/transfer?id=merch_10492",
    "timestamp": "2026-11-08T23:50:00Z"
  }'
```

**Response (`APPROVE`):**
```json
{
  "transaction_id": "tx-1001",
  "verdict": "APPROVE",
  "risk_score": 0.0842,
  "reason_codes": [],
  "processing_time_ms": 14.85,
  "ledger_block_hash": "a4f89d9e23bc...",
  "timestamp": "2026-11-08T23:50:00.015Z"
}
```

---

## 6. Empirical Research Benchmark Results

Benchmarked across 10,000 synthetic transactions (0.80% fraud ratio) on Python 3.11:

| Candidate Algorithm | Accuracy | Precision | Recall | Specificity | F1-Score | FPR | ROC-AUC | Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.14 ms |
| **Support Vector Machine** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.15 ms |
| **PyTorch MLP Neural Net** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.32 ms |
| **Random Forest (100 trees)** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 25.88 ms |
| **LightGBM (Production Supervised)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **0.0000** | **1.0000** | **0.78 ms** |
| **Isolation Forest (Unsupervised)** | 0.9787 | 0.3243 | 0.6316 | 0.9831 | 0.4286 | 0.0169 | 0.9807 | 8.90 ms |
| **Hybrid Composite Ensemble** | **0.9953** | **0.7308** | **1.0000** | **0.9953** | **0.8444** | **0.0047** | **1.0000** | **9.73 ms** |

---

## 7. Automated Testing & Verification Suite

```bash
# Execute complete regression test suite
python -m pytest tests/ -v

# Execute post-deployment smoke test suite
python scripts/smoke_test.py
```
- **Automated Test Results:** **54 / 54 passed (100% pass rate in 7.57s)**
- **Smoke Test Results:** **6 / 6 critical production workflows passed (100% success)**

---

## 8. Governance & Documentation Index

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md): Real-time milestone and phase tracking.
- [`CHANGELOG.md`](CHANGELOG.md): SemVer release history (`1.0.0`).
- [`DECISIONS.md`](DECISIONS.md): Architectural Decision Records (`ADR-001` through `ADR-008`).
- [`docs/11_Final_Delivery/FINAL_PROJECT_AUDIT.md`](docs/11_Final_Delivery/FINAL_PROJECT_AUDIT.md): Comprehensive source code and security audit report.
- [`docs/11_Final_Delivery/USER_MANUAL.md`](docs/11_Final_Delivery/USER_MANUAL.md): Full operator and developer manual.
- [`docs/11_Final_Delivery/MAINTENANCE_PLAN.md`](docs/11_Final_Delivery/MAINTENANCE_PLAN.md): Backup schedule, disaster recovery, and model drift plan.
- [`docs/11_Final_Delivery/KNOWN_LIMITATIONS.md`](docs/11_Final_Delivery/KNOWN_LIMITATIONS.md): Transparent disclosure of architectural boundaries.
