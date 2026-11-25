import sqlite3
from collections import Counter

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

print("==================================================================")
print("AUDIT & VERIFICATION OF ACADEMIC CLASSIFICATION IN DATABASE")
print("==================================================================")

# 1. Total students
c.execute("SELECT COUNT(*) FROM students")
total_students = c.fetchone()[0]
print(f"Total Student Records: {total_students}")

# 2. Total active enrollments
c.execute("SELECT COUNT(*) FROM enrollments")
total_enrollments = c.fetchone()[0]
print(f"Total Active Enrollments: {total_enrollments}")

# 3. Categorization of institutions & counts
c.execute("""
    SELECT sc.school_id, sc.school_name, sc.school_type, sc.category, COUNT(s.student_id)
    FROM schools sc
    LEFT JOIN students s ON s.school_id = sc.school_id
    GROUP BY sc.school_id
    ORDER BY sc.school_id
""")
inst_rows = c.fetchall()

def classify_institution(school_id, name, stype, category):
    stype_str = (stype or "").lower()
    cat_str = (category or "").lower()
    name_str = (name or "").lower()
    
    if "pu college" in stype_str or "pu" in cat_str or "pre-university" in name_str:
        return "PU College"
    elif "university" in stype_str or "universities" in cat_str or "university" in name_str:
        return "University"
    elif "engineering" in name_str or "technology" in name_str or "polytechnic" in name_str or "engineering" in stype_str:
        return "Engineering College"
    elif "degree" in stype_str or "degree" in cat_str or "college" in name_str:
        return "Degree College"
    else:
        return "School"

cat_inst_counts = Counter()
cat_student_counts = Counter()
for row in inst_rows:
    cat = classify_institution(row[0], row[1], row[2], row[3])
    cat_inst_counts[cat] += 1
    cat_student_counts[cat] += row[4]

print("\n--- Institution Categories & Student Counts ---")
for cat in ["School", "PU College", "Degree College", "Engineering College", "University"]:
    print(f"  {cat}s: {cat_inst_counts[cat]} institutions | {cat_student_counts[cat]} students")

# 4. PU College metrics
c.execute("SELECT COUNT(*) FROM students WHERE puc_year = '1st PUC'")
puc1_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM students WHERE puc_year = '2nd PUC'")
puc2_count = c.fetchone()[0]
print(f"\nNumber of PU students mapped to 1st PUC: {puc1_count}")
print(f"Number of PU students mapped to 2nd PUC: {puc2_count}")

# 5. PU Streams
c.execute("SELECT COUNT(*) FROM students WHERE subject_combination = 'PCMB'")
pcmb_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM students WHERE subject_combination = 'PCMC'")
pcmc_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM students WHERE subject_combination = 'PCME'")
pcme_count = c.fetchone()[0]
print(f"Number of PCMB students: {pcmb_count}")
print(f"Number of PCMC students: {pcmc_count}")
print(f"Number of PCME students: {pcme_count}")

# Commerce streams
c.execute("""
    SELECT subject_combination, COUNT(*)
    FROM students
    WHERE stream = 'Commerce'
    GROUP BY subject_combination
    ORDER BY subject_combination
""")
commerce_streams = c.fetchall()
print("\nNumber of Commerce students by stream:")
total_commerce = 0
for combo, cnt in commerce_streams:
    print(f"  {combo}: {cnt} students")
    total_commerce += cnt
print(f"Total Commerce students: {total_commerce}")

# Arts / Humanities
c.execute("SELECT COUNT(*) FROM students WHERE stream = 'Arts / Humanities'")
arts_count = c.fetchone()[0]
print(f"Total Arts / Humanities students (HEPS): {arts_count}")

# 6. Degree & Engineering Students
c.execute("""
    SELECT degree, branch, department, program_id, COUNT(*)
    FROM students
    WHERE school_id = 'COL003'
    GROUP BY degree, branch, department, program_id
""")
eng_students = c.fetchall()
print("\nEngineering College students mapped to branches:")
for r in eng_students:
    print(f"  Degree: {r[0]} | Branch: {r[1]} | Dept: {r[2]} | Prog: {r[3]} | Count: {r[4]}")

# 7. Flagged for review
c.execute("SELECT review_flag, COUNT(*) FROM students WHERE review_flag IS NOT NULL GROUP BY review_flag")
flagged_rows = c.fetchall()
total_flagged = sum(r[1] for r in flagged_rows)
print(f"\nNumber of records flagged for manual review: {total_flagged}")
for r in flagged_rows:
    print(f"  - {r[0]}: {r[1]} records")

# 8. Check for any incorrectly classified or unassigned records
c.execute("""
    SELECT COUNT(*) FROM students
    WHERE (school_id IN ('SCH001','SCH002','SCH003','SCH004','SCH005','SCH006','SCH007','SCH008','SCH009','SCH010') AND stream IS NULL)
       OR (school_id = 'COL003' AND branch IS NULL)
       OR (school_id IN ('SCH011','SCH012','SCH013','SCH014','SCH015') AND standard IN (11,12) AND puc_year IS NULL)
       OR (school_id IN ('SCH011','SCH012','SCH013','SCH014','SCH015') AND standard IN (11,12) AND subject_combination IS NULL)
""")
incorrect_count = c.fetchone()[0]
print(f"\nNumber of incorrectly classified records remaining: {incorrect_count}")

conn.close()
