# Advanced QR Code Payment Fraud Detection System

An enterprise-grade, low-latency predictive machine learning framework designed to detect, intercept, and explain fraudulent transactions in digital Quick Response (QR) code payment environments.

---

## 1. System Architecture Overview

```
[ QR Payment Client / POS ] ──> [ FastAPI Gateway (/api/v1/predict) ]
                                            │
                                            ▼
                             [ Pydantic v2 Boundary Validation ]
                                            │
                                            ▼
                             [ Haversine, Entropy & State Velocity ]
                                            │
                             ┌──────────────┴──────────────┐
                             ▼                             ▼
                 [ LightGBM Classifier ]        [ Isolation Forest ]
                 P(Fraud) in [0, 1]             S(Anomaly) in [0, 1]
                             │                             │
                             └──────────────┬──────────────┘
                                            ▼
                             [ Hybrid Gating: S_comp = 0.7*P + 0.3*S ]
                                            │
                             ┌──────────────┴──────────────┐
                             ▼                             ▼
                 [ SHAP TreeExplainer ]         [ SHA-256 Chained Ledger ]
                 Local Reason Codes             Tamper-Evident Non-Repudiation
```

---

## 2. Directory Layout

```
advanced-qr-code-payment-fraud-detection-system/
├── backend/
│   ├── api/             # FastAPI application, route handlers, Pydantic schemas, errors
│   ├── cache/           # Thread-safe in-memory sliding window TTL cache & Redis adapter
│   ├── config/          # Pydantic BaseSettings, centralized logging configuration
│   ├── database/        # SQLAlchemy session, SQLite WAL pragmas, relational ORM models
│   ├── utils/           # Salted SHA-256 masking, security helpers
│   ├── data/            # (Sprint 2) Synthetic QR generator, feature engineering, SMOTE
│   ├── models/          # (Sprint 3) Supervised classifiers, anomaly engines, hybrid ensemble
│   ├── xai/             # (Sprint 4) SHAP TreeExplainer & reason code generator
│   └── ledger/          # (Sprint 4) Cryptographic SHA-256 block-chained audit ledger
├── frontend/
│   └── prototype/       # Interactive Streamlit UI prototype (Fintech Dark Theme)
├── docs/                # Comprehensive engineering specifications (Reqs, PMP, Research, Design, UI)
├── tests/               # Pytest automated test suites (API, Database, Environment, Health)
├── logs/                # Rotating application log files
├── .env.example         # Environment variable template
├── pyproject.toml       # Build configuration, ruff linting, pytest settings
└── requirements.txt     # Locked production dependencies
```

---

## 3. Quickstart & Development Environment Setup

### 3.1 Prerequisites
- **Python:** `>= 3.10, < 3.12` (x86-64)
- **Git:** Installed on host system

### 3.2 Installation
```bash
# Clone and enter directory
cd advanced-qr-code-payment-fraud-detection-system

# (Optional) Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment variables
cp .env.example .env
```

### 3.3 Running the Backend Microservice
```bash
# Start FastAPI server on port 8000
python -m uvicorn backend.api.server:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Probe: `http://localhost:8000/api/v1/health`
- Telemetry Scoreboard: `http://localhost:8000/api/v1/metrics`

### 3.4 Running the Streamlit UI Prototype
```bash
# Start the interactive dashboard
streamlit run frontend/prototype/app_prototype.py
```
- Access in browser: `http://localhost:8501`

### 3.5 Executing Automated Tests
```bash
# Run complete test suite with coverage
pytest -v
```

---

## 4. Engineering Standards & Governance
All development proceeds under strict Agile Scrum governance documented in:
- [`AGENT_RULES.md`](AGENT_RULES.md): Non-negotiable operating principles.
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md): Real-time milestone and sprint tracking.
- [`CHANGELOG.md`](CHANGELOG.md): SemVer release history.
- [`DECISIONS.md`](DECISIONS.md): Architectural Decision Records.
