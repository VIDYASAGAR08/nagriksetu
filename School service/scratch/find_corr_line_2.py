with open(r"C:\Users\callm\nagriksetu\backend\request_management_service.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for j in range(1245, min(len(lines), 1275)):
    print(f"{j+1}: {lines[j]}", end="")
