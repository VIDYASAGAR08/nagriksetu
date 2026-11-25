import os

for root, dirs, files in os.walk(r"C:\Users\callm\nagriksetu\backend"):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                c = fp.read()
                if "service_requests" in c:
                    print("Found service_requests in:", path)
