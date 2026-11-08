# Work Breakdown Structure (WBS)

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 03)  
**Parent Document:** `docs/03_Project_Management/PROJECT_MANAGEMENT_PLAN.md`  
**Reference Document:** `docs/02_Requirements/SRS.md`

---

```
1.0 Advanced QR Fraud Detection System
├── 1.0 Project Management & Governance
├── 2.0 Requirements Engineering (Complete)
├── 3.0 System Architecture & Technical Design
├── 4.0 Environment & Dependency Setup
├── 5.0 Data Engineering & Synthetic Generator Pipeline
├── 6.0 Machine Learning Engine & Anomaly Detection
├── 7.0 Explainable AI (XAI) & Cryptographic Audit Ledger
├── 8.0 Backend API Gateway & Resilient Serving (FastAPI)
├── 9.0 Frontend Monitoring & Simulation UI (Streamlit)
├── 10.0 Privacy-Preserving Simulation (Federated Learning)
└── 11.0 Verification, Validation, Benchmarking & Final Thesis Release
```

---

## Detailed Work Package Breakdown

### 1.0 Project Management & Governance
- **1.1 Workspace Initialization & Scaffolding** *(Completed)*
  - 1.1.1 Source inspection and title extraction
  - 1.1.2 Scaffolding 9-tier directory structure
  - 1.1.3 Governance baseline (`AGENT_RULES.md`, `README.md`, `PROJECT_STATUS.md`)
- **1.2 Agile Sprint & Planning Management**
  - 1.2.1 Product Backlog creation and MoSCoW prioritization
  - 1.2.2 Sprint scheduling and dependency mapping
  - 1.2.3 Risk register formulation and mitigation strategies

### 2.0 Requirements Engineering *(Completed)*
- **2.1 Requirements Elicitation & Domain Analysis** (`PROJECT_ANALYSIS.md`)
- **2.2 Formal Requirements Specification** (`SRS.md`, `FUNCTIONAL_REQUIREMENTS.md`, `NON_FUNCTIONAL_REQUIREMENTS.md`)
- **2.3 Agile Scenarios & Acceptance Baseline** (`USE_CASES.md`, `USER_STORIES.md`, `ACCEPTANCE_CRITERIA.md`)
- **2.4 Traceability & Gap Audit** (`RTM.md`, `REQUIREMENTS_GAP_ANALYSIS.md`)

### 3.0 System Architecture & Technical Design
- **3.1 High-Level Architecture & Topology Design**
  - 3.1.1 Microservice pipeline sequence diagrams
  - 3.1.2 Class diagrams and abstract base interfaces (`models.base`)
- **3.2 Data Contracts & Database Schema Design**
  - 3.2.1 Pydantic v2 transaction ingestion schemas
  - 3.2.2 SQLAlchemy relational schema for transaction logs and ledger blocks
- **3.3 OpenAPI v3 REST API Specification**
  - 3.3.1 Contract definitions for `/predict`, `/batch-predict`, `/explain`, `/metrics`
- **3.4 Stage-Gate 1 Review & Approval**

### 4.0 Environment & Dependency Setup
- **4.1 Dependency Formulation & Manifests**
  - 4.1.1 Python environment pinning (`pyproject.toml`, `requirements.txt`)
  - 4.1.2 Build isolation and toolchain configuration (ruff, pytest, mypy)
- **4.2 Containerization & Deployment Configuration**
  - 4.2.1 Dockerfile multi-stage build setup
  - 4.2.2 Environment variable configuration (`.env.example`)
- **4.3 Test Harness Scaffolding**
  - 4.3.1 Pytest fixtures, mock caches, and test runners

### 5.0 Data Engineering & Synthetic Generator Pipeline
- **5.1 Synthetic QR Transaction Generator (`data.generator`)**
  - 5.1.1 Legitimate transaction stream synthesis (baseline distributions)
  - 5.1.2 Sticker replacement / Quishing fraud vector generator
  - 5.1.3 Dynamic QR payload tampering / MITM fraud vector generator
  - 5.1.4 Velocity micro-probing fraud vector generator
- **5.2 Feature Extraction Pipeline (`data.feature_engineering`)**
  - 5.2.1 Haversine spatial displacement calculator
  - 5.2.2 Shannon entropy analyzer for QR payload strings
  - 5.2.3 Stateful sliding window velocity aggregator ($V_{5\text{m}}, V_{1\text{h}}, V_{24\text{h}}$)
  - 5.2.4 Customer baseline Z-score calculator
- **5.3 Data Preprocessing & Class Imbalance Balancing (`data.preprocessor`, `models.trainer`)**
  - 5.3.1 RobustScaler / StandardScaler normalization
  - 5.3.2 Stratified train/val/test temporal splitting ($70/15/15$)
  - 5.3.3 SMOTE and Borderline-SMOTE oversampling pipeline

### 6.0 Machine Learning Engine & Anomaly Detection
- **6.1 Supervised Classifier Benchmark Suite (`models.supervised`)**
  - 6.1.1 Baseline Logistic Regression and Decision Tree implementations
  - 6.1.2 Random Forest classifier implementation
  - 6.1.3 Support Vector Machine (SVM with RBF kernel)
  - 6.1.4 LightGBM classifier implementation (Production Engine)
  - 6.1.5 PyTorch Tabular Multi-Layer Perceptron (Deep Neural Baseline)
- **6.2 Unsupervised Anomaly Detection (`models.unsupervised`)**
  - 6.2.1 Isolation Forest implementation fitted on legitimate transaction vectors
  - 6.2.2 Anomaly score normalization ($S_{\text{anomaly}} \in [0, 1]$)
- **6.3 Hybrid Risk Scoring & Decision Gating (`models.ensemble`)**
  - 6.3.1 Calibrated composite score aggregator ($S_{\text{composite}} = 0.70 P_{\text{sup}} + 0.30 S_{\text{unsup}}$)
  - 6.3.2 Three-tier gating policy (`APPROVE`, `CHALLENGE_MFA`, `BLOCK`)
  - 6.3.3 Ambiguous score zero-day anomaly escalation override
- **6.4 Automated Training & Model Evaluation Runner (`models.trainer`)**
  - 6.4.1 Comprehensive cross-validation and hyperparameter tuning
  - 6.4.2 Metric calculation: Recall ($\ge 95\%$), Precision ($\ge 90\%$), F2, PR-AUC, Asymmetric Loss

### 7.0 Explainable AI (XAI) & Cryptographic Audit Ledger
- **7.1 Explainable AI Engine (`xai.explainer`)**
  - 7.1.1 SHAP TreeExplainer integration for LightGBM
  - 7.1.2 Local Shapley feature contribution calculations
  - 7.1.3 Top-3 human-readable reason code extractor
  - 7.1.4 Selective synchronous execution policy for latency optimization
- **7.2 Cryptographic Audit Ledger Engine (`ledger.audit_chain`)**
  - 7.2.1 Deterministic Genesis Block initialization ($H_0$)
  - 7.2.2 Sequential SHA-256 block chaining logic ($H_k = \text{SHA256}(H_{k-1} \,\|\, \text{TxID} \,\|\, S_{\text{comp}} \,\|\, \text{Verdict} \,\|\, t)$)
  - 7.2.3 SQLite ledger persistence and JSONL export
  - 7.2.4 Cryptographic chain verification and tamper detection utility

### 8.0 Backend API Gateway & Resilient Serving (FastAPI)
- **8.1 Core Microservice Architecture (`api.server`, `api.routes`)**
  - 8.1.1 Endpoint `/api/v1/predict` (sub-100ms inference)
  - 8.1.2 Endpoint `/api/v1/batch-predict` (bulk evaluation)
  - 8.1.3 Endpoint `/api/v1/explain` (on-demand SHAP attribution)
  - 8.1.4 Endpoint `/api/v1/metrics` and `/api/v1/health`
  - 8.1.5 Endpoint `/api/v1/ledger/verify` (audit chain validation)
- **8.2 State Cache Management (`backend.cache`)**
  - 8.2.1 In-memory thread-safe sliding window TTL cache (default offline)
  - 8.2.2 Pluggable Redis cache connector
- **8.3 Resilience & Fallback Circuit Breaker**
  - 8.3.1 120ms timeout interceptor
  - 8.3.2 Deterministic heuristic fallback engine (amount cap + velocity check)

### 9.0 Frontend Monitoring & Simulation UI (Streamlit)
- **9.1 Interactive Telemetry Dashboard (`ui.app`)**
  - 9.1.1 Live transaction feed with color-coded risk badges
  - 9.1.2 Aggregate risk score gauges and throughput metrics
  - 9.1.3 Historical audit ledger inspection table
- **9.2 Fraud Scenario Simulator**
  - 9.2.1 Interactive sliders for distance, entropy, velocity, and amount
  - 9.2.2 Live verdict execution and visual SHAP waterfall plot rendering
- **9.3 Model Benchmark Comparison Viewer**
  - 9.3.1 ROC/PR curve visualization and confusion matrix plots
  - 9.3.2 Tabular algorithm performance scoreboard

### 10.0 Privacy-Preserving Simulation (Federated Learning)
- **10.1 Decentralized Partitioning & Client Simulation (`research.federation`)**
  - 10.1.1 Partition synthetic dataset across 3 distinct merchant institutions
  - 10.1.2 Local training simulation on client edge nodes
- **10.2 Federated Averaging (FedAvg) Coordinator**
  - 10.2.1 Weight extraction and weighted parameter averaging
  - 10.2.2 Global model distribution and benchmark comparison vs centralized models

### 11.0 Verification, Validation, Benchmarking & Final Thesis Release
- **11.1 Test Suite Execution (`tests/`)**
  - 11.1.1 Unit tests for all modules ($\ge 85\%$ coverage)
  - 11.1.2 Integration tests for end-to-end payment lifecycle
- **11.2 Performance & Latency Load Profiling**
  - 11.2.1 Automated concurrency load testing (Locust / HTTP benchmark)
  - 11.2.2 Percentile verification (p50 $< 35\text{ ms}$, p95 $< 75\text{ ms}$, p99 $\le 100\text{ ms}$)
- **11.3 Final Documentation & Academic Report Package**
  - 11.3.1 Comprehensive verification report and benchmark tables
  - 11.3.2 Final stage-gate review and thesis demonstration sign-off

