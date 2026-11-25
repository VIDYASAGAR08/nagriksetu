import re

with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx", "r", encoding="utf-8") as f:
    text = f.read()

tabs = re.findall(r"mainTab === ['\"]([^'\"]+)['\"]", text)
print("Tabs in InstitutionAdminDashboard.jsx:", sorted(list(set(tabs))))

# Find where InstitutionStudentManagementDesk is used
for idx, line in enumerate(text.split("\n")):
    if "InstitutionStudentManagementDesk" in line or "Student" in line and "tab" in line.lower():
        print(f"Line {idx+1}: {line}")
