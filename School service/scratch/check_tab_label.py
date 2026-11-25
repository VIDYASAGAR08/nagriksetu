with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r"'students'", text)]
for pos in matches[:5]:
    print(text[pos-100:pos+150])
    print("---")
