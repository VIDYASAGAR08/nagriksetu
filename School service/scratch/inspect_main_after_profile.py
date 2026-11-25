with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Lines around 13850-13920:")
for j in range(13850, min(13930, len(lines))):
    print(f"{j+1}: {lines[j]}", end="")
