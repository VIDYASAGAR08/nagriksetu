import re

with open('C:/Users/callm/nagriksetu/backend/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

endpoints = re.findall(r'@app\.(get|post|put|delete)\(["\']([^"\']+)["\']', text)
for method, path in endpoints:
    if any(k in path for k in ['student', 'school', 'parent', 'auth']):
        print(f'{method.upper():6} {path}')
