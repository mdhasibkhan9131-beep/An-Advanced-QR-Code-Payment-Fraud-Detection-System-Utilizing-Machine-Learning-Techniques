# Advanced QR Code Payment Fraud Detection System

An enterprise-grade, low-latency predictive machine learning framework designed to detect, intercept, and explain fraudulent transactions in digital Quick Response (QR) code payment environments.

---

## 1. Executive Summary

Contactless and peer-to-peer (P2P/POS) QR payment ecosystems present novel security challenges, including payload tampering, static QR spoofing, malicious redirect injection, and velocity bursts. Conventional rule-based fraud detection engines are rigid, cause excessive false-positive friction, and audit transactions post-facto.

This project implements an intelligent, real-time defense architecture capable of evaluating transaction risk mid-flight. Operating at sub-100ms inference latencies, the system leverages:
- **Spatial-Temporal & QR Feature Engineering**: Dynamic entropy analysis, Haversine displacement, and rolling velocity counters.
- **Class Imbalance Resolution**: Synthetic Minority Over-sampling Technique (SMOTE) to address severe financial class skew.
- **Hybrid Inference Engine**: Blends supervised classification (LightGBM, Random Forest, Deep MLP) with unsupervised anomaly detection (Isolation Forest) for known and zero-day threat interception.
- **Explainable AI (XAI)**: Generates real-time local feature attributions via SHAP for regulatory transparency.
- **Cryptographic Audit Ledger**: Append-only SHA-256 hash chaining to ensure tamper-evident auditability.

---

## 2. Directory Scaffolding

```
advanced-qr-code-payment-fraud-detection-system/
├── source/          # Preserved immutable original proposal specifications
├── docs/            # Technical documentation, sprint plans, and API specs
├── frontend/        # Interactive Streamlit dashboard and UI simulation
├── backend/         # FastAPI REST service, ML inference pipelines, and XAI engine
├── database/        # Database schemas, migrations, and local storage models
├── tests/           # Unit, integration, and performance benchmarking test suites
├── scripts/         # Automation scripts for data generation, training, and evaluation
├── research/        # Model exploratory analysis, notebooks, and experimental benchmarks
├── deployment/      # Docker, environment configurations, and deployment manifests
├── README.md        # High-level project index and documentation
├── PROJECT_STATUS.md# Active sprint phase, task tracking, and milestone status
├── CHANGELOG.md     # Version history and chronological project increments
├── DECISIONS.md     # Architectural Decision Records (ADRs)
└── AGENT_RULES.md   # Mandatory engineering governance and operating rules
```

---

## 3. Technology Stack Summary

- **Core Language**: Python 3.10+
- **Machine Learning**: Scikit-Learn, LightGBM, PyTorch, Imbalanced-Learn
- **Anomaly Detection & XAI**: PyOD (Isolation Forest), SHAP
- **Application Services**: FastAPI, Pydantic v2, Uvicorn
- **User Interface**: Streamlit
- **State & Storage**: Redis (caching/velocities), SQLite / SQLAlchemy (audit & logs)

---

## 4. Governance & SDLC

This project is governed by strict agile SDLC standards defined in [AGENT_RULES.md](AGENT_RULES.md). All development proceeds in staged phases with formal approval gates. Current progress is tracked in [PROJECT_STATUS.md](PROJECT_STATUS.md).

