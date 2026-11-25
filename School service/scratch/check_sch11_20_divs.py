import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("""
    SELECT division_id, parent_institution_id, division_name, division_type 
    FROM institution_divisions 
    WHERE parent_institution_id BETWEEN 'SCH011' AND 'SCH020'
""")
rows = cur.fetchall()
print(f"Total divisions for SCH011-SCH020: {len(rows)}")
for r in rows:
    print(r)

conn.close()
