import re

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if ('@app.get' in line or '@app.post' in line) and 'notification' in line:
        print(f'{i+1}: {line.strip()}')
