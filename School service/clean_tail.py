with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionParentRequestsDesk.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the last "}"
for i in range(len(lines)-1, -1, -1):
    if lines[i].strip() == "}":
        lines = lines[:i+1]
        break

with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionParentRequestsDesk.jsx', 'w', encoding='utf-8') as f:
    f.writelines(lines)
    f.write("\n")

print(f"Truncated clean to {len(lines)} lines.")
