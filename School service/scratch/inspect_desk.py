with open(r"C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines in InstitutionStudentManagementDesk.jsx: {len(lines)}")
for idx, line in enumerate(lines[:80]):
    print(f"{idx+1}: {line}", end="")
