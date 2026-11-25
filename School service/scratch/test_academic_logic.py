import sqlite3
import re

# Read classify_institution_tier and build_institution_academic_details source directly from main.py
with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract classify_institution_tier and build_institution_academic_details definitions
c_match = re.search(r'(def classify_institution_tier\(.*?\n\ndef build_institution_academic_details\(.*?\n\nclass VerifyAndLinkChildPayload)', content, re.DOTALL)
if not c_match:
    # Alternative boundary
    c_match = re.search(r'(def classify_institution_tier\(.*?\n\ndef build_institution_academic_details\(.*?\n\n(?:class |def |@app))', content, re.DOTALL)

# Let's extract between line 3408 and 3590
lines = content.splitlines()
func_lines = []
capturing = False
for line in lines:
    if line.startswith("def classify_institution_tier"):
        capturing = True
    elif line.startswith("@app.") and capturing:
        break
    if capturing:
        func_lines.append(line)

funcs_code = "\n".join(func_lines)
local_ns = {}
exec(funcs_code, {}, local_ns)

classify_institution_tier = local_ns["classify_institution_tier"]
build_institution_academic_details = local_ns["build_institution_academic_details"]

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

test_cases = [
    ("SCH011 (was flagged Std 1)", "SELECT s.*, sc.school_name, sc.school_type, sc.category FROM students s JOIN schools sc ON sc.school_id = s.school_id WHERE s.school_id = 'SCH011' AND s.standard = 1 LIMIT 1"),
    ("SCH011 (genuine PU Std 11)", "SELECT s.*, sc.school_name, sc.school_type, sc.category FROM students s JOIN schools sc ON sc.school_id = s.school_id WHERE s.school_id = 'SCH011' AND s.standard = 11 LIMIT 1"),
    ("SCH016 (was flagged Std 11)", "SELECT s.*, sc.school_name, sc.school_type, sc.category FROM students s JOIN schools sc ON sc.school_id = s.school_id WHERE s.school_id = 'SCH016' AND s.standard = 11 LIMIT 1"),
    ("SCH016 (genuine School Std 1)", "SELECT s.*, sc.school_name, sc.school_type, sc.category FROM students s JOIN schools sc ON sc.school_id = s.school_id WHERE s.school_id = 'SCH016' AND s.standard = 1 LIMIT 1"),
    ("COL003 (Engineering)", "SELECT s.*, sc.school_name, sc.school_type, sc.category FROM students s JOIN schools sc ON sc.school_id = s.school_id WHERE s.school_id = 'COL003' LIMIT 1"),
]

for label, sql in test_cases:
    cur.execute(sql)
    r = dict(cur.fetchone())
    cur.execute("SELECT * FROM enrollments WHERE permanent_student_id = ?", (r["permanent_student_id"],))
    e = dict(cur.fetchone())
    
    tier = classify_institution_tier(r["school_id"], r["school_name"], r["school_type"], r["category"])
    acad = build_institution_academic_details(tier, r, e, r)
    
    print(f"\n--- {label} ---")
    print(f"Institution: {r['school_name']} ({r['school_id']}) | Type: {r['school_type']}")
    print(f"Class: {acad.get('class_or_standard')} | Division: {acad.get('academic_division')}")
    print(f"Tier: {acad.get('institution_tier')} | Board: {acad.get('board')}")
    print(f"Program: {acad.get('programme')} | Combination: {acad.get('subject_combination')}")
    print(f"Review Flag: {acad.get('review_flag')}")
    assert acad.get('review_flag') is None, f"Expected None review_flag but got: {acad.get('review_flag')}"

conn.close()
print("\n[✓] ALL CLASSIFICATION LOGIC CHECKS PASSED PERFECTLY!")
