with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r"service_requests", text)]
print(f"service_requests occurs {len(matches)} times. Positions:", matches[:10])
for pos in matches[:3]:
    print("--- SNIPPET ---")
    print(text[pos-50:pos+500])
