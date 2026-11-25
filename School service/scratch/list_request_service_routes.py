with open(r"C:\Users\callm\nagriksetu\backend\request_management_service.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
endpoints = re.findall(r"@router\.(get|post|put|patch|delete)\([\"']([^\"']+)[\"']", text)
for m, u in endpoints:
    print(f"  {m.upper():<6} {u}")
