import sqlite3

def run_migration():
    conn = sqlite3.connect('data/nagriksetu.db')
    c = conn.cursor()

    # 1. Add columns to enrollments if they don't exist
    c.execute("PRAGMA table_info(enrollments)")
    enr_cols = [col[1] for col in c.fetchall()]
    new_enr_cols = [
        ("program_id", "TEXT"),
        ("degree", "TEXT"),
        ("branch", "TEXT"),
        ("department", "TEXT"),
        ("semester", "INTEGER"),
        ("puc_year", "TEXT"),
        ("curriculum_or_board", "TEXT"),
        ("review_flag", "TEXT")
    ]
    for col_name, col_type in new_enr_cols:
        if col_name not in enr_cols:
            print(f"Adding column '{col_name}' to enrollments...")
            c.execute(f"ALTER TABLE enrollments ADD COLUMN {col_name} {col_type}")

    # 2. Add columns to students if they don't exist
    c.execute("PRAGMA table_info(students)")
    stu_cols = [col[1] for col in c.fetchall()]
    new_stu_cols = [
        ("program_id", "TEXT"),
        ("degree", "TEXT"),
        ("branch", "TEXT"),
        ("department", "TEXT"),
        ("semester", "INTEGER"),
        ("puc_year", "TEXT"),
        ("stream", "TEXT"),
        ("subject_combination", "TEXT"),
        ("curriculum_or_board", "TEXT"),
        ("review_flag", "TEXT")
    ]
    for col_name, col_type in new_stu_cols:
        if col_name not in stu_cols:
            print(f"Adding column '{col_name}' to students...")
            c.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}")

    conn.commit()

    print("Beginning transaction for academic classification update...")
    conn.execute("BEGIN IMMEDIATE")

    # 3. Update Schools: SCH001 - SCH010 (all standards 1-10)
    print("Updating School Education records (SCH001 - SCH010)...")
    for sch_num in range(1, 11):
        sch_id = f"SCH{sch_num:03d}"
        prog_id = f"PROG-{sch_id}-K10"
        c.execute("""
            UPDATE enrollments
            SET stream = 'General',
                subject_combination = 'KSEEB Core Curriculum (Kannada, English, Mathematics, Science, Social Science)',
                program_id = ?,
                degree = 'School Education',
                branch = NULL,
                department = NULL,
                semester = NULL,
                puc_year = NULL,
                curriculum_or_board = 'Karnataka State Board (KSEEB)',
                review_flag = NULL
            WHERE school_id = ?
        """, (prog_id, sch_id))

        c.execute("""
            UPDATE students
            SET stream = 'General',
                subject_combination = 'KSEEB Core Curriculum (Kannada, English, Mathematics, Science, Social Science)',
                program_id = ?,
                degree = 'School Education',
                branch = NULL,
                department = NULL,
                semester = NULL,
                puc_year = NULL,
                curriculum_or_board = 'Karnataka State Board (KSEEB)',
                review_flag = NULL
            WHERE school_id = ?
        """, (prog_id, sch_id))

    # 4. Update Schools: SCH016 - SCH020 (Belagavi, Dharwad, Shivamogga, Ballari, Kalaburagi)
    print("Updating School Education records (SCH016 - SCH020)...")
    for sch_num in range(16, 21):
        sch_id = f"SCH{sch_num:03d}"
        prog_id = f"PROG-{sch_id}-K10"
        # Valid standards 1 to 10
        c.execute("""
            UPDATE enrollments
            SET stream = 'General',
                subject_combination = 'KSEEB Core Curriculum (Kannada, English, Mathematics, Science, Social Science)',
                program_id = ?,
                degree = 'School Education',
                branch = NULL,
                department = NULL,
                semester = NULL,
                puc_year = NULL,
                curriculum_or_board = 'Karnataka State Board (KSEEB)',
                review_flag = NULL
            WHERE school_id = ? AND standard BETWEEN 1 AND 10
        """, (prog_id, sch_id))

        c.execute("""
            UPDATE students
            SET stream = 'General',
                subject_combination = 'KSEEB Core Curriculum (Kannada, English, Mathematics, Science, Social Science)',
                program_id = ?,
                degree = 'School Education',
                branch = NULL,
                department = NULL,
                semester = NULL,
                puc_year = NULL,
                curriculum_or_board = 'Karnataka State Board (KSEEB)',
                review_flag = NULL
            WHERE school_id = ? AND standard BETWEEN 1 AND 10
        """, (prog_id, sch_id))

        # Anomalous standards 11 and 12 in K-10 Schools -> Flag for Review
        c.execute("""
            UPDATE enrollments
            SET stream = 'Unassigned Higher Secondary (Standards 11-12 in K-10 School)',
                subject_combination = 'FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS',
                program_id = NULL,
                degree = NULL,
                branch = NULL,
                department = NULL,
                semester = NULL,
                puc_year = NULL,
                curriculum_or_board = 'Unassigned',
                review_flag = 'FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS'
            WHERE school_id = ? AND standard IN (11, 12)
        """, (sch_id,))

        c.execute("""
            UPDATE students
            SET stream = 'Unassigned Higher Secondary (Standards 11-12 in K-10 School)',
                subject_combination = 'FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS',
                program_id = NULL,
                degree = NULL,
                branch = NULL,
                department = NULL,
                semester = NULL,
                puc_year = NULL,
                curriculum_or_board = 'Unassigned',
                review_flag = 'FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS'
            WHERE school_id = ? AND standard IN (11, 12)
        """, (sch_id,))

    # 5. Update PU Colleges: SCH011 - SCH015 (Tumakuru, Mysuru, Mandya, Hassan Valley, Udupi)
    print("Updating PU College records (SCH011 - SCH015)...")
    pu_institutions = ['SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015']

    for pu_id in pu_institutions:
        # Standards 1 to 10 in PU College -> Flag for review
        c.execute("""
            UPDATE enrollments
            SET stream = 'Unassigned Primary/Secondary (Standards 1-10 in PU College)',
                subject_combination = 'FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS',
                program_id = NULL,
                degree = NULL,
                branch = NULL,
                department = NULL,
                semester = NULL,
                puc_year = NULL,
                curriculum_or_board = 'Department of Pre-University Education (DPUE)',
                review_flag = 'FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS'
            WHERE school_id = ? AND standard BETWEEN 1 AND 10
        """, (pu_id,))

        c.execute("""
            UPDATE students
            SET stream = 'Unassigned Primary/Secondary (Standards 1-10 in PU College)',
                subject_combination = 'FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS',
                program_id = NULL,
                degree = NULL,
                branch = NULL,
                department = NULL,
                semester = NULL,
                puc_year = NULL,
                curriculum_or_board = 'Department of Pre-University Education (DPUE)',
                review_flag = 'FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS'
            WHERE school_id = ? AND standard BETWEEN 1 AND 10
        """, (pu_id,))

        # Standards 11 (1st PUC) and 12 (2nd PUC)
        # 200 students in Std 11, 200 students in Std 12.
        # Order students deterministically by student_id
        for std, puc_yr_label in [(11, '1st PUC'), (12, '2nd PUC')]:
            c.execute("""
                SELECT permanent_student_id, student_id, section
                FROM students
                WHERE school_id = ? AND standard = ?
                ORDER BY student_id
            """, (pu_id, std))
            std_students = c.fetchall()

            # Partition 200 students into realistic combinations matching institution's catalogue:
            # 1. PCMB (Science): 50 students
            # 2. PCMC (Science): 30 students
            # 3. PCME (Science): 20 students
            # 4. CEBA (Commerce): 30 students
            # 5. SEBA (Commerce): 25 students
            # 6. HEBA (Commerce): 20 students
            # 7. MEBA (Commerce): 15 students
            # 8. HEPS (Arts / Humanities): 10 students
            # Total = 50 + 30 + 20 + 30 + 25 + 20 + 15 + 10 = 200 students!

            allocation_specs = [
                ('Science', 'PCMB', 'Pre-University (PCMB: Physics, Chemistry, Mathematics, Biology)', f'PROG-{pu_id}-PCMB', 50),
                ('Science', 'PCMC', 'Pre-University (PCMC: Physics, Chemistry, Mathematics, Computer Science)', f'PROG-{pu_id}-PCMC', 30),
                ('Science', 'PCME', 'Pre-University (PCME: Physics, Chemistry, Mathematics, Electronics)', f'PROG-{pu_id}-PCME', 20),
                ('Commerce', 'CEBA', 'Pre-University (CEBA: Computer Science, Economics, Business Studies, Accountancy)', f'PROG-{pu_id}-CEBA', 30),
                ('Commerce', 'SEBA', 'Pre-University (SEBA: Statistics, Economics, Business Studies, Accountancy)', f'PROG-{pu_id}-SEBA', 25),
                ('Commerce', 'HEBA', 'Pre-University (HEBA: History, Economics, Business Studies, Accountancy)', f'PROG-{pu_id}-HEBA', 20),
                ('Commerce', 'MEBA', 'Pre-University (MEBA: Basic Mathematics, Economics, Business Studies, Accountancy)', f'PROG-{pu_id}-MEBA', 15),
                ('Arts / Humanities', 'HEPS', 'Pre-University (HEPS: History, Economics, Political Science, Sociology)', f'PROG-{pu_id}-HEPS', 10),
            ]

            offset = 0
            for stream_name, combo_code, combo_full, prog_id, count in allocation_specs:
                slice_students = std_students[offset:offset + count]
                offset += count

                for perm_id, s_id, sec in slice_students:
                    c.execute("""
                        UPDATE enrollments
                        SET stream = ?,
                            subject_combination = ?,
                            program_id = ?,
                            degree = 'Pre-University',
                            branch = NULL,
                            department = NULL,
                            semester = NULL,
                            puc_year = ?,
                            curriculum_or_board = 'Department of Pre-University Education (DPUE)',
                            review_flag = NULL
                        WHERE permanent_student_id = ?
                    """, (stream_name, combo_code, prog_id, puc_yr_label, perm_id))

                    c.execute("""
                        UPDATE students
                        SET stream = ?,
                            subject_combination = ?,
                            program_id = ?,
                            degree = 'Pre-University',
                            branch = NULL,
                            department = NULL,
                            semester = NULL,
                            puc_year = ?,
                            curriculum_or_board = 'Department of Pre-University Education (DPUE)',
                            review_flag = NULL
                        WHERE permanent_student_id = ?
                    """, (stream_name, combo_code, prog_id, puc_yr_label, perm_id))

    # 6. Update Degree / Engineering College: COL003 (BMS College of Engineering)
    print("Updating Engineering College records (COL003)...")
    c.execute("""
        UPDATE enrollments
        SET stream = 'Civil Engineering',
            subject_combination = 'Bachelor of Engineering in Civil Engineering',
            program_id = 'PROG-COL003-UG-02',
            degree = 'B.E.',
            branch = 'Civil Engineering',
            department = 'Department of Civil Engineering',
            semester = 1,
            puc_year = NULL,
            curriculum_or_board = 'VTU / Autonomous (AICTE Approved)',
            review_flag = NULL
        WHERE school_id = 'COL003'
    """)

    c.execute("""
        UPDATE students
        SET stream = 'Civil Engineering',
            subject_combination = 'Bachelor of Engineering in Civil Engineering',
            program_id = 'PROG-COL003-UG-02',
            degree = 'B.E.',
            branch = 'Civil Engineering',
            department = 'Department of Civil Engineering',
            semester = 1,
            puc_year = NULL,
            curriculum_or_board = 'VTU / Autonomous (AICTE Approved)',
            review_flag = NULL
        WHERE school_id = 'COL003'
    """)

    conn.commit()
    print("Academic classification update committed successfully!")
    conn.close()

if __name__ == '__main__':
    run_migration()
