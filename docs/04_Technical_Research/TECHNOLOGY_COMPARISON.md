# Technology Comparison & Architectural Trade-Off Analysis

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 04)  
**Author:** Principal Software Architect & Research Engineer  
**Parent Document:** `source/PROJECT_SPEC.md` | `docs/02_Requirements/SRS.md`

---

## 1. Executive Summary

This document presents a comprehensive, evidence-based comparative evaluation of candidate technologies, frameworks, and algorithms across all architectural layers of the system. In accordance with project requirements, candidate selections are evaluated against five core criteria:
1. **Inference Latency:** Ability to complete computation within the allocated sub-component budget ($\le 100\text{ ms}$ total).
2. **Computational Footprint:** Operability within a 4 GB RAM container on standard x86 CPU hardware without mandatory GPU dependencies.
3. **Accuracy & Recall on Skewed Data:** Robust handling of acute class imbalance ($\le 1\%$ fraud).
4. **Offline Autonomy:** 100% functionality without external cloud subscriptions or proprietary paid APIs.
5. **Permissive Licensing:** Compatibility with open-source academic and commercial software standards (MIT, Apache 2.0, BSD).

---

## 2. Supervised Machine Learning Engines

| Candidate Framework | Median Inference Latency (Tabular) | Memory Footprint | Handling of Tabular Imbalance | Training Velocity | Selected / Rejected | Architectural Justification |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **LightGBM** | **$\approx 3 - 8\text{ ms}$** | **$\approx 45\text{ MB}$** | **Excellent (built-in `is_unbalance`)** | **Ultra-Fast (GOSS + EFB)** | **SELECTED (Primary Production Engine)** | Delivers state-of-the-art tabular recall ($\approx 99\%$ in literature), native leaf-wise tree splitting, minimal RAM footprint, and instant SHAP TreeExplainer compatibility. |
| **Scikit-Learn (Random Forest)** | $\approx 12 - 25\text{ ms}$ | $\approx 85\text{ MB}$ | Good (`class_weight='balanced'`) | Moderate | **SELECTED (Benchmark Baseline)** | Standard, robust bagging baseline. Excellent interpretability and resistance to single-feature noise. |
| **PyTorch (Tabular MLP)** | $\approx 15 - 30\text{ ms}$ (CPU) | $\approx 120\text{ MB}$ | Moderate (requires custom loss) | Slow (CPU Epochs) | **SELECTED (Deep Neural Baseline)** | Implemented as a research benchmark to satisfy the proposal's mandate for deep neural variant comparison. |
| **XGBoost** | $\approx 6 - 15\text{ ms}$ | $\approx 65\text{ MB}$ | Excellent (`scale_pos_weight`) | Fast | *Rejected* | Slightly higher memory footprint and marginally slower training than LightGBM on tabular datasets without significant recall gains. |
| **CatBoost** | $\approx 10 - 20\text{ ms}$ | $\approx 110\text{ MB}$ | Excellent | Slow on CPU | *Rejected* | Best suited for high-cardinality categorical text fields; unnecessary overhead for numerical QR velocity/distance vectors. |
| **TensorFlow / Keras** | $\approx 25 - 50\text{ ms}$ | $\approx 250\text{ MB}$ | Moderate | Slow on CPU | *Rejected* | Prohibitive initialization overhead and memory consumption exceeding the 250MB model footprint budget. |

---

## 3. Unsupervised Anomaly Detection Engines

| Candidate Algorithm | In-Distribution Detection Speed | Contamination Tuning | Cold-Start Capability | Interpretability | Selected / Rejected | Architectural Justification |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Isolation Forest (PyOD / Scikit-Learn)** | **$\approx 4 - 10\text{ ms}$** | **Parametric (`contamination`)** | **High ($O(n \log n)$)** | **Moderate (Path length)** | **SELECTED (Primary Anomaly Engine)** | Isolates anomalies using recursive random hyperplanes. Linear time complexity $O(n)$, sub-10ms scoring, and optimal performance on low-dimensional numerical vectors. |
| **Deep Autoencoder (PyTorch)** | $\approx 20 - 45\text{ ms}$ | Non-parametric (Reconstruction error threshold) | Low (Needs extensive tuning) | Low (Latent bottleneck) | **SELECTED (Secondary Research Variant)** | Evaluated in `research/` to explore non-linear reconstruction loss for complex, multi-feature fraud clusters. |
| **Local Outlier Factor (LOF)** | $\approx 40 - 120\text{ ms}$ | Non-parametric | Very Low ($O(n^2)$ neighbor search) | High (Local density) | *Rejected* | Unacceptable $O(n^2)$ computational complexity during real-time inference; cannot meet sub-35ms model budget under production loads. |
| **One-Class SVM (RBF Kernel)** | $\approx 35 - 80\text{ ms}$ | Non-parametric ($\nu$-parameter) | Moderate ($O(n^2 - n^3)$) | Low (Kernel dual space) | *Rejected* | High quadratic scaling overhead with dataset size and sensitive to hyperparameter tuning under high noise. |

---

## 4. Class Imbalance Mitigation Techniques

| Technique | Method Mechanism | Risk of Overfitting | Computational Overhead | Selected / Rejected | Architectural Justification |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Borderline-SMOTE** | Generates synthetic samples strictly along the borderline decision boundary ($DANGER$ set). | Low | Moderate | **SELECTED (Primary Oversampling Strategy)** | Focuses interpolation on ambiguous boundary points between legitimate and fraudulent transactions, avoiding noise in deep majority space. |
| **Standard SMOTE** | Uniform linear interpolation across $k$-nearest minority neighbors. | Moderate | Low | **SELECTED (Benchmark Comparison)** | Proposal-mandated baseline technique for synthetic sample augmentation. |
| **ADASYN** | Adaptive synthesis weighted by minority sample difficulty distribution. | High | Moderate | *Rejected* | Prone to synthesizing outliers in extreme noise regions, diluting boundary precision for QR payment velocities. |
| **Random Under-Sampling (RUS)** | Randomly discards majority-class (legitimate) transactions. | None | Minimal | *Rejected* | Discards valuable legitimate transaction variance, increasing false-positive rates at merchant POS terminals. |

---

## 5. Explainable AI (XAI) Frameworks

| Framework | Execution Latency (Single Record) | Mathematical Foundation | Local Interpretability | Selected / Rejected | Architectural Justification |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **SHAP (TreeExplainer)** | **$\approx 15 - 35\text{ ms}$** | **Shapley Values (Game Theory)** | **Exact & Additive** | **SELECTED (Production XAI Engine)** | Exploits tree graph structure to compute exact Shapley values in polynomial time $O(T L D^2)$, satisfying both the regulatory non-black-box requirement and latency budget. |
| **LIME** | $\approx 80 - 250\text{ ms}$ | Local Surrogate Linear Model | Perturbation Approximation | **SELECTED (Offline Comparative Analysis)** | Valuable for model-agnostic benchmarking in `research/`, but too slow for synchronous real-time API serving. |
| **Integrated Gradients** | $\approx 50 - 150\text{ ms}$ | Path integral of gradients | Neural Networks only | *Rejected* | Inapplicable to gradient-boosted decision trees (LightGBM). |

---

## 6. Backend Application Frameworks

| Framework | Overhead Latency | Concurrency Architecture | Schema Validation Engine | Selected / Rejected | Architectural Justification |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **FastAPI + Uvicorn** | **$\approx 2 - 5\text{ ms}$** | **Asynchronous (ASGI / uvloop)** | **Pydantic v2 (Rust-backed core)** | **SELECTED (Primary API Microservice)** | Industry standard for high-performance ML microservices. Sub-5ms internal routing overhead, strict JSON deserialization via Pydantic v2, and automatic OpenAPI documentation. |
| **Flask + Gunicorn** | $\approx 10 - 20\text{ ms}$ | Synchronous (WSGI) | Manual / Marshmallow | *Rejected* | Synchronous blocking worker model struggles with concurrent inference; lacks native async state cache lookups. |
| **Django REST Framework** | $\approx 25 - 55\text{ ms}$ | Monolithic WSGI/ASGI | Serializers | *Rejected* | Heavyweight ORM and monolithic overhead unnecessary for a dedicated, microservice-based fraud detection engine. |

---

## 7. State & Velocity Caching Infrastructure

| Cache Backend | Retrieval Latency | External Daemon Required | Memory Footprint | Selected / Rejected | Architectural Justification |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **In-Memory TTL Cache (Thread-Safe)** | **$< 0.5\text{ ms}$** | **No (Pure Python/C)** | **$< 20\text{ MB}$** | **SELECTED (Default Standalone Mode)** | Guarantees 100% offline standalone capability out-of-the-box with sub-millisecond sliding window velocity computation and zero daemon setup. |
| **Redis** | $\approx 1.5 - 4\text{ ms}$ (TCP loopback) | Yes (`redis-server`) | $\approx 35\text{ MB}$ | **SELECTED (Optional Enterprise Adapter)** | Supported via pluggable configuration (`CACHE_BACKEND=redis`) for distributed multi-worker production deployments. |
| **Memcached** | $\approx 2 - 5\text{ ms}$ | Yes | $\approx 30\text{ MB}$ | *Rejected* | Lacks built-in key expiry sliding structures and sorted sets, complicating rolling time-window frequency counts. |

---

## 8. Persistence & Cryptographic Ledger Architecture

| Strategy | Write Latency | Verification Speed | Tamper Evident | Selected / Rejected | Architectural Justification |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Relational SQLite (WAL Mode) + SHA-256 Chaining** | **$< 5\text{ ms}$** | **Linear $O(N)$ Hash Recalculation** | **Yes (Parent Digest Linking)** | **SELECTED (Production Storage & Audit)** | Zero-configuration single-file database. Write-Ahead Logging (WAL) mode enables concurrent reads during writes. SHA-256 block linking provides mathematical non-repudiation. |
| **PostgreSQL + Hash Chaining** | $\approx 8 - 15\text{ ms}$ | Linear $O(N)$ | Yes | *Rejected (for default local baseline)* | Requires dedicated database server daemon; unnecessary overhead for local thesis evaluation (supported as future enhancement). |
| **Public/Private Distributed Blockchain (Ethereum / Hyperledger)** | $\approx 1500 - 15000\text{ ms}$ | Decentralized Consensus | Yes | *Rejected* | Prohibitive block finality latency ($> 1\text{s}$), transaction gas/resource overhead, and severe scope creep violating Rule 2 of `AGENT_RULES.md`. |

---

## 9. User Interface & Telemetry Dashboard

| Tool / Framework | Development Speed | Real-Time Telemetry | Charting / Visual XAI | Selected / Rejected | Architectural Justification |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Streamlit** | **Rapid (Python Native)** | **Native Auto-Refresh** | **Plotly / Matplotlib / SHAP** | **SELECTED (Primary Operational UI)** | Eliminates JavaScript/frontend build toolchains. Seamlessly displays live transaction tables, interactive risk sliders, and dynamic SHAP waterfall plots. |
| **Gradio** | Rapid | Focused on ML inputs | Basic | *Rejected* | Geared towards single-model demonstration rather than full operational fraud monitoring dashboards with audit ledger inspection. |
| **React + Tailwind + Vite** | Moderate-Slow | High (WebSockets) | Custom Canvas/D3 | *Rejected* | Introduces Node.js/npm dependencies, build complexity, and maintenance overhead without providing substantial value for thesis evaluation. |

---

## 10. Licensing Compliance Summary

All selected libraries carry permissive, royalty-free open-source licenses:
- **LightGBM:** Microsoft MIT License
- **Scikit-Learn:** BSD 3-Clause License
- **PyTorch:** Modified BSD License
- **FastAPI / Pydantic / Uvicorn:** MIT License
- **SHAP:** MIT License
- **Streamlit:** Apache License 2.0
- **SQLAlchemy:** MIT License

*Compliance Statement:* No copyleft (GPL/AGPL) viral licenses or commercial proprietary libraries are incorporated, guaranteeing full freedom for academic distribution and commercial adoption.

