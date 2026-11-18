import sys

# 1. Update SelectInstitutionPage.jsx
sel_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\SelectInstitutionPage.jsx"
with open(sel_path, "r", encoding="utf-8") as f:
    sel_content = f.read()

old_sel_routing = """      if (res.role === 'school_admin' || res.role === 'platform_admin') {
        navigate('/institution-admin')
      } else if (['school_staff', 'admissions_officer', 'academic_admin', 'student_records_officer', 'general_staff'].includes(res.role)) {
        navigate('/staff')
      } else {
        navigate('/institution-admin')
      }"""

new_sel_routing = """      if (['school_admin', 'academic_admin', 'institution_admin', 'platform_admin'].includes(res.role)) {
        navigate('/institution-admin')
      } else if (['school_staff', 'admissions_officer', 'student_records_officer', 'general_staff'].includes(res.role)) {
        navigate('/staff')
      } else {
        navigate('/institution-admin')
      }"""

assert old_sel_routing in sel_content, "old_sel_routing not found"
sel_content = sel_content.replace(old_sel_routing, new_sel_routing, 1)
with open(sel_path, "w", encoding="utf-8") as f:
    f.write(sel_content)
print("SelectInstitutionPage.jsx routing fixed!")

# 2. Update LoginPage.jsx
login_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx"
with open(login_path, "r", encoding="utf-8") as f:
    login_content = f.read()

old_login_routing = """      } else if (res.role === 'school_admin') {
        navigate('/institution-admin')
      } else if (['school_staff', 'admissions_officer', 'academic_admin', 'student_records_officer', 'general_staff'].includes(res.role)) {
        navigate('/staff')
      }"""

new_login_routing = """      } else if (['school_admin', 'academic_admin', 'institution_admin'].includes(res.role)) {
        navigate('/institution-admin')
      } else if (['school_staff', 'admissions_officer', 'student_records_officer', 'general_staff'].includes(res.role)) {
        navigate('/staff')
      }"""

assert old_login_routing in login_content, "old_login_routing not found"
login_content = login_content.replace(old_login_routing, new_login_routing, 1)
with open(login_path, "w", encoding="utf-8") as f:
    f.write(login_content)
print("LoginPage.jsx routing fixed!")

# 3. Update StaffDashboard.jsx
staff_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\staff\StaffDashboard.jsx"
with open(staff_path, "r", encoding="utf-8") as f:
    staff_content = f.read()

old_staff_guard = "if (!isAuthenticated || (user?.role !== 'school_staff' && user?.role !== 'school_admin' && user?.role !== 'platform_admin')) {"
new_staff_guard = "if (!isAuthenticated || (!['school_staff', 'school_admin', 'academic_admin', 'institution_admin', 'platform_admin', 'admissions_officer'].includes(user?.role))) {"

assert old_staff_guard in staff_content, "old_staff_guard not found"
staff_content = staff_content.replace(old_staff_guard, new_staff_guard, 1)
with open(staff_path, "w", encoding="utf-8") as f:
    f.write(staff_content)
print("StaffDashboard.jsx guard fixed!")
