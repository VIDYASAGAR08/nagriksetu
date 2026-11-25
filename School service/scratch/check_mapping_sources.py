import csv

print("=== Checking NagrikSetu_Complete_Student_Institution_Mapping.csv ===")
with open(r'C:\Users\callm\nagriksetu\NagrikSetu_Complete_Student_Institution_Mapping.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    print("Header:", header)
    count = 0
    for row in reader:
        if row[1] in ('SCH11097', 'SCH11047', 'SCH16047', 'SCH16097'):
            print("Row:", row)
            count += 1
            if count >= 10:
                break
