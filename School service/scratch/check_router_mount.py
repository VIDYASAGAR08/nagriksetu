with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r"request_management_service", text)]
print("Found request_management_service in main.py at:", matches)
if matches:
    print(text[matches[0]-50:matches[0]+200])
