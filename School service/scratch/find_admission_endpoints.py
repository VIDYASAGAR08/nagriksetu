with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "/school/admissions/" in line and "@app." in line:
        print(f"Line {i+1}: {line.strip()}")
        # print function name
        for j in range(i+1, min(i+5, len(lines))):
            if lines[j].strip().startswith("def "):
                print(f"   -> {lines[j].strip()}")
                break
