import sqlite3
import sys

def run_migration(db_path):
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # 1. Inspect current state for SCH011-SCH015
        cur.execute("SELECT count(*) FROM academic_programs WHERE institution_id BETWEEN 'SCH011' AND 'SCH015' AND program_id LIKE '%-K10'")
        k10_progs = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM program_sections WHERE institution_id BETWEEN 'SCH011' AND 'SCH015' AND program_id LIKE '%-K10'")
        k10_secs = cur.fetchone()[0]
        print(f"Before migration: {k10_progs} K10 programs and {k10_secs} K10 sections found for SCH011-SCH015")

        # 2. Delete legacy school sections for PU colleges
        cur.execute("""
            DELETE FROM program_sections 
            WHERE institution_id BETWEEN 'SCH011' AND 'SCH015' 
              AND program_id LIKE '%-K10'
        """)
        deleted_sections = cur.rowcount
        print(f"Deleted {deleted_sections} legacy school sections from program_sections for PU colleges.")

        # 3. Delete legacy school programs for PU colleges
        cur.execute("""
            DELETE FROM academic_programs 
            WHERE institution_id BETWEEN 'SCH011' AND 'SCH015' 
              AND program_id LIKE '%-K10'
        """)
        deleted_programs = cur.rowcount
        print(f"Deleted {deleted_programs} legacy school programs from academic_programs for PU colleges.")

        # 4. Standardize academic_year format for PU sections
        cur.execute("""
            UPDATE program_sections
            SET academic_year = '2026-27'
            WHERE institution_id BETWEEN 'SCH011' AND 'SCH015'
              AND academic_year = '2026-2027'
        """)
        updated_ay = cur.rowcount
        print(f"Standardized academic_year to '2026-27' for {updated_ay} PU sections.")

        # 5. Integrity and foreign key checks
        cur.execute("PRAGMA integrity_check")
        integrity = cur.fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"Integrity check failed: {integrity}")

        cur.execute("PRAGMA foreign_key_check")
        fk_violations = cur.fetchall()
        if len(fk_violations) > 0:
            raise RuntimeError(f"Foreign key violations found: {fk_violations}")

        # 6. Verify student & enrolment counts are 100% preserved
        cur.execute("SELECT count(*) FROM students")
        students_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM enrollments")
        enrollments_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM schools")
        schools_count = cur.fetchone()[0]

        print(f"Verified Entity Baseline:")
        print(f"  - Schools: {schools_count} (Expected 30)")
        print(f"  - Students: {students_count} (Expected 30,001)")
        print(f"  - Enrollments: {enrollments_count} (Expected 30,001)")

        if schools_count != 30:
            raise RuntimeError(f"Schools count mismatch: {schools_count}")
        if students_count != 30001:
            raise RuntimeError(f"Students count mismatch: {students_count}")
        if enrollments_count != 30001:
            raise RuntimeError(f"Enrollments count mismatch: {enrollments_count}")

        # 7. Check PU capacity and sections per PU college
        print("\nVerifying PU Colleges (SCH011 - SCH015):")
        for inst_id in ['SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015']:
            cur.execute("SELECT count(*) FROM academic_programs WHERE institution_id = ?", (inst_id,))
            p_cnt = cur.fetchone()[0]
            cur.execute("""
                SELECT count(section_id), sum(capacity), sum(current_strength), sum(capacity - current_strength)
                FROM program_sections WHERE institution_id = ?
            """, (inst_id,))
            s_row = cur.fetchone()
            print(f"  {inst_id}: Programs={p_cnt} | Sections={s_row[0]} | Capacity={s_row[1]} | Strength={s_row[2]} | Available={s_row[3]}")
            if p_cnt != 10:
                raise RuntimeError(f"Expected 10 PU programs for {inst_id}, got {p_cnt}")
            if s_row[0] != 20:
                raise RuntimeError(f"Expected 20 PU sections for {inst_id}, got {s_row[0]}")
            if s_row[3] != 200:
                raise RuntimeError(f"Expected 200 available seats for {inst_id}, got {s_row[3]}")

        conn.commit()
        print("\nMigration committed successfully!")
    except Exception as e:
        conn.rollback()
        print(f"MIGRATION FAILED, ROLLED BACK: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
    run_migration(db_file)
