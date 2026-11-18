import sqlite3
import os

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def run_migration():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 1. Check existing columns in schools
    schools_cols = {r[1] for r in c.execute("PRAGMA table_info(schools)").fetchall()}
    new_school_cols = [
        ("logo_url", "TEXT"),
        ("cover_image_url", "TEXT"),
        ("email", "TEXT"),
        ("affiliation", "TEXT"),
        ("recognition", "TEXT"),
        ("campus_name", "TEXT"),
        ("is_parent_group", "INTEGER DEFAULT 0"),
        ("map_url", "TEXT"),
        ("about_json", "TEXT"),
        ("facilities_details_json", "TEXT"),
        ("hostel_details_json", "TEXT"),
        ("transport_details_json", "TEXT"),
        ("admissions_details_json", "TEXT"),
    ]

    for col_name, col_type in new_school_cols:
        if col_name not in schools_cols:
            c.execute(f"ALTER TABLE schools ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to schools")

    # 2. Check existing columns in school_achievements
    achievements_cols = {r[1] for r in c.execute("PRAGMA table_info(school_achievements)").fetchall()}
    new_ach_cols = [
        ("year", "INTEGER"),
        ("award_level", "TEXT DEFAULT 'State'"),
        ("issuing_authority", "TEXT"),
        ("verification_status", "TEXT DEFAULT 'verified'"),
    ]

    for col_name, col_type in new_ach_cols:
        if col_name not in achievements_cols:
            c.execute(f"ALTER TABLE school_achievements ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to school_achievements")

    # 3. Create institution_divisions table
    c.execute("""
    CREATE TABLE IF NOT EXISTS institution_divisions (
        division_id VARCHAR(50) PRIMARY KEY,
        parent_institution_id VARCHAR(20) NOT NULL,
        division_name VARCHAR(255) NOT NULL,
        division_type VARCHAR(100) NOT NULL,
        campus_location VARCHAR(255) NOT NULL,
        head_of_division VARCHAR(100),
        contact_phone VARCHAR(50),
        contact_email VARCHAR(100),
        facilities_summary TEXT,
        description TEXT,
        display_order INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_institution_id) REFERENCES schools(school_id) ON DELETE CASCADE
    )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_inst_divisions_parent ON institution_divisions(parent_institution_id)")
    print("Ensured institution_divisions table and index")

    conn.commit()

    # 4. Verify integrity
    c.execute("PRAGMA integrity_check")
    integ = c.fetchone()[0]
    c.execute("PRAGMA foreign_key_check")
    fk = c.fetchall()
    students_count = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    enrollments_count = c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    programs_count = c.execute("SELECT COUNT(*) FROM academic_programs").fetchone()[0]
    sections_count = c.execute("SELECT COUNT(*) FROM program_sections").fetchone()[0]
    conn.close()

    print(f"Migration completed successfully.")
    print(f"Integrity check: {integ}")
    print(f"Foreign key check: {fk}")
    print(f"Counts - Students: {students_count}, Enrollments: {enrollments_count}, Programs: {programs_count}, Sections: {sections_count}")

if __name__ == "__main__":
    run_migration()
