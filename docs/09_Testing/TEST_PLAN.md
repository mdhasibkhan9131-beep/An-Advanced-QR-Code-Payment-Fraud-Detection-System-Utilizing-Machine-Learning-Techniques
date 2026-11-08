# Software Quality Assurance Test Plan

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System Utilizing Machine Learning Techniques  
**Document Version:** 1.0.0  
**Status:** Approved Quality Baseline  
**Author:** Principal Software Quality Specialist & Senior Test Automation Engineer  
**Parent Document:** `docs/02_Requirements/SRS.md` | `docs/03_Project_Management/PROJECT_MANAGEMENT_PLAN.md`  
**Evaluation Scope:** Complete Full-Stack System (Models, Feature Pipeline, Cryptographic Ledger, API Gateway, Dashboard)

---

## 1. Executive Summary & Objective

This Software Quality Assurance Test Plan establishes the rigorous, independent verification and validation framework for the Advanced QR Code Payment Fraud Detection System. Operating under strict QA discipline ("do not assume the application works simply because the developer agent reported success"), this plan defines the procedures, tooling, test configurations, and pass/fail thresholds required to guarantee full functional compliance, proposal SLA adherence, algorithmic integrity, and security hardening.

---

## 2. Test Items & System Scope

| Component / Subsystem | Primary Code Location | Target Quality Dimension |
| :--- | :--- | :--- |
| **Ingestion Schema & Sanitization** | `backend/api/schema.py`, `errors.py` | Input validation, type boundaries, RFC 7807 compliance |
| **Feature Extraction & Spatial Trigonometry** | `backend/data/feature_engineering.py` | Mathematical precision of Haversine & Shannon entropy |
| **Synthetic Transaction Generator** | `backend/data/generator.py` | Domain fidelity of 4 fraud archetypes, acute $\le 1.0\%$ imbalance |
| **Dataset Resampling & Split Isolation** | `backend/data/preprocessor.py` | Zero test-fold data leakage, Borderline-SMOTE isolation |
| **Supervised Classifiers Suite** | `backend/models/supervised.py` | LightGBM, Random Forest, SVM, MLP benchmark SLAs |
| **Unsupervised Anomaly Detector** | `backend/models/unsupervised.py` | Isolation Forest out-of-distribution calibration $[0, 1]$ |
| **Hybrid Composite Scorer & Gating** | `backend/models/ensemble.py` | $S_{\text{comp}}$ weighting, 3-tier gating, Zero-Day escalation |
| **Explainable AI (SHAP TreeExplainer)** | `backend/xai/explainer.py` | Local feature attributions, reason codes, latency budget $\le 40\text{ms}$ |
| **Cryptographic Block-Chained Ledger** | `backend/ledger/audit_chain.py` | Parent SHA-256 links, state signatures, tamper detection |
| **FastAPI Microservice Gateway** | `backend/api/server.py`, `routes.py` | Sub-100ms inference SLA, batch serving, heuristic fallback |
| **Streamlit Interactive UI Dashboard** | `frontend/app.py` | Usability, telemetry streaming, fraud vector simulation |

---

## 3. Test Environments & Hardware Configuration

- **Host Operating System:** Microsoft Windows 11 Enterprise (x86_64)
- **Runtime Environment:** Python 3.11.9 (64-bit)
- **Compute Hardware:** Intel/AMD Multi-Core CPU, 16.0 GB Physical RAM, Direct CPU Tensor Execution (PyTorch CPU build)
- **Primary Database Engine:** SQLite 3.45.3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`)
- **State Caching Layer:** Thread-Safe In-Memory Sliding Window TTL Cache (`backend/cache/memory.py`)
- **Automated Test Harness:** Pytest 9.1.1, AnyIO 4.14.2, Pytest-Asyncio 1.4.1

---

## 4. Testing Methodologies & Classification

```
┌────────────────────────────────────────────────────────────────────────┐
│                        COMPREHENSIVE TEST PYRAMID                      │
├────────────────────────────────────────────────────────────────────────┤
│  [E2E & UI Acceptance]     FastAPI Live Client, Streamlit Verification │
│  [Security & Pen Tests]    SQLi, Replay Attacks, Boundary Violations   │
│  [Performance Benchmark]   P50/P95/P99 Latency SLA (< 100ms), 5.5k rec/s│
│  [Integration Testing]     DB Persistence + Ledger Chaining + SHAP XAI │
│  [Unit Testing]            Haversine, Shannon, Scaler, SMOTE, Classifiers│
└────────────────────────────────────────────────────────────────────────┘
```

1. **Unit Testing:** Individual mathematical functions, Pydantic schemas, and model wrappers tested in isolation.
2. **Integration Testing:** Cross-boundary interactions between feature pipelines, ML models, SQLite WAL, and cryptographic ledger.
3. **End-to-End Functional Testing:** Full `/api/v1/predict` request-response cycles simulating live customer payment flows.
4. **Performance & Latency SLA Testing:** Validating that end-to-end inference takes $< 100\text{ ms}$ at P95 across consecutive transactions.
5. **Security & Penetration Testing:** SQL injection injection attacks, malicious QR script strings, negative monetary values, out-of-bounds GPS coordinates, and PII masking audits.
6. **Regression Testing:** Automated verification ensuring newly integrated features do not break existing working code.
7. **Empirical Research Evaluation:** Objective benchmarking of candidate algorithms (Accuracy, Precision, Recall, F1, FPR, ROC-AUC).

---

## 5. Entry & Exit Criteria

### 5.1 Entry Criteria
- Codebase fully compiled and syntax checked without fatal warnings.
- All dependencies pinned in `requirements.txt` and installed.
- Pre-trained models (`lightgbm_model.joblib`, `isolation_forest.joblib`, `scaler.joblib`) available in `backend/models/`.

### 5.2 Exit Criteria
- 100% of defined automated test cases executed.
- Zero critical, high, or medium severity defects outstanding.
- P95 transaction inference latency strictly $< 100\text{ ms}$.
- Borderline-SMOTE oversampling strictly isolated from test folds.
- Unbroken SHA-256 cryptographic chain validated across all evaluated transactions.

