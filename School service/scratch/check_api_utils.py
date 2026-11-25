with open(r"C:\Users\callm\nagriksetu\frontend\src\utils\api.js", "r", encoding="utf-8") as f:
    text = f.read()

import re
funcs = re.findall(r"export\s+(?:async\s+)?function\s+([a-zA-Z0-9_]+)", text)
print("Exported functions in api.js:", funcs)
