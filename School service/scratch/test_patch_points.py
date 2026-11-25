import re

with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update search and return in get_institution_students
target_search = """        if search and search.strip():
            q = f"%{search.strip()}%"
            where_clauses.append("(s.student_name LIKE ? OR s.student_id LIKE ? OR s.permanent_student_id LIKE ?)")
            params.extend([q, q, q])"""

replacement_search = """        if search and search.strip():
            q = f"%{search.strip()}%"
            where_clauses.append(\"\"\"(
                s.student_name LIKE ? OR s.student_id LIKE ? OR s.permanent_student_id LIKE ? OR
                s.permanent_student_id IN (
                    SELECT sg.permanent_student_id
                    FROM student_guardians sg
                    JOIN guardians g ON g.guardian_id = sg.guardian_id
                    WHERE g.full_name LIKE ? AND sg.is_verified = 1
                )
            )\"\"\")
            params.extend([q, q, q, q])"""

if target_search in content:
    print("Found target_search in content.")
else:
    print("WARNING: target_search NOT found.")

# Check get_institution_student_profile return
target_profile_return = """            "documents": documents
        }
    finally:
        conn.close()"""

if target_profile_return in content:
    print("Found target_profile_return in content.")
else:
    print("WARNING: target_profile_return NOT found.")
