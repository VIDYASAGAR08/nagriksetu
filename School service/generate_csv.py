import sqlite3
import csv
import os
import sys

DB_PATH = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
CSV_PATH = r'C:\Users\callm\nagriksetu\NagrikSetu_Complete_Student_Institution_Mapping.csv'

print(f"Connecting to database: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Query all students joined with schools, enrollments, and academic_programs
# Sorting deterministically by school_id, standard, section, student_id
query = """
SELECT 
    s.student_id,
    s.permanent_student_id,
    s.student_name,
    s.school_id,
    sc.school_name,
    sc.school_type,
    sc.category,
    s.standard,
    s.section,
    e.stream,
    e.subject_combination,
    e.academic_year,
    e.enrollment_status,
    ap.program_name,
    ap.discipline_or_stream,
    ap.department_name
FROM students s
LEFT JOIN schools sc ON s.school_id = sc.school_id
LEFT JOIN enrollments e ON s.permanent_student_id = e.permanent_student_id
LEFT JOIN academic_programs ap ON s.school_id = ap.institution_id
GROUP BY s.permanent_student_id
ORDER BY s.school_id, s.standard, s.section, s.student_id
"""

cur.execute(query)
rows = cur.fetchall()

print(f"Total student records retrieved from query: {len(rows)}")

headers = [
    "Serial Number",
    "Student ID",
    "Permanent Student ID",
    "Student Full Name",
    "Institution ID",
    "Institution Name",
    "Institution Type",
    "Standard / Class",
    "Section",
    "Stream",
    "Programme",
    "Department",
    "Academic Year",
    "Semester / Year",
    "Enrollment Status"
]

with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    
    for idx, r in enumerate(rows, start=1):
        # Format values cleanly
        sid = r["student_id"] or "Not Available"
        psid = r["permanent_student_id"] or "Not Available"
        name = r["student_name"] or "Not Available"
        inst_id = r["school_id"] or "Not Available"
        inst_name = r["school_name"] or "Not Available"
        inst_type = r["school_type"] or r["category"] or "Not Available"
        std = f"Standard {r['standard']}" if r["standard"] is not None else "Not Available"
        sec = r["section"] or "Not Available"
        
        # Stream / Programme / Dept
        stream = r["stream"] or r["discipline_or_stream"] or "Not Available"
        prog = r["program_name"] or "Not Available"
        dept = r["department_name"] or "Not Available"
        
        acad_year = r["academic_year"] or "2026-2027"
        
        # Semester / Year
        if r["standard"] is not None:
            if "PU" in str(inst_type) or "College" in str(inst_type) or "University" in str(inst_type):
                sem_year = f"Year {r['standard']}"
            else:
                sem_year = "Not Applicable"
        else:
            sem_year = "Not Available"
            
        status = (r["enrollment_status"] or "active").capitalize()
        
        writer.writerow([
            idx,
            sid,
            psid,
            name,
            inst_id,
            inst_name,
            inst_type,
            std,
            sec,
            stream,
            prog,
            dept,
            acad_year,
            sem_year,
            status
        ])

print(f"Successfully generated CSV at: {CSV_PATH}")
print(f"Total rows written (including header): {len(rows) + 1}")
file_size = os.path.getsize(CSV_PATH)
print(f"CSV file size: {file_size / (1024*1024):.2f} MB")
