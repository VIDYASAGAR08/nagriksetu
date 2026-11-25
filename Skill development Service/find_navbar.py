with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '<header' in l or 'className="header' in l or 'className="navbar' in l:
        print(f"Header/Navbar at line {i+1}: {l.strip()[:100]}")
    if 'activeTab === "home"' in l or "activeTab === 'home'" in l:
        print(f"Home tab check at line {i+1}")
