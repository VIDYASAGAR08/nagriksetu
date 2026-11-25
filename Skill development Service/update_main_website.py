path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '        "website": inst.get("website") or "Not provided by institute",'
replacement = '        "website": inst.get("website") if (inst.get("website") and str(inst.get("website")).strip().lower().startswith("http")) else None,'

if target in content:
    content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("main.py updated successfully.")
else:
    print("Target line not found in main.py")
