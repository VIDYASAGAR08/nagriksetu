#!/usr/bin/env python3
"""
backup_production.py — Automated Production Backup System for NagrikSetu.
Creates verified timestamped physical snapshots of SQLite database and uploaded documents.
Enforces integrity check before finalization and applies automated retention pruning.
"""

import os
import sys
import shutil
import sqlite3
import datetime
import tarfile

BACKUP_DIR = os.getenv("BACKUP_DIR", r"C:\Users\callm\nagriksetu\backend\data\backups")
DB_PATH = os.getenv("DATABASE_PATH", r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
UPLOADS_DIR = os.getenv("UPLOADS_DIR", r"C:\Users\callm\nagriksetu\backend\data\uploads")
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "7"))


def create_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_db_name = f"nagriksetu_backup_{timestamp}.db"
    backup_db_path = os.path.join(BACKUP_DIR, backup_db_name)

    print(f"[*] Initiating backup at UTC {timestamp}...")

    if not os.path.exists(DB_PATH):
        print(f"[-] ERROR: Source database does not exist at {DB_PATH}")
        sys.exit(1)

    # 1. Use SQLite online backup API for ACID safety during active connections
    src_conn = sqlite3.connect(DB_PATH)
    dst_conn = sqlite3.connect(backup_db_path)
    with dst_conn:
        src_conn.backup(dst_conn, pages=100)
    dst_conn.close()
    src_conn.close()

    print(f"[+] Physical database snapshot created: {backup_db_path} ({os.path.getsize(backup_db_path)} bytes)")

    # 2. Verify integrity of the backup file
    test_conn = sqlite3.connect(backup_db_path)
    cur = test_conn.cursor()
    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]
    if integrity != "ok":
        test_conn.close()
        print(f"[-] CRITICAL: Integrity check failed for backup: {integrity}")
        sys.exit(1)

    cur.execute("PRAGMA foreign_key_check")
    fks = cur.fetchall()
    if len(fks) > 0:
        test_conn.close()
        print(f"[-] CRITICAL: Foreign key check failed: {len(fks)} violations")
        sys.exit(1)

    inst_count = cur.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
    stud_count = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    enr_count = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    app_count = cur.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0]
    test_conn.close()

    print(f"[+] Backup verified intact: Integrity={integrity}, FK violations={len(fks)}")
    print(f"[+] Verified Counts: Institutions={inst_count}, Students={stud_count}, Enrolments={enr_count}, Applications={app_count}")

    # 3. Archive documents if uploads directory exists
    if os.path.exists(UPLOADS_DIR):
        archive_name = f"nagriksetu_uploads_{timestamp}.tar.gz"
        archive_path = os.path.join(BACKUP_DIR, archive_name)
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(UPLOADS_DIR, arcname="uploads")
        print(f"[+] Uploaded documents archived: {archive_path} ({os.path.getsize(archive_path)} bytes)")

    # 4. Apply retention policy
    prune_old_backups(RETENTION_DAYS)
    return backup_db_path


def prune_old_backups(days: int):
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(days=days)
    print(f"[*] Applying retention policy: pruning backups older than {days} days (before {cutoff.isoformat()})...")

    pruned = 0
    for fname in os.listdir(BACKUP_DIR):
        fpath = os.path.join(BACKUP_DIR, fname)
        if os.path.isfile(fpath) and fname.startswith("nagriksetu_"):
            mtime = datetime.datetime.utcfromtimestamp(os.path.getmtime(fpath))
            if mtime < cutoff:
                os.remove(fpath)
                print(f"    [-] Removed expired backup: {fname}")
                pruned += 1

    print(f"[+] Retention pruning complete: {pruned} old backup files removed.")


if __name__ == "__main__":
    create_backup()
