# User Stories Specification

**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 02)  
**Parent Document:** `docs/02_Requirements/SRS.md`  
**Framework:** Agile Scrum (INVEST Compliant)  
**Reference Document:** `source/PROJECT_SPEC.md`

---

## Epic 1: Data Ingestion & Contextual Feature Pipeline

- **US-01: Strict Schema Validation & Sanitization**  
  *As a* Backend API Gateway,  
  *I want to* validate incoming JSON payloads against strict Pydantic schemas and sanitize sensitive PII,  
  *so that* malformed, malicious, or unencrypted data cannot corrupt downstream feature tensors or violate data privacy standards.  
  *Priority:* Critical | *Story Points:* 3

- **US-02: Spatial Haversine Distance Calculation**  
  *As an* ML Feature Engineer,  
  *I want to* calculate the exact geographic distance between payer GPS coordinates and registered merchant coordinates,  
  *so that* physical QR sticker replacement and remote account takeover attacks can be detected immediately.  
  *Priority:* High | *Story Points:* 3

- **US-03: QR Payload Shannon Entropy Extraction**  
  *As a* Security Architect,  
  *I want to* compute the Shannon entropy of scanned QR text strings,  
  *so that* obfuscated phishing redirects and encrypted dynamic tampering attempts are quantitatively flagged.  
  *Priority:* High | *Story Points:* 3

- **US-04: Stateful Rolling Velocity Counters**  
  *As a* Fraud Prevention Analyst,  
  *I want to* query real-time sliding transaction frequencies ($5\text{m}, 1\text{h}, 24\text{h}$) from an in-memory cache,  
  *so that* high-velocity micro-probing attacks can be intercepted before draining user accounts.  
  *Priority:* Critical | *Story Points:* 5

- **US-05: Realistic Synthetic Data Generation & SMOTE Balancing**  
  *As a* Data Scientist,  
  *I want to* synthesize realistic QR transaction streams and balance training distributions using SMOTE,  
  *so that* supervised classifiers learn robust decision boundaries despite extreme real-world class imbalance ($\le 1\%$ fraud).  
  *Priority:* Critical | *Story Points:* 5

---

## Epic 2: Real-Time Hybrid ML Fraud Scoring

- **US-06: Supervised Classifier Benchmark Suite**  
  *As an* ML Engineer,  
  *I want to* benchmark Logistic Regression, Random Forest, SVM, LightGBM, and Deep MLP on standardized test splits,  
  *so that* the optimal production classifier is selected based on Recall ($\ge 95\%$), Precision ($\ge 90\%$), and latency.  
  *Priority:* Critical | *Story Points:* 8

- **US-07: Unsupervised Anomaly Isolation**  
  *As a* Fraud Risk Architect,  
  *I want to* deploy an Isolation Forest trained on normal payment baseline data,  
  *so that* novel, zero-day fraud tactics that evade supervised decision trees are flagged.  
  *Priority:* High | *Story Points:* 5

- **US-08: Calibrated Hybrid Score Arbitration**  
  *As a* Risk Policy Manager,  
  *I want to* combine supervised fraud probability and unsupervised anomaly scores via a weighted formula ($0.70 P_{\text{sup}} + 0.30 S_{\text{unsup}}$),  
  *so that* transactions receive a holistic composite risk index reflecting both known threats and unexpected anomalies.  
  *Priority:* Critical | *Story Points:* 3

- **US-09: Three-Tier Decision Gating & Edge Escalation**  
  *As a* Payment Authorization Engine,  
  *I want to* route transactions into `APPROVE`, `CHALLENGE_MFA`, or `BLOCK` tiers with automatic escalation for high-anomaly marginal scores,  
  *so that* legitimate users experience zero friction while high-risk attempts are intercepted.  
  *Priority:* Critical | *Story Points:* 5

---

## Epic 3: Explainable AI & Regulatory Compliance

- **US-10: Dynamic Local SHAP Attribution**  
  *As a* Fraud Operations Analyst,  
  *I want to* receive local SHAP feature attributions for any flagged or blocked transaction,  
  *so that* I can inspect the exact mathematical drivers behind the algorithmic intervention.  
  *Priority:* High | *Story Points:* 5

- **US-11: Standardized Human-Readable Reason Codes**  
  *As a* Compliance Officer,  
  *I want to* translate top SHAP feature drivers into standardized reason codes,  
  *so that* regulatory audit standards are satisfied and non-technical stakeholders understand rejection causes.  
  *Priority:* High | *Story Points:* 3

---

## Epic 4: Cryptographic Ledger & Auditability

- **US-12: SHA-256 Hash-Chained Audit Trail**  
  *As an* Internal Auditor,  
  *I want to* cryptographically chain every transaction decision record to the previous block's SHA-256 hash,  
  *so that* historical decision logs are mathematically tamper-evident and immune to retroactive alteration.  
  *Priority:* High | *Story Points:* 5

- **US-13: Automated Ledger Integrity Verification**  
  *As a* Security Compliance Officer,  
  *I want to* run an automated verification check over the entire ledger sequence,  
  *so that* any unauthorized database row tampering or record deletion is detected instantly.  
  *Priority:* Medium | *Story Points:* 3

---

## Epic 5: Serving API & Integration Gateway

- **US-14: Sub-100ms FastAPI Prediction Endpoint**  
  *As a* POS Client Integration Engineer,  
  *I want to* call `/api/v1/predict` and receive an authorization verdict within $100\text{ ms}$,  
  *so that* checkout lane throughput is preserved and customer payment flow is seamless.  
  *Priority:* Critical | *Story Points:* 5

- **US-15: Resilient Heuristic Fallback on Timeout**  
  *As a* Production Site Reliability Engineer,  
  *I want to* trigger a fallback heuristic rule set if ML inference exceeds $120\text{ ms}$,  
  *so that* high latency spikes never stall transaction processing.  
  *Priority:* High | *Story Points:* 3

- **US-16: Batch Evaluation & Operational Metrics API**  
  *As an* Operations Specialist,  
  *I want to* submit batch transaction arrays via `/api/v1/batch-predict` and query live system health via `/api/v1/metrics`,  
  *so that* offline audits and system health checks can be executed reliably.  
  *Priority:* Medium | *Story Points:* 3

---

## Epic 6: Simulation Dashboard & Operational Telemetry

- **US-17: Real-Time Streamlit Telemetry Dashboard**  
  *As a* Fraud Operations Lead,  
  *I want to* monitor live transaction streams, verdict percentages, and latency metrics on an auto-refreshing dashboard,  
  *so that* operational status is visible at a glance.  
  *Priority:* High | *Story Points:* 5

- **US-18: Interactive Fraud Vector Simulator**  
  *As an* Academic Evaluator / Thesis Committee Member,  
  *I want to* interactively simulate custom fraud scenarios (adjusting geo-distance, entropy, velocity, and amounts) in the UI,  
  *so that* I can evaluate the responsiveness and accuracy of the hybrid detection pipeline in real time.  
  *Priority:* High | *Story Points:* 5

---

## Epic 7: Privacy-Preserving Federated Model Simulation

- **US-19: Federated Averaging (FedAvg) Simulation**  
  *As a* Data Privacy Researcher,  
  *I want to* simulate decentralized model training across 3 merchant banking institutions using FedAvg,  
  *so that* I can demonstrate that cross-institutional fraud detection can be achieved without centralizing sensitive customer financial data.  
  *Priority:* Medium | *Story Points:* 5

