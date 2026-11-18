import shutil
import os
from datetime import datetime

src = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
dst = rf"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db.bak_phase12_{ts}"
shutil.copy2(src, dst)
print(f"Created backup: {dst} ({os.path.getsize(dst)} bytes)")
