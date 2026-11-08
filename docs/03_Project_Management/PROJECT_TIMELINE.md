# Project Timeline & Milestone Schedule

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 03)  
**Parent Document:** `docs/03_Project_Management/PROJECT_MANAGEMENT_PLAN.md`  
**Reference Policy:** `AGENT_RULES.md` (No invented calendar deadlines; provisional iteration cycles)

---

## 1. Project Milestone Schedule

All milestones follow a sequential stage-gate structure based on verified deliverables rather than artificial calendar assumptions:

| Milestone ID | Milestone Description | Target Iteration | Key Exit Deliverables | Approval Gate | Current Status |
| :---: | :--- | :---: | :--- | :---: | :---: |
| **M0** | **Workspace Initialization & Scaffolding** | Pre-Sprint | Directory scaffolding, `AGENT_RULES.md`, mirrored source. | Gate 0 | **COMPLETED** |
| **M1** | **Requirements Analysis & SRS Approval** | Pre-Sprint | 9 requirements specs in `docs/02_Requirements/`, RTM. | Gate 0 | **COMPLETED** |
| **M2** | **Architecture & Data Contract Baseline** | Sprint 1 | `docs/04_Architecture/`, Pydantic schemas, dependency lock. | Gate 1 | **PLANNED** |
| **M3** | **Data Engineering & SMOTE Pipeline** | Sprint 2 | Synthetic generator, feature extractors, balanced splits. | Gate 2 | **PLANNED** |
| **M4** | **ML Model Benchmarks & Hybrid Engine** | Sprint 3 | LightGBM, RF, SVM, MLP, Isolation Forest, hybrid scores. | Gate 3 | **PLANNED** |
| **M5** | **XAI Explainer & Cryptographic Ledger** | Sprint 4 | SHAP TreeExplainer, reason codes, SHA-256 block ledger. | Gate 4 | **PLANNED** |
| **M6** | **API Microservice & Simulation Dashboard** | Sprint 5 | FastAPI `/predict` (<100ms), fallback, Streamlit dashboard. | Gate 5 | **PLANNED** |
| **M7** | **Final System Verification & Thesis Release**| Sprint 6 | FedAvg simulation, load/latency benchmarks, test suite. | Final Gate | **PLANNED** |

---

## 2. Critical Path Analysis (CPA)

The critical path represents the minimum sequence of dependent tasks that directly dictates project completion:

```
[M0: Scaffolding] ──> [M1: Requirements] ──> [M2: Architecture & Schemas]
                                                        │
                                                        ▼
                                              [M3: Data & SMOTE Engine]
                                                        │
                                                        ▼
                                              [M4: ML Models & Hybrid Gating]
                                                        │
                                                        ▼
                                              [M5: XAI & Cryptographic Ledger]
                                                        │
                                                        ▼
                                              [M6: API Serving & Streamlit UI]
                                                        │
                                                        ▼
                                              [M7: Load Benchmark & Final Release]
```

### Critical Path Dependencies:
1. **M2 $\rightarrow$ M3:** Feature extraction logic cannot be finalized without approved mathematical definitions and Pydantic schemas.
2. **M3 $\rightarrow$ M4:** Supervised classifiers and Isolation Forest cannot be trained without the balanced synthetic dataset.
3. **M4 $\rightarrow$ M5:** SHAP feature attribution and decision gating depend directly on trained model artifacts.
4. **M5 $\rightarrow$ M6:** The FastAPI gateway and Streamlit UI require the model engine, XAI explainer, and ledger interfaces.
5. **M6 $\rightarrow$ M7:** Concurrency load testing, latency benchmarking, and final thesis packaging require a fully integrated stack.

---

## 3. Iteration Velocity & Estimation Parameters

- **Planning Paradigm:** Iteration-based incremental delivery (provisional 1-week to 2-week iteration cycles depending on execution resource availability).
- **Provisional Sprint Sizing:**
  - Sprint 1: 15 Story Points
  - Sprint 2: 23 Story Points
  - Sprint 3: 31 Story Points
  - Sprint 4: 19 Story Points
  - Sprint 5: 27 Story Points
  - Sprint 6: 23 Story Points
  - **Total Estimated Effort:** 138 Story Points (inclusive of scaffolding and verification).
- **Contingency Buffer:** 15% effort buffer allocated in Sprint 6 for latency profiling optimizations and refactoring.

