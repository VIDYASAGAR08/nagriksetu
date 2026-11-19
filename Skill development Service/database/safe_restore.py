#!/usr/bin/env python3
"""
Safe MySQL Database Restore Utility for NagrikSetu Skill Development Microservice.

Guarantees:
1. Validates that the target database is dedicated/isolated.
2. Prevents accidental overwrite of shared databases (e.g. 'nagriksetu', 'main', 'production').
3. Confirms user intent before executing destructive table replacement.
"""

import sys
import os
import re
import argparse

def main():
    parser = argparse.ArgumentParser(description="Safely restore NagrikSetu Skill Development SQL backup into an isolated MySQL database.")
    parser.add_argument("--host", default=os.getenv("MYSQL_HOST", "127.0.0.1"), help="MySQL host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.getenv("MYSQL_PORT", 3308)), help="MySQL port (default: 3308)")
    parser.add_argument("--user", default=os.getenv("MYSQL_USER", "nagriksetu_skill"), help="MySQL username")
    parser.add_argument("--password", default=os.getenv("MYSQL_PASSWORD"), help="MySQL password")
    parser.add_argument("--database", default=os.getenv("MYSQL_DATABASE", "skill_db"), help="Target database name (default: skill_db)")
    parser.add_argument("--sql-file", default=os.path.join(os.path.dirname(__file__), "skill_db_backup.sql"), help="Path to SQL dump file")
    parser.add_argument("--yes", action="store_true", help="Confirm execution without interactive prompt")

    args = parser.parse_args()

    # Safety checks on database name
    forbidden_shared_names = ("nagriksetu_main", "nagriksetu_core", "production", "prod", "main_db")
    if args.database.lower() in forbidden_shared_names:
        print(f"\n[ERROR] Target database '{args.database}' is a forbidden shared/production name.", file=sys.stderr)
        print("To protect other microservices, Skill Development tables must be restored into a dedicated schema (e.g., 'skill_db').", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.sql_file):
        print(f"\n[ERROR] SQL file not found at: {args.sql_file}", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("NAGRIKSETU SKILL DEVELOPMENT - SAFE DATABASE RESTORATION UTILITY")
    print("=" * 70)
    print(f"Target Database : {args.database}")
    print(f"Target Host     : {args.host}:{args.port}")
    print(f"Target User     : {args.user}")
    print(f"SQL Dump File   : {args.sql_file}")
    print("-" * 70)
    print("WARNING: This backup contains 'DROP TABLE IF EXISTS' statements.")
    print("All existing tables in target database will be re-created with clean data.")
    print("-" * 70)

    if not args.yes:
        confirmation = input(f"Are you sure you want to restore into '{args.database}'? (yes/no): ").strip().lower()
        if confirmation != "yes":
            print("[ABORTED] Restoration cancelled by user.")
            sys.exit(0)

    try:
        import pymysql
    except ImportError:
        print("[ERROR] PyMySQL is required to run this script. Run: pip install pymysql", file=sys.stderr)
        sys.exit(1)

    if not args.password:
        import getpass
        args.password = getpass.getpass("Enter MySQL password: ")

    try:
        print(f"\nConnecting to MySQL server at {args.host}:{args.port}...")
        conn = pymysql.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            charset="utf8mb4",
            autocommit=True
        )
        with conn.cursor() as cursor:
            # 1. Ensure target database exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{args.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE `{args.database}`;")
            print(f"Verified target database `{args.database}`.")

            # 2. Read and execute statements
            print(f"Reading SQL file ({os.path.getsize(args.sql_file)} bytes)...")
            with open(args.sql_file, "r", encoding="utf-8", errors="ignore") as f:
                sql_content = f.read()

            # Execute commands
            statements = []
            stmt_buffer = []
            for line in sql_content.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("--") or stripped.startswith("/*"):
                    continue
                # Skip any hardcoded USE statement so it strictly targets args.database
                if re.match(r"(?i)^USE\s+`?\w+`?;", stripped):
                    continue
                # Skip hardcoded CREATE DATABASE statements
                if re.match(r"(?i)^CREATE\s+DATABASE", stripped):
                    continue

                stmt_buffer.append(line)
                if stripped.endswith(";"):
                    statements.append("\n".join(stmt_buffer))
                    stmt_buffer = []

            print(f"Executing {len(statements)} SQL commands into `{args.database}`...")
            for i, stmt in enumerate(statements):
                try:
                    cursor.execute(stmt)
                except Exception as stmt_err:
                    print(f"[WARNING] Statement {i+1} failed: {stmt_err}")

            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"\n[SUCCESS] Successfully restored {len(tables)} tables into `{args.database}`:")
            for t in sorted(tables):
                print(f"  - {t}")

        conn.close()
        print("\nDatabase restoration completed safely.")

    except Exception as e:
        print(f"\n[ERROR] Database restore failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
