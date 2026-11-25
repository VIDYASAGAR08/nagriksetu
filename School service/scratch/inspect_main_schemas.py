with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Lines around 13380-13400:")
for j in range(13375, 13410):
    print(f"{j+1}: {lines[j]}", end="")
