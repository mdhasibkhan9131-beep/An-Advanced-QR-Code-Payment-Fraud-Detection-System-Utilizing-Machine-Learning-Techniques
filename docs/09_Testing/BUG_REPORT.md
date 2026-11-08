# Defect & Bug Tracking Report

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** All Identified Defects Resolved & Verified  
**Active Defect Backlog:** 0 Open Defects (100% Resolved)

---

## 1. Defect Summary Table

| Bug ID | Title & Summary | Severity | Priority | Component | Initial Status | Final Status |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| **`BUG-001`** | Foreign Key constraint failure during ledger block append | **High** | P1 | `backend/api/routes.py` | Open | **RESOLVED** |
| **`BUG-002`** | Missing `numpy as np` import in `/api/v1/metrics` handler | **Medium** | P2 | `backend/api/routes.py` | Open | **RESOLVED** |
| **`BUG-003`** | Hardcoded static `transaction_id` collisions in test fixtures | **Medium** | P2 | `tests/test_api_e2e.py` | Open | **RESOLVED** |
| **`BUG-004`** | Unexported default model path constants in model modules | **Low** | P3 | `backend/models/` | Open | **RESOLVED** |

---

## 2. Detailed Defect Records

### `BUG-001`: Foreign Key Constraint Failure During Ledger Block Append
- **Bug ID:** `BUG-001`
- **Description:** When evaluating incoming transactions via `/api/v1/predict`, the API attempted to insert a `LedgerBlock` before the corresponding `TransactionRecord` had been persisted in the SQLite database. Because `LedgerBlock.transaction_id` enforces a relational Foreign Key constraint referencing `transactions.transaction_id`, SQLite threw an `IntegrityError: FOREIGN KEY constraint failed`.
- **Severity:** **High (P1)** — Prevented transactions from being persisted and caused fallback hash strings (`GENESIS_PENDING`).
- **Reproduction Steps:**
  1. Initialize fresh SQLite database schema.
  2. Send a `POST` request to `/api/v1/predict` with valid payload.
  3. Observe exception log `(sqlite3.IntegrityError) FOREIGN KEY constraint failed`.
- **Expected Result:** `TransactionRecord` and `LedgerBlock` successfully committed with valid relational link and SHA-256 block hash.
- **Actual Result:** Transaction persistence aborted; response fell back to `GENESIS_PENDING`.
- **Resolution & Fix:** Re-ordered database operations in `backend/api/routes.py`:
  1. Stage `TransactionRecord` and call `db.flush()`.
  2. Invoke `ledger_instance.append_block(db, transaction_id, ...)`.
  3. Execute single unified `db.commit()`.
- **Verification:** `tests/test_api_e2e.py` and `tests/test_security.py` re-executed; 100% passing with 64-character SHA-256 hashes generated.
- **Status:** **RESOLVED & VERIFIED**

---

### `BUG-002`: Missing `numpy` Import in Telemetry Metrics Endpoint
- **Bug ID:** `BUG-002`
- **Description:** In `backend/api/routes.py`, `get_metrics()` invoked `np.percentile()` to calculate latency percentiles (P50, P95, P99) without explicitly importing `numpy as np` at the module header.
- **Severity:** **Medium (P2)** — Caused `GET /api/v1/metrics` to fail with HTTP 500 `NameError: name 'np' is not defined`.
- **Reproduction Steps:**
  1. Start FastAPI server.
  2. Send `GET /api/v1/metrics`.
  3. Observe `NameError: name 'np' is not defined`.
- **Expected Result:** HTTP 200 with operational metrics JSON payload.
- **Actual Result:** HTTP 500 internal server error.
- **Resolution & Fix:** Added `import numpy as np` to the module imports of `backend/api/routes.py`.
- **Verification:** `tests/test_health.py::test_metrics_endpoint` passed with HTTP 200.
- **Status:** **RESOLVED & VERIFIED**

---

### `BUG-003`: Static Transaction ID Collisions in Test Suites
- **Bug ID:** `BUG-003`
- **Description:** Test cases in `tests/test_api_e2e.py` and `tests/test_security.py` used static hardcoded transaction IDs (e.g. `test-e2e-routine-001`). When the test suite was executed consecutively against the same SQLite database file, SQLite threw `IntegrityError: UNIQUE constraint failed: ledger_blocks.transaction_id`.
- **Severity:** **Medium (P2)** — Broke idempotency of repeated automated test runs.
- **Reproduction Steps:**
  1. Run `pytest tests/test_api_e2e.py` twice consecutively.
  2. Second run fails with `UNIQUE constraint failed`.
- **Expected Result:** Test suite executes idempotently across arbitrary runs.
- **Actual Result:** Secondary test runs failed due to primary key collisions.
- **Resolution & Fix:** Updated all test cases to dynamically incorporate millisecond epoch timestamps into `transaction_id` (e.g., `f"test-e2e-routine-{now_ms}"`).
- **Verification:** Ran test suite 3 consecutive times with zero unique constraint violations.
- **Status:** **RESOLVED & VERIFIED**

---

### `BUG-004`: Unexported Default Model Path Constants
- **Bug ID:** `BUG-004`
- **Description:** `DEFAULT_LIGHTGBM_PATH` and `DEFAULT_IFOREST_PATH` were declared solely in `backend/models/trainer.py` rather than their respective wrapper modules, causing `ImportError` when referenced by `backend/api/routes.py`.
- **Severity:** **Low (P3)** — Module import failure during application bootstrapping.
- **Reproduction Steps:**
  1. Import `DEFAULT_LIGHTGBM_PATH` from `backend.models.supervised`.
  2. Observe `ImportError`.
- **Expected Result:** Module cleanly exports default file paths.
- **Actual Result:** `ImportError` raised.
- **Resolution & Fix:** Exported constants directly in `backend/models/supervised.py` and `backend/models/unsupervised.py`.
- **Verification:** Clean module import verified across `routes.py` and test harnesses.
- **Status:** **RESOLVED & VERIFIED**

