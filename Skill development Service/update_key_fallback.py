import os

file_path = r"C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

target = 'return key or "NagrikSetu@OwnerSecureKey2026!"'
replacement = 'return key or "NagrikSetu#OwnerAuth2026$Rotated9x!"'

if target in text:
    text = text.replace(target, replacement, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("UPDATED_FALLBACK_KEY")
else:
    print("TARGET_NOT_FOUND")
