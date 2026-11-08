# Research Analysis & Academic Gap Synthesis

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 04)  
**Parent Document:** `source/PROJECT_SPEC.md` | `research/REFERENCES.md`  
**Reference Standards:** IEEE Access, MDPI Information, Applied Sciences Review

---

## 1. Synthesis of Literature Review

Recent financial security and computer science literature demonstrates a critical paradigm shift: traditional, reactive static heuristic rule engines are structurally incapable of defending digital payment systems against dynamic, non-linear fraud architectures.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             EVOLUTION OF FRAUD DETECTION                         │
├─────────────────────────┬────────────────────────────┬───────────────────────────┤
│ Generation 1 (Legacy)   │ Generation 2 (Early ML)    │ Generation 3 (Our System) │
│ - Hardcoded Rules       │ - Supervised Classifiers   │ - Hybrid (Supervised +    │
│ - Static Ceilings       │ - Manual Feature Eng.      │   Unsupervised Anomaly)   │
│ - Delayed Batch Audits  │ - Severely Biased by Skew  │ - Real-Time Sub-100ms     │
│ - High False Positives  │ - Black-Box Deep Networks  │ - Dynamic XAI (SHAP)      │
│ - Zero Contextual QR    │ - Single Transaction Scope │ - Cryptographic Ledger    │
│   Entropy / Geo-Checks  │ - Centralized Raw Data     │ - Federated Simulation    │
└─────────────────────────┴────────────────────────────┴───────────────────────────┘
```

### 1.1 Empirical Literature Findings

1. **Systematic Findings on ML in Financial Fraud (Ali et al., 2022):**
   - Ali et al. reviewed 93 core studies across IEEE Xplore, ACM, and Scopus, finding that while Decision Trees, Random Forests, and Artificial Neural Networks dominate financial fraud research, more than $70\%$ of existing approaches struggle with extreme class imbalance, concept drift, high-dimensional data, and real-time inference latency.
   - The authors emphasize the urgent need for multi-tier architectures capable of bridging the gap between batch training and low-latency mid-transaction interception.

2. **The Imbalance Challenge in Online Payments (Almazroi & Ayub, 2023):**
   - Almazroi & Ayub demonstrated that conventional machine learning algorithms suffer severe performance degradation when applied directly to raw financial transaction datasets where fraud comprises $< 1\%$ of observations.
   - Their findings proved that handcrafted features fail to capture emerging fraud vectors and that data-level rebalancing (e.g., SMOTE) or algorithmic cost weighting is strictly necessary to prevent models from defaulting to majority-class bias.

3. **QR Code Vulnerability Paradigms (Chelouah & Nwaekwu, 2026):**
   - Chelouah & Nwaekwu highlight that while legacy literature concentrated almost exclusively on physical credit cards and web payment portals, QR code contactless payments introduce unique attack surfaces:
     - *Physical Quishing:* Overlaying fraudulent static QR stickers on merchant POS counters.
     - *Dynamic Injection / MITM:* Modifying amount parameters or recipient IDs within dynamic QR barcodes in transit.
     - *Rapid Micro-Scanning:* Automated scanning bots probing stolen accounts.
   - The authors stress the necessity of specialized feature engineering tailored specifically to QR transaction loops.

4. **Classifier Performance & LightGBM Dominance (Farouk et al., 2024):**
   - Farouk et al. benchmarked multiple supervised classifiers (Decision Trees, Random Forest, AdaBoost, Naive Bayes, Bagging, and LightGBM).
   - Their experimental results proved that LightGBM achieved the highest recall ($99.0\%$) and fastest inference speed among tree ensembles, while demonstrating that bagging and random forests provide strong secondary baselines.

5. **Real-Time Threat Mitigation in E-Commerce (Wang, 2022):**
   - Wang emphasized that rapid digitization and mobile wallet adoption have eliminated the feasibility of post-facto fraud auditing. If a fraudulent transaction is not blocked mid-flight, funds settle irreversibly, resulting in merchant chargebacks and user attrition.

---

## 2. Analysis of the 5 Proposal Research Gaps & Architectural Solutions

The thesis proposal explicitly identified 5 fundamental operational and research gaps in the literature. Our system architecture directly addresses each gap:

```
┌─────────────────────────────────┐     ┌──────────────────────────────────────────────┐
│     Identified Research Gap     │     │             Architectural Solution           │
├─────────────────────────────────┼─────┼──────────────────────────────────────────────┤
│ 1. The Imbalance Impasse        │ ──> │ Borderline-SMOTE & Stratified Temporal Split │
│ 2. The "Black-Box" Dilemma      │ ──> │ Polynomial-Time SHAP TreeExplainer & Reasons │
│ 3. Adversarial Vulnerability    │ ──> │ Input Clamping & Unsupervised Isolation Forest│
│ 4. Privacy & Regulatory Deficit │ ──> │ Salted SHA-256 Hashing & FedAvg Simulation   │
│ 5. Contextual Deficit in QR     │ ──> │ Haversine Spatial, Shannon Entropy, Velocity │
└─────────────────────────────────┘     └──────────────────────────────────────────────┘
```

### Gap 1: The Imbalance Impasse
- **Problem:** Financial datasets feature extreme class skew ($\le 1\%$ fraud). Naive models maximize global accuracy ($99.2\%$) by classifying all records as legitimate, resulting in $0\%$ fraud recall.
- **Project Solution:** The data engineering pipeline applies **Borderline-SMOTE** strictly to the training split, synthesizing minority instances along the decision boundary ($DANGER$ set) while maintaining un-oversampled test partitions to evaluate true out-of-time generalizability.

### Gap 2: The "Black-Box" Dilemma (Auditability & Governance)
- **Problem:** Modern financial regulators (e.g., GDPR Article 22, FCRA) mandate an individual's right to an explanation when algorithmic decisions negatively impact them. High-performing deep neural networks lack interpretability, creating institutional adoption barriers.
- **Project Solution:** Integration of **SHAP (SHapley Additive exPlanations) TreeExplainer**. Every transaction resulting in `CHALLENGE_MFA` or `BLOCK` is dynamically annotated with local Shapley values ($\phi_j$), outputting human-readable root reason codes (e.g., `["AmountDeviation > 3.8 sigma", "GeoDistance > 450 km"]`).

### Gap 3: Adversarial Fragility & Concept Drift
- **Problem:** Fraudsters systematically probe algorithmic thresholds by tweaking input values (e.g., keeping transaction amounts just below standard blocking rules), evading static supervised boundaries.
- **Project Solution:** **Dual-Engine Hybrid Scoring**. A supervised LightGBM model is paired with an unsupervised **Isolation Forest** trained on normal customer behavior. If a novel exploit generates an ambiguous supervised score ($P_{\text{fraud}} \in [0.25, 0.45]$) but exhibits high structural outlier behavior ($S_{\text{anomaly}} > 0.80$), the decision engine automatically escalates the transaction to `CHALLENGE_MFA`.

### Gap 4: Regulatory & Data Privacy Non-Alignment
- **Problem:** Financial privacy statutes strictly prohibit pooling raw transaction records across competitive banking institutions or merchants for centralized training.
- **Project Solution:** 
  1. Internal PII sanitization: All customer identifiers are salted and hashed (SHA-256) at ingestion.
  2. **Federated Learning Simulation:** A dedicated research module implements Federated Averaging (FedAvg), demonstrating decentralized collaborative training across 3 simulated bank nodes without centralizing raw customer financial vectors.

### Gap 5: Contextual Deficit in QR Payment Paradigms
- **Problem:** Prior literature primarily evaluates legacy credit card datasets (e.g., Kaggle Credit Card Fraud dataset), which lack variables reflecting physical QR code presentation dynamics.
- **Project Solution:** Our feature engineering pipeline extracts domain-specific QR contextual attributes:
  - *Optical Scan Dynamics:* `scan_to_pay_latency_ms` flags automated scripted bot attacks.
  - *Spatial Divergence:* Haversine distance between payer mobile GPS and merchant POS coordinates detects physical sticker spoofing.
  - *Payload Obfuscation:* Shannon entropy identifies encoded phishing URLs or manipulated payloads.
  - *Stateful Velocity:* Rolling $5\text{m}$, $1\text{h}$, and $24\text{h}$ sliding counters flag micro-probing.

---

## 3. Novel Architectural Contributions of This Thesis Project

1. **Sub-100ms Hybrid Inference Pipeline:** Seamlessly blending supervised gradient boosting with unsupervised anomaly isolation within a strict $100\text{ ms}$ round-trip latency ceiling.
2. **Deterministic Fallback Circuit Breaker:** Ensuring financial payment availability by failing over safely to deterministic heuristics if ML inference encounters unexpected latency spikes ($> 120\text{ ms}$).
3. **Cryptographic Non-Repudiation:** Linking all inference verdicts, timestamps, and model scores into an append-only SHA-256 hash-chained ledger to ensure immutable auditability.

