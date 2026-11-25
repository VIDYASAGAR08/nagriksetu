with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "{activeTab === 'history'" in line:
        print(f"Found line {i+1}: {line}")
        for j in range(i, min(len(lines), i+30)):
            print(f'{j+1}: {lines[j]}', end='')
