import shutil
import os

src = r"C:\Users\callm\nagriksetu\backend\main.py"
bak = r"C:\Users\callm\nagriksetu\backend\main.py.bak_student_admin"
shutil.copy2(src, bak)
print(f"Backed up main.py to {bak} ({os.path.getsize(bak)} bytes)")
