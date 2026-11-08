# Functional Requirements Specification (FRS)

**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 02)  
**Parent Document:** `docs/02_Requirements/SRS.md`  
**Reference Document:** `source/PROJECT_SPEC.md`

---

## 1. Ingestion & Validation Module (`FR-ING`)

- **FR-ING-001: Schema Deserialization & Boundary Validation**  
  The system MUST validate incoming HTTP POST requests against a strict Pydantic v2 data model conforming to the 16-attribute specification (UUID format, positive amounts, valid lat/lon ranges). Any request violating the schema MUST immediately return HTTP 422 Unprocessable Entity with structured field-level error diagnostics.

- **FR-ING-002: Timestamp & Freshness Gating**  
  The system MUST check transaction timestamps against the server clock. Any transaction payload with a timestamp exceeding $\pm 300\text{ seconds}$ drift from system time MUST be flagged with a `TIMESTAMP_DRIFT_EXCEEDED` anomaly code.

- **FR-ING-003: Cryptographic Payload Integrity Check**  
  The system MUST verify the transaction integrity signature or hash (if provided by the client application). Tampered payloads MUST be immediately rejected with an HTTP 400 Bad Request error.

- **FR-ING-004: PII Masking and Salting**  
  The system MUST salt and hash raw customer account identifiers (`payer_id`) using SHA-256 prior to persisting records or querying state history.

---

## 2. Feature Engineering & State Pipeline (`FR-FEA`)

- **FR-FEA-001: Haversine Spatial Displacement Calculation**  
  The system MUST compute the geographic distance in kilometers ($d$) between the payer coordinates $(\phi_p, \lambda_p)$ and registered merchant POS coordinates $(\phi_m, \lambda_m)$ using the Haversine formula:
  $$d = 2R \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_p)\cos(\phi_m)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$
  where $R = 6371\text{ km}$.

- **FR-FEA-002: Shannon Entropy Calculation of QR Payload**  
  The system MUST compute the Shannon entropy of the decoded QR payload string to identify obfuscation, dynamic URL redirects, or encrypted injection patterns:
  $$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$

- **FR-FEA-003: Stateful Rolling Velocity Computation**  
  The system MUST query the state cache to calculate the rolling transaction frequencies for the payer account across three discrete temporal windows:
  - $V_{5\text{m}}$: Number of transactions within the trailing 5 minutes.
  - $V_{1\text{h}}$: Number of transactions within the trailing 1 hour.
  - $V_{24\text{h}}$: Number of transactions within the trailing 24 hours.
  - Velocity ratio: $\text{Ratio}_{\text{vel}} = \frac{V_{1\text{h}}}{V_{24\text{h}} + 1}$.

- **FR-FEA-004: Amount Z-Score Relative to Historical Payer Baseline**  
  The system MUST normalize the transaction amount against the payer historical mean ($\mu_p$) and standard deviation ($\sigma_p$):
  $$Z_{\text{amount}} = \frac{\text{amount} - \mu_p}{\sigma_p + \epsilon} \quad (\epsilon = 10^{-5})$$
  If the payer has no prior history, a population-wide merchant category default MUST be substituted.

- **FR-FEA-005: Online Scaler Normalization**  
  The engineered feature vector MUST be normalized using pre-fitted RobustScaler / StandardScaler transformation matrices before ingestion by the model engine.

---

## 3. Synthetic Data Generation & Balancing (`FR-DAT`)

- **FR-DAT-001: Realistic QR Fraud Archetype Simulation**  
  The data generator module MUST produce synthetic datasets exhibiting realistic fraud archetypes:
  1. *Sticker Replacement / Quishing:* High spatial distance, anomalous merchant category mismatch, elevated QR payload entropy.
  2. *Dynamic QR Injection / MITM:* Amount drastically exceeding payer baseline, altered payload checksum.
  3. *High-Velocity Credential Probing:* High $V_{5\text{m}}$ frequency, sub-second `scan_to_pay_latency_ms`, low device trust scores.
  4. *Legitimate Baseline Transactions:* Routine amounts, low spatial displacement ($< 5\text{ km}$), standard scan-to-pay latencies ($2\text{s} - 15\text{s}$).

- **FR-DAT-002: Acute Imbalance Preservation & Partitioning**  
  The synthetic raw dataset MUST reproduce acute financial class imbalance ($0.5\% - 1.0\%$ fraudulent transactions). Splitting MUST utilize stratified train/validation/test partitions ($70\% / 15\% / 15\%$) with temporal ordering preserved.

- **FR-DAT-003: SMOTE Oversampling Pipeline**  
  The training pipeline MUST apply Synthetic Minority Over-sampling Technique (SMOTE) strictly on the training partition:
  $$x_{\text{new}} = x_i + \lambda \cdot (x_{zi} - x_i), \quad \lambda \sim U(0, 1), \quad k=5$$
  The validation and test partitions MUST remain un-oversampled to preserve realistic evaluation fidelity.

---

## 4. Model Engine & Hybrid Inference (`FR-MOD`)

- **FR-MOD-001: Supervised Classifier Benchmark Suite**  
  The system MUST implement and benchmark candidate supervised classifiers:
  - Logistic Regression (Baseline)
  - Random Forest Classifier
  - Support Vector Machine (SVM with RBF kernel)
  - LightGBM Classifier (Primary Production Engine)
  - Deep Multi-Layer Perceptron (PyTorch MLP)

- **FR-MOD-002: Unsupervised Anomaly Detection Engine**  
  The system MUST implement an Isolation Forest (and Autoencoder variant) trained exclusively on legitimate baseline transactions to generate an isolation anomaly score:
  $$S_{\text{anomaly}}(X) \in [0, 1]$$

- **FR-MOD-003: Hybrid Risk Score Synthesis**  
  The system MUST compute a composite fraud risk score ($S_{\text{composite}}$) combining the supervised probability and unsupervised anomaly score:
  $$S_{\text{composite}} = w_1 \cdot P_{\text{supervised}}(\text{Fraud} \mid X) + w_2 \cdot S_{\text{anomaly}}(X)$$
  where default weights are $w_1 = 0.70$ and $w_2 = 0.30$. Both weights MUST be configurable via environment variables.

---

## 5. Multi-Tier Decision & Policy Gating (`FR-DEC`)

- **FR-DEC-001: Deterministic Decision Tier Execution**  
  The system MUST classify incoming transactions into one of three distinct verdicts:
  - $\mathbf{APPROVE}$ if $S_{\text{composite}} < 0.30$
  - $\mathbf{CHALLENGE\_MFA}$ if $0.30 \le S_{\text{composite}} \le 0.70$
  - $\mathbf{BLOCK}$ if $S_{\text{composite}} > 0.70$

- **FR-DEC-002: Unsupervised Zero-Day Escalation Override**  
  If $P_{\text{supervised}}(\text{Fraud} \mid X)$ falls into the ambiguous marginal zone ($0.25 \le P_{\text{supervised}} \le 0.45$) but the unsupervised anomaly score is exceptionally high ($S_{\text{anomaly}} > 0.80$), the verdict MUST automatically escalate to $\mathbf{CHALLENGE\_MFA}$.

- **FR-DEC-003: Heuristic Fallback Engine**  
  If the ML inference engine experiences an unhandled exception or timeout exceeding $120\text{ ms}$, the system MUST execute a deterministic heuristic fallback:
  - If $\text{amount} > \$1000$ or $V_{5\text{m}} > 5$, verdict = `CHALLENGE_MFA`.
  - Otherwise, verdict = `APPROVE` with a degraded warning flag.

---

## 6. Explainable AI Engine (`FR-XAI`)

- **FR-XAI-001: Dynamic Local SHAP Attribution Generation**  
  For all transactions resulting in `CHALLENGE_MFA` or `BLOCK`, the system MUST calculate local Shapley feature attributions using SHAP TreeExplainer:
  $$f(x) = \phi_0 + \sum_{j=1}^{M} \phi_j$$

- **FR-XAI-002: Human-Readable Reason Code Extraction**  
  The system MUST extract the top-3 positive contributing features (drivers increasing the fraud score) and format them into standardized, human-readable reason codes (e.g., `GEO_DISTANCE_ANOMALOUS`, `AMOUNT_SPIKE_ABOVE_BASELINE`, `SCAN_VELOCITY_CRITICAL`).

- **FR-XAI-003: Bypass for Low-Risk Transactions**  
  To conserve compute cycles and enforce the sub-100ms latency budget, SHAP calculation MUST be bypassed for transactions with $S_{\text{composite}} < 0.30$ unless explicitly requested via `/api/v1/explain`.

---

## 7. Cryptographic Audit Ledger (`FR-AUD`)

- **FR-AUD-001: SHA-256 Block Chaining**  
  The system MUST commit every transaction authorization event to an append-only cryptographic ledger. Each block MUST calculate a SHA-256 digest linked to the previous block's hash:
  $$H_k = \text{SHA256}(H_{k-1} \,\|\, \text{TxID}_k \,\|\, S_{\text{composite}} \,\|\, \text{Verdict}_k \,\|\, t_k)$$

- **FR-AUD-002: Genesis Block Initialization**  
  The ledger MUST initialize with a deterministic Genesis Block ($H_0$) upon first startup.

- **FR-AUD-003: Ledger Chain Verification API**  
  The system MUST expose a verification utility that iterates through the ledger sequence to validate hash continuity, returning an alert if any tampering or row deletion has occurred.

---

## 8. REST API Microservice (`FR-API`)

- **FR-API-001: `/api/v1/predict` (Single Transaction Inference)**  
  Accepts raw JSON payload, executes preprocessing, feature engineering, hybrid inference, decision gating, ledger write, and returns decision within $\le 100\text{ ms}$.

- **FR-API-002: `/api/v1/batch-predict` (Batch Processing)**  
  Accepts a JSON array of up to 500 transactions for offline or bulk evaluation, returning an array of scores and verdicts.

- **FR-API-003: `/api/v1/explain` (Dedicated Explanation)**  
  Accepts a transaction vector and returns complete SHAP values, base value, and feature impact rankings.

- **FR-API-004: `/api/v1/metrics` (Operational & ML Telemetry)**  
  Exposes current model performance metrics (Accuracy, Recall, Precision, PR-AUC, p50/p95 latency, total ledger blocks).

- **FR-API-005: `/api/v1/health` (Liveness & Readiness)**  
  Returns system status, active model version, and state cache connectivity status.

---

## 9. Interactive Telemetry & Dashboard (`FR-UI`)

- **FR-UI-001: Live Streamlit Telemetry Display**  
  The UI MUST present an auto-refreshing dashboard displaying real-time transaction throughput, verdict distributions (Approve/Challenge/Block ratios), and current latency stats.

- **FR-UI-002: Interactive Fraud Scenario Simulator**  
  The UI MUST provide input widgets allowing users to simulate custom transaction scenarios (adjusting amount, distance, scan latency, QR entropy) and immediately inspect the resulting risk verdict and SHAP explanation.

- **FR-UI-003: Comparative Model Benchmark Visualizer**  
  The UI MUST render comparative ROC and PR curves, confusion matrices, and tabular metrics across all trained baseline algorithms.

---

## 10. Federated Learning Simulation (`FR-FED`)

- **FR-FED-001: Decentralized Multi-Client Partitioning**  
  The module MUST partition transaction datasets across $K=3$ mock merchant banking institutions without sharing raw transaction rows.

- **FR-FED-002: Federated Averaging (FedAvg) Weight Aggregation**  
  The module MUST execute iterative weight aggregation across the client models:
  $$W_{t+1} = \sum_{k=1}^{K} \frac{n_k}{n} W_{t+1}^k$$
  and compare the global federated model accuracy against centrally trained baselines.

