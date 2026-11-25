with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
endpoints = re.findall(r"@app\.(get|post|put|patch|delete)\([\"']([^\"']+)[\"']", text)
req_endpoints = [e for e in endpoints if 'request' in e[1] or 'correction' in e[1] or 'audit' in e[1]]
print("Request / Correction / Audit endpoints:")
for m, u in req_endpoints:
    print(f"  {m.upper():<6} {u}")
