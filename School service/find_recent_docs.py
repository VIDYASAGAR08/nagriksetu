import os
import datetime

now = datetime.datetime.now()
recent_files = []

for root, dirs, files in os.walk(r"C:\Users\callm"):
    # skip virtualenvs, appdata, node_modules, .git, .cache
    if any(s in root.lower() for s in ["node_modules", "venv", ".git", ".cache", "appdata", "anaconda3", "__pycache__"]):
        continue
    for f in files:
        if f.endswith((".txt", ".json", ".md", ".csv", ".docx", ".pdf")):
            fp = os.path.join(root, f)
            try:
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fp))
                if (now - mtime).days < 3:
                    recent_files.append((mtime, fp))
            except Exception:
                pass

recent_files.sort(reverse=True)
print(f"Total recent files: {len(recent_files)}")
for mt, fp in recent_files[:40]:
    print(f"{mt} -> {fp}")
