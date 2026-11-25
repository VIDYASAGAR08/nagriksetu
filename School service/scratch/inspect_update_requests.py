with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r"/school/update-requests", text)]
print("Found update-requests matches at:", matches)
if matches:
    pos = matches[0]
    print(text[pos-100:pos+1500])
