# Acceptance Criteria Specification

**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 02)  
**Parent Document:** `docs/02_Requirements/SRS.md`  
**Syntax Standard:** Gherkin (`Given / When / Then`)  
**Reference Document:** `source/PROJECT_SPEC.md`

---

## 1. Data Ingestion & Contextual Feature Pipeline

### AC-01: Schema Deserialization & Boundary Validation (Ref: US-01, FR-ING-001)
- **Scenario 1: Valid Ingestion Payload**
  - **Given** an HTTP POST request to `/api/v1/predict` containing all 16 required attributes formatted correctly
  - **When** the payload is deserialized by the API gateway
  - **Then** the request MUST pass schema validation without warnings and proceed to the feature pipeline.
- **Scenario 2: Negative Amount or Out-of-Bound Coordinates**
  - **Given** an incoming transaction payload with `amount: -45.00` or `payer_latitude: 195.4`
  - **When** the request is evaluated against the Pydantic schema
  - **Then** the system MUST reject the request immediately with `HTTP 422 Unprocessable Entity`
  - **And** the JSON response MUST specify the offending field name and validation constraint violated.

### AC-02: Spatial Haversine Distance Calculation (Ref: US-02, FR-FEA-001)
- **Scenario 1: Co-located Payer and Merchant**
  - **Given** payer coordinates `(23.8103, 90.4125)` and merchant coordinates `(23.8105, 90.4128)`
  - **When** the Haversine distance algorithm executes
  - **Then** the computed spatial distance MUST be $\le 0.05\text{ km}$ ($50\text{ meters}$) with precision to 4 decimal places.
- **Scenario 2: Severe Remote Spoofing Discrepancy**
  - **Given** payer coordinates `(23.8103, 90.4125)` (Dhaka) and merchant coordinates `(22.3569, 91.7832)` (Chittagong)
  - **When** the Haversine distance algorithm executes
  - **Then** the computed spatial distance MUST exceed $200.0\text{ km}$
  - **And** the downstream feature vector MUST reflect a significant spatial anomaly.

### AC-03: QR Payload Shannon Entropy (Ref: US-03, FR-FEA-002)
- **Scenario 1: Standard Plaintext Merchant URI**
  - **Given** a decoded QR payload string `"https://pay.merchant.com/checkout?id=M9982"`
  - **When** Shannon entropy $H(X) = -\sum P(x) \log_2 P(x)$ is calculated
  - **Then** the entropy score MUST evaluate to $< 4.5\text{ bits/char}$.
- **Scenario 2: Heavily Obfuscated / Encrypted Malicious URI**
  - **Given** a suspicious QR payload `"https://x9.io/q?token=a8f9c4b2e1d09876faec12938475"`
  - **When** Shannon entropy is calculated
  - **Then** the entropy score MUST evaluate to $\ge 4.5\text{ bits/char}$.

### AC-04: Stateful Velocity Counting (Ref: US-04, FR-FEA-003)
- **Scenario 1: Rapid Micro-Probing Frequency**
  - **Given** a payer account that has initiated 6 transactions within the preceding 120 seconds
  - **When** a new transaction request is evaluated
  - **Then** the in-memory velocity lookup MUST return $V_{5\text{m}} = 6$
  - **And** the calculated velocity ratio MUST trigger an elevated risk signal in the feature vector.

---

## 2. Hybrid Machine Learning Scoring & Gating

### AC-05: Supervised Benchmark Performance (Ref: US-06, NFR-ACC-001, NFR-ACC-002)
- **Scenario 1: Production Model Accuracy Thresholds**
  - **Given** the trained LightGBM model evaluated against the holdout test set (un-oversampled, $\le 1\%$ fraud)
  - **When** classification metrics are computed
  - **Then** the model Recall MUST be $\ge 0.950$ ($95.0\%$)
  - **And** the model Precision MUST be $\ge 0.900$ ($90.0\%$)
  - **And** the False Positive Rate MUST be $\le 0.015$ ($1.5\%$)
  - **And** PR-AUC MUST be $\ge 0.88$.

### AC-06: Unsupervised Anomaly Detection (Ref: US-07, FR-MOD-002)
- **Scenario 1: Identification of Outlier Transaction**
  - **Given** a transaction with an unprecedented combination of feature values (e.g., zero scan latency, extreme velocity, high entropy)
  - **When** processed by the Isolation Forest model
  - **Then** the returned anomaly score $S_{\text{anomaly}}$ MUST be $\ge 0.80$ on a normalized $[0, 1]$ scale.

### AC-07: Composite Risk Gating & Decision Tiers (Ref: US-08, US-09, FR-DEC-001)
- **Scenario 1: Low-Risk Transaction Approval**
  - **Given** $P_{\text{supervised}} = 0.05$ and $S_{\text{anomaly}} = 0.10$
  - **When** composite risk score is evaluated: $S_{\text{composite}} = (0.7 \times 0.05) + (0.3 \times 0.10) = 0.065$
  - **Then** the system MUST return verdict `APPROVE`
  - **And** bypass real-time SHAP generation to conserve compute latency.
- **Scenario 2: Medium-Risk Step-Up Challenge**
  - **Given** $P_{\text{supervised}} = 0.45$ and $S_{\text{anomaly}} = 0.50 \implies S_{\text{composite}} = 0.465$
  - **When** evaluated against decision thresholds ($0.30 \le S_{\text{composite}} \le 0.70$)
  - **Then** the system MUST return verdict `CHALLENGE_MFA`
  - **And** generate local SHAP reason codes.
- **Scenario 3: High-Risk Transaction Block**
  - **Given** $P_{\text{supervised}} = 0.88$ and $S_{\text{anomaly}} = 0.80 \implies S_{\text{composite}} = 0.856$
  - **When** evaluated against decision thresholds ($S_{\text{composite}} > 0.70$)
  - **Then** the system MUST return verdict `BLOCK`
  - **And** generate local SHAP reason codes.

### AC-08: Zero-Day Anomaly Escalation Override (Ref: US-09, FR-DEC-002)
- **Scenario 1: Ambiguous Supervised Score with High Anomaly**
  - **Given** $P_{\text{supervised}} = 0.35$ (normally low-risk/ambiguous)
  - **And** $S_{\text{anomaly}} = 0.86$ ($> 0.80$, severe structural outlier)
  - **When** the decision override policy is evaluated
  - **Then** the system MUST override standard composite gating and escalate the verdict directly to `CHALLENGE_MFA`.

---

## 3. Explainable AI & Cryptographic Audit Ledger

### AC-09: Local SHAP Feature Explanations (Ref: US-10, US-11, FR-XAI-001, FR-XAI-002)
- **Scenario 1: Extraction of Top-3 Explanatory Reason Codes**
  - **Given** a transaction assigned verdict `BLOCK`
  - **When** the SHAP TreeExplainer calculates feature attributions
  - **Then** the system MUST identify the top 3 positive Shapley contributors ($\phi_j$)
  - **And** format them into structured strings (e.g., `["AmountDeviation (+0.34)", "HaversineDistance (+0.28)", "ScanVelocity_1h (+0.19)"]`).

### AC-10: Cryptographic Hash Chaining Integrity (Ref: US-12, US-13, FR-AUD-001, FR-AUD-003)
- **Scenario 1: Continuous Append-Only Hash Chaining**
  - **Given** the previous ledger block has hash $H_{k-1}$
  - **When** transaction $k$ is committed to the ledger
  - **Then** block $k$ MUST calculate its hash as:
    $$H_k = \text{SHA256}(H_{k-1} \,\|\, \text{TxID}_k \,\|\, S_{\text{composite}} \,\|\, \text{Verdict}_k \,\|\, t_k)$$
  - **And** the block MUST store both $H_{k-1}$ (parent hash) and $H_k$ (current hash).
- **Scenario 2: Tamper Detection Verification**
  - **Given** an existing ledger with $N$ blocks
  - **When** a database row's transaction amount or score is manually altered in storage
  - **And** `/api/v1/ledger/verify` is executed
  - **Then** the verification service MUST detect the hash mismatch at that specific block index
  - **And** return status `TAMPER_DETECTED` with the exact corrupted block ID.

---

## 4. Operational API & Fallback SLA

### AC-11: Sub-100ms API Response Latency (Ref: US-14, NFR-PERF-001)
- **Scenario 1: End-to-End Latency Verification**
  - **Given** the FastAPI application running under normal concurrent load (50 users)
  - **When** 1,000 transaction requests are submitted to `/api/v1/predict`
  - **Then** the 99th percentile (p99) round-trip latency MUST be $\le 100\text{ ms}$
  - **And** the median (p50) latency MUST be $\le 35\text{ ms}$.

### AC-12: Deterministic Heuristic Fallback (Ref: US-15, NFR-REL-001)
- **Scenario 1: Inference Engine Timeout Trigger**
  - **Given** an artificial thread hang or delay exceeding $120\text{ ms}$ in the ML model inference pipeline
  - **When** the request timeout interceptor fires
  - **Then** the system MUST terminate the ML process within $10\text{ ms}$
  - **And** execute the deterministic heuristic rules (amount check + velocity cap)
  - **And** return a valid response containing the fallback verdict with diagnostic header `X-Fallback-Engaged: true`.

