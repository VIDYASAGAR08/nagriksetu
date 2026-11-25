with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

target = "{authPortalView === 'login_centre' && ("
print("Found target:", target in text)
print("register_centre_rep in text:", "register_centre_rep" in text)
