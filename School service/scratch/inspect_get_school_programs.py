with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'def get_school_programs' in l:
        print(f"Line {i+1}")
        for j in range(i, min(i+60, len(lines))):
            print(f"{j+1}: {lines[j]}", end='')
        break
