# Requirements Traceability Matrix (RTM)

**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 02)  
**Parent Document:** `docs/02_Requirements/SRS.md`  
**Reference Document:** `source/PROJECT_SPEC.md`

---

## 1. Traceability Mapping

| Proposal Scope / Section | Req ID | Description | Use Case ID | User Story ID | Target Module | Verification Method | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Data Ingestion & Gateway** | `FR-ING-001` | Pydantic Schema Validation | `UC-01`, `UC-02` | `US-01` | `api.schema` | Unit / API Test | Specified |
| **Data Ingestion & Gateway** | `FR-ING-002` | Timestamp Freshness Check | `UC-01` | `US-01` | `api.schema` | Unit Test | Specified |
| **Data Ingestion & Gateway** | `FR-ING-004` | PII Salted Hashing | `UC-01` | `US-01` | `data.preprocessor` | Unit Test | Specified |
| **Data Engineering** | `FR-FEA-001` | Spatial Haversine Distance | `UC-01`, `UC-03` | `US-02` | `data.feature_eng` | Unit Test | Specified |
| **Data Engineering** | `FR-FEA-002` | Shannon Entropy of QR Payload | `UC-03` | `US-03` | `data.feature_eng` | Unit Test | Specified |
| **Data Engineering** | `FR-FEA-003` | Stateful Rolling Velocities | `UC-01`, `UC-03` | `US-04` | `data.feature_eng` | Integration Test | Specified |
| **Data Engineering** | `FR-FEA-004` | Amount Z-Score Relative to Base | `UC-02`, `UC-03` | `US-02` | `data.feature_eng` | Unit Test | Specified |
| **Data Engineering** | `FR-DAT-001` | Synthetic QR Transaction Generator | `UC-06` | `US-05` | `data.generator` | Inspection / Test | Specified |
| **Class Imbalance** | `FR-DAT-003` | SMOTE Oversampling Pipeline | `UC-06` | `US-05` | `models.trainer` | Benchmark Test | Specified |
| **Supervised Modeling** | `FR-MOD-001` | Multi-Algorithm Benchmark Suite | `UC-06` | `US-06` | `models.supervised` | Benchmark Test | Specified |
| **Anomaly Detection** | `FR-MOD-002` | Unsupervised Isolation Forest | `UC-04` | `US-07` | `models.unsupervised` | Benchmark Test | Specified |
| **Hybrid Decision Engine** | `FR-MOD-003` | Composite Risk Calculation | `UC-01`, `UC-03` | `US-08` | `models.ensemble` | Unit Test | Specified |
| **Decision Gating** | `FR-DEC-001` | 3-Tier Classification Gating | `UC-01`, `UC-02` | `US-09` | `models.ensemble` | Unit Test | Specified |
| **Decision Gating** | `FR-DEC-002` | Zero-Day Anomaly Escalation | `UC-04` | `US-09` | `models.ensemble` | Unit Test | Specified |
| **Fault Tolerance** | `FR-DEC-003` | Heuristic Fallback on Timeout | `UC-01` | `US-15` | `api.routes` | Integration Test | Specified |
| **Explainable AI (XAI)** | `FR-XAI-001` | Dynamic SHAP TreeExplainer | `UC-02`, `UC-03` | `US-10` | `xai.explainer` | Unit / Benchmark | Specified |
| **Explainable AI (XAI)** | `FR-XAI-002` | Human-Readable Reason Codes | `UC-02`, `UC-03` | `US-11` | `xai.explainer` | Unit Test | Specified |
| **Audit & Governance** | `FR-AUD-001` | Cryptographic SHA-256 Ledger | `UC-01`, `UC-03` | `US-12` | `ledger.audit_chain` | Unit Test | Specified |
| **Audit & Governance** | `FR-AUD-003` | Ledger Chain Verification API | `UC-07` | `US-13` | `ledger.audit_chain` | Integration Test | Specified |
| **API Serving** | `FR-API-001` | Real-Time `/predict` Endpoint | `UC-01`, `UC-03` | `US-14` | `api.routes` | API Latency Test | Specified |
| **API Serving** | `FR-API-002` | Batch `/batch-predict` Endpoint | `UC-06` | `US-16` | `api.routes` | API Test | Specified |
| **API Serving** | `FR-API-004` | Telemetry `/metrics` Endpoint | `UC-05` | `US-16` | `api.routes` | API Test | Specified |
| **UI & Simulation** | `FR-UI-001` | Streamlit Live Dashboard | `UC-05` | `US-17` | `ui.app` | UI Inspection | Specified |
| **UI & Simulation** | `FR-UI-002` | Interactive Fraud Simulator | `UC-05` | `US-18` | `ui.app` | UI Inspection | Specified |
| **Privacy Compliance** | `FR-FED-001` | Federated Learning FedAvg Sim | `UC-08` | `US-19` | `federation.mock` | Benchmark Test | Specified |
| **Non-Functional: Latency** | `NFR-PERF-001` | Sub-100ms Inference (p99) | `UC-01` | `US-14` | System Wide | Load / Benchmark | Specified |
| **Non-Functional: Throughput** | `NFR-PERF-002` | $\ge 200\text{ req/s}$ Throughput | `UC-01` | `US-14` | `api.server` | Load Test | Specified |
| **Non-Functional: Accuracy** | `NFR-ACC-001` | Recall $\ge 95.0\%$ | `UC-06` | `US-06` | `models.trainer` | Evaluation Run | Specified |
| **Non-Functional: Precision** | `NFR-ACC-002` | Precision $\ge 90.0\%$, FPR $\le 1.5\%$ | `UC-06` | `US-06` | `models.trainer` | Evaluation Run | Specified |
| **Non-Functional: Cost Loss** | `NFR-ACC-003` | Asymmetric Loss Optimization | `UC-06` | `US-06` | `models.trainer` | Evaluation Run | Specified |
| **Non-Functional: Memory** | `NFR-RES-001` | Model Memory Footprint $\le 250\text{MB}$ | `UC-01` | `US-06` | `models` | Resource Profiling | Specified |
| **Non-Functional: Security** | `NFR-SEC-001` | Zero Plaintext PII Storage | `UC-01` | `US-01` | `data.preprocessor` | Security Audit | Specified |

---

## 2. Verification Method Legend
- **Unit Test:** Automated test of isolated function/class logic with mocked dependencies.
- **Integration Test:** End-to-end component interaction (e.g., API to cache to ML engine to DB).
- **Benchmark Test:** Automated quantitative performance run measuring ML metrics (Recall, Precision, PR-AUC).
- **API Latency Test:** High-concurrency load testing verifying p50/p95/p99 latency ceilings under simulated network load.
- **Security Audit:** Static analysis and database dump inspection to ensure zero plaintext PII leaks.
- **UI Inspection:** Manual and automated verification of browser rendering in Streamlit.

