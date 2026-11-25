with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "profileTab ===" in l or "{/* TAB " in l:
        print(f"Line {i+1}: {l.strip()}")
