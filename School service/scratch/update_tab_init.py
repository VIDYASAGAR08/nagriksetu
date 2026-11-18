# -*- coding: utf-8 -*-
# 1. Update InstitutionAdminDashboard.jsx
with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx", "r", encoding="utf-8") as f:
    text = f.read()

target = "const [mainTab, setMainTab] = useState(() => searchParams.get('tab') === 'staff' ? 'staff' : 'applications')"
replacement = "const [mainTab, setMainTab] = useState(() => ['staff', 'academics'].includes(searchParams.get('tab')) ? searchParams.get('tab') : 'applications')"
if target in text:
    text = text.replace(target, replacement, 1)
    with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx", "w", encoding="utf-8") as f:
        f.write(text)
    print("InstitutionAdminDashboard updated!")
else:
    print("InstitutionAdminDashboard target not found!")

# 2. Update StaffDashboard.jsx
with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\staff\StaffDashboard.jsx", "r", encoding="utf-8") as f:
    stext = f.read()

starget = "if (window.location.search.includes('tab=admissions')) return 'admissions'"
sreplacement = """if (window.location.search.includes('tab=admissions') || window.location.hash.includes('tab=admissions')) return 'admissions'
    if (window.location.search.includes('tab=academics') || window.location.hash.includes('tab=academics')) return 'academics'"""

if starget in stext:
    stext = stext.replace(starget, sreplacement, 1)
    with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\staff\StaffDashboard.jsx", "w", encoding="utf-8") as f:
        f.write(stext)
    print("StaffDashboard updated!")
else:
    print("StaffDashboard target not found!")
