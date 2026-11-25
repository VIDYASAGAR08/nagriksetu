import os
import datetime

now = datetime.datetime.now()
recent_files = []

for root, dirs, files in os.walk(r"C:\Users\callm\nagriksetu"):
    if any(s in root.lower() for s in ["node_modules", "venv", ".git", "dist", "__pycache__"]):
        continue
    for f in files:
        fp = os.path.join(root, f)
        try:
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fp))
            if (now - mtime).days < 7:
                recent_files.append((mtime, fp))
        except Exception:
            pass

recent_files.sort(reverse=True)
print(f"Total recent files in nagriksetu: {len(recent_files)}")
for mt, fp in recent_files[:30]:
    print(f"{mt} -> {fp}")
