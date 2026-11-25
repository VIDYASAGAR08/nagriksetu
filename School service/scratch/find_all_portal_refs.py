import os

search_terms = [
    "CITIZEN & STAKEHOLDER PORTALS",
    "Choose Your Portal Experience",
    "Open Public Access",
    "Student Sign In & Activation",
    "Parent Portal Sign In",
    "Official Access Only"
]

root_dir = r"C:\Users\callm\nagriksetu"
matches = []

for root, dirs, files in os.walk(root_dir):
    if any(ignore in root for ignore in [".git", "node_modules", ".venv", "backups", "__pycache__"]):
        continue
    for file in files:
        if file.endswith((".jsx", ".js", ".html", ".tsx", ".ts", ".css")):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for term in search_terms:
                        if term in content:
                            matches.append((file_path, term))
            except Exception as e:
                pass

print(f"Total occurrences found: {len(matches)}")
for m in matches:
    print(f"File: {m[0]} | Match: {m[1]}")
