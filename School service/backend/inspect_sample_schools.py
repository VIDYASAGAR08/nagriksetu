import sqlite3

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
c = conn.cursor()

for r in c.execute("SELECT school_id, school_name, district, state, school_type, address, established_year, description, public_phone, website FROM schools WHERE school_id IN ('SCH001', 'SCH011', 'COL001', 'COL006')").fetchall():
    print(r)
