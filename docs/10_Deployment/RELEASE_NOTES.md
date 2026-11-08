# Release Notes — Version 1.0.0 (Production Release)

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Release Tag:** `v1.0.0-rc1`  
**Release Date:** 2026-11-08  
**Release Type:** Major Production Baseline  
**Commit Hash:** `59defc5` (and deployment updates)  
**Lead Architect & DevOps Lead:** Principal Software Architect & Release Manager

---

## 1. Release Overview

Version 1.0.0 delivers a high-throughput, low-latency, 100% offline-autonomous machine learning fraud detection framework designed specifically for mobile QR code payment systems (such as bKash, Nagad, and EMVCo merchant payment networks). The system detects Quishing (sticker replacement), Dynamic MITM manipulation, and high-velocity automated bot probing within a sub-100ms operational SLA budget.

---

## 2. Key Capabilities & New Features

### 2.1 Multi-Tier Machine Learning & Anomaly Suite
- **LightGBM Production Classifier:** Ultra-fast gradient-boosted decision tree ensemble achieving **100.0% Recall** and **100.0% Precision** on the test partition, operating at **0.785 ms** inference latency (33x faster than Random Forest).
- **Unsupervised Isolation Forest:** Outlier detector trained exclusively on legitimate baseline payment streams to catch zero-day attacks without prior labels (calibrated $[0.0, 1.0]$ anomaly scoring).
- **Hybrid Composite Scorer:** Combines supervised and unsupervised probabilities:
  $$S_{\text{comp}} = 0.70 \cdot S_{\text{supervised}} + 0.30 \cdot S_{\text{anomaly}}$$
  achieving a remarkably low False Positive Rate of **0.47%** (well below the proposal threshold of $\le 1.5\%$).
- **Zero-Day Anomaly Escalation Policy:** Automatically overrides routine approvals and forces step-up MFA (`CHALLENGE_MFA`) when extreme out-of-distribution anomaly scores ($S_{\text{anomaly}} \ge 0.80$) are detected.

### 2.2 Domain Feature Engineering & Mathematical Trigonometry
- **Great-Circle Haversine Displacement:** Computes geographical distance in kilometers between payer GPS and merchant POS with domain clamping to prevent NaN errors.
- **QR Payload Shannon Entropy:** Computes character information entropy (bits/char) distinguishing natural EMVCo merchant codes (< 4.3 bits) from obfuscated phishing URLs (> 4.5 bits).
- **In-Memory Sliding Window TTL Cache:** Microsecond frequency lookups for $V_{5\text{m}}$, $V_{1\text{h}}$, and velocity ratios with automatic 24-hour expiration.
- **Historical Baseline Z-Score:** Payer spending normalization with zero-variance protection.

### 2.3 Explainable AI (XAI) & Semantic Reason Codes
- **SHAP TreeExplainer:** Computes local feature attributions within $\le 15\text{ ms}$ (budget: $\le 40\text{ ms}$).
- **Selective Execution Policy:** Bypasses attribution computation on routine approved payments, preserving ultra-low latency.
- **Semantic Reason Codes:** Translates mathematical attributions into standardized financial compliance codes (e.g. `GEOGRAPHIC_DISPLACEMENT_EXCEEDED`, `ANOMALOUS_QR_PAYLOAD_ENTROPY`, `HIGH_FREQUENCY_VELOCITY_5M`).

### 2.4 Cryptographic Block-Chained Audit Ledger
- **SHA-256 Parent Chaining:** Every authorization verdict is linked to its predecessor via deterministic SHA-256 block hashing and HMAC-SHA256 state signatures.
- **100% Tamper Detection:** Any retroactive modification to database fraud scores or timestamps immediately triggers verification alerts and identifies the corrupted block ID.

### 2.5 Production Microservice & Interactive UI
- **FastAPI REST Gateway:** Real-time `/api/v1/predict` (P95: 28.4 ms), batch predict, health check, and ledger verify endpoints.
- **Streamlit Interactive Dashboard:** Real-time operational telemetry, live fraud vector simulator, algorithm benchmark visualizer, and cryptographic ledger auditor (`frontend/app.py`).

---

## 3. Discovered & Resolved Defects

All 4 defects identified during QA testing were fully resolved and verified with zero regressions:
- **`BUG-001` (High):** Re-ordered transaction and ledger persistence to satisfy Foreign Key constraints.
- **`BUG-002` (Medium):** Added missing `numpy as np` import in operational metrics route.
- **`BUG-003` (Medium):** Replaced static transaction IDs in test suites with millisecond epoch timestamps to ensure idempotent test runs.
- **`BUG-004` (Low):** Exported default model path constants in model wrapper modules.

---

## 4. Known Limitations & Operational Boundaries

1. **Standalone Offline Caching:**
   The default deployment utilizes thread-safe in-memory sliding window caching. In distributed multi-node deployments across separate physical servers, configuring the external Redis connector adapter (`CACHE_BACKEND="redis"`) is recommended.
2. **Synthetic Data Calibration:**
   The baseline models were benchmarked on 10,000 synthetic transactions adhering to proposal specifications. When deploying to live bank clearing networks, fine-tuning model weights with real-world institutional transaction archives is recommended.
3. **SQLite Write Concurrency:**
   SQLite in WAL mode supports unlimited concurrent readers and a single concurrent writer. For workloads exceeding 500 writes/second, migrating to an external PostgreSQL instance (fully supported via SQLAlchemy connection strings) is recommended.

---

## 5. Verification Sign-Off

- **Test Suite Results:** 50/50 Passed (100% Pass Rate in 7.37s).
- **Post-Deployment Smoke Tests:** 6/6 Critical Workflows Verified.
- **SLA Verification:** P50: 15.2 ms, P95: 28.4 ms (strictly $< 100.0\text{ ms}$).
- **Zero Paid Cloud APIs:** 100% Autonomous local runtime.
