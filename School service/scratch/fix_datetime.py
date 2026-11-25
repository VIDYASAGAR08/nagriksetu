with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    text = f.read()

count = text.count("datetime.datetime")
print(f"Occurrences of datetime.datetime: {count}")

text_fixed = text.replace("datetime.datetime.now()", "datetime.now()")
text_fixed = text_fixed.replace("datetime.datetime", "datetime")

with open(r"C:\Users\callm\nagriksetu\backend\main.py", "w", encoding="utf-8") as f:
    f.write(text_fixed)

print("Fixed datetime in backend/main.py!")
