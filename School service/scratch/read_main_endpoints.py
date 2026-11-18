with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Line 10722 to 10945:")
for idx in range(10721, min(10945, len(lines))):
    print(f"{idx+1}: {lines[idx]}", end='')
