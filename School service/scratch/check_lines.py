with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Line 10720 to 10740:")
for i in range(10719, min(10740, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')

print("\nLine 10940 to 10955:")
for i in range(10939, min(10955, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')
