import openpyxl
import os

XLSX_PATH = r"C:\Users\callm\nagriksetu\reports\NagrikSetu_Institution_Wise_Student_Course_Enrollment_Register.xlsx"

print("Loading workbook for verification (read-only mode)...")
wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)

print("Sheet names:", wb.sheetnames)

expected_sheets = [
    "Institution Directory",
    "Complete Student Register",
    "Institution-wise Student List",
    "Course Enrollment Register",
    "Course Summary",
    "Academic Classification",
    "Unmapped Review Records"
]

all_sheets_present = all(s in wb.sheetnames for s in expected_sheets)
print(f"All 7 sheets present: {all_sheets_present}")

# Inspect Sheet 1
ws1 = wb["Institution Directory"]
rows1 = list(ws1.iter_rows(values_only=True))
print(f"Sheet 1 rows: {len(rows1)} (Expected: 33 -> 1 header + 31 institutions + 1 total)")
print("Sheet 1 Header:", rows1[0])
print("Sheet 1 Sample Row 1:", rows1[1][:4], "Reg Students:", rows1[1][7])
print("Sheet 1 Total Row:", rows1[-1][:4], "Sum Reg Students:", rows1[-1][7], "Sum Active:", rows1[-1][8])

# Inspect Sheet 2
ws2 = wb["Complete Student Register"]
rows2_count = 0
student_ids = set()
psids = set()
dup_sid = 0
dup_psid = 0
none_sid = 0
none_psid = 0

for r_idx, r in enumerate(ws2.iter_rows(values_only=True)):
    if r_idx == 0:
        continue
    rows2_count += 1
    sid = r[1]
    psid = r[2]
    if not sid:
        none_sid += 1
    elif sid in student_ids:
        dup_sid += 1
    else:
        student_ids.add(sid)
        
    if not psid:
        none_psid += 1
    elif psid in psids:
        dup_psid += 1
    else:
        psids.add(psid)

print(f"\nSheet 2 rows count: {rows2_count} (Expected: 30003)")
print(f"Unique Student IDs: {len(student_ids)}, Duplicates: {dup_sid}, Missing: {none_sid}")
print(f"Unique PSIDs: {len(psids)}, Duplicates: {dup_psid}, Missing: {none_psid}")

# Inspect Sheet 3
ws3 = wb["Institution-wise Student List"]
rows3_count = sum(1 for _ in ws3.iter_rows(values_only=True)) - 1
print(f"\nSheet 3 rows count: {rows3_count} (Expected: 30003)")

# Inspect Sheet 4
ws4 = wb["Course Enrollment Register"]
rows4_count = sum(1 for _ in ws4.iter_rows(values_only=True)) - 1
print(f"Sheet 4 rows count: {rows4_count} (Expected: 30003)")

# Inspect Sheet 5
ws5 = wb["Course Summary"]
rows5 = list(ws5.iter_rows(values_only=True))
print(f"Sheet 5 rows count: {len(rows5)}")
print("Sheet 5 Total Row:", rows5[-1])

# Inspect Sheet 7
ws7 = wb["Unmapped Review Records"]
rows7_count = sum(1 for _ in ws7.iter_rows(values_only=True)) - 1
print(f"\nSheet 7 rows count: {rows7_count} (Expected: 12000 unmapped records)")

wb.close()
print("\nVERIFICATION COMPLETE!")
