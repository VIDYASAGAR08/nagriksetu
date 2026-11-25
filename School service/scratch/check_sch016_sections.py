import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("SELECT section_id, institution_id, program_id, standard, section_name, capacity, current_strength FROM program_sections WHERE institution_id = 'SCH016'")
for r in cur.fetchall():
    print(r)

conn.close()
