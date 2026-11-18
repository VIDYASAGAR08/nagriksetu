import re

with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

endpoints = []
for i, line in enumerate(lines):
    if line.strip().startswith("@app."):
        # Find the function def
        fn = ""
        for j in range(i+1, min(i+10, len(lines))):
            if lines[j].strip().startswith("def ") or lines[j].strip().startswith("async def "):
                fn = lines[j].strip()
                break
        endpoints.append((i+1, line.strip(), fn))

print(f"Total endpoints found: {len(endpoints)}")
for ep in endpoints:
    print(f"Line {ep[0]:4d}: {ep[1]:<50} -> {ep[2]}")
