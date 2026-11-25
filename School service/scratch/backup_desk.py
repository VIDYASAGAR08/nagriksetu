import shutil
import os

src = r"C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx"
bak = r"C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx.bak"
shutil.copy2(src, bak)
print(f"Backed up desk component to {bak} ({os.path.getsize(bak)} bytes)")
