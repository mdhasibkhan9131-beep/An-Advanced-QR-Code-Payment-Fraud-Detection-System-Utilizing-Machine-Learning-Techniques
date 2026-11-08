# User & Operator Manual

**Project Title:** Advanced Quick Response (QR) Code Payment Fraud Detection System Utilizing Machine Learning Techniques  
**Document Version:** `1.0.0`  
**Classification:** Operational Guide for System Administrators, Fraud Analysts & Fintech Developers  
**Target Environments:** Containerized (Docker Compose) & Bare-Metal Local Server  

---

## 1. System Overview & Target Audiences

The *Advanced QR Code Payment Fraud Detection System* is an automated, high-throughput fraud risk engine designed to protect digital wallet, merchant payment, and POS transactions from Quishing (QR phishing), Dynamic MITM payment surges, and credential probing bot attacks.

### Primary User Roles:
- **System Administrators & DevOps:** Responsible for deploying, monitoring, backing up, and maintaining the microservice stack.
- **Fraud Risk Analysts & Compliance Officers:** Responsible for reviewing flagged transactions, auditing explainability reason codes, and verifying cryptographic ledger integrity.
- **Fintech Integration Developers:** Responsible for connecting merchant mobile apps and core banking payment gateways to the REST API.

---

## 2. System Startup & Quickstart Guide

### Option A: Running with Docker Compose (Recommended for Production)

Ensure Docker 24.0+ and Docker Compose v2 are installed:

```bash
# 1. Navigate to the project root
cd advanced-qr-code-payment-fraud-detection-system

# 2. Build and launch the multi-container stack in the background
docker compose -f deployment/docker-compose.yml up -d --build

# 3. Verify container statuses
docker compose -f deployment/docker-compose.yml ps
```

The stack exposes two primary services:
- **API Microservice Gateway:** `http://localhost:8000`
- **Streamlit Fraud Monitoring UI:** `http://localhost:8501`

### Option B: Running on Bare-Metal (Python 3.11)

```bash
# 1. Activate virtual environment
cd advanced-qr-code-payment-fraud-detection-system
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/macOS

# 2. Start the FastAPI microservice gateway (Terminal 1)
python -m uvicorn backend.api.server:app --host 0.0.0.0 --port 8000 --workers 4

# 3. Start the Streamlit monitoring dashboard (Terminal 2)
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 3. Web Interfaces & Operational Portals

### 3.1 FastAPI Interactive OpenAPI Documentation
Open your browser and navigate to:  
`http://localhost:8000/docs`

- Provides a live, interactive Swagger interface to test endpoints, inspect JSON schemas, and review HTTP error codes.
- Alternative ReDoc specification available at `http://localhost:8000/redoc`.

### 3.2 System Health & Telemetry Probes
- **Health Check Probe:** `GET http://localhost:8000/api/v1/health`  
  Returns JSON status indicating API readiness, database WAL connectivity, and pre-warmed model status.
- **Operational Metrics Probe:** `GET http://localhost:8000/api/v1/metrics`  
  Returns real-time operational metrics including total transactions evaluated, approval/challenge/block counts, and latency percentiles (P50, P95, P99).

---

## 4. Streamlit Monitoring Dashboard Walkthrough

Open your browser and navigate to:  
`http://localhost:8501`

The dashboard is organized into five dedicated functional views designed in a high-contrast **Fintech Dark Theme**:

```
┌────────────────────────────────────────────────────────────────────────┐
│               ADVANCED QR CODE PAYMENT FRAUD MONITORING UI             │
├──────────────┬──────────────┬──────────────┬──────────────┬────────────┤
│ [1] Overview │ [2] Single Tx│ [3] Batch UI │ [4] Ledger   │ [5] Model  │
│  & Telemetry │   Simulator  │   Clearance  │   Auditor    │  Benchmark │
└──────────────┴──────────────┴──────────────┴──────────────┴────────────┘
```

### Tab 1: System Telemetry Scoreboard
- **Real-Time KPIs:** Visual counters for Total Processed Transactions, Intercepted Fraud Count, Mean Processing Latency (ms), and Cryptographic Ledger Height.
- **Verdict Distribution Chart:** Interactive donut chart displaying the live ratio of `APPROVE`, `CHALLENGE_MFA`, and `BLOCK` decisions.
- **Inference Latency Timeline:** Real-time line chart tracking transaction response times against the sub-100ms financial SLA ceiling.

### Tab 2: Single Transaction Risk Evaluator & Simulator
- **Transaction Parameter Controls:**
  - Customer ID & Merchant ID inputs.
  - Transaction Amount (USD) slider.
  - Decoded QR Payload String (supports pasting arbitrary URLs or static tokens).
  - Geolocation Pickers (Customer Latitude/Longitude vs Merchant Latitude/Longitude).
- **Execution Button:** Click *"Evaluate Transaction Risk"*.
- **Visual Output:**
  - **Verdict Banner:** Color-coded status badge (`APPROVE` in emerald, `CHALLENGE_MFA` in amber, `BLOCK` in crimson).
  - **Composite Risk Gauge:** Metric dial indicating $S_{\text{composite}} \in [0.0, 1.0]$.
  - **SHAP Explanation Bar:** Breakdown of top risk-contributing factors with standardized reason codes (e.g., `ANOMALOUS_QR_PAYLOAD_ENTROPY`, `GEOGRAPHIC_DISPLACEMENT_EXCEEDED`).
  - **Audit Block Info:** SHA-256 block hash and HMAC signature.

### Tab 3: Batch Clearance & Bulk Scoring
- **Bulk Data Ingestion:** Allows compliance officers to upload a CSV or JSON settlement file containing multiple QR payment records.
- **Batch Processing:** Runs high-speed parallel evaluation across all records.
- **Data Grid:** Exportable tabular report with flagged transactions highlighted for manual review.

### Tab 4: Cryptographic Blockchain Ledger Auditor
- **Ledger Explorer:** Chronological table displaying all committed blocks, parent hashes, transaction IDs, verdicts, and cryptographic signatures.
- **Chain Verification Button:** Click *"Verify Blockchain Integrity"*.
- **Verification Engine:** Sequentially recomputes SHA-256 hashes from the Genesis block to the tip of the chain.
- **Tamper Alert:** Displays a green banner if integrity is verified (`CHAIN_INTEGRITY_VERIFIED`). If any database row has been altered, displays a red alert indicating the exact block index of the detected tampering.

### Tab 5: Empirical Machine Learning Benchmark Visualizer
- **Candidate Algorithm Comparison:** Comparative tables and radar charts contrasting Logistic Regression, SVM, PyTorch MLP, Random Forest, Isolation Forest, LightGBM, and the Proposed Hybrid Model.
- **Evaluation Metrics:** Accuracy, Precision, Recall, Specificity, F1-Score, False Positive Rate (FPR), ROC-AUC, and Inference Latency.

---

## 5. REST API Integration Guide (Examples)

### 5.1 Real-Time Transaction Prediction (`POST /api/v1/predict`)

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx-20261108-001",
    "customer_id": "cust_84920",
    "merchant_id": "merch_10492",
    "amount": 45.00,
    "currency": "USD",
    "customer_lat": 40.7128,
    "customer_lon": -74.0060,
    "merchant_lat": 40.7130,
    "merchant_lon": -74.0058,
    "qr_payload": "https://pay.bank.com/transfer?id=merch_10492",
    "timestamp": "2026-11-08T23:45:00Z"
  }'
```

**JSON Response (`APPROVE`):**
```json
{
  "transaction_id": "tx-20261108-001",
  "verdict": "APPROVE",
  "risk_score": 0.0842,
  "supervised_score": 0.0410,
  "unsupervised_score": 0.1850,
  "reason_codes": [],
  "processing_time_ms": 14.85,
  "ledger_block_hash": "a4f89d9e23bc...",
  "timestamp": "2026-11-08T23:45:00.015Z"
}
```

### 5.2 Quishing Attack Detection Example (`POST /api/v1/predict`)

**Payload with Obfuscated Phishing QR Payload & High Entropy:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx-20261108-002",
    "customer_id": "cust_84920",
    "merchant_id": "merch_10492",
    "amount": 250.00,
    "currency": "USD",
    "customer_lat": 40.7128,
    "customer_lon": -74.0060,
    "merchant_lat": 51.5074,
    "merchant_lon": -0.1278,
    "qr_payload": "https://phish.net/?token=q8$Z#2!kL9%wP*vM&1^xR7@bC5",
    "timestamp": "2026-11-08T23:45:00Z"
  }'
```

**JSON Response (`BLOCK` with SHAP Explanations):**
```json
{
  "transaction_id": "tx-20261108-002",
  "verdict": "BLOCK",
  "risk_score": 0.9449,
  "supervised_score": 0.9980,
  "unsupervised_score": 0.8210,
  "reason_codes": [
    "ANOMALOUS_QR_PAYLOAD_ENTROPY",
    "GEOGRAPHIC_DISPLACEMENT_EXCEEDED"
  ],
  "processing_time_ms": 26.40,
  "ledger_block_hash": "c81d3f01b7a2...",
  "timestamp": "2026-11-08T23:45:00.026Z"
}
```

### 5.3 Cryptographic Ledger Audit Probe (`GET /api/v1/ledger/verify`)

```bash
curl -X GET "http://localhost:8000/api/v1/ledger/verify"
```

**JSON Response (Integrity Verified):**
```json
{
  "status": "CHAIN_INTEGRITY_VERIFIED",
  "total_blocks_verified": 243,
  "last_block_hash": "7e48b3c9a1d...",
  "tamper_detected": false,
  "corrupted_block_index": null,
  "verified_at": "2026-11-08T23:45:10Z"
}
```

---

## 6. Operational Troubleshooting & Error Resolution

| Symptom / Error Code | Probable Root Cause | Resolution Action |
| :--- | :--- | :--- |
| **HTTP 422: `TIMESTAMP_DRIFT_EXCEEDED`** | Client device clock is desynchronized by more than 300 seconds from server clock. | Synchronize client system clock via NTP (`pool.ntp.org`). |
| **HTTP 500: Database Locked** | Massive concurrent writes without WAL mode enabled. | Verify SQLite WAL mode is active: execute `python -c "import sqlite3; con = sqlite3.connect('database/fraud_detection.db'); print(con.execute('PRAGMA journal_mode;').fetchone())"`. Output must be `('wal',)`. |
| **First Request Latency > 100ms** | Model container was not pre-warmed during server startup. | Ensure server is started through `backend.api.server:app` which executes the `lifespan` hook. |
| **Ledger Verification Reports `CHAIN_TAMPERED`** | An external process or administrator altered a record in the `transactions` or `ledger_blocks` table. | Restore the database from the most recent verified backup: `python scripts/restore_database.py --backup database/backups/<backup_file>.db.gz`. |
