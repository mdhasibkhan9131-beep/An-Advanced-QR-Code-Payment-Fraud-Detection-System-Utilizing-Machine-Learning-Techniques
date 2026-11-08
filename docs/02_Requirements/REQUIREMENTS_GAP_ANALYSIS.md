# Requirements Gap Analysis & Architectural Ambiguities

**Document Version:** 1.0.0  
**Status:** Under Review (Phase 02 Deliverable)  
**Parent Document:** `docs/02_Requirements/SRS.md`  
**Reference Document:** `source/PROJECT_SPEC.md`

---

## 1. Confirmed Requirements vs. Recommended Enhancements

### 1.1 Confirmed Requirements (Directly Mandated by Proposal)
- Multi-vector ingestion for QR transactions (16-attribute schema).
- Real-time ML inference targeting sub-100ms response time.
- Severe class imbalance handling via SMOTE oversampling.
- Multi-algorithm benchmark suite (Logistic Regression, Decision Trees, Random Forest, SVM, LightGBM, Deep MLP).
- Unsupervised anomaly detection via Isolation Forest to detect novel zero-day exploits.
- Explainable AI (XAI) using SHAP TreeExplainer for high-risk flags.
- Three-tier decision gating (`APPROVE`, `CHALLENGE_MFA`, `BLOCK`).
- Cryptographic hash-chained immutable audit ledger (SHA-256).
- Federated learning (FedAvg) architectural simulation for financial privacy.
- Interactive telemetry dashboard and simulation interface.

### 1.2 Recommended Architectural Enhancements (Proposed for Operational Robustness)
- **Heuristic Fallback Circuit Breaker:** In the event of thread lock or timeout ($> 120\text{ ms}$), automatically fail over to a deterministic heuristic rule set to ensure non-blocking payment flow.
- **Selective SHAP Computation:** Computing SHAP on every single transaction can introduce $25 - 40\text{ ms}$ latency overhead. We recommend restricting automatic SHAP calculation to transactions receiving `CHALLENGE_MFA` or `BLOCK` (or explicit API `/explain` calls), bypassing it for clearly low-risk payments (`APPROVE`).
- **Hybrid In-Memory State Cache:** Use an internal thread-safe in-memory sliding window TTL cache when Redis is unavailable, ensuring the entire system can run 100% standalone and offline without requiring an external Redis server daemon.

---

## 2. Identified Ambiguities, Gaps, and Conflicts

| ID | Specification Item | Nature of Ambiguity / Gap | Proposal Baseline | Impact | Recommended Resolution | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GAP-01** | **Redis vs. Standalone Local Caching** | The proposal cites Redis for sliding window velocities ($V_{5\text{m}}, V_{1\text{h}}, V_{24\text{h}}$) but also mandates standalone offline execution without complex service dependencies. | Redis listed in tech stack; standalone constraint mentioned in NFRs. | High | Implement a unified `StateCache` interface with an in-memory TTL implementation by default, with an optional pluggable Redis adapter via environment variable (`CACHE_BACKEND=memory|redis`). | **DECISION REQUIRED** |
| **GAP-02** | **Step-Up MFA Challenge Protocol** | When a verdict is `CHALLENGE_MFA`, how does the client application confirm authentication back to the fraud engine? | Mentioned in decision gating (`0.30 - 0.70`), but feedback endpoint was unspecified. | Medium | Add an optional endpoint `/api/v1/challenge/verify` that accepts a challenge token and updates the ledger record to `MFA_VERIFIED`. | **DECISION REQUIRED** |
| **GAP-03** | **Federated Learning Execution Boundary** | Is the Federated Learning module an active online microservice or a standalone reproducible simulation script? | Proposal designates it as an "architectural exploration" / "simulation". | Medium | Implement as an offline reproducible research module (`research/federation/` & `scripts/run_federated_simulation.py`) rather than a live multi-tenant network daemon. | **DECISION REQUIRED** |
| **GAP-04** | **Deep Learning Framework Choice** | Proposal references "deep neural variants (MLP / Tabular ResNet)" and lists PyTorch in technical stack. | PyTorch specified in stack table. | Low | Adopt PyTorch (CPU-compatible) for the Tabular MLP baseline; export to ONNX for low-latency inference if needed. | **DECISION REQUIRED** |
| **GAP-05** | **Cryptographic Ledger Persistence** | Should the append-only SHA-256 ledger be stored as a flat JSONL chain or managed within SQLite tables? | "Local cryptographic hash ledger" / SQLite. | Low | Implement as an SQLite table (`audit_ledger`) where each row contains `prev_hash`, `block_hash`, and transaction metadata, with an export utility to verifiable JSONL. | **DECISION REQUIRED** |

---

## 3. Items Marked as TBD (To Be Decided / Finalized)

1. **TBD-01: PII Salting Key Management**  
   *Current Proposal:* Salted SHA-256 hashing.  
   *TBD:* Whether salt is loaded via `.env` (`SALT_SECRET_KEY`) or generated per installation.  
   *Recommendation:* Load from `.env` with a strong default for development.

2. **TBD-02: Target Imbalance Ratio in Synthetic Data Generator**  
   *Current Proposal:* Fraud represents a marginal fraction ($< 1\%$).  
   *TBD:* Exact synthetic benchmark ratio (e.g., $0.5\%$, $0.8\%$, or $1.0\%$).  
   *Recommendation:* Configurable via parameter `fraud_ratio=0.008` ($0.8\%$).

3. **TBD-03: Asymmetric Cost Utility Values**  
   *Current Proposal:* $C_{\text{fraud}} = \$150.00$, $C_{\text{friction}} = \$5.00$, $C_{\text{review}} = \$0.50$.  
   *TBD:* Whether to allow dynamic customization via the Streamlit UI.  
   *Recommendation:* Expose interactive loss tuning sliders in the Streamlit benchmark view.

---

## 4. Decisions Requiring Stakeholder Approval

Before proceeding to **Phase 03: Architecture & Technical Design**, the project manager and stakeholder must formally authorize the following 5 decisions:

1. **Decision D-01: Dual Cache Backend**  
   *Approve* defaulting to an in-memory sliding window cache for zero-dependency local runs, with optional Redis connectivity.
2. **Decision D-02: Selective SHAP Execution for Performance**  
   *Approve* calculating SHAP attributions synchronously only for transactions classified as `CHALLENGE_MFA` or `BLOCK`, and on-demand via `/api/v1/explain`, guaranteeing p99 latency $< 100\text{ ms}$ for low-risk traffic.
3. **Decision D-03: Scope of Federated Learning Integration**  
   *Approve* packaging Federated Learning (FedAvg) as an automated simulation and comparative evaluation module rather than a live multi-node network cluster.
4. **Decision D-04: Deep Learning Implementation in PyTorch**  
   *Approve* PyTorch CPU-compatible Tabular Multi-Layer Perceptron as the primary deep neural candidate alongside LightGBM and Random Forest.
5. **Decision D-05: Ledger Storage Architecture**  
   *Approve* SQLite-backed relational storage with SHA-256 block linking, complete with a `/api/v1/ledger/verify` integrity auditing endpoint.

