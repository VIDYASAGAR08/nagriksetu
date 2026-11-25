import csv
from collections import Counter

with open('data/student_id_restructuring_mapping.csv', 'r', encoding='utf-8') as f:
    r = csv.DictReader(f)
    sch11_rows = [row for row in r if row['Institution ID'] == 'SCH011']

print(f"Total SCH011 rows in student_id_restructuring_mapping.csv: {len(sch11_rows)}")

prog_counter = Counter()
status_counter = Counter()
for row in sch11_rows:
    prog_counter[(row['Class / Standard'], row['Academic Programme / Stream'])] += 1
    status_counter[row['Mapping Status']] += 1

print("\nSCH011 Program distribution in student_id_restructuring_mapping.csv:")
for k, v in sorted(prog_counter.items()):
    print(f"  Std {k[0]}: {k[1]} -> {v}")

print("\nSCH011 Mapping status counts:")
for k, v in sorted(status_counter.items()):
    print(f"  {k}: {v}")
