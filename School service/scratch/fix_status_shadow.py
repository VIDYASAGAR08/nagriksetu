with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    text = f.read()

target = "status_code=status.HTTP_403_FORBIDDEN,\n                    detail=f\"Access denied: You cannot view examinations"
replacement = "status_code=403,\n                    detail=f\"Access denied: You cannot view examinations"

assert target in text, "target not found"
text = text.replace(target, replacement)

with open(r"C:\Users\callm\nagriksetu\backend\main.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated status_code=403 in main.py")
