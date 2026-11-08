# Technical Recommendations & Technology Stack Selection

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 04)  
**Parent Document:** `docs/04_Technical_Research/TECHNOLOGY_COMPARISON.md`  
**Reference Document:** `source/PROJECT_SPEC.md` | `AGENT_RULES.md`

---

## 1. Selected Technology Stack & Justification

| Architectural Tier | Selected Technology | Primary Justification |
| :--- | :--- | :--- |
| **Language & Runtime** | **Python 3.10+ (x86-64)** | High-performance asynchronous ecosystem, comprehensive ML library support, and enterprise runtime stability. |
| **Primary Supervised Classifier** | **LightGBM (`lightgbm >= 4.1.0`)** | Industry-leading tabular classification speed ($3 - 8\text{ ms}$ inference), high recall ($> 97\%$), native leaf-wise GBDT, minimal RAM usage ($< 50\text{ MB}$), and direct SHAP TreeExplainer optimization. |
| **Supervised Benchmarks** | **Scikit-Learn (Random Forest, SVM, LogReg) & PyTorch (Tabular MLP)** | Fulfills proposal mandate for comprehensive comparative algorithm benchmarking across bagging, kernel methods, and deep neural networks. |
| **Unsupervised Anomaly Engine**| **Isolation Forest (PyOD / Scikit-Learn)** | Detects zero-day and unmapped fraud exploits via recursive random partitioning ($O(n)$ complexity), executing in $< 10\text{ ms}$. |
| **Data Imbalance Rebalancing** | **Borderline-SMOTE (`imbalanced-learn`)** | Overcomes majority-class bias by generating synthetic instances along ambiguous decision boundaries ($DANGER$ set) without injecting noise into safe zones. |
| **Explainable AI (XAI)** | **SHAP TreeExplainer (`shap >= 0.43.0`)** | Delivers exact, game-theoretic Shapley feature attributions in polynomial time ($< 35\text{ ms}$), providing human-readable reason codes for regulatory compliance. |
| **API Serving Gateway** | **FastAPI + Uvicorn (`fastapi >= 0.104`)** | High-concurrency asynchronous ASGI microservice with sub-5ms overhead and compiled Rust-backed schema validation via Pydantic v2. |
| **State & Velocity Caching** | **In-Memory TTL Cache (with optional Redis Adapter)** | Pure Python/C thread-safe sliding window cache providing sub-millisecond velocity lookups offline; pluggable Redis adapter for production clustering. |
| **Storage & Audit Ledger** | **SQLite (WAL Mode) + SHA-256 Hash Chaining** | Zero-configuration single-file relational storage with Write-Ahead Logging; cryptographic parent-hash block chaining ensures mathematical non-repudiation. |
| **Interactive UI & Telemetry**| **Streamlit (`streamlit >= 1.28.0`)** | Rapid, pure-Python dashboard rendering real-time transaction streams, risk dials, SHAP force plots, and interactive fraud vector simulation sliders. |

---

## 2. Rejected Alternatives & Technical Rationale

| Layer | Rejected Alternative | Technical Reason for Rejection |
| :--- | :--- | :--- |
| **Machine Learning** | **TensorFlow / Keras** | Heavy initialization overhead and excessive memory footprint ($> 250\text{ MB}$) that violates container hardware budgets. |
| **Machine Learning** | **XGBoost / CatBoost** | LightGBM demonstrated faster training and lower inference latency on numerical tabular vectors without sacrificing predictive recall. |
| **Anomaly Detection** | **Local Outlier Factor (LOF)** | $O(n^2)$ computational complexity during inference violates the sub-35ms model latency SLA under production concurrency. |
| **Oversampling** | **Random Under-Sampling (RUS)**| Discards massive volumes of legitimate transaction data, leading to severe false-positive degradation at POS terminals. |
| **Explainability** | **LIME** | Local perturbation approach is too computationally expensive ($80 - 250\text{ ms}$) for synchronous real-time payment authorization. |
| **Backend API** | **Flask / Django** | Synchronous WSGI thread blocking degrades concurrent throughput; lacks native async event loops and Rust-compiled schema validation. |
| **Ledger** | **Public Distributed Blockchain**| Block finality latency ($> 1\text{s}$) and network gas/infrastructure overhead violate sub-100ms real-time constraints and introduce scope creep. |
| **Frontend UI** | **React / Next.js SPA** | Introduces Node.js build complexity, separate tooling, and extensive frontend overhead without adding technical value to core thesis validation. |

---

## 3. Key Technical Risks & Engineered Safeguards

1. **Risk: Synchronous SHAP Attribution Causes Latency Spikes ($> 100\text{ ms}$)**
   - *Engineered Safeguard:* Selective execution policy. Automatic SHAP calculation executes strictly for transactions resulting in `CHALLENGE_MFA` or `BLOCK` (or explicit `/api/v1/explain` queries). Low-risk payments (`APPROVE`) bypass SHAP, maintaining p99 latency $< 50\text{ ms}$.
2. **Risk: ML Thread Hang Stalling Payment Checkouts**
   - *Engineered Safeguard:* Deterministic heuristic fallback circuit breaker. An asyncio timeout interceptor triggers at $120\text{ ms}$, failing over to hardcoded amount and velocity caps within $10\text{ ms}$.
3. **Risk: External Redis Server Dependency Halting Standalone Execution**
   - *Engineered Safeguard:* Default in-memory thread-safe sliding window cache. The system requires zero external daemons to run out-of-the-box.
4. **Risk: Synthetic Data Overfitting in SMOTE Pipeline**
   - *Engineered Safeguard:* Strict partition isolation. Borderline-SMOTE is applied strictly to training folds; validation and test splits remain un-oversampled and chronologically ordered.

---

## 4. Decisions Requiring Stakeholder Approval

Before proceeding to **Sprint 1: System Architecture, Data Contracts & Environment Scaffolding (Milestone M2)**, the following technical selections are submitted for formal authorization:

1. **Approval of Primary Production Stack:** Authorize Python 3.10+, LightGBM, Isolation Forest, SHAP TreeExplainer, FastAPI, and Streamlit as the primary operational architecture.
2. **Approval of Deep Learning Benchmark Baseline:** Authorize PyTorch Tabular Multi-Layer Perceptron (CPU execution) as the candidate deep neural architecture.
3. **Approval of Standalone Caching Strategy:** Authorize the thread-safe in-memory sliding window TTL cache as the default state store, with optional Redis adapter configuration.
4. **Approval of Ledger Architecture:** Authorize SQLite WAL relational persistence with SHA-256 block chaining and `/api/v1/ledger/verify` audit API.

