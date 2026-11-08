# Non-Functional Requirements Specification (NFRS)

**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 02)  
**Parent Document:** `docs/02_Requirements/SRS.md`  
**Reference Document:** `source/PROJECT_SPEC.md`

---

## 1. Performance & Latency Requirements (`NFR-PERF`)

- **NFR-PERF-001: End-to-End Inference Latency Budget**  
  The total server-side execution time for the single transaction inference endpoint (`/api/v1/predict`) MUST adhere to the following percentile thresholds under normal load (50 concurrent requests):
  - **p50 (Median Latency):** $< 35\text{ ms}$
  - **p95 Latency:** $< 75\text{ ms}$
  - **p99 Latency:** $\le 100\text{ ms}$

  *Sub-Component Budget Breakdown:*
  | Pipeline Stage | Maximum Allocated Time |
  | :--- | :--- |
  | Payload Ingestion & Validation | $< 15\text{ ms}$ |
  | Feature Engineering & Cache Lookup | $< 15\text{ ms}$ |
  | Dual-Model ML Inference | $< 35\text{ ms}$ |
  | Dynamic SHAP Attribution (if flagged) | $< 40\text{ ms}$ |
  | Ledger Commit & Storage | $< 10\text{ ms}$ |

- **NFR-PERF-002: Sustained Throughput Capacity**  
  The FastAPI service MUST sustain a minimum throughput of $200\text{ requests per second (req/s)}$ on a standard 4-core virtualized CPU environment without dropping connections or leaking memory.

- **NFR-PERF-003: High-Speed Synthetic Data Generation & SMOTE**  
  The data synthesis and SMOTE oversampling pipeline MUST process at least $10,000\text{ records per second}$ during offline model training routines.

---

## 2. Accuracy & Fraud Detection Metrics (`NFR-ACC`)

- **NFR-ACC-001: Minimum Fraud Recall Ceiling**  
  The operational hybrid model MUST achieve a minimum Recall (Sensitivity) of:
  $$\text{Recall} = \frac{TP}{TP + FN} \ge 95.0\% \quad (0.95)$$
  on the holdout out-of-time evaluation test partition. Undetected fraud represents unacceptable monetary loss.

- **NFR-ACC-002: Minimum Precision & False Positive Rate Control**  
  The model MUST maintain a minimum Precision of:
  $$\text{Precision} = \frac{TP}{TP + FP} \ge 90.0\% \quad (0.90)$$
  and MUST cap the False Positive Rate (FPR) at:
  $$\text{FPR} = \frac{FP}{FP + TN} \le 1.5\% \quad (0.015)$$
  to avoid excessive customer friction and false declines at merchant POS terminals.

- **NFR-ACC-003: Asymmetric Cost Function Optimization**  
  During hyperparameter tuning and model selection, models MUST be ranked and optimized against the proposal's asymmetric financial loss utility function:
  $$\text{Total Cost} = C_{\text{fraud}} \cdot FN + C_{\text{friction}} \cdot FP + C_{\text{review}} \cdot (\text{Challenged Cases})$$
  Default cost weights: $C_{\text{fraud}} = \$150.00$, $C_{\text{friction}} = \$5.00$, $C_{\text{review}} = \$0.50$.

- **NFR-ACC-004: Precision-Recall Area Under Curve (PR-AUC)**  
  Given the acute class imbalance ($\le 1\%$ fraud rate), model discriminative capability MUST be validated using PR-AUC, targeting a benchmark of $\text{PR-AUC} \ge 0.88$.

---

## 3. Reliability, Resilience & Fault Tolerance (`NFR-REL`)

- **NFR-REL-001: Graceful Deterministic Fallback on Timeout**  
  If ML model inference exceeds $120\text{ ms}$ due to system load or thread contention, the system MUST terminate the ML process and execute the deterministic heuristic rule engine within $10\text{ ms}$, ensuring the customer payment is never stalled indefinitely.

- **NFR-REL-002: Fault-Isolated Service Architecture**  
  A failure in auxiliary services (e.g., Streamlit UI crash, SQLite log write lock, or SHAP explanation error) MUST NOT cause payment inference in FastAPI to fail or reject valid transactions.

- **NFR-REL-003: Idempotency & Duplicate Prevention**  
  The system MUST track `transaction_id` within a sliding 60-second window. Resubmission of an identical `transaction_id` within this window MUST return the cached decision and prevent duplicate debiting or duplicate ledger entries.

---

## 4. Resource & Hardware Constraints (`NFR-RES`)

- **NFR-RES-001: Model Memory Footprint**  
  The total serialized and active in-memory footprint of all loaded models (LightGBM classifier + Isolation Forest + Scalers) MUST NOT exceed $250\text{ MB}$.

- **NFR-RES-002: Execution Environment Footprint**  
  The entire application stack (API gateway, state cache, ML models, and audit logger) MUST be capable of running smoothly inside a standard container allocated:
  - RAM: $\le 4\text{ GB}$
  - CPU: $\ge 2\text{ virtual cores}$ (x86-64)
  - Dedicated GPU: **None required** (full CPU inference capability).

---

## 5. Security, Privacy & Compliance (`NFR-SEC`)

- **NFR-SEC-001: Zero Plaintext PII Persistence**  
  Personal Identifiable Information (customer names, raw bank account numbers, physical card numbers) MUST NEVER be ingested, logged, or stored in plaintext. All identifiers MUST be salted and cryptographically hashed (SHA-256).

- **NFR-SEC-002: Cryptographic Ledger Immutability**  
  All audit log entries MUST be cryptographically bound using SHA-256 block chaining. Any manual alteration of historical transaction records, scores, or timestamps MUST invalidate the chain verification check.

- **NFR-SEC-003: Input Sanitization & Adversarial Defenses**  
  Numerical inputs MUST be bounded and clamped to valid physiological/financial ranges (e.g., amount $> 0$, latitude $[-90, +90]$, longitude $[-180, +180]$, scan latency $[0, 600000\text{ ms}]$) to prevent adversarial perturbation attacks designed to evade decision thresholds.

---

## 6. Maintainability, Portability & Code Quality (`NFR-MAINT`)

- **NFR-MAINT-001: PEP 8 & Static Typing Compliance**  
  All backend codebase MUST adhere to PEP 8 standards with complete type annotations passing `mypy --strict` or standard `ruff / flake8` linting checks.

- **NFR-MAINT-002: Automated Test Coverage**  
  The codebase MUST maintain an automated test coverage of $\ge 85\%$ across all core modules (`data`, `models`, `xai`, `ledger`, `api`).

- **NFR-MAINT-003: Offline Portability**  
  The entire system MUST be executable in an air-gapped / offline environment without calling external network APIs or third-party paid services.

