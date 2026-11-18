import re

with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    text = f.read()

routes = re.findall(r'@app\.(post|get)\(["\'](/auth[^"\']*)["\']', text)
for method, r in routes:
    print(f"{method.upper():<6} {r}")
