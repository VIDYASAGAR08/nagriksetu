with open(r"C:\Users\callm\nagriksetu\scratch\verify_all_requirements.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for j in range(320, min(len(lines), 350)):
    print(f"{j+1}: {lines[j]}", end="")
