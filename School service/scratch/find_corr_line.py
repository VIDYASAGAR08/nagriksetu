with open(r"C:\Users\callm\nagriksetu\backend\request_management_service.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, l in enumerate(lines):
    if "INSERT INTO request_corrections" in l:
        print(f"Found request_corrections insert at line {idx+1}")
        for j in range(max(0, idx-5), min(len(lines), idx+35)):
            print(f"{j+1}: {lines[j]}", end="")
        break
