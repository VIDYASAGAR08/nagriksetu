with open(r"C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx", "r", encoding="utf-8") as f:
    text = f.read()

import re

# Find api calls
api_calls = re.findall(r"api(Get|Post|Put|Patch|Delete)\([`'\"]([^`'\"]+)[`'\"]", text)
print("API calls in InstitutionStudentManagementDesk.jsx:")
for method, url in set(api_calls):
    print(f"  api{method} -> {url}")

# Find section titles or headers
headings = re.findall(r"<h[1-4][^>]*>(.*?)</h[1-4]>", text)
print("\nHeadings found:")
for h in headings[:20]:
    print(f"  {h.strip()}")
