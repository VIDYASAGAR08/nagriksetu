import ast
import re

with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    content = f.read()

pattern = r'@app\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']'
matches = re.findall(pattern, content)

print(f"Total Routes in backend/main.py: {len(matches)}")
for method, path in matches:
    print(f"  {method.upper():6} {path}")
