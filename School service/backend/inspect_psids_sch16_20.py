import sqlite3
from collections import Counter

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

c.execute("SELECT school_id, permanent_student_id FROM students WHERE school_id IN ('SCH016', 'SCH017', 'SCH018', 'SCH019', 'SCH020')")
rows = c.fetchall()
psid_patterns = Counter()
for sch, psid in rows:
    parts = psid.split('-')
    tag = f"{parts[1]}-{parts[2]}" if len(parts) >= 3 else psid[:8]
    psid_patterns[(sch, tag)] += 1

for (sch, tag), cnt in sorted(psid_patterns.items()):
    print(f"  {sch} | {tag}: {cnt}")

conn.close()
