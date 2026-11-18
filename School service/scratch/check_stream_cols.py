import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

# Check all tables and columns for stream or combination or program
for table in ['students', 'enrollments', 'collegiate_enrollments', 'admission_applications', 'admission_detailed_submissions']:
    cols = [c[1] for c in cur.execute(f"PRAGMA table_info({table})").fetchall()]
    stream_cols = [c for c in cols if any(k in c.lower() for k in ['stream', 'combination', 'program', 'degree'])]
    if stream_cols:
        print(f"Table {table}: cols={stream_cols}")
        for sc in stream_cols:
            cnt = cur.execute(f"SELECT count(*) FROM {table} WHERE {sc} IS NOT NULL").fetchone()[0]
            print(f"  {sc} non-null count: {cnt}")
            if cnt > 0:
                samples = cur.execute(f"SELECT {sc}, count(*) FROM {table} WHERE {sc} IS NOT NULL GROUP BY {sc} LIMIT 5").fetchall()
                print(f"    sample values: {samples}")

conn.close()
