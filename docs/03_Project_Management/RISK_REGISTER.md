# Risk Management Plan & Risk Register

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 03)  
**Parent Document:** `docs/03_Project_Management/PROJECT_MANAGEMENT_PLAN.md`  
**Reference Standards:** ISO 31000, PMBOK Risk Management

---

## 1. Risk Management Methodology

Risks are systematically evaluated based on Qualitative Probability and Impact metrics:
- **Probability ($P$):** Low (1), Medium (2), High (3)
- **Impact ($I$):** Low (1), Medium (2), High (3)
- **Risk Score ($R = P \times I$):**
  - **1 - 2:** Low Risk (Monitor)
  - **3 - 4:** Medium Risk (Manage proactively)
  - **6 - 9:** High / Critical Risk (Immediate mitigation plan mandatory)

---

## 2. Comprehensive Risk Register

| Risk ID | Category | Risk Description | $P$ | $I$ | Score | Trigger / Indicator | Mitigation Strategy | Contingency Plan | Owner |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :---: |
| **RSK-01** | **Technical** | **Inference Latency Exceeds 100ms SLA Under High Load:** SHAP computation or multi-model evaluation causes response delays. | Med (2) | High (3) | **6 (High)** | p95 latency $> 75\text{ ms}$ during load testing. | Enforce selective synchronous SHAP calculation for flagged transactions only; pre-compute scaler parameters; use lightweight LightGBM. | Engage heuristic fallback circuit breaker after $120\text{ ms}$; return cached decision. | Backend & ML Engineer |
| **RSK-02** | **Technical** | **Severe Class Imbalance Causes Model Overfitting on SMOTE Artifacts:** Synthetic samples skew decision boundaries. | Med (2) | High (3) | **6 (High)** | High validation recall but steep precision drop on holdout test set. | Use Borderline-SMOTE; tune $k$-neighbors; strictly evaluate models on un-oversampled, chronologically split test partitions. | Implement class-weighted cost loss functions in place of aggressive oversampling. | ML Engineer |
| **RSK-03** | **Architectural**| **External Redis Daemon Dependency Breaks Standalone Offline Constraint:** Missing local Redis instance halts execution. | High (3) | Med (2) | **6 (High)** | Connection refused error on `localhost:6379`. | Implement a thread-safe in-memory TTL cache adapter as the primary default; support Redis optionally via environment variable. | Automatic silent fallback to in-memory cache if Redis ping fails. | Backend Engineer |
| **RSK-04** | **Technical** | **Novel Unmapped Fraud Vectors Evade Supervised Classifier:** Attackers modify QR payloads in ways unseen during training. | High (3) | High (3) | **9 (Crit)**| Spike in undetected fraudulent chargebacks. | Deploy unsupervised Isolation Forest concurrently; implement ambiguous score escalation override policy. | Escalate any transaction with $S_{\text{anomaly}} > 0.80$ to `CHALLENGE_MFA`. | ML Engineer |
| **RSK-05** | **Operational** | **Excessive False Positive Rate Causes Customer Checkout Friction:** High-value legitimate payments blocked erroneously. | Med (2) | High (3) | **6 (High)** | FPR $> 1.5\%$ on validation evaluation runs. | Implement three-tier decision gating with `CHALLENGE_MFA` step-up instead of hard `BLOCK` for ambiguous scores ($0.30 - 0.70$). | Re-calibrate decision thresholds using asymmetric loss utility function ($C_{\text{friction}}$). | Risk Policy Manager |
| **RSK-06** | **Security** | **Cryptographic Audit Ledger Corruption or Write Contention:** Concurrent SQLite write locks degrade API throughput. | Med (2) | Med (2) | **4 (Med)** | SQLite `database is locked` OperationalErrors. | Utilize Write-Ahead Logging (WAL) mode in SQLite; execute ledger commits asynchronously via background worker queue. | Buffer blocks in in-memory queue and batch-commit to ledger table. | Backend Engineer |
| **RSK-07** | **Compliance** | **Accidental Plaintext PII Ingestion or Storage:** Raw customer IDs stored in cleartext logs. | Low (1) | High (3) | **3 (Med)** | Plaintext account numbers found in SQLite dumps. | Enforce strict Pydantic sanitization and SHA-256 salted hashing at the API gateway layer before data touches feature vectors. | Automated static security test that fails builds if non-hashed identifiers are detected. | Security Architect |
| **RSK-08** | **Technical** | **PyTorch Deep MLP Memory Overhead Exceeds 250MB Footprint:** Model tensor allocations saturate memory limits. | Med (2) | Low (1) | **2 (Low)** | Container RAM usage exceeds budget ($> 250\text{ MB}$). | Optimize network depth (compact 3-layer tabular MLP); prune weights or export to lightweight ONNX runtime. | Disable PyTorch MLP from online real-time serving; retain LightGBM as sole production engine. | ML Engineer |
| **RSK-09** | **Governance** | **Requirement Creep Violating Approved Thesis Scope:** Unauthorized additions of live banking APIs or blockchain mining. | Med (2) | Med (2) | **4 (Med)** | Backlog items created outside of `source/PROJECT_SPEC.md`. | Enforce `AGENT_RULES.md` and mandatory stage-gate approval reviews with the Product Owner. | Reject out-of-scope tasks during Sprint Planning. | Scrum Master / PM |
| **RSK-10** | **Technical** | **Drift Between Synthetic Data and Real-World QR Payment Realities:** Synthetic patterns fail to represent actual user velocity. | Med (2) | Med (2) | **4 (Med)** | Statistical distribution divergence across empirical benchmarks. | Anchor synthetic generator distributions to published financial benchmarks cited in thesis proposal literature. | Adjust covariance matrices and noise injection parameters in `data.generator`. | ML Researcher |

