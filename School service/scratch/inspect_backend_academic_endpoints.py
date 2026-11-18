import re

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.findall(r'@app\.[a-z]+\([\'"]([^\'"]+)[\'"]', text)
print("All backend routes:")
for m in matches:
    if any(k in m for k in ['program', 'academic', 'degree', 'course', 'school', 'institution']):
        print(" ", m)
