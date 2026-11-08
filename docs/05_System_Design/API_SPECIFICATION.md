# REST API Specification (OpenAPI v3 Standard)

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 05)  
**Parent Document:** `docs/05_System_Design/HIGH_LEVEL_DESIGN.md`  
**Base URL:** `http://localhost:8000/api/v1`  
**Content-Type:** `application/json`

---

## 1. Endpoint Index

| Method | Endpoint | Description | SLA Latency |
| :---: | :--- | :--- | :---: |
| `POST` | `/predict` | Ingest single transaction payload and return risk verdict. | $\le 100\text{ ms}$ (p99) |
| `POST` | `/batch-predict` | Batch evaluation of up to 500 transaction records. | $\le 1500\text{ ms}$ |
| `POST` | `/explain` | On-demand SHAP local feature attribution calculation. | $\le 50\text{ ms}$ |
| `POST` | `/challenge/verify` | Verify secondary MFA step-up challenge token. | $\le 30\text{ ms}$ |
| `GET` | `/ledger/verify` | Cryptographic audit of SHA-256 block chain continuity. | $\le 200\text{ ms}$ |
| `GET` | `/metrics` | Operational system telemetry and model evaluation statistics. | $\le 20\text{ ms}$ |
| `GET` | `/health` | Service liveness and readiness probe. | $\le 5\text{ ms}$ |

---

## 2. Granular Endpoint Definitions

### 2.1 `POST /predict` — Real-Time Payment Fraud Evaluation

- **Description:** Primary production inference endpoint. Accepts raw transaction parameters, validates schema boundaries, computes contextual features, queries state velocity, executes dual ML inference, determines verdict, records SHA-256 ledger block, and returns authorization decision.
- **Headers:**
  - `Content-Type: application/json`
  - `X-API-Key: <api-secret-key>` *(Optional in dev, required in production)*

#### Request Body (`TransactionRequestSchema`):
```json
{
  "transaction_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "timestamp": 1731102000000,
  "payer_id": "ACC_PAYER_884920",
  "merchant_id": "MERCH_POS_104829",
  "qr_type": 1,
  "qr_payload": "https://secure.paygate.com/qr?m=MERCH_POS_104829&amt=145.50",
  "amount": 145.50,
  "merchant_category_code": 5411,
  "payer_latitude": 23.8103,
  "payer_longitude": 90.4125,
  "merchant_latitude": 23.8110,
  "merchant_longitude": 90.4132,
  "device_trust_score": 0.95,
  "scan_to_pay_latency_ms": 3200,
  "failed_pin_attempts": 0
}
```

#### Response Body (`TransactionResponseSchema`):
```json
{
  "transaction_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "timestamp": 1731102000000,
  "verdict": "APPROVE",
  "supervised_score": 0.0421,
  "anomaly_score": 0.0815,
  "composite_score": 0.0539,
  "is_zero_day_escalation": false,
  "reason_codes": [],
  "ledger_block_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "response_time_ms": 31.4
}
```

#### Custom Response Headers:
- `X-Response-Time-Ms`: Float execution duration (e.g., `31.4`).
- `X-Fallback-Engaged`: Boolean string (`true` or `false`).

---

### 2.2 `POST /explain` — On-Demand SHAP Attribution

- **Description:** Generates local Shapley values and feature importance rankings for any historical or candidate feature vector.

#### Request Body:
```json
{
  "transaction_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "include_all_features": false,
  "top_k": 3
}
```

#### Response Body:
```json
{
  "transaction_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "base_value": 0.0082,
  "predicted_probability": 0.8840,
  "top_reasons": [
    {
      "feature_name": "haversine_distance_km",
      "value": 412.5,
      "shap_value": 0.4210,
      "impact": "INCREASES_RISK",
      "reason_code": "GEO_DISTANCE_ANOMALOUS"
    },
    {
      "feature_name": "qr_payload_entropy",
      "value": 6.84,
      "shap_value": 0.2850,
      "impact": "INCREASES_RISK",
      "reason_code": "PAYLOAD_ENTROPY_CRITICAL"
    },
    {
      "feature_name": "velocity_1h",
      "value": 9.0,
      "shap_value": 0.1240,
      "impact": "INCREASES_RISK",
      "reason_code": "SCAN_VELOCITY_ELEVATED"
    }
  ]
}
```

---

### 2.3 `POST /challenge/verify` — MFA Step-Up Confirmation

- **Description:** Receives authentication confirmation from the client application after a customer completes step-up biometric or OTP verification for a `CHALLENGE_MFA` verdict.

#### Request Body:
```json
{
  "transaction_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "challenge_token": "CHAL_f83a09b4-1290-481b",
  "verification_status": "SUCCESS",
  "auth_method": "BIOMETRIC_FINGERPRINT"
}
```

#### Response Body:
```json
{
  "transaction_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "CHALLENGE_RESOLVED",
  "final_authorization": "APPROVED",
  "verified_at": "2026-11-08T22:20:00Z"
}
```

---

### 2.4 `GET /ledger/verify` — Cryptographic Chain Verification

- **Description:** Verifies that the SHA-256 cryptographic parent-hash chain is 100% unbroken and unaltered from the Genesis Block to the most recent transaction block.

#### Response Body (Clean Chain):
```json
{
  "integrity_status": "VERIFIED",
  "total_blocks_audited": 14820,
  "genesis_block_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "latest_block_hash": "9f83acb182049d10e82c819280148b8120384910284918209384019283401928",
  "tamper_detected": false,
  "corrupted_block_id": null
}
```

#### Response Body (Tamper Detected Alert):
```json
{
  "integrity_status": "CORRUPTED",
  "total_blocks_audited": 14820,
  "tamper_detected": true,
  "corrupted_block_id": 412,
  "error_description": "Hash mismatch at Block #412: Stored hash does not match recomputed SHA-256 digest."
}
```

---

### 2.5 `GET /metrics` — Telemetry & Operational Health

- **Description:** Returns aggregate statistics, model latency percentiles, and live throughput counts for the Streamlit dashboard and Prometheus monitors.

#### Response Body:
```json
{
  "system_status": "HEALTHY",
  "active_model": "LightGBM_v1.0.0",
  "total_processed_transactions": 254890,
  "verdict_distribution": {
    "APPROVE": 248920,
    "CHALLENGE_MFA": 3940,
    "BLOCK": 2030
  },
  "latency_metrics": {
    "p50_ms": 28.5,
    "p95_ms": 62.1,
    "p99_ms": 84.7
  },
  "accuracy_scoreboard": {
    "recall": 0.978,
    "precision": 0.924,
    "f1_score": 0.950,
    "f2_score": 0.967,
    "pr_auc": 0.912
  }
}
```

---

## 3. Error Handling & Standardized Diagnostics

All non-200 HTTP responses conform to the following RFC 7807 Problem Details schema:

```json
{
  "error_code": "UNPROCESSABLE_ENTITY",
  "message": "Validation failed for incoming transaction payload.",
  "status_code": 422,
  "timestamp": 1731102000000,
  "details": [
    {
      "field": "payer_latitude",
      "issue": "Value 142.5 exceeds permissible latitude range [-90.0, 90.0]."
    }
  ]
}
```

