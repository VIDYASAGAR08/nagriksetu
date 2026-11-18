with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    text = f.read()

for ep in ['/schools/{school_id}/programs', '/schools/{school_id}/academic-hierarchy']:
    idx = text.find(f'"{ep}"')
    if idx == -1:
        idx = text.find(f"'{ep}'")
    if idx != -1:
        print(f"=== {ep} ===")
        print(text[idx-20:idx+600])
