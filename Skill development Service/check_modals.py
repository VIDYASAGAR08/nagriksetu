with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

target = "{/* 3B. REPRESENTATIVE SELF-REGISTRATION MODAL */}"
print("Modal exists:", target in text)
