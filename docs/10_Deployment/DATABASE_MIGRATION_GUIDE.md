# Database Migration & Schema Evolution Guide

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved Quality Baseline  
**Database Engine:** SQLite 3.45.3 (WAL Mode) / SQLAlchemy 2.0 ORM

---

## 1. Schema Baseline (v1.0.0)

The production database is composed of three normalized relational entities conforming to `docs/05_System_Design/DATABASE_DESIGN.md`:

```
┌─────────────────────────────────┐       ┌──────────────────────────────────┐
│          transactions           │ 1   1 │          ledger_blocks           │
├─────────────────────────────────┤───────├──────────────────────────────────┤
│ transaction_id (PK, String(36)) │◄──────│ transaction_id (FK, Unique)      │
│ timestamp (BigInteger)          │       │ block_id (PK, Integer AutoInc)   │
│ payer_hash (String(64))         │       │ prev_hash (String(64), Index)    │
│ merchant_id (String(32))        │       │ block_hash (String(64), Unique)  │
│ qr_type (Integer)               │       │ composite_score (Float)          │
│ qr_payload_entropy (Float)      │       │ verdict (String(16))             │
│ amount (Float)                  │       │ timestamp (BigInteger)           │
│ merchant_category_code (Integer)│       │ reason_codes (Text JSON)         │
│ payer_latitude (Float)          │       │ state_signature (String(64))     │
│ payer_longitude (Float)         │       └──────────────────────────────────┘
│ merchant_latitude (Float)       │
│ merchant_longitude (Float)      │       ┌──────────────────────────────────┐
│ haversine_distance_km (Float)   │ 1   1 │          mfa_challenges          │
│ device_trust_score (Float)      │───────├──────────────────────────────────┤
│ scan_to_pay_latency_ms (Integer)│◄──────│ transaction_id (FK, Unique)      │
│ failed_pin_attempts (Integer)   │       │ challenge_id (PK, String(36))    │
│ velocity_1h (Float)             │       │ status (String(16), Index)       │
│ velocity_ratio (Float)          │       │ issued_at (BigInteger)           │
│ amount_zscore (Float)           │       │ expires_at (BigInteger)          │
│ supervised_score (Float)        │       │ verified_at (DateTime)           │
│ anomaly_score (Float)           │       └──────────────────────────────────┘
│ composite_score (Float)         │
│ verdict (String(16), Index)     │
│ is_fallback (Integer)           │
│ created_at (DateTime)           │
└─────────────────────────────────┘
```

---

## 2. Zero-Downtime Migration Policy

1. **Mandatory Pre-Migration Backup:**
   Before applying any DDL schema change or column addition, an online hot backup MUST be executed:
   ```bash
   python scripts/backup_database.py --db database/fraud_detection.db
   ```
2. **Schema Invariant:**
   `ledger_blocks` is an **append-only immutable cryptographic ledger**. Columns within `ledger_blocks` must never be dropped or mutated in-place.
3. **Foreign Key Integrity:**
   `PRAGMA foreign_keys = ON;` must be maintained at all times. Foreign key relationships between `transactions` and `ledger_blocks` must be populated atomically.

---

## 3. Schema Initialization Procedure

To initialize fresh schemas in a new deployment:
```bash
python -c "from backend.database.session import init_db; init_db()"
```
This executes SQLAlchemy's `Base.metadata.create_all(bind=engine)`, safely creating tables, primary keys, indices, and foreign key relationships idempotently (`CREATE TABLE IF NOT EXISTS`).

---

## 4. Forward Schema Evolution Strategy

When extending schemas in future sprints or releases:
1. **Adding Non-Breaking Columns:**
   Use non-blocking `ALTER TABLE ... ADD COLUMN` statements with sensible default values.
2. **Database Verification Query:**
   ```sql
   PRAGMA integrity_check;
   PRAGMA foreign_key_check;
   ```
3. **Cryptographic Ledger Continuity Audit:**
   After any schema change or data backfill, execute the automated verification endpoint:
   ```bash
   curl -s http://localhost:8000/api/v1/ledger/verify
   ```
   Ensure output reports `"is_valid": true` and `"status": "CHAIN_INTEGRITY_VERIFIED"`.

