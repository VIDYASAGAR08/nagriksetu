"""
Comprehensive Dossier Population Script for NagrikSetu
Populates missing attendance, examination results, and documents for all remaining students
ensuring 100% coverage across all 30,003 students in nagriksetu.db.
"""

import sqlite3
import os
import hashlib
import datetime
import time

DB_PATH = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'

# Instructional attendance dates across 2026 academic term (June to November 2026)
ATTENDANCE_DATES = [
    "2026-06-15", "2026-06-22", "2026-06-29",
    "2026-07-06", "2026-07-13", "2026-07-20", "2026-07-27",
    "2026-08-03", "2026-08-10", "2026-08-17", "2026-08-24", "2026-08-31",
    "2026-09-07", "2026-09-14", "2026-09-21", "2026-09-28",
    "2026-10-05", "2026-10-12", "2026-10-19", "2026-10-26",
    "2026-11-02", "2026-11-09", "2026-11-16", "2026-11-20"
]

def run_dossier_population():
    t0 = time.time()
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = 100000")
    cur = conn.cursor()

    # Load institutions
    cur.execute("SELECT school_id, school_name, school_type, district, state FROM schools")
    schools = {r[0]: {"name": r[1], "type": r[2], "district": r[3], "state": r[4]} for r in cur.fetchall()}
    print(f"Loaded {len(schools)} institutions.")

    # Identify existing attendance, results, documents
    cur.execute("SELECT DISTINCT permanent_student_id FROM student_attendance")
    existing_attendance_psids = {r[0] for r in cur.fetchall() if r[0]}
    print(f"Students with existing attendance: {len(existing_attendance_psids)}")

    cur.execute("SELECT DISTINCT permanent_student_id FROM academic_results")
    existing_results_psids = {r[0] for r in cur.fetchall() if r[0]}
    print(f"Students with existing academic results: {len(existing_results_psids)}")

    cur.execute("SELECT DISTINCT permanent_student_id FROM student_documents")
    existing_docs_psids = {r[0] for r in cur.fetchall() if r[0]}
    print(f"Students with existing documents: {len(existing_docs_psids)}")

    # Fetch students needing population
    cur.execute("""
        SELECT s.student_id, s.student_name, s.school_id, s.standard, s.section,
               s.permanent_student_id, s.date_of_birth, s.gender, s.first_language,
               e.enrollment_id, e.program_id, e.degree, e.branch, e.department,
               e.semester, e.puc_year, e.stream, e.subject_combination, e.curriculum_or_board
        FROM students s
        LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
        ORDER BY s.school_id, s.standard, s.section, s.student_id
    """)
    all_students = cur.fetchall()
    total_count = len(all_students)
    print(f"Total students to check: {total_count}")

    attendance_batch = []
    results_batch = []
    documents_batch = []
    
    total_att_added = 0
    total_res_added = 0
    total_docs_added = 0
    
    batch_size = 2000

    for idx, row in enumerate(all_students):
        (sid, sname, sch_id, standard, section, psid, dob, gender, first_lang,
         enr_id, prog_id, degree, branch, dept, semester, puc_year, stream, subj_comb, board) = row

        if not enr_id:
            enr_id = f"ENR-{sid}"

        sch = schools.get(sch_id, {"name": "NagrikSetu Institution", "type": "School", "district": "Bengaluru Urban"})
        sch_type_lower = sch["type"].lower()

        # Deterministic seed from student permanent ID
        seed_int = int(hashlib.md5(psid.encode()).hexdigest()[:8], 16)

        # 1. Populate Attendance if missing
        if psid not in existing_attendance_psids:
            att_type = seed_int % 100
            for d_idx, att_date in enumerate(ATTENDANCE_DATES):
                day_seed = (seed_int + d_idx * 17) % 100
                if att_type < 82:
                    if day_seed < 4:
                        status = "absent"
                        remarks = "Unexcused absence recorded"
                    elif day_seed == 4:
                        status = "leave"
                        remarks = "Medical leave with parent application"
                    else:
                        status = "present"
                        remarks = "Full day regular attendance"
                elif att_type < 95:
                    if day_seed < 12:
                        status = "absent"
                        remarks = "Absent during morning roll call"
                    elif day_seed < 16:
                        status = "leave"
                        remarks = "Sanctioned leave note from guardian"
                    else:
                        status = "present"
                        remarks = "Present in all sessions"
                else:
                    if day_seed < 28:
                        status = "absent"
                        remarks = "Unexcused absence"
                    elif day_seed < 35:
                        status = "leave"
                        remarks = "Leave application on file"
                    else:
                        status = "present"
                        remarks = "Present for instructional classes"

                # Unique, non-colliding primary key based on sid + d_idx
                att_id = f"ATT-{sid}-{d_idx+1:02d}"
                attendance_batch.append((
                    att_id, sch_id, psid, "2026-2027", att_date, status,
                    "General Curriculum", remarks, "SYSTEM-ADMIN",
                    f"{att_date} 09:00:00", f"{att_date} 09:00:00"
                ))
            total_att_added += 1

        # 2. Populate Examination Results if missing
        if psid not in existing_results_psids:
            # Subject determination based on level & institution
            if "pu" in sch_type_lower and standard in (11, 12):
                comb_upper = (subj_comb or stream or "PCMB").upper()
                if "PCMB" in comb_upper:
                    subjects = ["Physics", "Chemistry", "Mathematics", "Biology", "English", "Kannada"]
                elif "PCMC" in comb_upper:
                    subjects = ["Physics", "Chemistry", "Mathematics", "Computer Science", "English", "Kannada"]
                elif "PCME" in comb_upper:
                    subjects = ["Physics", "Chemistry", "Mathematics", "Electronics", "English", "Kannada"]
                elif "HEBA" in comb_upper:
                    subjects = ["History", "Economics", "Business Studies", "Accountancy", "English", "Kannada"]
                elif "MEBA" in comb_upper:
                    subjects = ["Basic Mathematics", "Economics", "Business Studies", "Accountancy", "English", "Kannada"]
                elif "CEBA" in comb_upper:
                    subjects = ["Computer Science", "Economics", "Business Studies", "Accountancy", "English", "Kannada"]
                else:
                    subjects = ["Physics", "Chemistry", "Mathematics", "Biology", "English", "Kannada"]
            elif "degree" in sch_type_lower or "engineering" in sch_type_lower or "university" in sch_type_lower or degree:
                subjects = [
                    "Data Structures & Algorithms",
                    "Discrete Mathematical Structures",
                    "Digital Design & Computer Organization",
                    "Object Oriented Programming with Java",
                    "Database Management Systems",
                    "Constitution of India & Professional Ethics"
                ]
            else:
                # School K-10 or K-10 standards within institutions
                subjects = [
                    "Kannada (First Language)",
                    "English (Second Language)",
                    "Hindi (Third Language)",
                    "Mathematics",
                    "General Science",
                    "Social Science"
                ]

            perf_category = seed_int % 100
            for s_idx, subj in enumerate(subjects):
                subj_seed = (seed_int + s_idx * 31) % 100
                if perf_category < 75:
                    marks = 70 + (subj_seed % 28)
                elif perf_category < 95:
                    marks = 42 + (subj_seed % 28)
                else:
                    if s_idx in (2, 3):
                        marks = 22 + (subj_seed % 12)  # Fail (<35)
                    else:
                        marks = 45 + (subj_seed % 25)

                max_marks = 100
                pct = round((marks / max_marks) * 100, 1)

                if pct >= 90:
                    grade = "A+"
                elif pct >= 80:
                    grade = "A"
                elif pct >= 70:
                    grade = "B+"
                elif pct >= 60:
                    grade = "B"
                elif pct >= 50:
                    grade = "C"
                elif pct >= 35:
                    grade = "P"
                else:
                    grade = "F"

                # Unique primary key based on sid + s_idx
                res_id = f"RES-{sid}-{s_idx+1:02d}"
                results_batch.append((
                    res_id, enr_id, subj, "Midterm Examination 2026",
                    marks, max_marks, "2026-2027", "2026-10-15",
                    "2026-10-20 12:00:00", psid, "EXAM-2026-MID",
                    grade, pct, "SYSTEM-EXAM-CELL", "2026-10-20 12:00:00"
                ))
            total_res_added += 1

        # 3. Populate Student Documents if missing
        if psid not in existing_docs_psids:
            doc_types = [
                ("Birth Certificate", f"DEMO_Birth_Certificate_{sid}.pdf", "verified"),
                ("Transfer Certificate (TC)", f"DEMO_Transfer_Certificate_{sid}.pdf", "verified"),
                ("Previous Standard Marks Card", f"DEMO_Previous_MarksCard_{sid}.pdf", "verified"),
                ("Institutional Admission Undertaking", f"DEMO_Admission_Form_{sid}.pdf", "verified" if (seed_int % 10 != 0) else "pending")
            ]
            for d_idx, (doc_type, doc_fname, ver_status) in enumerate(doc_types):
                doc_id = f"DOC-{sid}-{d_idx+1:02d}"
                documents_batch.append((
                    doc_id, psid, enr_id, doc_type, doc_fname,
                    f"demo_storage/documents/{psid}/{doc_fname}",
                    "SYSTEM-ADMISSION-PORTAL", "ADMIN-VERIFIER",
                    ver_status, "2026-06-01 10:00:00"
                ))
            total_docs_added += 1

        # Execute in transactions every batch_size students
        if (idx + 1) % batch_size == 0 or (idx + 1) == total_count:
            if attendance_batch:
                print(f"[{idx+1}/{total_count}] Committing {len(attendance_batch)} attendance rows...")
                cur.executemany("""
                    INSERT OR REPLACE INTO student_attendance
                    (attendance_id, institution_id, permanent_student_id, academic_year,
                     attendance_date, status, subject_name, remarks, recorded_by_user_id,
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, attendance_batch)
                attendance_batch = []

            if results_batch:
                print(f"[{idx+1}/{total_count}] Committing {len(results_batch)} result rows...")
                cur.executemany("""
                    INSERT OR REPLACE INTO academic_results
                    (result_id, enrollment_id, subject_name, exam_name, marks_obtained,
                     maximum_marks, academic_year, exam_date, created_at, permanent_student_id,
                     exam_id, grade, percentage, recorded_by_user_id, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, results_batch)
                results_batch = []

            if documents_batch:
                print(f"[{idx+1}/{total_count}] Committing {len(documents_batch)} document rows...")
                cur.executemany("""
                    INSERT OR REPLACE INTO student_documents
                    (document_id, permanent_student_id, enrollment_id, document_type,
                     file_name, private_storage_key, uploaded_by_user_id, verified_by_user_id,
                     verification_status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, documents_batch)
                documents_batch = []

            conn.commit()

    conn.close()
    elapsed = time.time() - t0
    print(f"\nDossier population complete in {elapsed:.2f}s!")
    print(f"  Attendance added for {total_att_added} students")
    print(f"  Results added for {total_res_added} students")
    print(f"  Documents added for {total_docs_added} students")

if __name__ == "__main__":
    run_dossier_population()
