import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

schools = cur.execute("SELECT school_id, school_name, school_type, category FROM schools ORDER BY school_id").fetchall()
for s in schools:
    progs = cur.execute("SELECT program_id, program_name, degree_type, discipline_or_stream, combination_code FROM academic_programs WHERE institution_id = ?", (s["school_id"],)).fetchall()
    divs = cur.execute("SELECT division_id, division_name FROM institution_divisions WHERE parent_institution_id = ?", (s["school_id"],)).fetchall()
    secs = cur.execute("SELECT count(*) FROM program_sections WHERE institution_id = ?", (s["school_id"],)).fetchone()[0]
    stds = cur.execute("SELECT count(*) FROM students WHERE school_id = ?", (s["school_id"],)).fetchone()[0]
    print(f"[{s['school_id']}] {s['school_name']} | Type: {s['school_type']} | Cat: {s['category']}")
    print(f"   Programs: {len(progs)}, Divisions: {len(divs)}, Sections: {secs}, Students: {stds}")
    if progs:
        p_summary = [f"{p['program_name'][:25]} ({p['discipline_or_stream'] or p['degree_type']})" for p in progs[:4]]
        print(f"   Sample progs: {', '.join(p_summary)}")

conn.close()
