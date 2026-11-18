import re

with open('C:/Users/callm/nagriksetu/backend/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

endpoints = re.findall(r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\'](?:,\s*response_model=[^,\)]+)?(?:,\s*status_code=[^,\)]+)?', code)

print(f"Total endpoints found in main.py: {len(endpoints)}")
for method, path in sorted(endpoints, key=lambda x: (x[1], x[0])):
    print(f"  {method.upper():6} {path}")
