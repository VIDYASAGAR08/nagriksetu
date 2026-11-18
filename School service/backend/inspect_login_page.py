with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "selectedCategory === 'parent'" in line or "Citizen Portal Sign In" in line or "Sign In (Mobile" in line:
        print(f"Line {i+1}: {line.strip()}")
