import re

path = r'C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Imports
old_import = "import InstitutionAdminAcademicDesk from '../../components/academic/InstitutionAdminAcademicDesk.jsx'"
new_imports = """import InstitutionAdminAcademicDesk from '../../components/academic/InstitutionAdminAcademicDesk.jsx'
import InstitutionStudentManagementDesk from '../../components/admin/InstitutionStudentManagementDesk.jsx'
import InstitutionParentRequestsDesk from '../../components/admin/InstitutionParentRequestsDesk.jsx'
import InstitutionParentsDirectory from '../../components/admin/InstitutionParentsDirectory.jsx'"""

if old_import in text:
    text = text.replace(old_import, new_imports)
    print("Imports updated.")

# 2. Default tab
old_tab = "const [mainTab, setMainTab] = useState(() => ['staff', 'academics'].includes(searchParams.get('tab')) ? searchParams.get('tab') : 'applications')"
new_tab = "const [mainTab, setMainTab] = useState(() => searchParams.get('tab') || 'overview')"
if old_tab in text:
    text = text.replace(old_tab, new_tab)
    print("Default tab updated to overview.")

# 3. Overview API
old_api = "const data = await apiGet('/institution/admin/overview', token)"
new_api = "const data = await apiGet(`/institution/${institutionId}/dashboard-overview`, token)"
if old_api in text:
    text = text.replace(old_api, new_api)
    print("Overview API updated to dashboard-overview.")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Step 1 complete.")
