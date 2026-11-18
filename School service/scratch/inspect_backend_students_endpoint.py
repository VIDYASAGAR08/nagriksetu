with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '/institution/{institution_id}/students"' in l:
        print(f"Found endpoint at line {i+1}: {l.strip()}")
        for j in range(i, min(i+160, len(lines))):
            print(f"{j+1}: {lines[j]}", end='')
        break
