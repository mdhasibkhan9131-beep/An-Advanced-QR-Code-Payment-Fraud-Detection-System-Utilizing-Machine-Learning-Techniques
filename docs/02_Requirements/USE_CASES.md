# Use Cases Specification

**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 02)  
**Parent Document:** `docs/02_Requirements/SRS.md`  
**Reference Document:** `source/PROJECT_SPEC.md`

---

## UC-01: Real-Time Legitimate QR Payment Evaluation

- **Primary Actor:** Payment App Client / POS Gateway
- **Secondary Actor:** Core Banking Authorization Engine
- **Preconditions:**
  - Client has scanned a legitimate merchant QR code and formulated a valid JSON payload.
  - Fraud Detection API is running and healthy.
- **Trigger:** Client sends HTTP POST `/api/v1/predict`.
- **Main Success Scenario:**
  1. System deserializes and validates transaction schema via Pydantic.
  2. System calculates Haversine distance ($< 1\text{ km}$), QR Shannon entropy ($< 4.0$), and retrieves rolling velocity ($V_{1\text{h}} = 1$).
  3. Supervised model calculates low fraud probability ($P_{\text{fraud}} = 0.04$).
  4. Unsupervised Isolation Forest indicates normal behavior ($S_{\text{anomaly}} = 0.12$).
  5. Composite risk score calculated: $S_{\text{composite}} = (0.7 \times 0.04) + (0.3 \times 0.12) = 0.064$.
  6. Score is $< 0.30$; system assigns verdict: `APPROVE`.
  7. System records event to SHA-256 cryptographic ledger.
  8. System responds with HTTP 200 OK containing verdict `APPROVE` and score within $32\text{ ms}$.
- **Postconditions:** Transaction proceeds to bank settlement; ledger block appended.

---

## UC-02: Suspicious Transaction Step-Up (MFA Challenge)

- **Primary Actor:** Payment App Client / Payer
- **Secondary Actor:** Authentication / OTP Service
- **Preconditions:** Payer initiates a transaction with anomalous parameters (e.g., amount is $3.2\times$ baseline, scan latency is unusually brief).
- **Trigger:** Client sends HTTP POST `/api/v1/predict`.
- **Main Success Scenario:**
  1. System extracts features: $Z_{\text{amount}} = 3.2$, $V_{1\text{h}} = 4$, distance $= 45\text{ km}$.
  2. Supervised model outputs $P_{\text{fraud}} = 0.52$; unsupervised model outputs $S_{\text{anomaly}} = 0.48$.
  3. Composite risk score: $S_{\text{composite}} = (0.7 \times 0.52) + (0.3 \times 0.48) = 0.508$.
  4. Since $0.30 \le S_{\text{composite}} \le 0.70$, system assigns verdict: `CHALLENGE_MFA`.
  5. System generates SHAP feature attribution: top driver `AmountDeviation > 3.0 sigma`.
  6. Event is committed to cryptographic audit ledger.
  7. System returns HTTP 200 with verdict `CHALLENGE_MFA`, reason codes, and challenge token.
  8. Payment app prompts customer for biometric / SMS OTP confirmation.
- **Postconditions:** Transaction is temporarily held pending step-up authentication.

---

## UC-03: Critical Fraud Threat Interception & Block

- **Primary Actor:** Fraudulent Actor / Stolen Device
- **Secondary Actor:** Payment App Client, Merchant POS
- **Preconditions:** Fraudster uses a static QR sticker replacement or compromised account with extreme geographical distance and high velocity.
- **Trigger:** Client sends HTTP POST `/api/v1/predict`.
- **Main Success Scenario:**
  1. System computes Haversine distance: $620\text{ km}$ from merchant registered location.
  2. System detects rapid velocity burst: $V_{5\text{m}} = 7$ attempts; QR entropy $= 6.8$ (malicious URL redirect payload).
  3. Supervised model outputs $P_{\text{fraud}} = 0.94$; unsupervised model outputs $S_{\text{anomaly}} = 0.91$.
  4. Composite risk score: $S_{\text{composite}} = (0.7 \times 0.94) + (0.3 \times 0.91) = 0.931$.
  5. Score exceeds $0.70$; system assigns verdict: `BLOCK`.
  6. SHAP engine extracts top 3 drivers: `["GeoDistance > 500 km", "QR_Entropy_Elevated", "VelocityBurst_5min"]`.
  7. SHA-256 block committed to ledger with `BLOCK` status.
  8. System returns HTTP 200 with verdict `BLOCK` and explanatory reason codes.
- **Postconditions:** Transaction is terminated immediately mid-flight; merchant and payer accounts protected.

---

## UC-04: Zero-Day Anomaly Detection & Escalation

- **Primary Actor:** Sophisticated Adversary
- **Preconditions:** Fraudster modifies input values in an unmapped manner that avoids triggering supervised classification thresholds ($P_{\text{fraud}} = 0.38$, appearing marginal).
- **Trigger:** Client sends HTTP POST `/api/v1/predict`.
- **Main Success Scenario:**
  1. Supervised model produces ambiguous probability: $P_{\text{fraud}} = 0.38$.
  2. Unsupervised Isolation Forest flags unprecedented structural anomaly: $S_{\text{anomaly}} = 0.88$.
  3. Edge rule evaluates: $P_{\text{fraud}} \in [0.25, 0.45]$ and $S_{\text{anomaly}} > 0.80$.
  4. Decision engine overrides standard weight and escalates verdict to `CHALLENGE_MFA`.
  5. Explainer notes zero-day distributional outlier; transaction is committed to ledger.
  6. System returns `CHALLENGE_MFA` with zero-day anomaly rationale.
- **Postconditions:** Novel fraud attempt is intercepted without causing hard false negatives.

---

## UC-05: Real-Time Fraud Operations Investigation

- **Primary Actor:** Fraud Operations Analyst
- **Preconditions:** Streamlit dashboard is active and connected to the backend database/ledger.
- **Trigger:** Analyst navigates to Streamlit UI in browser (`http://localhost:8501`).
- **Main Success Scenario:**
  1. Dashboard loads live telemetry cards: throughput, current block rate ($1.2\%$), challenge rate ($3.5\%$), and p95 latency ($64\text{ ms}$).
  2. Analyst selects a recent flagged transaction (`BLOCK`) from the transaction table.
  3. UI displays detailed transaction metadata, payer velocity timeline, and geographical map showing distance between payer and merchant.
  4. UI renders the interactive SHAP Waterfall plot showing exact quantitative contributions of each feature to the risk score.
  5. Analyst reviews and confirms the validity of the algorithmic intervention.
- **Postconditions:** Full transparency achieved without contacting engineering teams.

---

## UC-06: Batch Supervised & Unsupervised Model Benchmarking

- **Primary Actor:** ML Engineer / Data Scientist
- **Preconditions:** Synthetic dataset generated; training pipeline initialized.
- **Trigger:** Engineer runs CLI script `python scripts/train_and_benchmark.py`.
- **Main Success Scenario:**
  1. Script loads synthetic transactions, applies Haversine and entropy feature engineering.
  2. Script isolates train partition and applies SMOTE oversampling.
  3. Script trains candidate supervised models: Logistic Regression, Random Forest, SVM, LightGBM, and Deep MLP.
  4. Script fits unsupervised Isolation Forest on legitimate partition.
  5. Script evaluates all models on untouched test split, calculating Precision, Recall, F1, F2, PR-AUC, and total asymmetric loss cost.
  6. Script serializes winning LightGBM and Isolation Forest artifacts to `backend/models/`.
  7. Results saved to benchmark table in `docs/` and SQLite database.
- **Postconditions:** Validated model weights deployed for production serving.

---

## UC-07: Cryptographic Audit Trail Verification

- **Primary Actor:** Internal Compliance Officer / External Auditor
- **Preconditions:** System has processed historical transactions and created ledger blocks.
- **Trigger:** Auditor triggers verification script or API endpoint `/api/v1/ledger/verify`.
- **Main Success Scenario:**
  1. Verification service retrieves Genesis Block ($H_0$).
  2. Service sequentially recalculates expected hash for each block $k$:
     $$H_k^* = \text{SHA256}(H_{k-1} \,\|\, \text{TxID}_k \,\|\, S_{\text{composite}} \,\|\, \text{Verdict}_k \,\|\, t_k)$$
  3. Compares $H_k^*$ to stored $H_k$ across all sequential blocks.
  4. If all hashes match, service returns `LEDGER_INTEGRITY_VERIFIED: 100% (N blocks intact)`.
- **Alternative Flow (Tamper Detection):**
  - If a stored row was altered in the database, $H_k^* \ne H_k$.
  - Service immediately flags tamper location: `TAMPER_DETECTED at Block ID #412`.
- **Postconditions:** Non-repudiation and regulatory compliance mathematically validated.

---

## UC-08: Decentralized Federated Model Weight Aggregation

- **Primary Actor:** System Administrator / Consortium Coordinator
- **Preconditions:** Three mock banking institutions maintain decentralized local transaction logs.
- **Trigger:** Execution of `python scripts/run_federated_simulation.py`.
- **Main Success Scenario:**
  1. Simulation initiates 3 localized client nodes, each training on private local datasets.
  2. Nodes transmit local model parameter weights ($W_t^1, W_t^2, W_t^3$) to the central coordinator. No raw transactions leave client nodes.
  3. Central coordinator executes Federated Averaging:
     $$W_{t+1} = \sum_{k=1}^{3} \frac{n_k}{n} W_t^k$$
  4. Global aggregated model is redistributed to all 3 nodes.
  5. Script validates that the federated global model achieves comparable detection recall ($> 94\%$) to centralized training.
- **Postconditions:** Regulatory privacy compliance demonstrated for multi-institutional deployments.

