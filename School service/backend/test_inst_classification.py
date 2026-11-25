import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

c.execute("SELECT school_id, school_name, school_type, category FROM schools ORDER BY school_id")
institutions = c.fetchall()

def classify_institution(school_id, name, stype, category):
    stype_str = (stype or "").lower()
    cat_str = (category or "").lower()
    name_str = (name or "").lower()
    
    if "pu college" in stype_str or "pu" in cat_str or "pre-university" in name_str:
        return "PU College"
    elif "university" in stype_str or "universities" in cat_str or "university" in name_str:
        return "University"
    elif "engineering" in name_str or "technology" in name_str or "polytechnic" in name_str or "engineering" in stype_str:
        return "Engineering College"
    elif "degree" in stype_str or "degree" in cat_str or "college" in name_str:
        return "Degree College"
    else:
        return "School"

print(f"Total institutions: {len(institutions)}")
counts = {}
for i in institutions:
    cat = classify_institution(i[0], i[1], i[2], i[3])
    counts[cat] = counts.get(cat, 0) + 1
    print(f"  {i[0]} | {i[1]} | Type: {i[2]} | Cat: {i[3]} -> Classified As: {cat}")

print("\nSummary by classified type:")
for k, v in sorted(counts.items()):
    print(f"  {k}: {v}")

conn.close()
