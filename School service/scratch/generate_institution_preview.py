import sqlite3

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

def get_name_sort_key(name):
    clean = (name or "").strip()
    parts = clean.split()
    first_name = parts[0].lower() if parts else ""
    full_name = clean.lower()
    return (first_name, full_name)

schools = c.execute("SELECT school_id, school_name, school_type FROM schools ORDER BY school_id").fetchall()

summary = []

for s_id, s_name, s_type in schools:
    students = c.execute(
        "SELECT student_id, student_name, permanent_student_id FROM students WHERE school_id = ?",
        (s_id,)
    ).fetchall()
    
    cnt = len(students)
    if cnt == 0:
        summary.append({
            "school_id": s_id,
            "school_name": s_name,
            "school_type": s_type,
            "count": 0,
            "range": "None (Ready for sequence 001 on first admission)",
            "samples": []
        })
        continue
    
    sorted_stus = sorted(students, key=lambda s: get_name_sort_key(s[1]))
    first_id = f"{s_id}001"
    last_id = f"{s_id}{cnt:03d}"
    
    # Take first 3, middle 1, last 2 as samples
    sample_indices = [0, 1, 2]
    if cnt > 6:
        sample_indices.append(cnt // 2)
        sample_indices.append(cnt - 2)
        sample_indices.append(cnt - 1)
    
    samples = []
    for idx in sorted(set(sample_indices)):
        if idx < cnt:
            st = sorted_stus[idx]
            new_id = f"{s_id}{idx+1:03d}"
            samples.append({
                "seq": idx + 1,
                "name": st[1],
                "old_id": st[0],
                "new_id": new_id,
                "perm_id": st[2]
            })
            
    summary.append({
        "school_id": s_id,
        "school_name": s_name,
        "school_type": s_type,
        "count": cnt,
        "range": f"{first_id} — {last_id}",
        "samples": samples
    })

print(f"Generated summary for {len(summary)} institutions.")
for item in summary:
    print(f"{item['school_id']} | {item['school_type']:15} | count={item['count']:4} | range={item['range']}")

conn.close()
