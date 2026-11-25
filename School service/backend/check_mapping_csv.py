import csv
from collections import defaultdict, Counter

print("=== INSPECTING NagrikSetu_Complete_Student_Institution_Mapping.csv ===")

with open('data/NagrikSetu_Complete_Student_Institution_Mapping.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows in mapping CSV: {len(rows)}")

# Check institutions in CSV
inst_counts = Counter()
for row in rows:
    inst_counts[(row['Institution ID'], row['Institution Name'], row['Institution Type'])] += 1

print("\nInstitutions in mapping CSV:")
for (iid, iname, itype), count in sorted(inst_counts.items()):
    print(f"  {iid} | {iname} | {itype}: {count} students")

# Check PU College rows in CSV
pu_combos = defaultdict(Counter)
for row in rows:
    if 'PU' in row['Institution Type'] or row['Institution ID'] in ['SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015']:
        iid = row['Institution ID']
        std = row['Standard / Class']
        sec = row['Section']
        stream = row['Stream']
        prog = row['Programme']
        sem = row['Semester / Year']
        pu_combos[iid][(std, sec, stream, prog, sem)] += 1

print("\nSample PU College classifications in CSV:")
for iid in ['SCH011', 'SCH012']:
    print(f"  {iid}:")
    for combo, cnt in list(pu_combos[iid].items())[:10]:
        print(f"    {combo}: {cnt}")

# Check Degree College (COL003) rows in CSV
print("\nDegree College rows in CSV:")
for row in rows:
    if row['Institution ID'] == 'COL003':
        print(" ", dict(row))

conn.close()
