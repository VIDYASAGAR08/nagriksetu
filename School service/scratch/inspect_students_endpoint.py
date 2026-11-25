with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, l in enumerate(lines):
    if "/institution/{institution_id}/students" in l:
        print(f"Found at line {idx+1}")
        for j in range(idx, min(idx+120, len(lines))):
            print(f"{j+1}: {lines[j]}", end="")
        break
