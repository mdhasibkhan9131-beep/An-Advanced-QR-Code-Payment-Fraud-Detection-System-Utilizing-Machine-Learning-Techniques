# Product Backlog & MoSCoW Prioritization

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 03)  
**Parent Document:** `docs/03_Project_Management/PROJECT_MANAGEMENT_PLAN.md`  
**Reference Document:** `docs/02_Requirements/USER_STORIES.md` | `docs/02_Requirements/RTM.md`

---

## 1. MoSCoW Classification Definitions

- **Must Have (M):** Mandatory capabilities essential to the core thesis objectives and minimal viable product (MVP). Without these, the system cannot function or be validated.
- **Should Have (S):** Critical architectural integrations that provide major value (e.g., automated XAI explanation reason codes, cryptographic tamper detection).
- **Could Have (C):** Desirable secondary features or optimizations (e.g., pluggable Redis adapter, interactive parameter sliders in UI).
- **Won't Have (W) [for initial release]:** Items intentionally excluded or deferred (e.g., real-money banking API integration, live blockchain consensus mining, hardware camera scanner drivers).

---

## 2. Granular Product Backlog

| Backlog ID | Story ID | Title & Work Description | Req ID Mapping | MoSCoW | Prov. Points | Target Sprint | Acceptance Criteria Ref |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **PBI-001** | `US-01` | Pydantic v2 Ingestion Schema & Sanitization | `FR-ING-001`, `FR-ING-004` | **M** | 3 | Sprint 1 | `AC-01` |
| **PBI-002** | `US-01` | Timestamp Drift & Freshness Validation | `FR-ING-002` | **M** | 2 | Sprint 1 | `AC-01` |
| **PBI-003** | `US-02` | Haversine Spatial Displacement Algorithm | `FR-FEA-001` | **M** | 3 | Sprint 2 | `AC-02` |
| **PBI-004** | `US-03` | QR Payload Shannon Entropy Analyzer | `FR-FEA-002` | **M** | 3 | Sprint 2 | `AC-03` |
| **PBI-005** | `US-04` | In-Memory Sliding Window Velocity Cache | `FR-FEA-003` | **M** | 5 | Sprint 2 | `AC-04` |
| **PBI-006** | `US-04` | Customer Baseline Z-Score Calculator | `FR-FEA-004` | **M** | 2 | Sprint 2 | `AC-04` |
| **PBI-007** | `US-05` | Synthetic QR Transaction Generator Module | `FR-DAT-001` | **M** | 5 | Sprint 2 | `AC-01` |
| **PBI-008** | `US-05` | SMOTE & Borderline-SMOTE Oversampling | `FR-DAT-003` | **M** | 5 | Sprint 2 | `AC-05` |
| **PBI-009** | `US-06` | Supervised Baseline Models (LogReg, RF, SVM) | `FR-MOD-001` | **M** | 5 | Sprint 3 | `AC-05` |
| **PBI-010** | `US-06` | LightGBM Production Classifier Engine | `FR-MOD-001` | **M** | 5 | Sprint 3 | `AC-05` |
| **PBI-011** | `US-06` | PyTorch Tabular Deep MLP Classifier | `FR-MOD-001` | **S** | 8 | Sprint 3 | `AC-05` |
| **PBI-012** | `US-07` | Unsupervised Isolation Forest Anomaly Engine | `FR-MOD-002` | **M** | 5 | Sprint 3 | `AC-06` |
| **PBI-013** | `US-08` | Hybrid Risk Scoring Aggregator ($S_{\text{comp}}$) | `FR-MOD-003` | **M** | 3 | Sprint 3 | `AC-07` |
| **PBI-014** | `US-09` | Three-Tier Decision Gating Engine | `FR-DEC-001` | **M** | 3 | Sprint 3 | `AC-07` |
| **PBI-015** | `US-09` | Zero-Day Anomaly Escalation Override Policy | `FR-DEC-002` | **M** | 2 | Sprint 3 | `AC-08` |
| **PBI-016** | `US-10` | SHAP TreeExplainer Local Attribution Engine | `FR-XAI-001` | **M** | 5 | Sprint 4 | `AC-09` |
| **PBI-017** | `US-11` | Standardized Human-Readable Reason Codes | `FR-XAI-002` | **M** | 3 | Sprint 4 | `AC-09` |
| **PBI-018** | `US-10` | Selective Synchronous SHAP Execution Policy | `FR-XAI-003` | **S** | 3 | Sprint 4 | `AC-09`, `AC-11` |
| **PBI-019** | `US-12` | SHA-256 Block-Chained Cryptographic Ledger | `FR-AUD-001` | **M** | 5 | Sprint 4 | `AC-10` |
| **PBI-020** | `US-13` | Cryptographic Ledger Audit & Verification API | `FR-AUD-003` | **S** | 3 | Sprint 4 | `AC-10` |
| **PBI-021** | `US-14` | FastAPI `/api/v1/predict` (Sub-100ms Serving) | `FR-API-001` | **M** | 5 | Sprint 5 | `AC-11` |
| **PBI-022** | `US-15` | Deterministic Heuristic Fallback Engine | `FR-DEC-003` | **S** | 3 | Sprint 5 | `AC-12` |
| **PBI-023** | `US-16` | Batch Prediction & Health/Metrics Endpoints | `FR-API-002`, `FR-API-004` | **S** | 3 | Sprint 5 | `AC-11` |
| **PBI-024** | `US-04` | Pluggable Redis Cache Connector Adapter | `NFR-PERF-001` | **C** | 3 | Sprint 5 | `AC-04` |
| **PBI-025** | `US-17` | Streamlit Real-Time Monitoring Dashboard | `FR-UI-001` | **M** | 5 | Sprint 5 | `AC-07` |
| **PBI-026** | `US-18` | Interactive Fraud Vector Simulator in UI | `FR-UI-002` | **M** | 5 | Sprint 5 | `AC-07`, `AC-09` |
| **PBI-027** | `US-06` | Algorithm Benchmark Comparison Visualizer | `FR-UI-003` | **S** | 3 | Sprint 5 | `AC-05` |
| **PBI-028** | `US-19` | Federated Learning (FedAvg) Simulation Module| `FR-FED-001`, `FR-FED-002`| **S** | 5 | Sprint 6 | `AC-05` |
| **PBI-029** | N/A | End-to-End Latency & Load Benchmark Suite | `NFR-PERF-001`, `NFR-PERF-002`| **M** | 5 | Sprint 6 | `AC-11` |
| **PBI-030** | N/A | Automated Unit & Integration Test Suite ($\ge 85\%$)| `NFR-MAINT-002` | **M** | 5 | Sprint 6 | All ACs |
| **PBI-031** | N/A | Production Packaging & Docker Containerization | `NFR-RES-002` | **S** | 3 | Sprint 6 | `NFR-RES-002` |
| **PBI-032** | N/A | Final Thesis Evaluation & Benchmark Package | All Scope Items | **M** | 5 | Sprint 6 | All ACs |

---

## 3. Summary of Backlog Estimation

- **Total Story Points (Provisional):** 126 Points
- **Must Have (M) Total:** 83 Points (65.9% of Backlog)
- **Should Have (S) Total:** 40 Points (31.7% of Backlog)
- **Could Have (C) Total:** 3 Points (2.4% of Backlog)
- **Won't Have (W) Total:** 0 Points (Explicitly filtered during Requirements Engineering)

