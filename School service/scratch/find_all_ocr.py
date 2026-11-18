import os

frontend_dir = r"C:\Users\callm\nagriksetu\frontend\src"
matches = []
for root, dirs, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith(('.jsx', '.js', '.tsx', '.ts', '.css', '.html')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
            for i, line in enumerate(lines):
                l_lower = line.lower()
                if 'ocr' in l_lower or 'idp' in l_lower:
                    matches.append((os.path.relpath(path, frontend_dir), i+1, line.strip()))

# Group by file
files_map = {}
for relpath, line_num, line_text in matches:
    files_map.setdefault(relpath, []).append((line_num, line_text))

for relpath, line_list in files_map.items():
    print(f"\n=== {relpath} ({len(line_list)} occurrences) ===")
    for ln, txt in line_list[:5]:
        safe_txt = txt.encode('ascii', errors='replace').decode()
        print(f"  Line {ln}: {safe_txt}")
    if len(line_list) > 5:
        print(f"  ... and {len(line_list)-5} more lines")
