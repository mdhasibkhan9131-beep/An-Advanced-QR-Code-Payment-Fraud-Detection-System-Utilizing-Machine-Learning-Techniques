# Security Architecture & Defensive Engineering Specification

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 05)  
**Parent Document:** `docs/05_System_Design/HIGH_LEVEL_DESIGN.md`  
**Reference Standards:** OWASP API Security Top 10, ISO/IEC 27001, GDPR Article 22

---

## 1. Authentication & Role-Based Access Control (RBAC)

The system enforces a lightweight, defense-in-depth authorization model:

```
[ Client Request ] ──> [ Auth Middleware: API Key / JWT ] ──> [ Role-Based Gateway ]
                                                                       │
                    ┌───────────────────────────┬──────────────────────┴──────────────────────┐
                    ▼                           ▼                                             ▼
          [ Client Role: /predict ]   [ Analyst Role: /metrics, /explain ]          [ Admin: /ledger/verify ]
```

### 1.1 Defined User & System Roles:
1. **`ROLE_CLIENT` (Payment App / POS Scanner):** Authorized to invoke `/api/v1/predict` and `/api/v1/challenge/verify`. Authenticated via mutual TLS (mTLS) or static pre-shared `X-API-Key` headers.
2. **`ROLE_ANALYST` (Fraud Investigation Specialist):** Authorized to view Streamlit telemetry dashboards, inspect `/api/v1/metrics`, and execute on-demand `/api/v1/explain` calls.
3. **`ROLE_ADMIN` (Compliance Auditor / System Admin):** Authorized to trigger cryptographic chain auditing (`/api/v1/ledger/verify`) and execute offline model retraining pipelines.

---

## 2. PII Sanitization & Data Protection Architecture

In strict compliance with financial privacy standards, Personally Identifiable Information (PII) is masked immediately at the API gateway layer before any feature extraction or persistent storage takes place:

```python
import hashlib
import os

SECRET_SALT = os.getenv("PII_SECRET_SALT", "default_secure_salt_value_2026")

def sanitize_payer_identifier(raw_payer_id: str) -> str:
    """Computes irreversible salted SHA-256 digest of account identifier."""
    salted_str = f"{SECRET_SALT}:{raw_payer_id}".encode("utf-8")
    return hashlib.sha256(salted_str).hexdigest()
```

- **Zero Plaintext Persistence:** The raw `payer_id` is discarded from memory after validation; only `payer_hash` is written to the SQLite database or state cache.
- **Data Encryption at Rest:** When deployed in production environments, SQLite database volumes must utilize Linux LUKS volume encryption or SQLite SQLCipher extension.

---

## 3. Cryptographic Tamper-Evident Ledger Integrity

Each transaction decision is permanently linked to an append-only cryptographic ledger using the SHA-256 digest chaining formula:

$$H_k = \text{SHA256}\left(H_{k-1} \,\|\, \text{TxID}_k \,\|\, S_{\text{composite}} \,\|\, \text{Verdict}_k \,\|\, t_k \,\|\, \text{SaltedPayerHash}\right)$$

### Tamper-Evident Guarantees:
- **Parent Hash Binding ($H_{k-1}$):** Any alteration of a historical transaction row (e.g., modifying an authorization score or verdict post-facto) alters that block's hash, causing a hash mismatch in all subsequent child blocks.
- **Automated Audit Endpoint:** Calling `GET /api/v1/ledger/verify` performs a linear verification scan of the entire chain, pinpointing the exact corrupted block index within milliseconds.

---

## 4. Adversarial Machine Learning Defenses

To counter adversarial manipulation where attackers subtly manipulate inputs to evade algorithmic detection:
1. **Input Clamping & Physiological Boundary Verification:**
   All features are validated and clamped to strict numerical bounds:
   - Coordinates: Latitude $\in [-90.0, 90.0]$, Longitude $\in [-180.0, 180.0]$.
   - Transaction Amount: Clamped to $[0.01, 1{,}000{,}000.00]$.
   - Scan Latency: Clamped to $[0, 600{,}000\text{ ms}]$.
2. **Dual-Model Anomaly Trap:**
   Adversarial attacks that evade tree-based split thresholds in LightGBM are caught by the unsupervised **Isolation Forest**. Unprecedented feature vectors exhibit short average path lengths $\mathbb{E}[h(x)] \ll c(n)$, producing an anomaly score $S_{\text{anomaly}} > 0.80$ that triggers automatic escalation to `CHALLENGE_MFA`.

---

## 5. Resiliency & Deterministic Fallback Circuit Breaker

```
[ Request Ingestion ] ──> [ 120ms Async Timeout Watchdog ]
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
[ If Execution <= 120ms: ML Verdict ]               [ If Execution > 120ms: TIMEOUT ]
                                                                │
                                                                ▼
                                                    [ Fallback Rule Engine ]
                                                    - If Amount > $1000: CHALLENGE
                                                    - If Velocity > 5: CHALLENGE
                                                    - Else: APPROVE (Degraded Flag)
```

- **Availability Assurance:** Even in the event of thread lock, memory exhaustion, or model deadlock, payment authorization calls return within $130\text{ ms}$ with diagnostic header `X-Fallback-Engaged: true`.
- **Error Shielding:** Internal application stack traces, SQL error strings, or system paths are stripped from error responses and logged strictly to secure server-side diagnostic files.

