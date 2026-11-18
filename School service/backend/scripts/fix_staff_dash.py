with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\staff\StaffDashboard.jsx", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "Admission Desk" in l:
        print(f"Found on line {i+1}")
        # line before that is className
        lines[i-3] = "              onClick={() => setActiveTab('admissions')}\n"
        lines[i-2] = "              className={`btn btn--sm ${activeTab === 'admissions' ? 'btn--primary' : 'btn--ghost'}`}\n"

with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\staff\StaffDashboard.jsx", "w", encoding="utf-8") as f:
    lines = f.writelines(lines)

print("StaffDashboard.jsx line 347 cleaned successfully!")
