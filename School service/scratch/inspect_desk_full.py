with open(r"C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx", "r", encoding="utf-8") as f:
    text = f.read()

lines = text.split("\n")
print(f"Total lines: {len(lines)}")
print("First 30 lines:")
for l in lines[:30]:
    print(l)
