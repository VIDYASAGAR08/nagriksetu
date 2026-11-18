"""
Migration script: apply_higher_ed_academic_structure.py
Configures final higher education academic structure for:
- 5 Degree Colleges (COL001, COL002, COL003, COL005, COL007)
- 5 Universities (COL004, COL006, COL008, COL009, COL010)

Maintains:
- 30 total institutions
- University hierarchy: University -> Faculty/School -> Department -> Programme -> Academic Year/Level
- UG/PG/Doctoral levels for Universities
- Degree College course lists and clear affiliating university separation
- 30,001 students, 30,001 enrollments, admin accounts, foreign keys
"""

import sqlite3
import shutil
import time
import os

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
BACKUP_PATH = rf"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db.backup_higher_ed_{int(time.time())}"

def main():
    print(f"[*] Creating backup at {BACKUP_PATH}...")
    shutil.copyfile(DB_PATH, BACKUP_PATH)
    print("[+] Backup created successfully.")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF;")
    c = conn.cursor()

    # Step 1: Recreate academic_programs table without restrictive CHECK constraints and with faculty_name and department_name
    print("[*] Updating academic_programs table schema...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS academic_programs_new (
            program_id TEXT PRIMARY KEY,
            institution_id TEXT NOT NULL,
            education_level TEXT NOT NULL,
            program_name TEXT NOT NULL,
            degree_type TEXT NOT NULL DEFAULT 'None',
            discipline_or_stream TEXT,
            combination_code TEXT,
            faculty_name TEXT,
            department_name TEXT,
            duration_years INTEGER NOT NULL DEFAULT 1,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (institution_id) REFERENCES schools(school_id)
        );
    """)

    # Check existing columns of academic_programs
    c.execute("PRAGMA table_info(academic_programs)")
    existing_cols = [r[1] for r in c.fetchall()]
    
    has_faculty = "faculty_name" in existing_cols
    has_dept = "department_name" in existing_cols

    if has_faculty and has_dept:
        c.execute("""
            INSERT OR REPLACE INTO academic_programs_new (
                program_id, institution_id, education_level, program_name, degree_type,
                discipline_or_stream, combination_code, faculty_name, department_name,
                duration_years, is_active, created_at
            )
            SELECT program_id, institution_id, education_level, program_name, degree_type,
                   discipline_or_stream, combination_code, faculty_name, department_name,
                   duration_years, is_active, created_at
            FROM academic_programs;
        """)
    else:
        c.execute("""
            INSERT OR REPLACE INTO academic_programs_new (
                program_id, institution_id, education_level, program_name, degree_type,
                discipline_or_stream, combination_code,
                duration_years, is_active, created_at
            )
            SELECT program_id, institution_id, education_level, program_name, degree_type,
                   discipline_or_stream, combination_code,
                   duration_years, is_active, created_at
            FROM academic_programs;
        """)

    c.execute("DROP TABLE academic_programs;")
    c.execute("ALTER TABLE academic_programs_new RENAME TO academic_programs;")
    print("[+] academic_programs schema updated.")

    # Step 2: Ensure any admission applications pointing to DIP programs are redirected to active UG program
    print("[*] Realigning admission applications pointing to legacy DIP programs...")
    c.execute("""
        UPDATE admission_applications
        SET requested_program_id = 'PROG-COL001-UG-01'
        WHERE requested_program_id LIKE '%COL001%DIP%'
    """)
    c.execute("""
        UPDATE admission_applications
        SET requested_program_id = 'PROG-COL010-UG-01'
        WHERE requested_program_id LIKE '%COL010%DIP%'
    """)

    # Step 3: Remove sections of legacy diploma programs from COL001-COL010
    print("[*] Deleting sections for legacy diploma programs...")
    c.execute("DELETE FROM program_sections WHERE program_id LIKE '%-DIP';")

    # Step 4: Delete legacy diploma programs from academic_programs
    print("[*] Deleting legacy diploma programs from academic_programs...")
    c.execute("DELETE FROM academic_programs WHERE program_id LIKE '%-DIP';")

    # Also remove any polytechnic division
    c.execute("DELETE FROM institution_divisions WHERE division_id LIKE '%POLY%';")

    # Step 5: Configure 5 Degree Colleges
    print("[*] Configuring 5 Degree Colleges...")
    degree_colleges = [
        {
            "id": "COL001",
            "name": "Ramaiah Institute of Technology (MSRIT)",
            "school_type": "Degree College",
            "category": "Degree Colleges",
            "affiliation": "Visvesvaraya Technological University (VTU), Belagavi",
            "recognition": "Autonomous Institute Affiliated to VTU, NAAC A+, NBA Accredited",
            "programs": [
                ("PROG-COL001-UG-01", "COL001", "undergraduate", "B.E. in Computer Science and Engineering", "BE/B.Tech", "Computer Science & Engineering", None, "Faculty of Engineering & Technology", "Department of Computer Science & Engineering", 4, 1),
                ("PROG-COL001-UG-02", "COL001", "undergraduate", "B.E. in Artificial Intelligence and Machine Learning", "BE/B.Tech", "AI & Machine Learning", None, "Faculty of Engineering & Technology", "Department of Computer Science & Engineering", 4, 1),
                ("PROG-COL001-UG-03", "COL001", "undergraduate", "B.E. in Information Science and Engineering", "BE/B.Tech", "Information Science & Engineering", None, "Faculty of Engineering & Technology", "Department of Information Science", 4, 1),
                ("PROG-COL001-UG-04", "COL001", "undergraduate", "B.E. in Electronics and Communication Engineering", "BE/B.Tech", "Electronics & Communication", None, "Faculty of Engineering & Technology", "Department of Electronics & Communication", 4, 1),
                ("PROG-COL001-UG-05", "COL001", "undergraduate", "B.E. in Mechanical Engineering", "BE/B.Tech", "Mechanical Engineering", None, "Faculty of Engineering & Technology", "Department of Mechanical Engineering", 4, 1),
                ("PROG-COL001-BPHARM", "COL001", "undergraduate", "Bachelor of Pharmacy (B.Pharm)", "BPharm", "Pharmaceutical Sciences", None, "Faculty of Pharmacy & Health Sciences", "Department of Pharmaceutical Sciences", 4, 1),
                ("PROG-COL001-UG-08", "COL001", "undergraduate", "Bachelor of Architecture (B.Arch)", "Other", "Architecture & Design", None, "School of Architecture", "Department of Architecture", 5, 1),
                ("PROG-COL001-UG-07", "COL001", "postgraduate", "Master of Computer Applications (MCA)", "MCA", "Computer Applications", None, "Faculty of Engineering & Technology", "Department of Computer Applications", 2, 1),
            ],
            "sections": [
                # UG-01 (CSE)
                ("SEC-COL001-UG01-Y1-A", "COL001", "PROG-COL001-UG-01", "2026-27", 1, 1, "A", 70, 58),
                ("SEC-COL001-UG01-Y1-B", "COL001", "PROG-COL001-UG-01", "2026-27", 1, 1, "B", 70, 56),
                ("SEC-COL001-UG01-Y2-A", "COL001", "PROG-COL001-UG-01", "2026-27", 2, 3, "A", 68, 57),
                ("SEC-COL001-UG01-Y3-A", "COL001", "PROG-COL001-UG-01", "2026-27", 3, 5, "A", 68, 58),
                ("SEC-COL001-UG01-Y4-A", "COL001", "PROG-COL001-UG-01", "2026-27", 4, 7, "A", 65, 55),
                # UG-02 (AI/ML)
                ("SEC-COL001-UG02-Y1-A", "COL001", "PROG-COL001-UG-02", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL001-UG02-Y2-A", "COL001", "PROG-COL001-UG-02", "2026-27", 2, 3, "A", 60, 50),
                # UG-03 (ISE)
                ("SEC-COL001-UG03-Y1-A", "COL001", "PROG-COL001-UG-03", "2026-27", 1, 1, "A", 60, 49),
                ("SEC-COL001-UG03-Y2-A", "COL001", "PROG-COL001-UG-03", "2026-27", 2, 3, "A", 60, 51),
                # UG-04 (ECE)
                ("SEC-COL001-UG04-Y1-A", "COL001", "PROG-COL001-UG-04", "2026-27", 1, 1, "A", 65, 52),
                ("SEC-COL001-UG04-Y2-A", "COL001", "PROG-COL001-UG-04", "2026-27", 2, 3, "A", 65, 54),
                # UG-05 (Mech)
                ("SEC-COL001-UG05-Y1-A", "COL001", "PROG-COL001-UG-05", "2026-27", 1, 1, "A", 70, 60),
                ("SEC-COL001-UG05-Y1-B", "COL001", "PROG-COL001-UG-05", "2026-27", 1, 1, "B", 66, 56),
                ("SEC-COL001-UG05-Y2-A", "COL001", "PROG-COL001-UG-05", "2026-27", 2, 3, "A", 68, 58),
                # BPHARM
                ("SEC-COL001-PH-Y1-A", "COL001", "PROG-COL001-BPHARM", "2026-27", 1, 1, "A", 52, 42),
                ("SEC-COL001-PH-Y2-A", "COL001", "PROG-COL001-BPHARM", "2026-27", 2, 3, "A", 50, 40),
                # BARCH
                ("SEC-COL001-AR-Y1-A", "COL001", "PROG-COL001-UG-08", "2026-27", 1, 1, "A", 45, 35),
                ("SEC-COL001-AR-Y2-A", "COL001", "PROG-COL001-UG-08", "2026-27", 2, 3, "A", 43, 33),
                # MCA
                ("SEC-COL001-MCA-Y1-A", "COL001", "PROG-COL001-UG-07", "2026-27", 1, 1, "A", 60, 50),
            ]
        },
        {
            "id": "COL002",
            "name": "R.V. College of Engineering (RVCE)",
            "school_type": "Degree College",
            "category": "Degree Colleges",
            "affiliation": "Visvesvaraya Technological University (VTU), Belagavi",
            "recognition": "Autonomous Institution Affiliated to VTU, AICTE Approved, NAAC A+",
            "programs": [
                ("PROG-COL002-UG-01", "COL002", "undergraduate", "B.E. in Computer Science and Engineering", "BE/B.Tech", "Computer Science & Engineering", None, "Faculty of Engineering", "Department of Computer Science & Engineering", 4, 1),
                ("PROG-COL002-UG-02", "COL002", "undergraduate", "B.E. in Electronics and Communication Engineering", "BE/B.Tech", "Electronics & Communication", None, "Faculty of Engineering", "Department of Electronics & Communication", 4, 1),
                ("PROG-COL002-UG-03", "COL002", "undergraduate", "B.E. in Aerospace Engineering", "BE/B.Tech", "Aerospace Engineering", None, "Faculty of Engineering", "Department of Aerospace Engineering", 4, 1),
                ("PROG-COL002-UG-04", "COL002", "undergraduate", "B.E. in Mechanical Engineering", "BE/B.Tech", "Mechanical Engineering", None, "Faculty of Engineering", "Department of Mechanical Engineering", 4, 1),
                ("PROG-COL002-UG-05", "COL002", "undergraduate", "B.E. in Biotechnology", "BE/B.Tech", "Biotechnology", None, "Faculty of Engineering", "Department of Biotechnology", 4, 1),
            ],
            "sections": [
                ("SEC-COL002-UG01-Y1-A", "COL002", "PROG-COL002-UG-01", "2026-27", 1, 1, "A", 70, 58),
                ("SEC-COL002-UG01-Y1-B", "COL002", "PROG-COL002-UG-01", "2026-27", 1, 1, "B", 70, 59),
                ("SEC-COL002-UG01-Y2-A", "COL002", "PROG-COL002-UG-01", "2026-27", 2, 3, "A", 68, 56),
                ("SEC-COL002-UG02-Y1-A", "COL002", "PROG-COL002-UG-02", "2026-27", 1, 1, "A", 65, 52),
                ("SEC-COL002-UG02-Y2-A", "COL002", "PROG-COL002-UG-02", "2026-27", 2, 3, "A", 65, 54),
                ("SEC-COL002-UG03-Y1-A", "COL002", "PROG-COL002-UG-03", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL002-UG03-Y2-A", "COL002", "PROG-COL002-UG-03", "2026-27", 2, 3, "A", 60, 50),
                ("SEC-COL002-UG04-Y1-A", "COL002", "PROG-COL002-UG-04", "2026-27", 1, 1, "A", 65, 50),
                ("SEC-COL002-UG05-Y1-A", "COL002", "PROG-COL002-UG-05", "2026-27", 1, 1, "A", 55, 42),
            ]
        },
        {
            "id": "COL003",
            "name": "BMS College of Engineering (BMSCE)",
            "school_type": "Degree College",
            "category": "Degree Colleges",
            "affiliation": "Visvesvaraya Technological University (VTU), Belagavi",
            "recognition": "Autonomous College Affiliated to VTU, AICTE Approved, NAAC A++",
            "programs": [
                ("PROG-COL003-UG-01", "COL003", "undergraduate", "B.E. in Computer Science and Engineering", "BE/B.Tech", "Computer Science & Engineering", None, "Faculty of Engineering", "Department of Computer Science & Engineering", 4, 1),
                ("PROG-COL003-UG-02", "COL003", "undergraduate", "B.E. in Civil Engineering", "BE/B.Tech", "Civil Engineering", None, "Faculty of Engineering", "Department of Civil Engineering", 4, 1),
                ("PROG-COL003-UG-03", "COL003", "undergraduate", "B.E. in Electrical and Electronics Engineering", "BE/B.Tech", "Electrical & Electronics", None, "Faculty of Engineering", "Department of Electrical Engineering", 4, 1),
                ("PROG-COL003-UG-04", "COL003", "undergraduate", "B.E. in Information Science and Engineering", "BE/B.Tech", "Information Science", None, "Faculty of Engineering", "Department of Information Science", 4, 1),
            ],
            "sections": [
                ("SEC-COL003-UG01-Y1-A", "COL003", "PROG-COL003-UG-01", "2026-27", 1, 1, "A", 70, 58),
                ("SEC-COL003-UG01-Y2-A", "COL003", "PROG-COL003-UG-01", "2026-27", 2, 3, "A", 68, 55),
                ("SEC-COL003-UG02-Y1-A", "COL003", "PROG-COL003-UG-02", "2026-27", 1, 1, "A", 65, 50),
                ("SEC-COL003-UG02-Y2-A", "COL003", "PROG-COL003-UG-02", "2026-27", 2, 3, "A", 65, 52),
                ("SEC-COL003-UG03-Y1-A", "COL003", "PROG-COL003-UG-03", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL003-UG04-Y1-A", "COL003", "PROG-COL003-UG-04", "2026-27", 1, 1, "A", 60, 47),
            ]
        },
        {
            "id": "COL005",
            "name": "The National Institute of Engineering (NIE)",
            "school_type": "Degree College",
            "category": "Degree Colleges",
            "affiliation": "Visvesvaraya Technological University (VTU), Belagavi",
            "recognition": "Autonomous Institute Affiliated to VTU, Mysuru, AICTE Approved, NAAC A",
            "programs": [
                ("PROG-COL005-UG-01", "COL005", "undergraduate", "B.E. in Computer Science and Engineering", "BE/B.Tech", "Computer Science & Engineering", None, "Faculty of Engineering", "Department of Computer Science & Engineering", 4, 1),
                ("PROG-COL005-UG-02", "COL005", "undergraduate", "B.E. in Mechanical Engineering", "BE/B.Tech", "Mechanical Engineering", None, "Faculty of Engineering", "Department of Mechanical Engineering", 4, 1),
                ("PROG-COL005-UG-03", "COL005", "undergraduate", "B.E. in Civil Engineering", "BE/B.Tech", "Civil Engineering", None, "Faculty of Engineering", "Department of Civil Engineering", 4, 1),
                ("PROG-COL005-UG-04", "COL005", "undergraduate", "B.E. in Electronics and Communication Engineering", "BE/B.Tech", "Electronics & Communication", None, "Faculty of Engineering", "Department of Electronics & Communication", 4, 1),
            ],
            "sections": [
                ("SEC-COL005-UG01-Y1-A", "COL005", "PROG-COL005-UG-01", "2026-27", 1, 1, "A", 65, 52),
                ("SEC-COL005-UG01-Y2-A", "COL005", "PROG-COL005-UG-01", "2026-27", 2, 3, "A", 65, 54),
                ("SEC-COL005-UG02-Y1-A", "COL005", "PROG-COL005-UG-02", "2026-27", 1, 1, "A", 65, 50),
                ("SEC-COL005-UG03-Y1-A", "COL005", "PROG-COL005-UG-03", "2026-27", 1, 1, "A", 60, 46),
                ("SEC-COL005-UG04-Y1-A", "COL005", "PROG-COL005-UG-04", "2026-27", 1, 1, "A", 65, 51),
            ]
        },
        {
            "id": "COL007",
            "name": "Mount Carmel College (Autonomous)",
            "school_type": "Degree College",
            "category": "Degree Colleges",
            "affiliation": "Bengaluru City University",
            "recognition": "UGC Autonomous, NAAC A+ (Fourth Cycle), Bengaluru City University Affiliated",
            "programs": [
                ("PROG-COL007-BBA", "COL007", "undergraduate", "Bachelor of Business Administration (BBA)", "BBA", "Business Administration", None, "School of Commerce & Management", "Department of Management Studies", 3, 1),
                ("PROG-COL007-BCOM", "COL007", "undergraduate", "Bachelor of Commerce (Honours)", "BCom", "Commerce & Accounting", None, "School of Commerce & Management", "Department of Commerce", 3, 1),
                ("PROG-COL007-BCA", "COL007", "undergraduate", "Bachelor of Computer Applications (BCA)", "BCA", "Computer Applications & Analytics", None, "School of Sciences", "Department of Computer Science", 3, 1),
                ("PROG-COL007-BSC", "COL007", "undergraduate", "B.Sc in Biotechnology, Chemistry & Botany", "BSc", "Life Sciences", None, "School of Sciences", "Department of Biotechnology & Life Sciences", 3, 1),
                ("PROG-COL007-BA", "COL007", "undergraduate", "Bachelor of Arts in Journalism & Psychology", "BA", "Arts & Humanities", None, "School of Humanities", "Department of Humanities", 3, 1),
            ],
            "sections": [
                ("SEC-COL007-BBA-Y1-A", "COL007", "PROG-COL007-BBA", "2026-27", 1, 1, "A", 60, 50),
                ("SEC-COL007-BBA-Y2-A", "COL007", "PROG-COL007-BBA", "2026-27", 2, 3, "A", 60, 52),
                ("SEC-COL007-BCOM-Y1-A", "COL007", "PROG-COL007-BCOM", "2026-27", 1, 1, "A", 70, 60),
                ("SEC-COL007-BCOM-Y2-A", "COL007", "PROG-COL007-BCOM", "2026-27", 2, 3, "A", 70, 62),
                ("SEC-COL007-BCA-Y1-A", "COL007", "PROG-COL007-BCA", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL007-BSC-Y1-A", "COL007", "PROG-COL007-BSC", "2026-27", 1, 1, "A", 55, 42),
                ("SEC-COL007-BA-Y1-A", "COL007", "PROG-COL007-BA", "2026-27", 1, 1, "A", 55, 44),
            ]
        }
    ]

    for dc in degree_colleges:
        c.execute("""
            UPDATE schools
            SET school_type = ?, category = ?, affiliation = ?, recognition = ?
            WHERE school_id = ?
        """, (dc["school_type"], dc["category"], dc["affiliation"], dc["recognition"], dc["id"]))

        # Remove existing sections for this college
        c.execute("DELETE FROM program_sections WHERE institution_id = ?", (dc["id"],))

        # Remove existing programs for this college
        c.execute("DELETE FROM academic_programs WHERE institution_id = ?", (dc["id"],))

        # Insert updated programs
        for prog in dc["programs"]:
            c.execute("""
                INSERT INTO academic_programs (
                    program_id, institution_id, education_level, program_name, degree_type,
                    discipline_or_stream, combination_code, faculty_name, department_name,
                    duration_years, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, prog)

        # Insert sections
        for sec in dc["sections"]:
            c.execute("""
                INSERT INTO program_sections (
                    section_id, institution_id, program_id, academic_year,
                    term_or_year, semester, section_name, capacity, current_strength
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sec)

    print("[+] 5 Degree Colleges configured successfully.")

    # Step 6: Configure 5 Universities
    print("[*] Configuring 5 Universities with Hierarchical Academic Structure...")
    universities = [
        {
            "id": "COL004",
            "name": "PES University (Ring Road Campus)",
            "school_type": "University",
            "category": "Universities",
            "affiliation": "PES University Act, State Private University (UGC Recognized)",
            "recognition": "State Private University (Karnataka Act No. 16 of 2013), UGC Recognized, NAAC A+",
            "divisions": [
                ("DIV_PESU_ENG", "COL004", "Faculty of Engineering & Technology", "Engineering & Technology", "Ring Road Campus, Bengaluru", "Dr. V. Krishna (Dean, Engineering)", "080-26721983", "dean.engg@pes.edu", "AI Research Labs, High-Performance Compute Cluster, Robotics Arena", "Apex Engineering School offering UG, PG, and Doctoral research programmes.", 1),
                ("DIV_PESU_MGT", "COL004", "Faculty of Commerce & Management", "Commerce & Management", "Management Block, Bengaluru", "Dr. Shailashree Haridas (Dean, Management)", "080-26721984", "dean.mgmt@pes.edu", "FinTech Incubation Lab, Harvard Business Case Library", "Comprehensive business school offering BBA, MBA, and Management Research.", 2),
                ("DIV_PESU_SCI", "COL004", "Faculty of Science", "Science & Biotechnology", "Biotech Block, Bengaluru", "Dr. K. S. Sridhar (Dean, Science)", "080-26721985", "dean.science@pes.edu", "Advanced Bioinformatics & Cell Culture Facility", "Cutting-edge biotechnology and natural science research division.", 3),
                ("DIV_PESU_RES", "COL004", "Faculty of Research & Advanced Studies", "Doctoral & Advanced Research", "PES Central Research Centre, Bengaluru", "Dr. T. S. Chandrashekar (Dean, Research)", "080-26721986", "dean.research@pes.edu", "Centralized Research Core with sponsored international grants", "University-wide PhD programmes, postdoctoral fellowships, and patent cell.", 4),
            ],
            "programs": [
                # Engineering - UG, PG, Doctoral
                ("PROG-COL004-UG-CSE", "COL004", "undergraduate", "B.Tech in Computer Science and Engineering", "BE/B.Tech", "Computer Science", None, "Faculty of Engineering & Technology", "Department of Computer Science & Engineering", 4, 1),
                ("PROG-COL004-UG-ECE", "COL004", "undergraduate", "B.Tech in Electronics and Communication Engineering", "BE/B.Tech", "Electronics & Communication", None, "Faculty of Engineering & Technology", "Department of Electronics & Communication", 4, 1),
                ("PROG-COL004-PG-CSE", "COL004", "postgraduate", "M.Tech in Cloud Computing & Cybersecurity", "MTech", "Computer Science & Security", None, "Faculty of Engineering & Technology", "Department of Computer Science & Engineering", 2, 1),
                ("PROG-COL004-DOC-CSE", "COL004", "doctoral", "Ph.D. in Computer Science & Artificial Intelligence", "PhD", "Computer Science & AI", None, "Faculty of Engineering & Technology", "Department of Computer Science & Engineering", 3, 1),
                # Science - UG
                ("PROG-COL004-UG-BIO", "COL004", "undergraduate", "B.Tech in Biotechnology", "BE/B.Tech", "Biotechnology", None, "Faculty of Science", "Department of Biotechnology & Bioinformatics", 4, 1),
                # Management - UG, PG
                ("PROG-COL004-UG-BBA", "COL004", "undergraduate", "Bachelor of Business Administration (BBA)", "BBA", "Business Administration", None, "Faculty of Commerce & Management", "Department of Management Studies", 3, 1),
                ("PROG-COL004-PG-MBA", "COL004", "postgraduate", "Master of Business Administration (MBA)", "MBA", "Finance, Marketing & HR", None, "Faculty of Commerce & Management", "Department of Management Studies", 2, 1),
                # Research - Doctoral
                ("PROG-COL004-DOC-INT", "COL004", "doctoral", "Ph.D. in Interdisciplinary Engineering Sciences", "PhD", "Interdisciplinary Research", None, "Faculty of Research & Advanced Studies", "Centre for Doctoral Studies", 3, 1),
            ],
            "sections": [
                ("SEC-COL004-CSE-Y1-A", "COL004", "PROG-COL004-UG-CSE", "2026-27", 1, 1, "A", 75, 62),
                ("SEC-COL004-CSE-Y1-B", "COL004", "PROG-COL004-UG-CSE", "2026-27", 1, 1, "B", 75, 64),
                ("SEC-COL004-CSE-Y2-A", "COL004", "PROG-COL004-UG-CSE", "2026-27", 2, 3, "A", 72, 60),
                ("SEC-COL004-ECE-Y1-A", "COL004", "PROG-COL004-UG-ECE", "2026-27", 1, 1, "A", 65, 52),
                ("SEC-COL004-PGCSE-Y1", "COL004", "PROG-COL004-PG-CSE", "2026-27", 1, 1, "A", 30, 22),
                ("SEC-COL004-DOCCSE-Y1", "COL004", "PROG-COL004-DOC-CSE", "2026-27", 1, 1, "Research", 15, 10),
                ("SEC-COL004-BIO-Y1-A", "COL004", "PROG-COL004-UG-BIO", "2026-27", 1, 1, "A", 50, 38),
                ("SEC-COL004-BBA-Y1-A", "COL004", "PROG-COL004-UG-BBA", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL004-MBA-Y1-A", "COL004", "PROG-COL004-PG-MBA", "2026-27", 1, 1, "A", 60, 50),
                ("SEC-COL004-DOCINT-Y1", "COL004", "PROG-COL004-DOC-INT", "2026-27", 1, 1, "Research", 15, 8),
            ]
        },
        {
            "id": "COL006",
            "name": "St. Joseph's University",
            "school_type": "University",
            "category": "Universities",
            "affiliation": "St. Joseph's University Act, Jesuit Higher Education Institution (UGC Recognized)",
            "recognition": "Established under St. Joseph's University Act 2021 (Karnataka Act 18 of 2021), UGC Recognized, NAAC A++",
            "divisions": [
                ("DIV_SJU_HUM", "COL006", "Faculty of Arts & Humanities", "School of Humanities & Social Sciences", "Lalbagh Road Heritage Campus, Bengaluru", "Rev. Fr. Dr. Victor Lobo SJ (Dean)", "080-22274079", "dean.humanities@sju.edu.in", "Media Studio, Heritage Archives, Psychological Assessment Lab", "Historic faculty offering premier BA, MA, and Humanities doctoral studies.", 1),
                ("DIV_SJU_COM", "COL006", "Faculty of Commerce & Management", "School of Business & Commerce", "Arrupe Commerce Complex, Bengaluru", "Dr. D. Raja Jebasingh (Dean)", "080-22274080", "dean.commerce@sju.edu.in", "Bloomberg Trading Terminal Room, Incubation Cell", "Top-ranked commerce faculty offering B.Com (Hons), BBA, M.Com, and Research.", 2),
                ("DIV_SJU_SCI", "COL006", "Faculty of Science", "School of Chemical & Biological Sciences", "Loyola Science Block, Lalbagh Road, Bengaluru", "Dr. Ronald Mascarenhas (Dean)", "080-22274081", "dean.science@sju.edu.in", "Analytical Chemistry Instrumentation Facility, Herbarium, Tissue Culture Labs", "Advanced faculty offering B.Sc, M.Sc, and Chemical Sciences research.", 3),
                ("DIV_SJU_RES", "COL006", "Faculty of Research & Advanced Studies", "Directorate of Doctoral Research", "St. Joseph's Research Directorate, Bengaluru", "Dr. Melwin Colaco (Director, Research)", "080-22274082", "research@sju.edu.in", "Central Research Facility, UGC-STRIDE Supported Centre", "University research council overseeing interdisciplinary doctoral dissertations.", 4),
            ],
            "programs": [
                # Arts & Humanities - UG, PG, Doctoral
                ("PROG-COL006-UG-ECON", "COL006", "undergraduate", "Bachelor of Arts in Economics & International Relations", "BA", "Economics & Social Sciences", None, "Faculty of Arts & Humanities", "Department of Economics & Public Policy", 3, 1),
                ("PROG-COL006-PG-ECON", "COL006", "postgraduate", "Master of Arts in Public Policy and Governance", "MA", "Public Policy", None, "Faculty of Arts & Humanities", "Department of Economics & Public Policy", 2, 1),
                ("PROG-COL006-UG-ENG", "COL006", "undergraduate", "B.A. in English Literature & Journalism", "BA", "English & Media Studies", None, "Faculty of Arts & Humanities", "Department of English & Communication", 3, 1),
                ("PROG-COL006-DOC-HUM", "COL006", "doctoral", "Ph.D. in Humanities and Social Sciences", "PhD", "Social Sciences Research", None, "Faculty of Research & Advanced Studies", "Directorate of Doctoral Research", 3, 1),
                # Commerce & Management - UG, PG
                ("PROG-COL006-UG-BCOM", "COL006", "undergraduate", "B.Com (Honours) in International Accounting & Finance", "BCom", "Commerce & Finance", None, "Faculty of Commerce & Management", "Department of Commerce & Finance", 3, 1),
                ("PROG-COL006-PG-MCOM", "COL006", "postgraduate", "Master of Commerce (M.Com)", "MCom", "Advanced Commerce & Taxation", None, "Faculty of Commerce & Management", "Department of Commerce & Finance", 2, 1),
                ("PROG-COL006-UG-BBA", "COL006", "undergraduate", "Bachelor of Business Administration (BBA)", "BBA", "Business Administration", None, "Faculty of Commerce & Management", "Department of Management Studies", 3, 1),
                # Science - UG, PG, Doctoral
                ("PROG-COL006-UG-BSC", "COL006", "undergraduate", "B.Sc. in Chemistry, Botany & Zoology", "BSc", "Natural & Life Sciences", None, "Faculty of Science", "Department of Chemical & Biological Sciences", 3, 1),
                ("PROG-COL006-PG-MSC", "COL006", "postgraduate", "M.Sc. in Biotechnology & Molecular Biology", "MSc", "Biotechnology", None, "Faculty of Science", "Department of Chemical & Biological Sciences", 2, 1),
                ("PROG-COL006-DOC-SCI", "COL006", "doctoral", "Ph.D. in Chemical and Biological Sciences", "PhD", "Chemical Sciences Research", None, "Faculty of Research & Advanced Studies", "Directorate of Doctoral Research", 3, 1),
            ],
            "sections": [
                ("SEC-COL006-ECON-Y1-A", "COL006", "PROG-COL006-UG-ECON", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL006-ECON-Y2-A", "COL006", "PROG-COL006-UG-ECON", "2026-27", 2, 3, "A", 60, 50),
                ("SEC-COL006-MAEC-Y1", "COL006", "PROG-COL006-PG-ECON", "2026-27", 1, 1, "A", 35, 26),
                ("SEC-COL006-ENG-Y1-A", "COL006", "PROG-COL006-UG-ENG", "2026-27", 1, 1, "A", 55, 44),
                ("SEC-COL006-BCOM-Y1-A", "COL006", "PROG-COL006-UG-BCOM", "2026-27", 1, 1, "A", 70, 60),
                ("SEC-COL006-BCOM-Y1-B", "COL006", "PROG-COL006-UG-BCOM", "2026-27", 1, 1, "B", 70, 58),
                ("SEC-COL006-MCOM-Y1", "COL006", "PROG-COL006-PG-MCOM", "2026-27", 1, 1, "A", 40, 32),
                ("SEC-COL006-BBA-Y1-A", "COL006", "PROG-COL006-UG-BBA", "2026-27", 1, 1, "A", 60, 50),
                ("SEC-COL006-BSC-Y1-A", "COL006", "PROG-COL006-UG-BSC", "2026-27", 1, 1, "A", 55, 42),
                ("SEC-COL006-MSC-Y1", "COL006", "PROG-COL006-PG-MSC", "2026-27", 1, 1, "A", 30, 24),
                ("SEC-COL006-DOCHUM-Y1", "COL006", "PROG-COL006-DOC-HUM", "2026-27", 1, 1, "Research", 12, 8),
                ("SEC-COL006-DOCSCI-Y1", "COL006", "PROG-COL006-DOC-SCI", "2026-27", 1, 1, "Research", 12, 7),
            ]
        },
        {
            "id": "COL008",
            "name": "KLE Technological University (BVBCET)",
            "school_type": "University",
            "category": "Universities",
            "affiliation": "KLE Technological University Act, State Private University (UGC Recognized)",
            "recognition": "State Private University (Karnataka Act 22 of 2013), UGC Recognized, NBA Tier-1",
            "divisions": [
                ("DIV_KLE_ENG", "COL008", "Faculty of Engineering & Technology", "School of Engineering", "KLE Tech Campus, Vidyanagar, Hubballi", "Dr. B. L. Desai (Dean, Engineering)", "0836-2378123", "dean.engg@kletech.ac.in", "Robotics CoE, Center for VLSI & Embedded Systems, Automotive Prototyping Lab", "Leading technological faculty specializing in Industry 4.0 engineering fields.", 1),
                ("DIV_KLE_MGT", "COL008", "Faculty of Commerce & Management", "School of Management Studies", "Vidyanagar Campus, Hubballi", "Dr. P. R. Patil (Dean, Management)", "0836-2378124", "dean.som@kletech.ac.in", "Entrepreneurship & Innovation Center (CTIE), Case Analysis Suites", "Technology management school offering MBA and tech-venture incubation.", 2),
                ("DIV_KLE_RES", "COL008", "Faculty of Research & Advanced Studies", "Centre for Doctoral Studies & Research", "Research Complex, Hubballi", "Dr. Uma Mudenagudi (Dean, R&D)", "0836-2378125", "dean.rd@kletech.ac.in", "Funded Research Facilities with DRDO, ISRO, and DST collaborative tie-ups", "Doctoral research division awarding Ph.D. degrees in advanced sciences and engineering.", 3),
            ],
            "programs": [
                # Engineering - UG, PG
                ("PROG-COL008-UG-CSE", "COL008", "undergraduate", "B.Tech in Computer Science and Engineering", "BE/B.Tech", "Computer Science", None, "Faculty of Engineering & Technology", "Department of Computer Science & Engineering", 4, 1),
                ("PROG-COL008-UG-ROB", "COL008", "undergraduate", "B.Tech in Robotics and Automation", "BE/B.Tech", "Robotics & Automation", None, "Faculty of Engineering & Technology", "Department of Robotics & Automation", 4, 1),
                ("PROG-COL008-UG-MECH", "COL008", "undergraduate", "B.Tech in Mechanical Engineering", "BE/B.Tech", "Mechanical Engineering", None, "Faculty of Engineering & Technology", "Department of Mechanical Engineering", 4, 1),
                ("PROG-COL008-PG-AI", "COL008", "postgraduate", "M.Tech in Artificial Intelligence & Data Science", "MTech", "Artificial Intelligence", None, "Faculty of Engineering & Technology", "Department of Computer Science & Engineering", 2, 1),
                # Management - PG
                ("PROG-COL008-PG-MBA", "COL008", "postgraduate", "Master of Business Administration (MBA - Tech)", "MBA", "Technology Management", None, "Faculty of Commerce & Management", "Department of Business Administration", 2, 1),
                # Research - Doctoral
                ("PROG-COL008-DOC-ENG", "COL008", "doctoral", "Ph.D. in Advanced Manufacturing and Robotics", "PhD", "Manufacturing & Robotics", None, "Faculty of Research & Advanced Studies", "Centre for Doctoral Studies & Research", 3, 1),
            ],
            "sections": [
                ("SEC-COL008-CSE-Y1-A", "COL008", "PROG-COL008-UG-CSE", "2026-27", 1, 1, "A", 70, 58),
                ("SEC-COL008-CSE-Y1-B", "COL008", "PROG-COL008-UG-CSE", "2026-27", 1, 1, "B", 70, 56),
                ("SEC-COL008-CSE-Y2-A", "COL008", "PROG-COL008-UG-CSE", "2026-27", 2, 3, "A", 68, 55),
                ("SEC-COL008-ROB-Y1-A", "COL008", "PROG-COL008-UG-ROB", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL008-MECH-Y1-A", "COL008", "PROG-COL008-UG-MECH", "2026-27", 1, 1, "A", 65, 50),
                ("SEC-COL008-PGAI-Y1", "COL008", "PROG-COL008-PG-AI", "2026-27", 1, 1, "A", 30, 22),
                ("SEC-COL008-MBA-Y1", "COL008", "PROG-COL008-PG-MBA", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL008-DOC-Y1", "COL008", "PROG-COL008-DOC-ENG", "2026-27", 1, 1, "Research", 15, 9),
            ]
        },
        {
            "id": "COL009",
            "name": "University of Mysore (Manasagangotri)",
            "school_type": "University",
            "category": "Universities",
            "affiliation": "Public State University (Established 1916, UGC Act 12B Recognized)",
            "recognition": "First University in Karnataka (Est. 1916), NAAC A Grade, UGC Centre of Excellence",
            "divisions": [
                ("DIV_UOM_ARTS", "COL009", "Faculty of Arts & Humanities", "Humanities & Social Sciences Wing", "Manasagangotri Main Campus, Mysuru", "Prof. K. S. Rangappa (Dean, Arts)", "0821-2419301", "dean.arts@uni-mysore.ac.in", "Heritage Manuscript Library, Epigraphy Center, Folklore Museum", "Historic faculty offering foundational UG and PG liberal arts curricula.", 1),
                ("DIV_UOM_SCI", "COL009", "Faculty of Science", "Science & Technology Complex", "Manasagangotri Campus, Mysuru", "Prof. C. S. Ananda Kumar (Dean, Science)", "0821-2419302", "dean.science@uni-mysore.ac.in", "National Center for Raman Spectroscopy, High-field NMR Facility", "Premier science faculty with DST-FIST & DBT funded research labs.", 2),
                ("DIV_UOM_COM", "COL009", "Faculty of Commerce & Management", "Bahadur Institute of Management Sciences", "Manasagangotri Campus, Mysuru", "Prof. H. Rajashekar (Dean, Commerce)", "0821-2419303", "dean.commerce@uni-mysore.ac.in", "Financial Analytics Lab, Management Research Library", "State pioneer in collegiate commerce education, MBA, and doctoral research.", 3),
                ("DIV_UOM_RES", "COL009", "Faculty of Research & Advanced Studies", "Directorate of Research", "Manasagangotri Campus, Mysuru", "Prof. G. Hemantha Kumar (Director, Research)", "0821-2419304", "research@uni-mysore.ac.in", "Central Research Facility, IPR Cell, Technology Transfer Wing", "Apex university research board overseeing Ph.D. registrations and defence.", 4),
            ],
            "programs": [
                # Arts - UG, PG
                ("PROG-COL009-BA-ECON", "COL009", "undergraduate", "Bachelor of Arts in Economics & Public Policy", "BA", "Economics", None, "Faculty of Arts & Humanities", "Department of Economics", 3, 1),
                ("PROG-COL009-PG-ECON", "COL009", "postgraduate", "Master of Arts in Economics", "MA", "Economics", None, "Faculty of Arts & Humanities", "Department of Economics", 2, 1),
                ("PROG-COL009-BA-HIST", "COL009", "undergraduate", "Bachelor of Arts in History & Archaeology", "BA", "History", None, "Faculty of Arts & Humanities", "Department of History & Archaeology", 3, 1),
                ("PROG-COL009-BA-POLS", "COL009", "undergraduate", "Bachelor of Arts in Political Science & Governance", "BA", "Political Science", None, "Faculty of Arts & Humanities", "Department of Political Science & Governance", 3, 1),
                # Science - UG, PG
                ("PROG-COL009-BSC", "COL009", "undergraduate", "Bachelor of Science in Physics, Maths & Electronics", "BSc", "Physical Sciences", None, "Faculty of Science", "Department of Studies in Physics & Electronics", 3, 1),
                ("PROG-COL009-PG-PHYS", "COL009", "postgraduate", "Master of Science in Physics & Quantum Materials", "MSc", "Physics", None, "Faculty of Science", "Department of Studies in Physics & Electronics", 2, 1),
                ("PROG-COL009-BCA", "COL009", "undergraduate", "Bachelor of Computer Applications (BCA)", "BCA", "Computer Applications", None, "Faculty of Science", "Department of Computer Science", 3, 1),
                ("PROG-COL009-PG-MSC", "COL009", "postgraduate", "Master of Science in Computer Science", "MSc", "Computer Science", None, "Faculty of Science", "Department of Computer Science", 2, 1),
                ("PROG-COL009-BPHARM", "COL009", "undergraduate", "Bachelor of Pharmacy (B.Pharm)", "BPharm", "Pharmacy", None, "Faculty of Science", "Department of Pharmacy & Pharmaceutical Chemistry", 4, 1),
                # Commerce - UG, PG
                ("PROG-COL009-BCOM", "COL009", "undergraduate", "Bachelor of Commerce (Honours)", "BCom", "Commerce", None, "Faculty of Commerce & Management", "Department of Studies in Commerce", 3, 1),
                ("PROG-COL009-PG-MCOM", "COL009", "postgraduate", "Master of Commerce (M.Com)", "MCom", "Commerce", None, "Faculty of Commerce & Management", "Department of Studies in Commerce", 2, 1),
                ("PROG-COL009-BBA", "COL009", "undergraduate", "Bachelor of Business Administration (BBA)", "BBA", "Business Administration", None, "Faculty of Commerce & Management", "Department of Business Administration (BIMS)", 3, 1),
                ("PROG-COL009-PG-MBA", "COL009", "postgraduate", "Master of Business Administration (MBA)", "MBA", "Business Administration", None, "Faculty of Commerce & Management", "Department of Business Administration (BIMS)", 2, 1),
                # Research - Doctoral
                ("PROG-COL009-DOC-SCI", "COL009", "doctoral", "Ph.D. in Sciences & Interdisciplinary Research", "PhD", "Science Research", None, "Faculty of Research & Advanced Studies", "Directorate of Research (Manasagangotri)", 3, 1),
                ("PROG-COL009-DOC-HUM", "COL009", "doctoral", "Ph.D. in Humanities, Social Sciences & Languages", "PhD", "Humanities Research", None, "Faculty of Research & Advanced Studies", "Directorate of Research (Manasagangotri)", 3, 1),
            ],
            "sections": [
                ("SEC-COL009-BAEC-Y1-A", "COL009", "PROG-COL009-BA-ECON", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL009-BAEC-Y2-A", "COL009", "PROG-COL009-BA-ECON", "2026-27", 2, 3, "A", 60, 50),
                ("SEC-COL009-MAEC-Y1", "COL009", "PROG-COL009-PG-ECON", "2026-27", 1, 1, "A", 35, 26),
                ("SEC-COL009-BAHI-Y1-A", "COL009", "PROG-COL009-BA-HIST", "2026-27", 1, 1, "A", 55, 42),
                ("SEC-COL009-BAPO-Y1-A", "COL009", "PROG-COL009-BA-POLS", "2026-27", 1, 1, "A", 55, 44),
                ("SEC-COL009-BSC-Y1-A", "COL009", "PROG-COL009-BSC", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL009-MSCPH-Y1", "COL009", "PROG-COL009-PG-PHYS", "2026-27", 1, 1, "A", 30, 24),
                ("SEC-COL009-BCA-Y1-A", "COL009", "PROG-COL009-BCA", "2026-27", 1, 1, "A", 60, 50),
                ("SEC-COL009-MSCCS-Y1", "COL009", "PROG-COL009-PG-MSC", "2026-27", 1, 1, "A", 30, 22),
                ("SEC-COL009-BPH-Y1-A", "COL009", "PROG-COL009-BPHARM", "2026-27", 1, 1, "A", 50, 40),
                ("SEC-COL009-BCOM-Y1-A", "COL009", "PROG-COL009-BCOM", "2026-27", 1, 1, "A", 70, 60),
                ("SEC-COL009-MCOM-Y1", "COL009", "PROG-COL009-PG-MCOM", "2026-27", 1, 1, "A", 40, 32),
                ("SEC-COL009-BBA-Y1-A", "COL009", "PROG-COL009-BBA", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL009-MBA-Y1", "COL009", "PROG-COL009-PG-MBA", "2026-27", 1, 1, "A", 60, 52),
                ("SEC-COL009-DOCSCI-Y1", "COL009", "PROG-COL009-DOC-SCI", "2026-27", 1, 1, "Research", 15, 10),
                ("SEC-COL009-DOCHUM-Y1", "COL009", "PROG-COL009-DOC-HUM", "2026-27", 1, 1, "Research", 15, 8),
            ]
        },
        {
            "id": "COL010",
            "name": "Visvesvaraya Technological University (VTU)",
            "school_type": "University",
            "category": "Universities",
            "affiliation": "State Apex Technological University (Affiliates 200+ Engineering Colleges across Karnataka)",
            "recognition": "Established under VTU Act 1994, Karnataka State Apex Technological University, UGC Act 12B Recognized, AICTE Approved",
            "divisions": [
                ("DIV_VTU_ENG", "COL010", "Faculty of Engineering & Technology", "School of Computing & Engineering Sciences", "Jnana Sangama Campus, Belagavi", "Dr. B. E. Rangaswamy (Dean, Engineering)", "0831-2498100", "dean.engg@vtu.ac.in", "National Center for High-Performance Computing, Autonomous Vehicle Lab, 3D Nano-Additive Lab", "Apex technological division running advanced university constituent programs and research.", 1),
                ("DIV_VTU_SCI", "COL010", "Faculty of Science", "School of Basic Sciences & Applied Mathematics", "Jnana Sangama Campus, Belagavi", "Dr. T. N. Sreenivasa (Dean, Science)", "0831-2498101", "dean.science@vtu.ac.in", "Applied Mathematical Modeling Cell, Material Characterization Lab", "Basic science and computational research faculty for postgraduate and Ph.D. scholars.", 2),
                ("DIV_VTU_MGT", "COL010", "Faculty of Commerce & Management", "Department of Management & Computer Applications", "VTU Regional Center, Muddenahalli / Belagavi", "Dr. A. S. Deshpande (Dean, Management)", "0831-2498102", "dean.mgmt@vtu.ac.in", "Digital Enterprise Architecture Lab, Business Simulation Suites", "Postgraduate management and computer applications school offering MBA and MCA.", 3),
                ("DIV_VTU_RES", "COL010", "Faculty of Research & Advanced Studies", "Centre for Post-Graduate Studies & Doctoral Research", "VTU Headquarters, Jnana Sangama, Belagavi", "Dr. Rangaswamy (Director, Research)", "0831-2498103", "research@vtu.ac.in", "State Apex Doctoral Directorate granting Ph.D. & M.Sc. (Engg.) degrees", "Coordinates and awards Ph.D. degrees across engineering faculties and research centers.", 4),
            ],
            "programs": [
                # Engineering - UG, PG
                ("PROG-COL010-UG-01", "COL010", "undergraduate", "B.Tech in Computer Science and Engineering", "BE/B.Tech", "Computer Science & Engineering", None, "Faculty of Engineering & Technology", "Department of Computer Science & Engineering", 4, 1),
                ("PROG-COL010-UG-02", "COL010", "undergraduate", "B.Tech in Electronics and Communication Engineering", "BE/B.Tech", "Electronics & Communication", None, "Faculty of Engineering & Technology", "Department of Electronics & Communication", 4, 1),
                ("PROG-COL010-UG-MECH", "COL010", "undergraduate", "B.Tech in Mechanical & Smart Manufacturing", "BE/B.Tech", "Mechanical & Smart Systems", None, "Faculty of Engineering & Technology", "Department of Mechanical Engineering", 4, 1),
                ("PROG-COL010-PG-CSE", "COL010", "postgraduate", "M.Tech in Computer Science and Engineering", "MTech", "Computer Science", None, "Faculty of Engineering & Technology", "Department of Computer Science & Engineering", 2, 1),
                ("PROG-COL010-PG-VLSI", "COL010", "postgraduate", "M.Tech in VLSI Design & Embedded Systems", "MTech", "VLSI & Embedded Systems", None, "Faculty of Engineering & Technology", "Department of Electronics & Communication", 2, 1),
                # Science - PG
                ("PROG-COL010-PG-MATH", "COL010", "postgraduate", "M.Sc. in Applied Mathematics & Scientific Computing", "MSc", "Applied Mathematics", None, "Faculty of Science", "Department of Applied Mathematics & Computing", 2, 1),
                # Management & CS - PG
                ("PROG-COL010-PG-MBA", "COL010", "postgraduate", "Master of Business Administration (MBA)", "MBA", "Business Management", None, "Faculty of Commerce & Management", "Department of Management Studies", 2, 1),
                ("PROG-COL010-PG-MCA", "COL010", "postgraduate", "Master of Computer Applications (MCA)", "MCA", "Computer Applications", None, "Faculty of Commerce & Management", "Department of Computer Applications", 2, 1),
                # Research - Doctoral
                ("PROG-COL010-DOC-ENG", "COL010", "doctoral", "Ph.D. in Engineering & Technological Sciences", "PhD", "Engineering Research", None, "Faculty of Research & Advanced Studies", "Centre for Post-Graduate Studies & Doctoral Research", 3, 1),
                ("PROG-COL010-DOC-APP", "COL010", "doctoral", "Ph.D. in Computer Applications & Management", "PhD", "Interdisciplinary Research", None, "Faculty of Research & Advanced Studies", "Centre for Post-Graduate Studies & Doctoral Research", 3, 1),
            ],
            "sections": [
                ("SEC-COL010-CSE-Y1-A", "COL010", "PROG-COL010-UG-01", "2026-27", 1, 1, "A", 70, 56),
                ("SEC-COL010-CSE-Y1-B", "COL010", "PROG-COL010-UG-01", "2026-27", 1, 1, "B", 70, 58),
                ("SEC-COL010-CSE-Y2-A", "COL010", "PROG-COL010-UG-01", "2026-27", 2, 3, "A", 68, 55),
                ("SEC-COL010-ECE-Y1-A", "COL010", "PROG-COL010-UG-02", "2026-27", 1, 1, "A", 65, 52),
                ("SEC-COL010-ECE-Y2-A", "COL010", "PROG-COL010-UG-02", "2026-27", 2, 3, "A", 65, 54),
                ("SEC-COL010-MECH-Y1-A", "COL010", "PROG-COL010-UG-MECH", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL010-PGCSE-Y1", "COL010", "PROG-COL010-PG-CSE", "2026-27", 1, 1, "A", 30, 22),
                ("SEC-COL010-PGVLSI-Y1", "COL010", "PROG-COL010-PG-VLSI", "2026-27", 1, 1, "A", 30, 21),
                ("SEC-COL010-PGMATH-Y1", "COL010", "PROG-COL010-PG-MATH", "2026-27", 1, 1, "A", 30, 20),
                ("SEC-COL010-MBA-Y1", "COL010", "PROG-COL010-PG-MBA", "2026-27", 1, 1, "A", 60, 50),
                ("SEC-COL010-MCA-Y1", "COL010", "PROG-COL010-PG-MCA", "2026-27", 1, 1, "A", 60, 48),
                ("SEC-COL010-DOCENG-Y1", "COL010", "PROG-COL010-DOC-ENG", "2026-27", 1, 1, "Research", 15, 9),
                ("SEC-COL010-DOCAPP-Y1", "COL010", "PROG-COL010-DOC-APP", "2026-27", 1, 1, "Research", 15, 8),
            ]
        }
    ]

    for u in universities:
        c.execute("""
            UPDATE schools
            SET school_type = ?, category = ?, affiliation = ?, recognition = ?
            WHERE school_id = ?
        """, (u["school_type"], u["category"], u["affiliation"], u["recognition"], u["id"]))

        # Remove existing sections for this university
        c.execute("DELETE FROM program_sections WHERE institution_id = ?", (u["id"],))

        # Remove existing programs for this university
        c.execute("DELETE FROM academic_programs WHERE institution_id = ?", (u["id"],))

        # Re-register divisions
        c.execute("DELETE FROM institution_divisions WHERE parent_institution_id = ?", (u["id"],))
        for div in u["divisions"]:
            c.execute("""
                INSERT INTO institution_divisions (
                    division_id, parent_institution_id, division_name, division_type,
                    campus_location, head_of_division, contact_phone, contact_email,
                    facilities_summary, description, display_order
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, div)

        # Insert programs
        for prog in u["programs"]:
            c.execute("""
                INSERT INTO academic_programs (
                    program_id, institution_id, education_level, program_name, degree_type,
                    discipline_or_stream, combination_code, faculty_name, department_name,
                    duration_years, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, prog)

        # Insert sections
        for sec in u["sections"]:
            c.execute("""
                INSERT INTO program_sections (
                    section_id, institution_id, program_id, academic_year,
                    term_or_year, semester, section_name, capacity, current_strength
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sec)

    print("[+] 5 Universities configured successfully with hierarchical academic structure.")

    # Re-enable foreign keys and verify integrity
    conn.execute("PRAGMA foreign_keys = ON;")
    
    print("[*] Running PRAGMA foreign_key_check...")
    fk_violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
    if fk_violations:
        print("[!] Foreign key violations found:", fk_violations)
        raise RuntimeError("Foreign key check failed!")
    else:
        print("[+] Foreign key check passed: 0 violations.")

    print("[*] Running PRAGMA integrity_check...")
    integrity = conn.execute("PRAGMA integrity_check;").fetchone()
    if integrity[0] != "ok":
        print("[!] Integrity check failed:", integrity[0])
        raise RuntimeError("Integrity check failed!")
    else:
        print("[+] Database integrity check passed: ok.")

    # Check totals
    students_count = conn.execute("SELECT count(*) FROM students").fetchone()[0]
    enrollments_count = conn.execute("SELECT count(*) FROM enrollments").fetchone()[0]
    schools_count = conn.execute("SELECT count(*) FROM schools").fetchone()[0]
    colleges_count = conn.execute("SELECT count(*) FROM schools WHERE category = 'Degree Colleges'").fetchone()[0]
    univs_count = conn.execute("SELECT count(*) FROM schools WHERE category = 'Universities'").fetchone()[0]
    pu_count = conn.execute("SELECT count(*) FROM schools WHERE category = 'PU Colleges (11-12)'").fetchone()[0]
    sch_count = conn.execute("SELECT count(*) FROM schools WHERE category = 'Schools (K-10)'").fetchone()[0]

    print(f"[+] Total students: {students_count} (Expected 30001)")
    print(f"[+] Total enrollments: {enrollments_count} (Expected 30001)")
    print(f"[+] Total active institutions: {schools_count} (Expected 30)")
    print(f"    - Schools (K-10): {sch_count} (Expected 15)")
    print(f"    - PU Colleges (11-12): {pu_count} (Expected 5)")
    print(f"    - Degree Colleges: {colleges_count} (Expected 5)")
    print(f"    - Universities: {univs_count} (Expected 5)")

    conn.commit()
    conn.close()
    print("[+] Migration completed and committed successfully!")

if __name__ == "__main__":
    main()
