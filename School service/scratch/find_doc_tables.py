with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "admission_documents" in line or "student_documents" in line:
        print(f"Line {i+1}: {line.strip()}")
