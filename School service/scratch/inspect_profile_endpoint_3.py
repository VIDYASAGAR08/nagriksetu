with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for j in range(13760, min(13850, len(lines))):
    print(f"{j+1}: {lines[j]}", end="")
