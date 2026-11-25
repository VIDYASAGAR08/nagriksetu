import os

frontend_src = r'C:\Users\callm\nagriksetu\frontend\src'
matches = []
for root, dirs, files in os.walk(frontend_src):
    for f in files:
        if f.endswith(('.jsx', '.js')):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as file:
                txt = file.read()
                if 'linking-requests' in txt or 'linking_requests' in txt or 'Parent Linking' in txt or 'SchoolAdmin' in txt:
                    matches.append((p, f))

print("Matching frontend files:")
for p, f in matches:
    print(f"  {f}: {p}")
