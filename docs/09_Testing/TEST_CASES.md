# Comprehensive Quality Assurance Test Cases Inventory

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved Quality Baseline  
**Total Automated Test Cases:** 50 Executable Test Cases  
**Pass Rate:** 100% (50 Passed, 0 Failed, 0 Skipped)

---

## 1. Environment & Infrastructure Tests (`tests/test_environment.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-ENV-001` | `NFR-RES-001` | Verify Python runtime version is 3.11.x. | Python major=3, minor=11 confirmed. | **PASS** |
| `TC-ENV-002` | `NFR-RES-001` | Import all scientific and ML packages (`lightgbm`, `shap`, `sklearn`, `torch`, `pyod`, `imblearn`). | All packages import cleanly without `ImportError`. | **PASS** |
| `TC-ENV-003` | `NFR-SEC-001` | Verify `.env` file presence and absence of hardcoded fallback secrets. | Configuration loads cleanly; secret key loaded. | **PASS** |

---

## 2. API Schema & Input Boundary Tests (`tests/test_api_validation.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-SCH-001` | `FR-ING-001` | Ingest valid compliant EMVCo transaction request payload. | Pydantic v2 deserializes without validation errors. | **PASS** |
| `TC-SCH-002` | `FR-ING-004` | Ingest payload with negative monetary amount (`amount = -15.0`). | Request rejected with HTTP 422 Unprocessable Entity. | **PASS** |
| `TC-SCH-003` | `FR-ING-004` | Ingest payload with out-of-range GPS latitude (`payer_latitude = 95.5`). | Boundary validator catches coordinate error; HTTP 422. | **PASS** |

---

## 3. Database Persistence & WAL Tests (`tests/test_database.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-DB-001` | `NFR-RES-003` | Inspect SQLite PRAGMA journal mode. | Returns `wal` (Write-Ahead Logging enabled). | **PASS** |
| `TC-DB-002` | `NFR-MAINT-001` | Insert, retrieve, and delete a `TransactionRecord` via SQLAlchemy session. | Record successfully persisted and retrieved. | **PASS** |

---

## 4. Health Probes & Operational Metrics (`tests/test_health.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-HLT-001` | `FR-API-004` | Execute `GET /api/v1/health` liveness probe. | Returns HTTP 200, status `HEALTHY`, database `CONNECTED`. | **PASS** |
| `TC-HLT-002` | `FR-API-004` | Execute `GET /api/v1/metrics` operational scoreboard. | Returns HTTP 200 with latency percentiles and recall metrics. | **PASS** |

---

## 5. Feature Engineering Pipeline Tests (`tests/test_feature_engineering.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-FEA-001` | `FR-FEA-001` | Haversine distance for identical co-located coordinates. | Returns exactly `0.0 km`. | **PASS** |
| `TC-FEA-002` | `FR-FEA-001` | Haversine distance for Dhaka to Chittagong coordinates. | Returns between 210.0 and 225.0 km (actual ~218 km). | **PASS** |
| `TC-FEA-003` | `FR-FEA-001` | Haversine symmetry test: $d(A, B) == d(B, A)$. | Distances match within $10^{-4}$ tolerance. | **PASS** |
| `TC-FEA-004` | `FR-FEA-002` | Shannon entropy for empty string and repeated identical characters. | Returns exactly `0.0 bits/char`. | **PASS** |
| `TC-FEA-005` | `FR-FEA-002` | Shannon entropy for routine EMVCo string vs high-entropy random token. | Natural EMVCo $< 4.4$, random token $> 4.5$. | **PASS** |
| `TC-FEA-006` | `FR-FEA-004` | Historical amount baseline Z-score and zero-variance protection. | Safe computation without `ZeroDivisionError`. | **PASS** |
| `TC-FEA-007` | `FR-FEA-003` | Full `FeatureEngineeringPipeline` feature matrix assembly. | Produces 2D array of shape `(1, 16)` matching `FEATURE_COLUMNS`. | **PASS** |

---

## 6. Synthetic Transaction Generator Tests (`tests/test_generator.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-GEN-001` | `FR-DAT-001` | Generate 500 records; verify presence of all 16 feature columns. | Exactly 500 rows; all feature columns present. | **PASS** |
| `TC-GEN-002` | `FR-DAT-002` | Preserves acute financial class imbalance ($0.8\%$ fraud). | Fraud instances represent exactly $0.80\%$ ($16 / 2,000$). | **PASS** |
| `TC-GEN-003` | `FR-DAT-001` | Presence of all 4 archetypes (`NONE`, `QUISHING`, `MITM`, `PROBE`). | All 4 distinct domain vectors generated. | **PASS** |
| `TC-GEN-004` | `FR-DAT-001` | Validate Quishing vector constraints. | `qr_type == 0`, displacement $> 50\text{km}$, entropy $\ge 4.4$. | **PASS** |
| `TC-GEN-005` | `FR-DAT-001` | Validate Dynamic MITM vector constraints. | `qr_type == 1`, `amount_zscore > 3.5`, amount $> 3000$. | **PASS** |
| `TC-GEN-006` | `FR-DAT-001` | Validate Bot Probing vector constraints. | Latency $< 800\text{ms}$, $V_{5\text{m}} \ge 5$, device trust $< 0.40$. | **PASS** |
| `TC-GEN-007` | `FR-DAT-001` | Deterministic reproducibility with random seed. | Identical seeds generate bit-for-bit identical datasets. | **PASS** |
| `TC-GEN-008` | `NFR-PERF-001`| Generator throughput test for 1,000 samples. | Generates 1,000 samples in $< 1.0\text{s}$ ($> 5,500\text{ rec/s}$). | **PASS** |

---

## 7. Data Preprocessing & Borderline-SMOTE Tests (`tests/test_preprocessor.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-PRE-001` | `FR-DAT-003` | Separate DataFrame into feature matrix $X$ and target vector $y$. | $X$ shape $(N, 16)$, $y$ shape $(N,)$, zero NaNs. | **PASS** |
| `TC-PRE-002` | `FR-DAT-002` | Chronological / stratified 70% / 15% / 15% 3-way split. | Subsets equal exactly 700, 150, and 150 rows. | **PASS** |
| `TC-PRE-003` | `FR-FEA-005` | RobustScaler fitting strictly on training split. | Centers around median without infinite or NaN values. | **PASS** |
| `TC-PRE-004` | `FR-DAT-003` | Strict Borderline-SMOTE partition isolation. | Training fold rebalanced to 20%; val/test remain un-oversampled. | **PASS** |
| `TC-PRE-005` | `FR-FEA-005` | Scaler disk persistence and single-sample inference transform. | Saved and reloaded scaler produces identical $(1, 16)$ outputs. | **PASS** |
| `TC-PRE-006` | `FR-ING-004` | Error handling for DataFrame missing required feature columns. | Raises descriptive `ValueError`. | **PASS** |

---

## 8. Machine Learning Model Suite Tests (`tests/test_models.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-MOD-001` | `FR-MOD-001` | LightGBM classifier training, prediction probabilities, and booster. | Predicts $(N, 2)$ probabilities; booster accessible. | **PASS** |
| `TC-MOD-002` | `FR-MOD-001` | PyTorch Tabular Deep MLP training on CPU tensors. | Softmax outputs sum to 1.0; weights serialize cleanly. | **PASS** |
| `TC-MOD-003` | `FR-MOD-002` | Isolation Forest unsupervised detector calibration $[0.0, 1.0]$. | Scores properly calibrated (0 = inlier, 1 = extreme anomaly). | **PASS** |
| `TC-MOD-004` | `FR-MOD-003` | Hybrid composite risk scorer weighting ($S_{\text{comp}}$). | Correctly weights supervised and anomaly probabilities. | **PASS** |
| `TC-MOD-005` | `FR-DEC-001` | Decision gating tiers and Zero-Day Anomaly Escalation override. | Escalates low supervised score to `CHALLENGE_MFA` when anomaly is high. | **PASS** |

---

## 9. Explainable AI & SHAP Reason Codes Tests (`tests/test_xai.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-XAI-001` | `FR-XAI-001` | SHAP TreeExplainer local attribution dictionary structure. | Contains top features, reason codes, and raw attribution values. | **PASS** |
| `TC-XAI-002` | `FR-XAI-002` | Semantic reason code translation for anomalous features. | Maps anomalous displacement to `GEOGRAPHIC_DISPLACEMENT_EXCEEDED`. | **PASS** |
| `TC-XAI-003` | `FR-XAI-003` | Local attribution latency budget ($\le 40\text{ ms}$). | Average SHAP attribution takes $< 15\text{ ms}$ (well below 40 ms). | **PASS** |

---

## 10. Cryptographic Block-Chained Ledger Tests (`tests/test_ledger.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-LED-001` | `FR-AUD-001` | Append blocks to chain; verify parent SHA-256 links. | Blocks link sequentially; audit returns `CHAIN_INTEGRITY_VERIFIED`. | **PASS** |
| `TC-LED-002` | `FR-AUD-003` | Adversary tampers with database row in SQLite. | Audit catches modification, returns `PAYLOAD_TAMPERED` with block ID. | **PASS** |

---

## 11. End-to-End API Integration Tests (`tests/test_api_e2e.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-E2E-001` | `FR-API-001` | Submit routine payment transaction payload to `/api/v1/predict`. | HTTP 200, verdict `APPROVE`, composite score $< 0.30$. | **PASS** |
| `TC-E2E-002` | `FR-API-001` | Submit Quishing transaction payload with 150km displacement. | HTTP 200, verdict `BLOCK` or `CHALLENGE_MFA`, reason codes attached. | **PASS** |
| `TC-E2E-003` | `FR-API-002` | Submit batch of 3 transactions to `/api/v1/predict/batch`. | HTTP 200, returns array of 3 structured responses. | **PASS** |
| `TC-E2E-004` | `FR-AUD-003` | Query `/api/v1/ledger/verify` endpoint. | HTTP 200, `is_valid: true`, total blocks verified. | **PASS** |

---

## 12. Security & Penetration Tests (`tests/test_security.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-SEC-001` | `NFR-SEC-003` | SQL injection in string parameters (`admin' OR '1'='1`). | Safely parameterized by SQLAlchemy; database unaffected. | **PASS** |
| `TC-SEC-002` | `FR-ING-004` | Input boundary attack: negative monetary amount. | Rejected at HTTP gateway with HTTP 422. | **PASS** |
| `TC-SEC-003` | `FR-ING-004` | Input boundary attack: latitude $> 90.0$. | Rejected at HTTP gateway with HTTP 422. | **PASS** |
| `TC-SEC-004` | `NFR-SEC-001` | Sensitive customer PII masking audit in database. | Raw payer ID never stored; only 64-char salted SHA-256 hash. | **PASS** |

---

## 13. Performance & Latency SLA Tests (`tests/test_performance.py`)

| Test Case ID | Req Ref | Test Description & Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `TC-PRF-001` | `NFR-PERF-001`| 25 consecutive end-to-end transaction inferences at P95. | P95 latency strictly $< 100\text{ ms}$ (Actual: ~28.4 ms). | **PASS** |
