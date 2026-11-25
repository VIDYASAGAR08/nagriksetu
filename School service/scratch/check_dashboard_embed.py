with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx", "r", encoding="utf-8") as f:
    lines = f.readlines()

for j in range(1355, 1380):
    print(f"{j+1}: {lines[j]}", end="")
