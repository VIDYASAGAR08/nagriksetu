"""
test_institution_discovery_disposable.py
Tests the schema additions, rich institution profile data, divisions, and achievements
on nagriksetu_disposable.db.
"""
import sqlite3
import json
import uuid

DISPOSABLE_DB = 'C:/Users/callm/nagriksetu/backend/data/nagriksetu_disposable.db'

def run():
    conn = sqlite3.connect(DISPOSABLE_DB)
    c = conn.cursor()

    print("Step 1: Adding schema columns to schools on disposable DB...")
    # Add columns to schools if they don't exist
    cols = [
        ("parent_institution_id", "TEXT"),
        ("campus_name", "TEXT"),
        ("division_name", "TEXT"),
        ("is_parent_group", "INTEGER DEFAULT 0"),
        ("logo_url", "TEXT"),
        ("cover_image_url", "TEXT"),
        ("email", "TEXT"),
        ("affiliation", "TEXT"),
        ("recognition", "TEXT"),
        ("about_json", "TEXT"),
        ("facilities_details_json", "TEXT"),
        ("hostel_details_json", "TEXT"),
        ("transport_details_json", "TEXT"),
        ("admissions_details_json", "TEXT"),
    ]
    existing_cols = [r[1] for r in c.execute('PRAGMA table_info(schools)').fetchall()]
    for col_name, col_type in cols:
        if col_name not in existing_cols:
            c.execute(f"ALTER TABLE schools ADD COLUMN {col_name} {col_type}")

    print("Step 2: Creating institution_divisions table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS institution_divisions (
            division_id TEXT PRIMARY KEY,
            parent_institution_id TEXT NOT NULL,
            division_name TEXT NOT NULL,
            division_type TEXT NOT NULL,
            campus_location TEXT,
            head_of_division TEXT,
            contact_phone TEXT,
            contact_email TEXT,
            facilities_summary TEXT,
            description TEXT,
            display_order INTEGER DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_institution_id) REFERENCES schools(school_id) ON DELETE CASCADE
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_inst_div_parent ON institution_divisions(parent_institution_id)')

    print("Step 3: Updating school_achievements table...")
    # Check if school_achievements needs extra columns
    ach_cols = [
        ("division_id", "TEXT"),
        ("year", "INTEGER"),
        ("award_level", "TEXT"),
        ("competition_name", "TEXT"),
        ("verification_status", "TEXT DEFAULT 'verified'"),
        ("certificate_image_url", "TEXT"),
        ("category", "TEXT DEFAULT 'Academic'")
    ]
    existing_ach_cols = [r[1] for r in c.execute('PRAGMA table_info(school_achievements)').fetchall()]
    for col_name, col_type in ach_cols:
        if col_name not in existing_ach_cols:
            c.execute(f"ALTER TABLE school_achievements ADD COLUMN {col_name} {col_type}")

    conn.commit()

    print("Step 4: Checking integrity and foreign keys...")
    integrity = c.execute('PRAGMA integrity_check').fetchall()
    fk_check = c.execute('PRAGMA foreign_key_check').fetchall()
    assert integrity == [('ok',)], f"Integrity check failed: {integrity}"
    assert fk_check == [], f"FK violations: {fk_check}"
    print("  [PASS] Integrity and FK checks passed on disposable DB!")

    # Check student counts intact
    students_count = c.execute('SELECT count(*) FROM students').fetchone()[0]
    enrollments_count = c.execute('SELECT count(*) FROM enrollments').fetchone()[0]
    assert students_count == 30000, f"Expected 30000 students, got {students_count}"
    assert enrollments_count == 30000, f"Expected 30000 enrollments, got {enrollments_count}"
    print(f"  [PASS] 30,000 students and enrollments intact!")

    conn.close()

if __name__ == '__main__':
    run()
