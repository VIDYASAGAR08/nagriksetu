with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
endpoints = re.findall(r"@app\.(get|post|put|patch|delete)\([\"']([^\"']+)[\"']", text)
print(f"Total endpoints in main.py: {len(endpoints)}")
inst_endpoints = [e for e in endpoints if 'institution' in e[1] or 'student' in e[1]]
print("\nInstitution/Student endpoints:")
for m, u in inst_endpoints:
    print(f"  {m.upper():<6} {u}")
