with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Lines 13875-13890:")
for j in range(13875, 13890):
    print(f"{j+1}: {lines[j]}", end="")
