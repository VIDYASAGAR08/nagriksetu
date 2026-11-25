import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("SELECT school_id, school_name, admissions_details_json FROM schools WHERE school_id IN ('SCH001', 'SCH002', 'SCH009', 'SCH011', 'SCH016')")
for r in cur.fetchall():
    print(f"\n--- {r[0]}: {r[1]} ---")
    if r[2]:
        try:
            data = json.loads(r[2])
            print("admissions_details_json keys:", list(data.keys()))
            if 'total_seats' in data or 'capacity' in data or 'seat_matrix' in data:
                print("Capacity/Seat data:", {k: v for k, v in data.items() if 'seat' in k or 'cap' in k})
            else:
                print("Full json snippet:", repr(data)[:200])
        except Exception as e:
            print("Error parsing json:", e)
    else:
        print("admissions_details_json is None")

print("\n--- Check school_programs table ---")
cur.execute("SELECT * FROM school_programs LIMIT 5")
print(cur.fetchall())

print("\n--- Check program_sections table ---")
cur.execute("SELECT * FROM program_sections LIMIT 5")
print(cur.fetchall())

conn.close()
