"""
Migration: fix_school_admission_programs.py
Ensures all 15 Schools (SCH001-SCH010, SCH016-SCH020) are strictly School Education (K-10):
- Removes legacy higher_secondary PU programs & sections from SCH016-SCH020
- Ensures pure K-10 school education records
- Preserves all 30,001 students and 30,001 enrollments
- Confirms 0 FK violations
"""

import sqlite3
import shutil
import time

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
BACKUP_PATH = rf"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db.backup_fix_schools_{int(time.time())}"

def main():
    print(f"[*] Creating backup at {BACKUP_PATH}...")
    shutil.copyfile(DB_PATH, BACKUP_PATH)
    print("[+] Backup created.")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    school_ids = [f"SCH{i:03d}" for i in range(1, 11)] + [f"SCH{i:03d}" for i in range(16, 21)]
    print(f"[*] Verifying all 15 schools: {school_ids}")

    # Check categories
    for sid in school_ids:
        c.execute("""
            UPDATE schools
            SET category = 'Schools (K-10)', school_type = 'School'
            WHERE school_id = ?
        """, (sid,))

    # Remove PU sections for SCH016-SCH020
    print("[*] Cleaning up legacy PU sections in SCH016-SCH020...")
    c.execute("""
        DELETE FROM program_sections
        WHERE institution_id IN ('SCH016', 'SCH017', 'SCH018', 'SCH019', 'SCH020')
        AND program_id IN (
            SELECT program_id FROM academic_programs
            WHERE institution_id IN ('SCH016', 'SCH017', 'SCH018', 'SCH019', 'SCH020')
            AND education_level = 'higher_secondary'
        )
    """)

    # Remove PU programs for SCH016-SCH020
    print("[*] Cleaning up legacy PU programs in SCH016-SCH020...")
    c.execute("""
        DELETE FROM academic_programs
        WHERE institution_id IN ('SCH016', 'SCH017', 'SCH018', 'SCH019', 'SCH020')
        AND education_level = 'higher_secondary'
    """)

    # Ensure every school has its K10 program active
    for sid in school_ids:
        c.execute("SELECT program_id FROM academic_programs WHERE institution_id = ? AND education_level = 'school'", (sid,))
        prog = c.fetchone()
        if not prog:
            prog_id = f"PROG-{sid}-K10"
            c.execute("""
                INSERT INTO academic_programs (
                    program_id, institution_id, education_level, program_name, degree_type,
                    discipline_or_stream, duration_years, is_active
                ) VALUES (?, ?, 'school', 'Karnataka State School Education (Std 1-10)', 'None', 'General School Education', 10, 1)
            """, (prog_id, sid))

    # Verification
    print("[*] Checking foreign keys...")
    fk_check = c.execute("PRAGMA foreign_key_check").fetchall()
    if fk_check:
        print("[!] Foreign key violations:", fk_check)
        raise RuntimeError("FK check failed")
    print("[+] 0 foreign key violations.")

    integrity = c.execute("PRAGMA integrity_check").fetchone()[0]
    print(f"[+] Integrity check: {integrity}")

    students = c.execute("SELECT count(*) FROM students").fetchone()[0]
    enrollments = c.execute("SELECT count(*) FROM enrollments").fetchone()[0]
    print(f"[+] Students: {students} (Expected 30001) | Enrollments: {enrollments} (Expected 30001)")
    assert students == 30001 and enrollments == 30001, "Data loss detected!"

    conn.commit()
    conn.close()
    print("[+] Database update completed successfully.")

if __name__ == "__main__":
    main()
