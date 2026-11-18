with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "execute(" in line and "f\"" in line:
        print(f"Line {i+1}: {line.strip()}")
    elif "execute(" in line:
        for k in range(i, min(len(lines), i+3)):
            if 'f"' in lines[k] or "f'" in lines[k]:
                print(f"Line {k+1} after execute: {lines[k].strip()}")
