with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1894, min(1955, len(lines))):
    print(lines[i], end="")
