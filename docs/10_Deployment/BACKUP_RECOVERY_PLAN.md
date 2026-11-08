# Disaster Recovery & Database Backup Plan

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved Quality Baseline  
**Target SLAs:** RPO $\le 1.0$ Hour | RTO $\le 5.0$ Minutes

---

## 1. Disaster Recovery Objectives (RPO & RTO)

| Metric | Target SLA | Operational Implementation |
| :--- | :---: | :--- |
| **Recovery Point Objective (RPO)** | **$\le 1$ Hour** | Automated hourly online snapshots + continuous SQLite WAL stream. |
| **Recovery Time Objective (RTO)** | **$\le 5$ Minutes** | Point-in-time decompression and atomic restore script (`< 30\text{ seconds}`). |
| **Integrity Assurance** | **100% Cryptographic Verification** | SHA-256 backup checksums + PRAGMA integrity check + Ledger chain audit. |

---

## 2. Automated Hot-Backup Strategy

SQLite's Write-Ahead Logging (`WAL`) allows concurrent database snapshots to be captured without blocking ongoing reader transactions or delaying sub-100ms payment clearances.

### Online Backup Utility: `scripts/backup_database.py`
- Utilizes `sqlite3.connect().backup()` to stream pages consistently in the background.
- Compresses snapshots with `gzip` (reducing typical 144 KB databases to ~24 KB).
- Computes SHA-256 cryptographic checksum and saves to `.sha256` digest files.
- Automatically retains the last $N$ rolling backups (default: 7).

### Manual Backup Execution:
```bash
python scripts/backup_database.py --db database/fraud_detection.db --output-dir database/backups --keep 7
```

### Automated Cron Job (Linux / Docker Host):
Add to `/etc/cron.d/qr_fraud_backup`:
```cron
# Execute online hot backup hourly at minute 0
0 * * * * qruser /opt/qr-fraud/venv/bin/python /opt/qr-fraud/scripts/backup_database.py >> /opt/qr-fraud/logs/backup.log 2>&1
```

---

## 3. Disaster Recovery & Restore Procedure

If catastrophic hardware failure, database corruption, or unintended file deletion occurs:

### Step 1: Identify Latest Verified Backup
```bash
ls -lt database/backups/backup_*.db.gz | head -n 1
```

### Step 2: Execute Automated Restore Utility
The restore utility automatically validates the SHA-256 checksum, decompresses to a temporary file, executes `PRAGMA integrity_check;`, and atomically replaces the live database:
```bash
python scripts/restore_database.py --backup-file database/backups/backup_YYYYMMDD_HHMMSS.db.gz
```
Expected output:
```
[Restore] Verifying backup archive: database/backups/backup_20261108_172643.db.gz...
[Restore] SHA-256 checksum verified: 49cb1fb0049010b67d7621c1f325eaab76fd5d425f9d63c03971f93a94c4accf
[Restore] Decompressing archive to database/fraud_detection.db.restore_temp...
[Restore] Running SQLite PRAGMA integrity_check...
[Restore] SQLite integrity verified: OK
[Restore] Database successfully restored to database/fraud_detection.db!
```

### Step 3: Run Post-Recovery Cryptographic Ledger Audit
Verify that the ledger blockchain remains intact without missing or tampered blocks:
```bash
python scripts/smoke_test.py
```
Ensure Test 6 passes: `Auditing SHA-256 Ledger Blockchain -> PASS (CHAIN_INTEGRITY_VERIFIED)`.

---

## 4. Disaster Recovery Testing & Drills

1. **Scheduled Quarterly Drills:** Simulate sudden host shutdown and verify point-in-time recovery to a secondary machine within 5 minutes.
2. **Offsite Snapshot Archival:** Sync `database/backups/` to cold offline storage (e.g., encrypted local NAS or external drive) weekly.
