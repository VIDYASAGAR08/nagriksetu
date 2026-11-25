import os
import glob

search_dirs = [
    r"C:\Users\callm\nagriksetu",
    r"C:\Users\callm\Documents",
    r"C:\Users\callm\Desktop",
    r"C:\Users\callm\Downloads",
]

for d in search_dirs:
    if not os.path.exists(d):
        continue
    for root, dirs, files in os.walk(d):
        # skip virtualenvs and node_modules
        if any(skip in root.lower() for skip in ["node_modules", "venv", ".git", "dist", "anaconda3", "__pycache__"]):
            continue
        for f in files:
            ext = os.path.splitext(f)[-1].lower()
            if ext in [".txt", ".md", ".json", ".csv", ".docx", ".pdf", ".py"]:
                filepath = os.path.join(root, f)
                try:
                    # check size < 10MB
                    if os.path.getsize(filepath) < 10 * 1024 * 1024:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as fp:
                            sample = fp.read(5000)
                            if "Q001" in sample or "Question Bank" in sample or "School Discovery" in sample:
                                print("Found match:", filepath)
                except Exception:
                    pass
print("Search complete.")
