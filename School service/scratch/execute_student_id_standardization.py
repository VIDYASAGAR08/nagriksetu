import sqlite3
import re
import os

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
BACKUP_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db.bak_studentid_migration"

if not os.path.exists(BACKUP_PATH):
    raise RuntimeError(f"Backup file does not exist at {BACKUP_PATH}!")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

def get_institution_5char_prefix(school_id: str) -> str:
    m = re.match(r"^([A-Z]+)(\d+)$", school_id)
    if m:
        letters, num = m.groups()
        return f"{letters}{int(num):02d}"
    return school_id

def get_name_sort_key(name):
    clean = (name or "").strip()
    parts = clean.split()
    first_name = parts[0].lower() if parts else ""
    full_name = clean.lower()
    return (first_name, full_name)

print("Starting transaction for Standardized Student ID Migration...")
c.execute("BEGIN TRANSACTION")

schools = c.execute("SELECT school_id, school_name, school_type FROM schools ORDER BY school_id").fetchall()

total_migrated = 0
institution_stats = []

for s_id, s_name, s_type in schools:
    prefix = get_institution_5char_prefix(s_id)
    students = c.execute(
        "SELECT student_id, student_name, permanent_student_id FROM students WHERE school_id = ?",
        (s_id,)
    ).fetchall()
    
    cnt = len(students)
    if cnt == 0:
        institution_stats.append({
            "school_id": s_id,
            "prefix": prefix,
            "count": 0,
            "range": "None (Ready for 001)"
        })
        continue
    
    # Sort students alphabetically by first name (A-Z). If first names match, sort by complete student name.
    # Deterministic tie-breaker: permanent_student_id.
    sorted_stus = sorted(students, key=lambda s: (get_name_sort_key(s[1]), s[2]))
    
    for seq, st in enumerate(sorted_stus, 1):
        old_id = st[0]
        perm_id = st[2]
        new_id = f"{prefix}{seq:03d}"
        
        # Update students
        c.execute(
            "UPDATE students SET student_id = ? WHERE permanent_student_id = ?",
            (new_id, perm_id)
        )
        # Update users if any user account is linked to this student
        c.execute(
            "UPDATE users SET student_id = ? WHERE permanent_student_id = ?",
            (new_id, perm_id)
        )
        total_migrated += 1
    
    first_id = f"{prefix}001"
    last_id = f"{prefix}{cnt:03d}"
    institution_stats.append({
        "school_id": s_id,
        "prefix": prefix,
        "count": cnt,
        "range": f"{first_id} — {last_id}"
    })

c.execute("COMMIT")
print(f"Transaction committed. Total student records updated: {total_migrated}")

# Verify integrity and metrics
print("\n" + "=" * 65)
print("POST-MIGRATION VERIFICATION")
print("=" * 65)

tot_students = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
unique_student_ids = c.execute("SELECT COUNT(DISTINCT student_id) FROM students").fetchone()[0]
print(f"Total students: {tot_students}")
print(f"Unique student_ids: {unique_student_ids}")
assert tot_students == 30001, f"Expected 30001 students, found {tot_students}"
assert unique_student_ids == 30001, f"Expected 30001 unique IDs, found {unique_student_ids}"

# Check demo student in users table
asha_user = c.execute("SELECT user_id, email, role, student_id, permanent_student_id FROM users WHERE permanent_student_id = 'NS-FB8336A812DE468FB8E475443CF673EB'").fetchone()
print(f"Asha Sharma user account updated student_id: {asha_user}")

kiran_user = c.execute("SELECT user_id, email, role, student_id, permanent_student_id FROM users WHERE permanent_student_id = 'NS-2BC0159B30604BA8BB9537D32A3D8AE8'").fetchone()
print(f"Kiran Kumar user account updated student_id: {kiran_user}")

integrity = c.execute("PRAGMA integrity_check").fetchall()
print(f"PRAGMA integrity_check: {integrity}")

fk_check = c.execute("PRAGMA foreign_key_check").fetchall()
print(f"PRAGMA foreign_key_check: {len(fk_check)} violations")

conn.close()
