# Architecture Decision Records (ADR)

This file documents the architectural decisions made during the design and implementation of the Advanced QR Code Payment Fraud Detection System.

---

## ADR-001: Workspace Isolation and Monorepo Scaffolding
- **Date:** 2026-11-08
- **Status:** Accepted
- **Context:** The project requires a clean boundary between raw proposal assets and executable software artifacts, ensuring reproducible development without polluting the parent directory or losing the primary specification.
- **Decision:** Establish an isolated workspace directory named `advanced-qr-code-payment-fraud-detection-system/` containing dedicated tiers for `source/`, `docs/`, `frontend/`, `backend/`, `database/`, `tests/`, `scripts/`, `research/`, and `deployment/`. The original markdown specification is mirrored immutably into `source/`.
- **Consequences:** All future code, scripts, dependencies, tests, and documentation will remain strictly inside this directory tree.

---

## ADR-002: Hybrid Scoring Paradigm (Supervised + Unsupervised)
- **Date:** 2026-11-08
- **Status:** Accepted (from Proposal Specification)
- **Context:** Fraud vectors in QR payments continuously mutate. Supervised models trained on historical data excel at known attack patterns but fail to identify zero-day anomalies, whereas unsupervised models catch distributional outliers but lack targeted precision.
- **Decision:** Implement a dual-tier hybrid inference engine combining supervised classification probability ($P(\text{Fraud} \mid X)$) from tree ensembles/neural networks with an anomaly score ($S_{\text{unsupervised}}$) from Isolation Forest. Aggregate both via a calibrated weighted risk formula:
  $$S_{\text{composite}} = 0.70 \cdot P_{\text{supervised}} + 0.30 \cdot S_{\text{unsupervised}}$$
- **Consequences:** Maximizes recall while suppressing false positives and retaining the capacity to challenge novel attacks.

---

## ADR-003: Explainability and Auditability by Design
- **Date:** 2026-11-08
- **Status:** Accepted (from Proposal Specification)
- **Context:** Modern financial regulations mandate algorithmic transparency (countering the "black-box" dilemma) and non-repudiation of security decisions.
- **Decision:**
  1. Integrate SHAP (SHapley Additive exPlanations) to dynamically generate top contributing feature rationales for flagged or rejected payments.
  2. Implement an append-only SHA-256 hash-chained ledger to ensure immutable logging of all authorization verdicts.
- **Consequences:** The inference pipeline incurs a slight computational overhead (budgeted at $\le 40\text{ ms}$ for SHAP calculations), which satisfies the global $< 100\text{ ms}$ latency budget.

