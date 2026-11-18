"""
NagrikSetu safe SQLite backup script.

Uses Python's sqlite3 Connection.backup() API to perform an online,
consistent backup without file locking issues or partial writes.

Features & Guarantees:
1. Source: /app/data/nagriksetu.db
2. Target: timestamped backup inside /app/data (e.g. nagriksetu_backup_YYYYMMDD_HHMMSS.db)
3. Read-only connection to source database (URI mode=ro)
4. Never overwrites the source database or an existing backup file
5. Clean resource management: connections are closed FIRST before any file deletion
6. Failure cleanup during backup: incomplete backups are removed with all connections closed
7. Strict verification failure cleanup: if ANY check fails (integrity, parity, counts),
   both verification connections are closed first, the invalid backup is deleted, its path printed,
   and exit code 1 returned
8. Table list parity check between source and backup
9. Row count equality verification across ALL user tables
10. PRAGMA integrity_check on both source and backup
11. Mandatory baseline count validation (schools: 20, students: 30000, enrollments: 30000)
12. Prints exact path, file size in bytes and MB, and PASS/FAIL status

Note on Verification Consistency:
The SQLite Connection.backup() API creates a point-in-time, transactionally
consistent snapshot. During the subsequent verification step, the script
reads both the live source and the newly created backup to compare row counts.
To ensure exact row-count equality during verification, the live database
should not receive concurrent write operations (e.g. admin updates, record
edits) while this verification check is running.
"""

import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_PATH = Path(os.getenv("DATABASE_PATH", "/app/data/nagriksetu.db"))
BACKUP_DIR = SOURCE_PATH.parent

REQUIRED_COUNTS = {
    "schools": 20,
    "students": 30000,
    "enrollments": 30000,
}


def get_user_tables(conn: sqlite3.Connection) -> list[str]:
    cursor = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name ASC
        """
    )
    return [row[0] for row in cursor.fetchall()]


def get_table_count(conn: sqlite3.Connection, table_name: str) -> int:
    # table_name comes directly from sqlite_master, safe from injection
    cursor = conn.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
    return cursor.fetchone()[0]


def check_integrity(conn: sqlite3.Connection, label: str) -> bool:
    cursor = conn.execute("PRAGMA integrity_check")
    results = [row[0] for row in cursor.fetchall()]
    if results == ["ok"]:
        print(f"[{label}] PRAGMA integrity_check: ok")
        return True
    print(f"[{label}] PRAGMA integrity_check FAILED: {results}", file=sys.stderr)
    return False


def run_backup() -> int:
    print("=" * 60)
    print("NAGRIKSETU DATABASE BACKUP (sqlite3 Connection.backup API)")
    print("=" * 60)

    # 1. Verify source existence
    if not SOURCE_PATH.exists() or not SOURCE_PATH.is_file():
        print(f"FAIL: Source database does not exist at {SOURCE_PATH}", file=sys.stderr)
        return 1

    # 2. Compute destination filename with UTC timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest_path = BACKUP_DIR / f"nagriksetu_backup_{timestamp}.db"

    # 3. Guard against overwriting source or any existing backup
    if dest_path.resolve() == SOURCE_PATH.resolve():
        print("FAIL: Destination path is identical to the source database.", file=sys.stderr)
        return 1

    if dest_path.exists():
        print(f"FAIL: Target backup file already exists: {dest_path}", file=sys.stderr)
        return 1

    print(f"Source Database : {SOURCE_PATH.resolve()}")
    print(f"Target Backup   : {dest_path.resolve()}")
    print("-" * 60)

    src_conn = None
    dest_conn = None
    backup_failed = False

    try:
        # 4. Open source database in read-only mode
        src_uri = f"file:{SOURCE_PATH.resolve().as_posix()}?mode=ro"
        src_conn = sqlite3.connect(src_uri, uri=True, timeout=10.0)

        # 5. Open destination database and perform SQLite online backup
        dest_conn = sqlite3.connect(str(dest_path), timeout=10.0)
        print("Performing SQLite online backup...")
        src_conn.backup(dest_conn, pages=250)
        dest_conn.commit()
        print("Backup copy completed successfully.")

    except Exception as exc:
        backup_failed = True
        print(f"FAIL: Error during backup execution: {exc}", file=sys.stderr)

    finally:
        # Ensure both destination and source connections are explicitly closed FIRST
        if dest_conn is not None:
            try:
                dest_conn.close()
            except Exception:
                pass
            dest_conn = None

        if src_conn is not None:
            try:
                src_conn.close()
            except Exception:
                pass
            src_conn = None

    # If backup copy failed, delete the incomplete file after connections are closed
    if backup_failed:
        if dest_path.exists():
            try:
                dest_path.unlink()
                print(f"Deleted incomplete backup file: {dest_path.resolve()}")
            except OSError as cleanup_err:
                print(
                    f"Warning: Could not remove incomplete backup file {dest_path.resolve()}: {cleanup_err}",
                    file=sys.stderr,
                )
        print("\nFAIL: Backup copy procedure failed.\n", file=sys.stderr)
        return 1

    # 6-11. Verification Phase
    print("-" * 60)
    print("VERIFICATION PHASE")
    print("Note: Source database should not receive writes during verification")
    print("to ensure exact row count parity with the backup snapshot.")
    print("-" * 60)

    verify_src = None
    verify_dest = None
    verification_passed = True

    try:
        # Open both databases in read-only mode for verification
        verify_src = sqlite3.connect(
            f"file:{SOURCE_PATH.resolve().as_posix()}?mode=ro", uri=True
        )
        verify_dest = sqlite3.connect(
            f"file:{dest_path.resolve().as_posix()}?mode=ro", uri=True
        )

        # 10. PRAGMA integrity_check on both source and backup
        if not check_integrity(verify_src, "Source"):
            verification_passed = False
        if not check_integrity(verify_dest, "Backup"):
            verification_passed = False

        # 8. Compare table lists
        src_tables = get_user_tables(verify_src)
        dest_tables = get_user_tables(verify_dest)

        if src_tables != dest_tables:
            print("FAIL: Table lists differ between source and backup!", file=sys.stderr)
            print(f"  Source tables: {src_tables}", file=sys.stderr)
            print(f"  Backup tables: {dest_tables}", file=sys.stderr)
            verification_passed = False
        else:
            print(f"Table count parity verified: {len(src_tables)} tables match exactly.")

        # 9. Compare row counts for EVERY table
        print("\nTable Row Count Verification:")
        for table in src_tables:
            src_cnt = get_table_count(verify_src, table)
            dest_cnt = get_table_count(verify_dest, table)
            match_status = "OK" if src_cnt == dest_cnt else "MISMATCH"
            print(f"  - {table:25s}: Source={src_cnt:<7d} Backup={dest_cnt:<7d} [{match_status}]")
            if src_cnt != dest_cnt:
                print(
                    f"FAIL: Count mismatch on table '{table}': {src_cnt} != {dest_cnt}",
                    file=sys.stderr,
                )
                verification_passed = False

        # 11. Verify required baseline counts
        print("\nRequired Baseline Counts Verification:")
        for table, expected in REQUIRED_COUNTS.items():
            actual = get_table_count(verify_dest, table)
            if actual != expected:
                print(
                    f"FAIL: Table '{table}' expected {expected} records, found {actual}",
                    file=sys.stderr,
                )
                verification_passed = False
            else:
                print(f"  - {table:15s}: {actual} records (matches required {expected})")

    except Exception as exc:
        print(f"FAIL: Verification exception: {exc}", file=sys.stderr)
        verification_passed = False

    finally:
        # 1. Close both verification database connections FIRST
        if verify_src is not None:
            try:
                verify_src.close()
            except Exception:
                pass
            verify_src = None

        if verify_dest is not None:
            try:
                verify_dest.close()
            except Exception:
                pass
            verify_dest = None

    # Handle verification failure: delete failed backup after closing connections
    if not verification_passed:
        if dest_path.exists():
            try:
                dest_path.unlink()
                # 3. Print the exact path of the deleted file
                print(f"Deleted failed backup file: {dest_path.resolve()}")
            except OSError as cleanup_err:
                print(
                    f"Warning: Could not remove failed backup file {dest_path.resolve()}: {cleanup_err}",
                    file=sys.stderr,
                )
        # 4. Print clear FAIL status
        print("\nFAIL: One or more backup verification checks failed. Failed backup discarded.\n", file=sys.stderr)
        # 5. Return exit code 1
        return 1

    # If every verification check succeeded, preserve the backup
    size_bytes = dest_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    print("-" * 60)
    print(f"Backup Location : {dest_path.resolve()}")
    print(f"Backup Size     : {size_bytes:,} bytes ({size_mb:.2f} MB)")
    print("-" * 60)
    print("\nPASS: All backup and integrity verification checks succeeded.\n")
    return 0


if __name__ == "__main__":
    sys.exit(run_backup())
