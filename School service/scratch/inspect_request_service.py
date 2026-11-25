with open(r"C:\Users\callm\nagriksetu\backend\request_management_service.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines in request_management_service.py: {len(lines)}")
for idx, l in enumerate(lines[:60]):
    print(f"{idx+1}: {l}", end="")
