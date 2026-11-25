with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

import re
auth_matches = re.findall(r'authPortalView\s*===?\s*[\'"]([^\'"]+)[\'"]', text)
print("Auth portal views:", set(auth_matches))
tab_matches = re.findall(r'activeTab\s*===?\s*[\'"]([^\'"]+)[\'"]', text)
print("Active tabs:", set(tab_matches))
