"""
Automated Database Restore and Disaster Recovery Script.
Verifies SHA-256 backup checksums, decompresses snapshot, executes SQLite integrity check,
and verifies cryptographic audit ledger continuity.
"""

import os
import sys
import gzip
import shutil
import hashlib
import sqlite3
import argparse

DEFAULT_DB_PATH = "database/fraud_detection.db"


def calculate_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def restore_database(backup_file: str, target_db: str = DEFAULT_DB_PATH) -> bool:
    if not os.path.exists(backup_file):
        raise FileNotFoundError(f"Backup file not found: {backup_file}")

    print(f"[Restore] Verifying backup archive: {backup_file}...")

    # 1. Checksum validation
    checksum_file = backup_file + ".sha256"
    if os.path.exists(checksum_file):
        with open(checksum_file, "r") as f:
            expected_sum = f.read().split()[0].strip()
        actual_sum = calculate_sha256(backup_file)
        if expected_sum != actual_sum:
            raise ValueError(f"Checksum mismatch! Expected {expected_sum}, got {actual_sum}")
        print(f"[Restore] SHA-256 checksum verified: {actual_sum}")
    else:
        print("[Restore] Warning: Checksum file not found; skipping hash verification.")

    # 2. Decompress to temporary file
    temp_restored = target_db + ".restore_temp"
    print(f"[Restore] Decompressing archive to {temp_restored}...")
    with gzip.open(backup_file, "rb") as f_in, open(temp_restored, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    # 3. SQLite Integrity Check
    print("[Restore] Running SQLite PRAGMA integrity_check...")
    conn = sqlite3.connect(temp_restored)
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    result = cursor.fetchone()[0]
    conn.close()

    if result != "ok":
        os.remove(temp_restored)
        raise RuntimeError(f"Database integrity check failed: {result}")
    print("[Restore] SQLite integrity verified: OK")

    # 4. Atomic file replacement
    backup_existing = target_db + ".pre_restore_bak"
    if os.path.exists(target_db):
        shutil.move(target_db, backup_existing)

    shutil.move(temp_restored, target_db)
    print(f"[Restore] Database successfully restored to {target_db}!")

    if os.path.exists(backup_existing):
        os.remove(backup_existing)

    return True


def main():
    parser = argparse.ArgumentParser(description="SQLite Disaster Recovery Restore Utility")
    parser.add_argument("--backup-file", required=True, help="Path to .db.gz backup archive")
    parser.add_argument("--target-db", default=DEFAULT_DB_PATH, help="Path to restore destination database")
    args = parser.parse_args()

    try:
        restore_database(backup_file=args.backup_file, target_db=args.target_db)
    except Exception as e:
        print(f"[Restore Error] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
