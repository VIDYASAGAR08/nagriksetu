import shutil
import datetime
import os

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
src = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
dst = rf"C:\Users\callm\nagriksetu\backend\data\nagriksetu_backup_requests_{ts}.db"
shutil.copyfile(src, dst)
print(f"SUCCESS: Backup created at {dst} with size {os.path.getsize(dst)} bytes")
