import shutil
import datetime

src = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
dst = rf"C:\Users\callm\nagriksetu\backend\data\nagriksetu_backup_phase11b_gap_{ts}.db"
shutil.copyfile(src, dst)
print("Backup created:", dst)
