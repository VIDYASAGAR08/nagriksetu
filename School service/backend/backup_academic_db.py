import shutil
import datetime
import os

db_path = 'data/nagriksetu.db'
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
bak_path = f'data/nagriksetu_backup_academic_{ts}.db'
shutil.copy2(db_path, bak_path)
size = os.path.getsize(bak_path)
print(f"Backup created successfully: {bak_path} ({size} bytes)")
