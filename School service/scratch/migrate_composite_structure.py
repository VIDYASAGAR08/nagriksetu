"""
NagrikSetu - Composite Institution Academic Structure Migration Script
Implements Scenario B: Composite Institution Policy across SCH011-SCH020
strictly preserving all 30,003 student records, Student IDs, PSIDs, enrollments,
attendance, results, and parent relationships.
"""

import sqlite3
import datetime
import time

DB_PATH = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'

# Pre-University combinations distribution per 200 students
PU_COMBINATIONS = [
    # (Stream, Combination Code, Combination Name, count)
    ("Science", "PCMB", "Pre-University (PCMB: Physics, Chemistry, Mathematics, Biology)", 50),
    ("Science", "PCMC", "Pre-University (PCMC: Physics, Chemistry, Mathematics, Computer Science)", 30),
    ("Science", "PCME", "Pre-University (PCME: Physics, Chemistry, Mathematics, Electronics)", 20),
    ("Commerce", "CEBA", "Pre-University (CEBA: Computer Science, Economics, Business Studies, Accountancy)", 30),
    ("Commerce", "SEBA", "Pre-University (SEBA: Statistics, Economics, Business Studies, Accountancy)", 25),
    ("Commerce", "HEBA", "Pre-University (HEBA: History, Economics, Business Studies, Accountancy)", 20),
    ("Commerce", "MEBA", "Pre-University (MEBA: Basic Mathematics, Economics, Business Studies, Accountancy)", 15),
    ("Arts / Humanities", "HEPS", "Pre-University (HEPS: History, Economics, Political Science, Sociology)", 10)
]

def migrate_composite_structure():
    t0 = time.time()
    print("=== STARTING COMPOSITE INSTITUTION STRUCTURE MIGRATION ===")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    cur = conn.cursor()

    try:
        cur.execute("BEGIN TRANSACTION")

        # 1. Additive columns on students and enrollments
        cur.execute("PRAGMA table_info(students)")
        s_cols = {c[1] for c in cur.fetchall()}
        if "division_id" not in s_cols:
            print("Adding division_id to students...")
            cur.execute("ALTER TABLE students ADD COLUMN division_id TEXT")
        if "academic_division" not in s_cols:
            print("Adding academic_division to students...")
            cur.execute("ALTER TABLE students ADD COLUMN academic_division TEXT")

        cur.execute("PRAGMA table_info(enrollments)")
        e_cols = {c[1] for c in cur.fetchall()}
        if "division_id" not in e_cols:
            print("Adding division_id to enrollments...")
            cur.execute("ALTER TABLE enrollments ADD COLUMN division_id TEXT")
        if "academic_division" not in e_cols:
            print("Adding academic_division to enrollments...")
            cur.execute("ALTER TABLE enrollments ADD COLUMN academic_division TEXT")

        # 2. Update schools table for composite status
        print("Updating institution types for composite status (SCH011-SCH020)...")
        for i in range(11, 16):
            sch_id = f"SCH{i:03d}"
            cur.execute("""
                UPDATE schools 
                SET school_type = 'Composite Pre-University College'
                WHERE school_id = ?
            """, (sch_id,))

        for i in range(16, 21):
            sch_id = f"SCH{i:03d}"
            cur.execute("""
                UPDATE schools 
                SET school_type = 'Composite School & PU College'
                WHERE school_id = ?
            """, (sch_id,))

        # 3. Register divisions in institution_divisions
        print("Registering School and PU divisions in institution_divisions...")
        cur.execute("SELECT school_id, school_name, district FROM schools WHERE school_id BETWEEN 'SCH011' AND 'SCH020'")
        comp_schools = cur.fetchall()

        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for sch_id, sch_name, dist in comp_schools:
            # School Division
            div_school_id = f"DIV-{sch_id}-SCHOOL"
            cur.execute("""
                INSERT OR REPLACE INTO institution_divisions (
                    division_id, parent_institution_id, division_name, division_type,
                    campus_location, head_of_division, contact_phone, contact_email,
                    facilities_summary, description, display_order, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                div_school_id, sch_id, f"{sch_name} - School Division",
                "School (Standards 1-10)", f"{dist} Main Campus",
                "Headmaster / School Coordinator", "+91-80-2360-1001",
                f"school.{sch_id.lower()}@nagriksetu.karnataka.gov.in",
                "Dedicated smart primary and secondary classrooms, science lab, library, sports ground.",
                "Administers primary and secondary school education (Standards 1 to 10) under KSEEB Karnataka State Board.",
                1, now_str
            ))

            # PU Division
            div_pu_id = f"DIV-{sch_id}-PU"
            cur.execute("""
                INSERT OR REPLACE INTO institution_divisions (
                    division_id, parent_institution_id, division_name, division_type,
                    campus_location, head_of_division, contact_phone, contact_email,
                    facilities_summary, description, display_order, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                div_pu_id, sch_id, f"{sch_name} - Pre-University Division",
                "Higher Secondary / PU (11-12)", f"{dist} Higher Secondary Block",
                "Principal / PU Directorate", "+91-80-2360-1002",
                f"pu.{sch_id.lower()}@nagriksetu.karnataka.gov.in",
                "Physics, chemistry, biology, computer labs, electronics workshop, commerce studio.",
                "Administers Pre-University education (1st & 2nd PUC) under Department of Pre-University Education (DPUE) Karnataka.",
                2, now_str
            ))

        # 4. Register academic programs in academic_programs
        print("Registering programs in academic_programs...")
        # For SCH011-SCH015: add School K-10 program
        for i in range(11, 16):
            sch_id = f"SCH{i:03d}"
            prog_id = f"PROG-{sch_id}-K10"
            cur.execute("""
                INSERT OR REPLACE INTO academic_programs (
                    program_id, institution_id, education_level, program_name,
                    degree_type, discipline_or_stream, combination_code,
                    faculty_name, department_name, duration_years, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prog_id, sch_id, 'school',
                'Karnataka State School Education (Std 1-10)', 'None', 'General',
                'K10-GEN', 'School Division', 'Department of School Education',
                10, 1, now_str
            ))

        # For SCH016-SCH020: add the 8 PU programs
        for i in range(16, 21):
            sch_id = f"SCH{i:03d}"
            for st, code, pname, _ in PU_COMBINATIONS:
                prog_id = f"PROG-{sch_id}-{code}"
                cur.execute("""
                    INSERT OR REPLACE INTO academic_programs (
                        program_id, institution_id, education_level, program_name,
                        degree_type, discipline_or_stream, combination_code,
                        faculty_name, department_name, duration_years, is_active, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prog_id, sch_id, 'higher_secondary',
                    pname, 'None', st, code,
                    'Pre-University Division', 'Department of Pre-University Education',
                    2, 1, now_str
                ))

        # 5. Update students and enrollments for SCH011-SCH020
        print("Updating student and enrollment records across SCH011-SCH020...")

        # 5A. Standards 1-10 in SCH011-SCH015 (Group A: 10,000 students)
        for i in range(11, 16):
            sch_id = f"SCH{i:03d}"
            div_id = f"DIV-{sch_id}-SCHOOL"
            prog_id = f"PROG-{sch_id}-K10"
            cur.execute("""
                UPDATE students
                SET division_id = ?,
                    academic_division = 'School Division',
                    curriculum_or_board = 'KSEEB / Karnataka State Board (Std 1-10)',
                    stream = 'General',
                    subject_combination = 'KSEEB Core Curriculum (Kannada, English, Mathematics, Science, Social Science)',
                    program_id = ?,
                    degree = 'School Education',
                    puc_year = NULL,
                    semester = NULL,
                    review_flag = NULL
                WHERE school_id = ? AND standard BETWEEN 1 AND 10
            """, (div_id, prog_id, sch_id))

            cur.execute("""
                UPDATE enrollments
                SET division_id = ?,
                    academic_division = 'School Division',
                    curriculum_or_board = 'KSEEB / Karnataka State Board (Std 1-10)',
                    stream = 'General',
                    subject_combination = 'KSEEB Core Curriculum (Kannada, English, Mathematics, Science, Social Science)',
                    program_id = ?,
                    degree = 'School Education',
                    puc_year = NULL,
                    semester = NULL,
                    review_flag = NULL
                WHERE school_id = ? AND standard BETWEEN 1 AND 10
            """, (div_id, prog_id, sch_id))

        # 5B. Standards 11-12 in SCH011-SCH015 (genuine PU students: 2,000 students)
        for i in range(11, 16):
            sch_id = f"SCH{i:03d}"
            div_id = f"DIV-{sch_id}-PU"
            for std in (11, 12):
                puc_term = "1st PUC" if std == 11 else "2nd PUC"
                cur.execute("""
                    UPDATE students
                    SET division_id = ?,
                        academic_division = 'PU Division',
                        curriculum_or_board = 'Department of Pre-University Education (DPUE), Karnataka',
                        puc_year = ?,
                        degree = NULL,
                        semester = NULL,
                        review_flag = NULL
                    WHERE school_id = ? AND standard = ?
                """, (div_id, puc_term, sch_id, std))

                cur.execute("""
                    UPDATE enrollments
                    SET division_id = ?,
                        academic_division = 'PU Division',
                        curriculum_or_board = 'Department of Pre-University Education (DPUE), Karnataka',
                        puc_year = ?,
                        degree = NULL,
                        semester = NULL,
                        review_flag = NULL
                    WHERE school_id = ? AND standard = ?
                """, (div_id, puc_term, sch_id, std))

        # 5C. Standards 1-10 in SCH016-SCH020 (genuine School students: 10,000 students)
        for i in range(16, 21):
            sch_id = f"SCH{i:03d}"
            div_id = f"DIV-{sch_id}-SCHOOL"
            prog_id = f"PROG-{sch_id}-K10"
            cur.execute("""
                UPDATE students
                SET division_id = ?,
                    academic_division = 'School Division',
                    curriculum_or_board = 'KSEEB / Karnataka State Board (Std 1-10)',
                    stream = 'General',
                    subject_combination = 'KSEEB Core Curriculum (Kannada, English, Mathematics, Science, Social Science)',
                    program_id = ?,
                    degree = 'School Education',
                    puc_year = NULL,
                    semester = NULL,
                    review_flag = NULL
                WHERE school_id = ? AND standard BETWEEN 1 AND 10
            """, (div_id, prog_id, sch_id))

            cur.execute("""
                UPDATE enrollments
                SET division_id = ?,
                    academic_division = 'School Division',
                    curriculum_or_board = 'KSEEB / Karnataka State Board (Std 1-10)',
                    stream = 'General',
                    subject_combination = 'KSEEB Core Curriculum (Kannada, English, Mathematics, Science, Social Science)',
                    program_id = ?,
                    degree = 'School Education',
                    puc_year = NULL,
                    semester = NULL,
                    review_flag = NULL
                WHERE school_id = ? AND standard BETWEEN 1 AND 10
            """, (div_id, prog_id, sch_id))

        # 5D. Standards 11-12 in SCH016-SCH020 (Group B: 2,000 students)
        for i in range(16, 21):
            sch_id = f"SCH{i:03d}"
            div_id = f"DIV-{sch_id}-PU"

            for std in (11, 12):
                puc_term = "1st PUC" if std == 11 else "2nd PUC"
                
                # Fetch students ordered deterministically
                cur.execute("""
                    SELECT student_id, permanent_student_id
                    FROM students
                    WHERE school_id = ? AND standard = ?
                    ORDER BY section, student_id
                """, (sch_id, std))
                pu_students = cur.fetchall()

                # Distribute combinations matching the 200-student distribution
                s_cursor = 0
                for st, code, pname, count in PU_COMBINATIONS:
                    prog_id = f"PROG-{sch_id}-{code}"
                    chunk = pu_students[s_cursor:s_cursor + count]
                    s_cursor += count

                    for sid, psid in chunk:
                        cur.execute("""
                            UPDATE students
                            SET division_id = ?,
                                academic_division = 'PU Division',
                                curriculum_or_board = 'Department of Pre-University Education (DPUE), Karnataka',
                                puc_year = ?,
                                stream = ?,
                                subject_combination = ?,
                                program_id = ?,
                                degree = NULL,
                                semester = NULL,
                                review_flag = NULL
                            WHERE student_id = ?
                        """, (div_id, puc_term, st, code, prog_id, sid))

                        cur.execute("""
                            UPDATE enrollments
                            SET division_id = ?,
                                academic_division = 'PU Division',
                                curriculum_or_board = 'Department of Pre-University Education (DPUE), Karnataka',
                                puc_year = ?,
                                stream = ?,
                                subject_combination = ?,
                                program_id = ?,
                                degree = NULL,
                                semester = NULL,
                                review_flag = NULL
                            WHERE permanent_student_id = ?
                        """, (div_id, puc_term, st, code, prog_id, psid))

        # 5E. Set division for SCH001-SCH010 and COL003
        for i in range(1, 11):
            sch_id = f"SCH{i:03d}"
            cur.execute("""
                UPDATE students
                SET division_id = ?,
                    academic_division = 'School Division'
                WHERE school_id = ?
            """, (f"DIV-{sch_id}-SCHOOL", sch_id))
            cur.execute("""
                UPDATE enrollments
                SET division_id = ?,
                    academic_division = 'School Division'
                WHERE school_id = ?
            """, (f"DIV-{sch_id}-SCHOOL", sch_id))

        cur.execute("""
            UPDATE students
            SET division_id = 'DIV_BMS_ENG',
                academic_division = 'Faculty of Engineering & Technology'
            WHERE school_id = 'COL003'
        """)
        cur.execute("""
            UPDATE enrollments
            SET division_id = 'DIV_BMS_ENG',
                academic_division = 'Faculty of Engineering & Technology'
            WHERE school_id = 'COL003'
        """)

        conn.commit()
        print(f"Transaction successfully committed in {time.time() - t0:.2f}s!")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: Migration failed and rolled back: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_composite_structure()
