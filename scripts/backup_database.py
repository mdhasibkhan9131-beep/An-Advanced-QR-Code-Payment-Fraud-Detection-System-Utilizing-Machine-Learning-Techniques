"""
Automated Database Hot-Backup Script for SQLite WAL.
Uses SQLite Online Backup API to produce consistent, non-locking database snapshots
with gzip compression and SHA-256 integrity checksums.
"""

import os
import sys
import time
import gzip
import shutil
import hashlib
import sqlite3
import argparse
from datetime import datetime

DEFAULT_DB_PATH = "database/fraud_detection.db"
DEFAULT_BACKUP_DIR = "database/backups"


def calculate_sha256(filepath: str) -> str:
    """Computes SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def backup_database(
    db_path: str = DEFAULT_DB_PATH,
    backup_dir: str = DEFAULT_BACKUP_DIR,
    max_backups: int = 7,
) -> str:
    """
    Performs online non-blocking backup of SQLite database.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    temp_raw_backup = os.path.join(backup_dir, f"temp_{timestamp}.db")
    compressed_backup = os.path.join(backup_dir, f"backup_{timestamp}.db.gz")
    checksum_file = os.path.join(backup_dir, f"backup_{timestamp}.db.gz.sha256")

    print(f"[Backup] Initiating online snapshot of {db_path}...")
    t0 = time.time()

    # 1. Online SQLite Backup API (locks-free snapshot)
    source_conn = sqlite3.connect(db_path)
    dest_conn = sqlite3.connect(temp_raw_backup)
    with dest_conn:
        source_conn.backup(dest_conn, pages=100)
    dest_conn.close()
    source_conn.close()

    # 2. Compress with gzip
    print(f"[Backup] Compressing snapshot to {compressed_backup}...")
    with open(temp_raw_backup, "rb") as f_in, gzip.open(compressed_backup, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(temp_raw_backup)

    # 3. Compute and store SHA-256 checksum
    checksum = calculate_sha256(compressed_backup)
    with open(checksum_file, "w") as f_sum:
        f_sum.write(f"{checksum}  {os.path.basename(compressed_backup)}\n")

    elapsed = time.time() - t0
    orig_size = os.path.getsize(db_path) / 1024
    comp_size = os.path.getsize(compressed_backup) / 1024

    print(f"[Backup] Backup complete in {elapsed:.2f}s!")
    print(f"[Backup] Original: {orig_size:.1f} KB -> Compressed: {comp_size:.1f} KB")
    print(f"[Backup] SHA-256 Checksum: {checksum}")

    # 4. Rotate old backups
    all_backups = sorted(
        [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith(".db.gz")]
    )
    if len(all_backups) > max_backups:
        for old in all_backups[:-max_backups]:
            os.remove(old)
            old_sum = old + ".sha256"
            if os.path.exists(old_sum):
                os.remove(old_sum)
            print(f"[Backup] Rotated legacy backup: {old}")

    return compressed_backup


def main():
    parser = argparse.ArgumentParser(description="SQLite Online Hot Backup Utility")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to SQLite database")
    parser.add_argument("--output-dir", default=DEFAULT_BACKUP_DIR, help="Backup destination folder")
    parser.add_argument("--keep", type=int, default=7, help="Number of backup snapshots to retain")
    args = parser.parse_args()

    try:
        backup_database(db_path=args.db, backup_dir=args.output_dir, max_backups=args.keep)
    except Exception as e:
        print(f"[Backup Error] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

