import sqlite3
import csv
import os

DB_PATH = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
PU_CSV_PATH = r'C:\Users\callm\nagriksetu\flagged_pu_students_review.csv'
SCHOOL_CSV_PATH = r'C:\Users\callm\nagriksetu\flagged_school_students_review.csv'

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# District to candidate institution mapping for evidence/reference
DISTRICT_SCHOOL_MAP = {
    'Tumakuru': ('SCH009', 'Saraswati Vidya Kendra'),
    'Mysuru': ('SCH002', 'Shanti Vidya Mandir'),
    'Mandya': ('SCH013', 'Mandya Government Pre-University College'), # No separate school in Mandya
    'Hassan': ('SCH014', 'Hassan Valley Pre-University College'),    # No separate school in Hassan
    'Udupi': ('SCH008', 'Vivekananda School')
}

DISTRICT_PU_MAP = {
    'Belagavi': ('SCH015', 'Udupi / Belagavi PU College Network'),
    'Dharwad': ('COL008', 'Dharwad Higher Education Network'),
    'Shivamogga': ('SCH007', 'Shivamogga Model Secondary Network'),
    'Ballari': ('SCH006', 'Ballari Education Network'),
    'Kalaburagi': ('SCH010', 'Kalaburagi Secondary Network')
}

print("=== Generating flagged_pu_students_review.csv ===")
cur.execute("""
    SELECT 
        s.student_id,
        s.permanent_student_id,
        s.student_name,
        s.school_id,
        sc.school_name,
        sc.school_type,
        sc.district,
        s.standard,
        s.section,
        s.age,
        s.review_flag
    FROM students s
    JOIN schools sc ON s.school_id = sc.school_id
    WHERE s.school_id BETWEEN 'SCH011' AND 'SCH015'
      AND s.review_flag = 'FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS'
    ORDER BY s.school_id, s.standard, s.section, s.student_id
""")
pu_rows = cur.fetchall()

with open(PU_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "Student ID",
        "Permanent Student ID",
        "Student Name",
        "Current Institution ID",
        "Current Institution Name",
        "Current Institution Type",
        "Current Standard / Year",
        "Proposed Institution ID or Classification, where supported by evidence",
        "Reason for Flag",
        "Evidence Source"
    ])
    
    for r in pu_rows:
        std = r["standard"]
        dist = r["district"]
        candidate_school_id, candidate_school_name = DISTRICT_SCHOOL_MAP.get(dist, ("UNKNOWN", "District School"))
        
        # Rigorous evidence-backed proposed classification
        proposed_class = f"Standard {std} (Primary/Secondary, Age {r['age']}) - Administrative Review Required (Retain via Composite Institution Policy OR Transfer to District School e.g. {candidate_school_id} {candidate_school_name})"
        
        reason = f"Student enrolled in Standard {std} (Age {r['age']}) within Pre-University College ({r['school_name']}) which statutorily only admits Standards 11-12 (PUC 1st & 2nd Year)."
        evidence = f"nagriksetu.db:students.standard={std}, schools.school_type='PU College', academic_programs=PUC only; expand_dataset.py lines 105-130 uniform 12-standard generation artifact."
        
        writer.writerow([
            r["student_id"],
            r["permanent_student_id"],
            r["student_name"],
            r["school_id"],
            r["school_name"],
            r["school_type"],
            f"Standard {std}",
            proposed_class,
            reason,
            evidence
        ])

print(f"Wrote {len(pu_rows)} rows to {PU_CSV_PATH}")

print("=== Generating flagged_school_students_review.csv ===")
cur.execute("""
    SELECT 
        s.student_id,
        s.permanent_student_id,
        s.student_name,
        s.school_id,
        sc.school_name,
        sc.school_type,
        sc.district,
        s.standard,
        s.section,
        s.age,
        s.review_flag
    FROM students s
    JOIN schools sc ON s.school_id = sc.school_id
    WHERE s.school_id BETWEEN 'SCH016' AND 'SCH020'
      AND s.review_flag = 'FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS'
    ORDER BY s.school_id, s.standard, s.section, s.student_id
""")
school_rows = cur.fetchall()

with open(SCHOOL_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "Student ID",
        "Permanent Student ID",
        "Student Name",
        "Current Institution ID",
        "Current Institution Name",
        "Current Institution Type",
        "Current Standard / Year",
        "Proposed Institution ID or Classification, where supported by evidence",
        "Reason for Flag",
        "Evidence Source"
    ])
    
    for r in school_rows:
        std = r["standard"]
        dist = r["district"]
        puc_term = "1st PUC" if std == 11 else "2nd PUC"
        
        proposed_class = f"Standard {std} ({puc_term}, Higher Secondary, Age {r['age']}) - Administrative Review Required (Upgrade school to Composite Senior Secondary OR Transfer to District PU College)"
        
        reason = f"Student enrolled in Standard {std} ({puc_term}, Age {r['age']}) within K-10 School ({r['school_name']}) which statutorily only admits Standards 1-10 (KSEEB School Curriculum)."
        evidence = f"nagriksetu.db:students.standard={std}, schools.school_type='School', academic_programs=PROG-{r['school_id']}-K10 only; expand_dataset.py lines 105-130 uniform 12-standard generation artifact."
        
        writer.writerow([
            r["student_id"],
            r["permanent_student_id"],
            r["student_name"],
            r["school_id"],
            r["school_name"],
            r["school_type"],
            f"Standard {std}",
            proposed_class,
            reason,
            evidence
        ])

print(f"Wrote {len(school_rows)} rows to {SCHOOL_CSV_PATH}")

conn.close()
