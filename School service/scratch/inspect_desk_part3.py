with open(r"C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx", "r", encoding="utf-8") as f:
    text = f.read()

lines = text.split("\n")
for idx, l in enumerate(lines[150:280]):
    print(f"{idx+151}: {l}")
