# Project Analysis: Advanced QR Code Payment Fraud Detection System

**Document Version:** 1.0.0  
**Status:** Under Review (Phase 02 Deliverable)  
**Author:** Principal Business Analyst & Senior Software Requirements Engineer  
**Reference Document:** `source/PROJECT_SPEC.md`

---

## 1. Executive Summary & Problem Space

The modern digital economy has experienced unprecedented expansion in contactless, mobile wallet, and peer-to-peer (P2P) financial interactions, predominantly anchored by Quick Response (QR) code interfaces. While QR codes drastically reduce transaction friction at Point of Sale (POS) terminals and within mobile banking applications, their simplicity exposes unique cyber-financial vulnerabilities:
1. **Static QR Code Physical Spoofing (Quishing / Sticker Replacement):** Fraudsters replace legitimate merchant QR stickers with malicious replicas encoding alternative recipient IDs or phishing URLs.
2. **Dynamic QR Payload Tampering / MITM:** Interception or manipulation of dynamically generated transaction payloads, altering monetary amounts or merchant hashes mid-transit.
3. **High-Velocity Micro-Probing & Account Enumeration:** Automated bots repeatedly scanning static/dynamic QR codes in rapid succession to test stolen credentials or extract micro-balances.
4. **Spatial-Temporal Disconnects:** Scans executed from payer coordinates that are geographically inconsistent with merchant terminal coordinates, indicating cloned credentials or remote spoofing.

Traditional fraud detection engines predominantly rely on static heuristic rule engines (e.g., hardcoded transaction value ceilings, basic velocity caps). These systems exhibit severe shortcomings:
- **Excessive False Positive Rates (FPR):** Legitimate users face unnecessary transaction rejections, inducing severe customer friction and merchant revenue loss.
- **Post-Facto Latency:** Fraud is detected hours or days later during batch auditing, after funds have irreversibly settled.
- **Structural Inability to Counter Novel Exploits:** Rigid rules cannot generalize across multi-layered, non-linear transactional patterns.

This project delivers an autonomous, high-throughput, sub-100ms predictive Machine Learning (ML) system specifically engineered for QR transaction streams. It balances acute class imbalance via SMOTE, aggregates predictions across supervised and unsupervised models, provides local explainability via SHAP, and seals all authorization decisions inside a tamper-evident cryptographic ledger.

---

## 2. Project Objectives & Scope Boundaries

### 2.1 Core Project Objectives
- **Sub-100ms Inference Latency:** Deliver end-to-end fraud scoring ($P_{\text{fraud}}$, anomaly index, decision verdict, and XAI attribution) within 100 milliseconds.
- **High Recall with Low False Alarm Rate:** Attain $\ge 95.0\%$ recall on fraudulent events while constraining False Positive Rate to $\le 1.5\%$.
- **Zero-Day & Anomaly Resilience:** Detect previously unseen, unmapped fraud patterns through unsupervised anomaly detection.
- **Regulatory Transparency (XAI):** Solve the "black-box" dilemma by providing local, interpretable Shapley feature attributions for all escalated or blocked payments.
- **Tamper-Evident Non-Repudiation:** Maintain an append-only SHA-256 hash-chained ledger of all incoming transactions and corresponding verdicts.
- **Privacy-Preserving Architecture Simulation:** Formulate and simulate a Federated Learning (FedAvg) abstraction demonstrating decentralized multi-institution model training without centralizing sensitive raw data.

### 2.2 Scope Boundaries

| In-Scope | Out-of-Scope (Deferred / Non-Target) |
| :--- | :--- |
| Synthetic generation of realistic QR payment transaction datasets incorporating physical sticker spoofing, dynamic payload tampering, and velocity attacks. | Direct hardware camera sensor drivers and optical image rendering/decoding engines (input is parsed JSON/string payload). |
| Feature engineering for spatial Haversine distance, temporal sliding velocity windows, payload Shannon entropy, and payer z-score deviations. | Live production integration with central bank settlement rails (ACH, SWIFT, RTGS). |
| Supervised benchmarking across Logistic Regression, Random Forest, Support Vector Machines (SVM), LightGBM, and Deep Multi-Layer Perceptrons (MLP). | Real-money banking authorization, actual fund escrow, or merchant fiat disbursement. |
| Unsupervised anomaly detection via Isolation Forest to detect novel fraud archetypes. | Deployment across physical multi-node geographic cloud clusters (system is designed for containerized local/cloud deployment). |
| Dynamic explainability via SHAP TreeExplainer. | Live distributed blockchain consensus mining (system uses local SHA-256 hash-chaining). |
| Asynchronous REST API serving via FastAPI and an interactive simulation dashboard via Streamlit. | Native mobile iOS/Android client application development (REST contracts provided). |

---

## 3. Stakeholder Matrix & User Personas

| Stakeholder / Persona | Primary Goals | Interaction Points with System |
| :--- | :--- | :--- |
| **Payment App Consumer (Payer)** | Fast, frictionless payment experience; protection against unauthorized balance drains and spoofed merchant codes. | Initiates payment request via mobile client; receives instant APPROVE or secondary MFA challenge. |
| **Merchant / POS Terminal Operator** | Instant transaction settlement; zero chargebacks from fraudulent customer scans; immediate payment verification. | Generates dynamic QR or presents static QR; receives verified transaction status. |
| **Fraud Operations Analyst** | Real-time monitoring of suspicious transaction streams; inspection of escalated payments with clear explanatory rationales. | Uses Streamlit dashboard to audit `CHALLENGE_MFA` and `BLOCK` events, inspect SHAP force plots, and review velocity spikes. |
| **Compliance & Audit Officer** | Verification of regulatory adherence (anti-discrimination, auditability, data privacy compliance). | Inspects cryptographic hash-chained ledger to ensure non-repudiation; reviews feature distributions to verify absence of demographic bias. |
| **ML Engineer / System Administrator** | Model retraining, monitoring concept drift, benchmarking classifier variants, maintaining sub-100ms API latency. | Interacts with FastAPI `/metrics` and `/benchmark` endpoints; runs offline training scripts in `scripts/`. |

---

## 4. End-to-End System Processes

```
[Raw Ingestion] ──> [Feature Enrichment] ──> [Hybrid ML Inference] ──> [Decision Gating] ──> [XAI & Cryptographic Audit]
```

### Process 1: Ingestion & Structural Validation
- Accepts HTTP POST payload (`/api/v1/predict`).
- Pydantic v2 verifies schema integrity, parameter boundaries, and timestamp synchronization.
- Sensitive identifiers (`payer_id`, `merchant_id`) are sanitized/hashed before internal tensor mapping.

### Process 2: Stateful Feature Enrichment
- Decodes QR payload parameters and calculates Shannon entropy:
  $$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$
- Queries in-memory cache (Redis/TTL store) to compute dynamic rolling velocities ($V_{5\text{m}}, V_{1\text{h}}, V_{24\text{h}}$).
- Computes Haversine spatial displacement ($d$) between payer device coordinates and registered merchant terminal coordinates.
- Calculates transaction amount deviation relative to historical customer baseline ($Z_{\text{amount}}$).

### Process 3: Dual-Engine Hybrid Inference
- Feeds normalized feature vector $X \in \mathbb{R}^d$ into:
  1. **Supervised Classifier Ensemble (LightGBM/RF):** Generates probability of known fraud: $P(\text{Fraud} \mid X) \in [0, 1]$.
  2. **Unsupervised Anomaly Detector (Isolation Forest):** Computes normalized isolation anomaly score: $S_{\text{anomaly}}(X) \in [0, 1]$.

### Process 4: Multi-Tier Decision Gating
- Synthesizes composite risk index:
  $$S_{\text{composite}} = 0.70 \cdot P(\text{Fraud} \mid X) + 0.30 \cdot S_{\text{anomaly}}(X)$$
- Applies deterministic tier thresholds:
  - $S_{\text{composite}} < 0.30 \implies \mathbf{APPROVE}$
  - $0.30 \le S_{\text{composite}} \le 0.70 \implies \mathbf{CHALLENGE\_MFA}$
  - $S_{\text{composite}} > 0.70 \implies \mathbf{BLOCK}$
- *Edge Rule:* If $P(\text{Fraud} \mid X) \in [0.25, 0.45]$ but $S_{\text{anomaly}}(X) > 0.80$, verdict is automatically escalated to $\mathbf{CHALLENGE\_MFA}$.

### Process 5: Explainability & Audit Trail Commitment
- If verdict is `CHALLENGE_MFA` or `BLOCK`, invokes SHAP TreeExplainer to extract the top-3 feature attribution vectors.
- Appends block to SHA-256 cryptographic ledger:
  $$H_k = \text{SHA256}(H_{k-1} \,\|\, \text{TxID}_k \,\|\, S_{\text{composite}} \,\|\, \text{Verdict}_k \,\|\, t_k)$$
- Returns structured JSON response to client.

---

## 5. Architectural Feasibility & Theoretical Formulation

1. **Class Imbalance Formulation:**  
   Given training dataset $D = \{(x_i, y_i)\}_{i=1}^N$ with $|D_1| \ll |D_0|$, SMOTE creates synthetic points along the line segment joining $k$-nearest minority neighbors:
   $$x_{\text{synthetic}} = x_i + \lambda(x_{zi} - x_i), \quad \lambda \sim \text{Uniform}(0, 1), \quad x_{zi} \in \mathcal{N}_k(x_i)$$
2. **Explainable AI (Shapley Values):**  
   Local attribution satisfies efficiency, symmetry, dummy, and additivity properties:
   $$\phi_j(val) = \sum_{S \subseteq F \setminus \{j\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ val(S \cup \{j\}) - val(S) \right]$$
3. **Decentralized Privacy Simulation (FedAvg):**  
   Simulates model weight aggregation across $K$ regional/merchant silos without data centralization:
   $$W_{t+1} = \sum_{k=1}^K \frac{n_k}{n} W_{t+1}^k$$

---

## 6. Project Risk Assessment & Mitigation Matrix

| Identified Risk | Severity | Probability | Proposed Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Inference Latency Spike under High Concurrency** | High | Medium | Pre-compute baseline historical user stats in Redis; utilize lightweight LightGBM inference engine; restrict SHAP calculations to flagged/challenged transactions only. |
| **Concept Drift in QR Fraud Patterns** | High | High | Dual-tier hybrid scoring ensures unmapped patterns are flagged by unsupervised Isolation Forest; scheduled retraining pipelines included. |
| **Overfitting on Synthetic SMOTE Data** | Medium | Medium | Apply Borderline-SMOTE; perform cross-validation strictly on untouched out-of-time evaluation splits. |
| **False-Positive Backlash from Legitimate Users** | High | Low | Three-tier decision framework incorporates `CHALLENGE_MFA` rather than outright rejection for ambiguous scores ($0.30 - 0.70$). |
| **Ledger Storage Growth Overhead** | Low | Low | Store compact fixed-size binary SHA-256 state digests with SQLite persistence for transaction telemetry. |

