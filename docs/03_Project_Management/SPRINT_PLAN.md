# Sprint Plan & Iteration Schedule

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 03)  
**Parent Document:** `docs/03_Project_Management/PROJECT_MANAGEMENT_PLAN.md`  
**Reference Document:** `docs/03_Project_Management/PRODUCT_BACKLOG.md` | `AGENT_RULES.md`

---

## Sprint Cadence Overview

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                                  SPRINT ROADMAP                                   │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┤
│  Sprint 1   │  Sprint 2   │  Sprint 3   │  Sprint 4   │  Sprint 5   │  Sprint 6   │
│ Architecture│ Data Engine │  ML Models  │  XAI & Hash │ API Gateway │ Verification│
│  & Schemas  │ & Synthetics│ & Hybrid ML │Audit Ledger │ & UI Dash   │ & Final Rpt │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│  Gate 1     │  Gate 2     │  Gate 3     │  Gate 4     │  Gate 5     │ Final Gate  │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## Sprint 1: System Architecture, Data Contracts & Environment Scaffolding

- **Sprint Goal:** Finalize the end-to-end technical architecture, define strict Pydantic and database schemas, pin dependencies, and establish the automated test harness.
- **In-Scope PBIs:**
  - `PBI-001`: Pydantic v2 Ingestion Schema & Sanitization (3 pts)
  - `PBI-002`: Timestamp Drift & Freshness Validation (2 pts)
  - Architecture documentation & OpenAPI contract definitions
  - Environment pinning (`pyproject.toml`, `requirements.txt`)
- **Total Points:** 15 pts (provisional)
- **Dependencies:** Approved Phase 02 Requirements (`docs/02_Requirements/`).
- **Deliverables & Artifacts:**
  - `docs/04_Architecture/ARCHITECTURE_DESIGN.md`
  - `docs/04_Architecture/DATA_DICTIONARY.md`
  - `docs/04_Architecture/API_SPECIFICATION.md`
  - `pyproject.toml`, `requirements.txt`, `.env.example`
  - `backend/api/schema.py`
  - Pytest baseline configuration (`tests/conftest.py`)
- **Sprint Exit Criteria:**
  - Pydantic schema validated with unit tests.
  - Zero hardcoded configuration strings.
  - **Stage-Gate 1 Review:** Technical architecture approved by stakeholder.

---

## Sprint 2: Data Engineering, Contextual Features & Synthetic Generation

- **Sprint Goal:** Build the synthetic QR transaction generator with realistic fraud archetypes, implement spatial and temporal feature extraction, and establish the SMOTE balancing pipeline.
- **In-Scope PBIs:**
  - `PBI-003`: Haversine Spatial Displacement Algorithm (3 pts)
  - `PBI-004`: QR Payload Shannon Entropy Analyzer (3 pts)
  - `PBI-005`: In-Memory Sliding Window Velocity Cache (5 pts)
  - `PBI-006`: Customer Baseline Z-Score Calculator (2 pts)
  - `PBI-007`: Synthetic QR Transaction Generator Module (5 pts)
  - `PBI-008`: SMOTE & Borderline-SMOTE Oversampling (5 pts)
- **Total Points:** 23 pts (provisional)
- **Dependencies:** Sprint 1 schema contracts and test harness.
- **Deliverables & Artifacts:**
  - `backend/data/generator.py`
  - `backend/data/feature_engineering.py`
  - `backend/data/preprocessor.py`
  - `backend/cache/memory_cache.py`
  - Automated tests: `tests/test_feature_engineering.py`, `tests/test_generator.py`
- **Sprint Exit Criteria:**
  - Generator successfully produces synthetic dataset with acute $\le 1\%$ fraud imbalance.
  - Haversine and Shannon entropy algorithms pass mathematical accuracy unit tests.
  - SMOTE oversampling confirmed strictly isolated to training splits.
  - **Stage-Gate 2 Review:** Data generator and feature pipeline approved.

---

## Sprint 3: Supervised Model Suite, Anomaly Detection & Hybrid Gating

- **Sprint Goal:** Implement and benchmark candidate supervised classifiers (LightGBM, RF, SVM, Deep MLP), train the unsupervised Isolation Forest, and integrate the hybrid composite risk scoring engine.
- **In-Scope PBIs:**
  - `PBI-009`: Supervised Baseline Models (LogReg, RF, SVM) (5 pts)
  - `PBI-010`: LightGBM Production Classifier Engine (5 pts)
  - `PBI-011`: PyTorch Tabular Deep MLP Classifier (8 pts)
  - `PBI-012`: Unsupervised Isolation Forest Anomaly Engine (5 pts)
  - `PBI-013`: Hybrid Risk Scoring Aggregator ($S_{\text{comp}}$) (3 pts)
  - `PBI-014`: Three-Tier Decision Gating Engine (3 pts)
  - `PBI-015`: Zero-Day Anomaly Escalation Override Policy (2 pts)
- **Total Points:** 31 pts (provisional)
- **Dependencies:** Sprint 2 balanced dataset and feature pipelines.
- **Deliverables & Artifacts:**
  - `backend/models/base.py`, `supervised.py`, `unsupervised.py`, `ensemble.py`, `trainer.py`
  - Serialized model weights (`.joblib`, `.pt`)
  - Automated tests: `tests/test_models.py`, `tests/test_ensemble.py`
  - Benchmark performance tables in `research/benchmarks/`
- **Sprint Exit Criteria:**
  - LightGBM achieves Recall $\ge 95.0\%$, Precision $\ge 90.0\%$, FPR $\le 1.5\%$.
  - Isolation Forest successfully flags out-of-distribution transactions.
  - Hybrid decision gating passes unit tests for all tiers and escalation overrides.
  - **Stage-Gate 3 Review:** Model benchmarks validated against proposal SLA.

---

## Sprint 4: Explainable AI (SHAP) & Cryptographic Audit Ledger

- **Sprint Goal:** Integrate dynamic local SHAP feature attribution with human-readable reason codes, and implement the SHA-256 block-chained tamper-evident audit ledger.
- **In-Scope PBIs:**
  - `PBI-016`: SHAP TreeExplainer Local Attribution Engine (5 pts)
  - `PBI-017`: Standardized Human-Readable Reason Codes (3 pts)
  - `PBI-018`: Selective Synchronous SHAP Execution Policy (3 pts)
  - `PBI-019`: SHA-256 Block-Chained Cryptographic Ledger (5 pts)
  - `PBI-020`: Cryptographic Ledger Audit & Verification API (3 pts)
- **Total Points:** 19 pts (provisional)
- **Dependencies:** Sprint 3 trained LightGBM model and decision gating.
- **Deliverables & Artifacts:**
  - `backend/xai/explainer.py`
  - `backend/ledger/audit_chain.py`
  - SQLite schema / SQLAlchemy model for ledger persistence
  - Automated tests: `tests/test_xai.py`, `tests/test_ledger.py`
- **Sprint Exit Criteria:**
  - SHAP TreeExplainer outputs top-3 reason codes for flagged transactions within $\le 40\text{ ms}$.
  - Cryptographic ledger maintains unbroken SHA-256 parent block hash links.
  - Tamper detection test successfully catches modified database rows.
  - **Stage-Gate 4 Review:** XAI and audit ledger functionality approved.

---

## Sprint 5: FastAPI Serving Gateway & Streamlit Simulation Dashboard

- **Sprint Goal:** Deploy the asynchronous FastAPI microservice with sub-100ms inference and heuristic fallback, and build the interactive Streamlit monitoring and simulation dashboard.
- **In-Scope PBIs:**
  - `PBI-021`: FastAPI `/api/v1/predict` (Sub-100ms Serving) (5 pts)
  - `PBI-022`: Deterministic Heuristic Fallback Engine (3 pts)
  - `PBI-023`: Batch Prediction & Health/Metrics Endpoints (3 pts)
  - `PBI-024`: Pluggable Redis Cache Connector Adapter (3 pts)
  - `PBI-025`: Streamlit Real-Time Monitoring Dashboard (5 pts)
  - `PBI-026`: Interactive Fraud Vector Simulator in UI (5 pts)
  - `PBI-027`: Algorithm Benchmark Comparison Visualizer (3 pts)
- **Total Points:** 27 pts (provisional)
- **Dependencies:** Sprints 1 through 4 modules.
- **Deliverables & Artifacts:**
  - `backend/api/server.py`, `routes.py`, `fallback.py`
  - `frontend/app.py`, `components/gauges.py`, `components/simulator.py`
  - Automated tests: `tests/test_api.py`, `tests/test_fallback.py`
- **Sprint Exit Criteria:**
  - `/api/v1/predict` returns valid verdict and reasons under 100ms.
  - Heuristic fallback engages when inference is artificially delayed $> 120\text{ ms}$.
  - Streamlit dashboard renders live transactions, simulator sliders, and SHAP plots.
  - **Stage-Gate 5 Review:** Complete interactive full-stack system verified.

---

## Sprint 6: Federated Privacy Simulation, End-to-End Verification & Release

- **Sprint Goal:** Implement the privacy-preserving Federated Learning (FedAvg) simulation, execute high-concurrency load and latency benchmarking, and package the final academic thesis artifacts.
- **In-Scope PBIs:**
  - `PBI-028`: Federated Learning (FedAvg) Simulation Module (5 pts)
  - `PBI-029`: End-to-End Latency & Load Benchmark Suite (5 pts)
  - `PBI-030`: Automated Unit & Integration Test Suite ($\ge 85\%$ coverage) (5 pts)
  - `PBI-031`: Production Packaging & Docker Containerization (3 pts)
  - `PBI-032`: Final Thesis Evaluation & Benchmark Package (5 pts)
- **Total Points:** 23 pts (provisional)
- **Dependencies:** Fully integrated system from Sprint 5.
- **Deliverables & Artifacts:**
  - `research/federation/mock_federated.py`, `scripts/run_federated_simulation.py`
  - `scripts/benchmark_latency.py`, `scripts/evaluate_models.py`
  - Dockerfile, `docker-compose.yml`
  - Final Verification & Thesis Benchmark Report in `docs/`
- **Sprint Exit Criteria:**
  - Overall automated test coverage $\ge 85\%$.
  - p99 latency verified $\le 100\text{ ms}$ under 200 req/s load.
  - Federated learning simulation demonstrates decentralized convergence.
  - **Final Stage-Gate Review:** Full system acceptance and thesis sign-off.

