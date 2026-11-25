import csv
import sqlite3
from collections import defaultdict, Counter

print("=== DEEP AUDIT OF NAGRIKSETU ACADEMIC CLASSIFICATION ===")

# 1. Inspect student_id_restructuring_mapping.csv
print("\n--- Inspecting student_id_restructuring_mapping.csv ---")
with open('data/student_id_restructuring_mapping.csv', 'r', encoding='utf-8') as f:
    r = csv.DictReader(f)
    csv_rows = list(r)

print(f"Total rows in student_id_restructuring_mapping.csv: {len(csv_rows)}")

by_inst = defaultdict(lambda: defaultdict(int))
by_type_prog = defaultdict(lambda: defaultdict(int))
for row in csv_rows:
    inst_id = row['Institution ID']
    inst_type = row['Institution Type']
    prog = row['Academic Programme / Stream']
    std = row['Class / Standard']
    by_inst[inst_id][(inst_type, prog, std)] += 1
    by_type_prog[inst_type][prog] += 1

print("\nStudent ID restructuring mapping summary by Institution Type & Programs:")
for itype, progs in by_type_prog.items():
    print(f"\nInstitution Type: {itype}")
    for prog, cnt in sorted(progs.items()):
        print(f"  {prog}: {cnt} students")

# 2. Inspect NagrikSetu_Complete_Student_Institution_Mapping.csv
print("\n--- Inspecting NagrikSetu_Complete_Student_Institution_Mapping.csv ---")
with open('data/NagrikSetu_Complete_Student_Institution_Mapping.csv', 'r', encoding='utf-8') as f:
    r = csv.DictReader(f)
    comp_rows = list(r)

print(f"Total rows in Complete Mapping CSV: {len(comp_rows)}")

comp_by_type_prog = defaultdict(lambda: defaultdict(int))
comp_by_inst_std_sem = defaultdict(lambda: Counter())

for row in comp_rows:
    itype = row['Institution Type']
    inst_id = row['Institution ID']
    prog = row['Programme']
    stream = row['Stream']
    dept = row['Department']
    std = row['Standard / Class']
    sem = row['Semester / Year']
    comp_by_type_prog[itype][(prog, stream, dept)] += 1
    comp_by_inst_std_sem[inst_id][(std, sem)] += 1

for itype, progs in comp_by_type_prog.items():
    print(f"\nInstitution Type: {itype}")
    for (prog, stream, dept), cnt in sorted(progs.items()):
        print(f"  Prog: {prog} | Stream: {stream} | Dept: {dept} -> {cnt} students")

# 3. Check what institutions have students in the database
conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

c.execute("""
    SELECT sc.school_id, sc.school_name, sc.school_type, sc.category, COUNT(s.student_id)
    FROM schools sc
    LEFT JOIN students s ON sc.school_id = s.school_id
    GROUP BY sc.school_id
    ORDER BY sc.school_id
""")
print("\n--- Current Live Database: Students per School ---")
for r in c.fetchall():
    print(f"  {r[0]} | {r[1]} | Type: {r[2]} | Cat: {r[3]} | Count: {r[4]}")

# 4. Check academic_programs in live database for all institutions
print("\n--- Academic Programs in Live Database ---")
c.execute("""
    SELECT institution_id, program_id, program_name, degree_type, discipline_or_stream, combination_code, department_name, faculty_name, duration_years
    FROM academic_programs
    ORDER BY institution_id, program_id
""")
ap_list = c.fetchall()
print(f"Total academic_programs: {len(ap_list)}")
for r in ap_list[:30]:
    print(f"  {r[0]} | {r[1]} | {r[2]} | Deg: {r[3]} | Stream: {r[4]} | Code: {r[5]} | Dept: {r[6]} | Dur: {r[8]}")

conn.close()
