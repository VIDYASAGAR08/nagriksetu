import csv
from collections import Counter

print("=== Analyzing NagrikSetu_Complete_Student_Institution_Mapping.csv ===")
inst_std_counts = Counter()
inst_prog_counts = Counter()

with open(r'C:\Users\callm\nagriksetu\NagrikSetu_Complete_Student_Institution_Mapping.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        inst_id = row['Institution ID']
        if inst_id in [f'SCH{i:03d}' for i in range(11, 21)]:
            std = row['Standard / Class']
            prog = row['Programme']
            inst_std_counts[(inst_id, std)] += 1
            inst_prog_counts[(inst_id, prog)] += 1

print("\n--- Standard distribution for SCH011-SCH015 (PU Colleges) in mapping CSV ---")
for inst_id in [f'SCH{i:03d}' for i in range(11, 16)]:
    stds = [f"{s.replace('Standard ', '')}:{c}" for (i, s), c in sorted(inst_std_counts.items()) if i == inst_id]
    print(f"{inst_id}: {', '.join(stds)}")

print("\n--- Standard distribution for SCH016-SCH020 (Schools) in mapping CSV ---")
for inst_id in [f'SCH{i:03d}' for i in range(16, 21)]:
    stds = [f"{s.replace('Standard ', '')}:{c}" for (i, s), c in sorted(inst_std_counts.items()) if i == inst_id]
    print(f"{inst_id}: {', '.join(stds)}")

print("\n--- Programme samples for SCH011 Standards 1-10 in mapping CSV ---")
with open(r'C:\Users\callm\nagriksetu\NagrikSetu_Complete_Student_Institution_Mapping.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        if row['Institution ID'] == 'SCH011' and row['Standard / Class'] == 'Standard 1':
            print(f"ID={row['Student ID']}, PSID={row['Permanent Student ID']}, Name={row['Student Full Name']}, Std={row['Standard / Class']}, Stream={row['Stream']}, Prog={row['Programme']}")
            count += 1
            if count >= 3:
                break
