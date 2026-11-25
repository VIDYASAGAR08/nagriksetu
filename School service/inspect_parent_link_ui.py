with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "activeTab === 'link'" in l or "activeTab === 'history'" in l:
        print(f"Line {i+1}: {l.strip()}")
        for k in range(i, min(len(lines), i+80)):
            print(f"{k+1}: {lines[k]}", end='')
        break
