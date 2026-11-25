with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if any(k in l for k in ['lookup-student', 'linking-requests', 'linkingModalOpen', 'handleLinkStudent', 'studentLookup']):
        print(f"Line {i+1}: {l.strip()}")
