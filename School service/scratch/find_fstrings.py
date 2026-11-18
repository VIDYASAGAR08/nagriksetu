with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if ".execute(f\"" in line or ".execute(f'" in line or ".execute(\n        f\"" in line:
        print(f"Line {i+1}: {line.strip()}")
        # print 5 lines context
        for j in range(max(0, i-2), min(len(lines), i+6)):
            print(f"  {j+1}: {lines[j].rstrip()}")
