import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

for t in ["academic_programs", "program_sections", "admission_applications", "users"]:
    for inst in ["COL001", "COL004", "COL010"]:
        col_name = "institution_id" if "institution_id" in [r[1] for r in c.execute(f"PRAGMA table_info({t})").fetchall()] else "school_id"
        cnt = c.execute(f"SELECT COUNT(*) FROM {t} WHERE {col_name}=?", (inst,)).fetchone()[0]
        if cnt > 0:
            print(f"{t} for {inst}: {cnt}")

conn.close()
