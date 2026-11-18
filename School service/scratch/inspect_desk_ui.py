with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Lines 380 to 450:")
for i in range(379, min(450, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')

print("\nLines 500 to 570:")
for i in range(499, min(570, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')
