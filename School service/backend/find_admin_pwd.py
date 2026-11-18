import glob

for f in glob.glob("*.py") + glob.glob("scripts/*.py") + glob.glob("data/*.py") + glob.glob("migrations/*.py"):
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            c = fp.read()
            if "admin.central" in c or "9800000003" in c:
                print("Matched file:", f)
                for line in c.splitlines():
                    if "password" in line.lower() or "admin.central" in line:
                        print("  ", line.strip())
    except Exception as e:
        pass
