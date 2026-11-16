"""
NagrikSetu (नागरिक सेतु) — Database Inspection & Live Demonstration Utility
Use this script during your university project presentation to display
the database structure, entity relationships, and live data to your teacher.

Usage:
    docker compose exec backend python inspect_db.py          # Complete live demonstration
    docker compose exec backend python inspect_db.py --joins  # Show multi-table foreign key joins
    docker compose exec backend python inspect_db.py --family # Show family tree & role delegation
"""

import sys
import os
from sqlalchemy import text
from app.database import engine
from app.config import settings


def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_table_data(title, query, params={}):
    print_header(title)
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            rows = result.mappings().all()
            if not rows:
                print("  (No records found)")
                return

            cols = list(rows[0].keys())

            col_widths = {c: len(c) for c in cols}
            for r in rows:
                for c in cols:
                    val_str = str(r[c]) if r[c] is not None else "NULL"
                    if len(val_str) > col_widths[c]:
                        col_widths[c] = min(len(val_str), 35)

            header_line = " | ".join(c.ljust(col_widths[c]) for c in cols)
            sep_line = "-+-".join("-" * col_widths[c] for c in cols)
            print(f"  {header_line}")
            print(f"  {sep_line}")

            for r in rows:
                row_str = []
                for c in cols:
                    val = r[c]
                    val_str = str(val) if val is not None else "NULL"
                    if len(val_str) > 35:
                        val_str = val_str[:32] + "..."
                    row_str.append(val_str.ljust(col_widths[c]))
                print(f"  {' | '.join(row_str)}")
            print(f"  Total Rows: {len(rows)}")
    except Exception as e:
        print(f"  ❌ Query execution error: {e}")


def show_joins():
    print_header("Relational Joins Demonstration: Citizens ⋈ Households ⋈ Administrative Area")
    query = """
    SELECT 
        c.citizen_code,
        c.full_name,
        c.profile_status,
        c.preferred_language AS lang,
        COALESCE(h.household_code, 'UNASSIGNED') AS household_code,
        COALESCE(c.household_relationship, '—') AS household_role,
        COALESCE(u.identifier, 'NATIONAL') AS area_code,
        COALESCE(u.name, 'National Republic') AS area_name
    FROM citizen_profiles c
    LEFT JOIN households h ON c.household_id = h.id
    LEFT JOIN administrative_units u ON c.administrative_unit_id = u.id
    ORDER BY c.id ASC
    LIMIT 10;
    """
    print_table_data("Linked Citizen Records (Joining citizen_profiles ⋈ households ⋈ administrative_units)", query)


def show_family_hierarchy():
    print_header("Family Tree Hierarchy & Permission Delegation (Teacher Feedback Feature)")
    query = """
    SELECT 
        h.household_code,
        c.full_name AS member_name,
        m.relationship_type AS user_specified_role,
        m.status AS membership_status,
        m.start_date,
        m.notes AS audit_remark
    FROM household_memberships m
    JOIN households h ON m.household_id = h.id
    JOIN citizen_profiles c ON m.citizen_id = c.id
    ORDER BY h.household_code, m.id ASC;
    """
    print_table_data("Family Memberships & User-Defined Hierarchy (Admin Verification Only)", query)


def show_overview():
    db_engine_name = engine.dialect.name.upper()
    print("=" * 80)
    print("     NAGRIKSETU (नागरिक सेतु) — DATABASE ARCHITECTURE & LIVE RECORDS")
    print(f"     Active Engine: {db_engine_name} (Production-Grade Containerized)")
    print(f"     Target Database: {settings.POSTGRES_DB if hasattr(settings, 'POSTGRES_DB') else 'civicadmin_db'}")
    print("=" * 80)

    # 1. Administrative Units
    print_table_data(
        "1. administrative_units (Self-Referential Hierarchy: Parent-Child Trees)",
        "SELECT id, identifier, name, unit_type, parent_id, status FROM administrative_units ORDER BY id ASC;"
    )

    # 2. Users (Authentication & Admin Area Scope)
    print_table_data(
        "2. users (Authentication, Argon2 Security & Assigned Admin Scope)",
        "SELECT id, email, role, account_status, administrative_unit_id AS scope_unit_id, created_at FROM users ORDER BY id ASC;"
    )

    # 3. Households (Residential Dwellings & Area Mapping)
    print_table_data(
        "3. households (Municipal Dwellings & Address Records)",
        "SELECT id, household_code, address_line, locality, city, state, postal_code, administrative_unit_id AS area_id FROM households ORDER BY id ASC;"
    )

    # 4. Citizen Profiles (Verified Citizens Linked to Households & Areas)
    print_table_data(
        "4. citizen_profiles (Citizen Registry Linked to User, Household & Area)",
        "SELECT id, citizen_code, full_name, profile_status, user_id, household_id, household_relationship AS role, administrative_unit_id AS area_id FROM citizen_profiles ORDER BY id ASC LIMIT 8;"
    )

    # 5. Household Memberships (Historical Audit Ledger - FR-ADM-016)
    print_table_data(
        "5. household_memberships (Historical Membership Timeline & Status)",
        "SELECT id, household_id, citizen_id, relationship_type, start_date, end_date, status, notes FROM household_memberships ORDER BY id DESC LIMIT 6;"
    )

    # 6. Audit Logs (FR-ADM-024 Mutation Trail)
    print_table_data(
        "6. audit_logs (Complete Mutation Trail - FR-ADM-024)",
        "SELECT id, actor_email, action, resource_type, resource_id, created_at FROM audit_logs ORDER BY id DESC LIMIT 5;"
    )

    # 7. Outbox Events (FR-ADM-025 Service Integration)
    print_table_data(
        "7. outbox_events (Transactional Outbox Domain Events - FR-ADM-025)",
        "SELECT id, event_id, event_type, aggregate_type, aggregate_id, created_at FROM outbox_events ORDER BY id DESC LIMIT 5;"
    )


if __name__ == "__main__":
    if "--joins" in sys.argv:
        show_joins()
    elif "--family" in sys.argv:
        show_family_hierarchy()
    else:
        show_overview()
