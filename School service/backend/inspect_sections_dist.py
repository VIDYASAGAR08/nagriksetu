import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

print("Sections in SCH011 per standard:")
c.execute("""
    SELECT standard, section, COUNT(*)
    FROM students
    WHERE school_id = 'SCH011'
    GROUP BY standard, section
    ORDER BY standard, section
""")
for r in c.fetchall():
    print(f"  Std {r[0]} | Sec {r[1]}: {r[2]}")

print("\nSections in SCH016 per standard:")
c.execute("""
    SELECT standard, section, COUNT(*)
    FROM students
    WHERE school_id = 'SCH016'
    GROUP BY standard, section
    ORDER BY standard, section
""")
for r in c.fetchall():
    print(f"  Std {r[0]} | Sec {r[1]}: {r[2]}")

conn.close()
