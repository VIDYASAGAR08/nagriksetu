import csv

with open(r'C:\Users\callm\nagriksetu\NagrikSetu_Complete_Student_Institution_Mapping.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        if row['Institution ID'] == 'SCH016' and row['Standard / Class'] in ('Standard 11', 'Standard 12'):
            print(f"ID={row['Student ID']}, PSID={row['Permanent Student ID']}, Name={row['Student Full Name']}, Std={row['Standard / Class']}, Stream={row['Stream']}, Prog={row['Programme']}")
            count += 1
            if count >= 3:
                break
