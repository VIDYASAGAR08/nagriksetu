import re

files_to_check = [
    r"C:\Users\callm\nagriksetu\frontend\src\pages\public\HomePage.jsx",
    r"C:\Users\callm\nagriksetu\frontend\src\pages\public\InfoPage.jsx",
    r"C:\Users\callm\nagriksetu\frontend\src\components\layout\Footer.jsx",
    r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx",
]

for fpath in files_to_check:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"\nChecking {fpath}...")
    for word in ["ocr", "idp", "ocr-demo", "demo page"]:
        matches = [m.start() for m in re.finditer(word, content, re.IGNORECASE)]
        if matches:
            print(f"  Found '{word}': {len(matches)} times")
            for idx in matches:
                start = max(0, idx - 40)
                end = min(len(content), idx + 60)
                print(f"    Snippet: {content[start:end].replace(chr(10), ' ')}")
