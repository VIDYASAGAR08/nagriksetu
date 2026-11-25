import os

file_path = r"C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

target = "const [authPortalView, setAuthPortalView] = useState<'none' | 'select_role' | 'login_citizen' | 'login_centre' | 'login_admin' | 'register_citizen' | 'register_centre_rep' | 'project_owner_register' | 'forgot_password' | 'set_password'>('none');"

replacement = """const [authPortalView, setAuthPortalView] = useState<'none' | 'select_role' | 'login_citizen' | 'login_centre' | 'login_admin' | 'register_citizen' | 'register_centre_rep' | 'project_owner_register' | 'forgot_password' | 'set_password'>(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('portal') === 'owner' || params.get('mode') === 'project_owner') {
        return 'project_owner_register';
      }
    }
    return 'none';
  });"""

if target in text:
    text = text.replace(target, replacement, 1)
    print("SUCCESS: Added URL parameter support for private Project Owner access.")
else:
    print("TARGET NOT FOUND")

# Also ensure fetchCentreRegister is triggered if opened via URL param
target_effect = "fetch(`${API_BASE}/api/skill-gap/roles`)\n      .then(r => r.json())\n      .then(setSupportedRoles)\n      .catch(console.error);"
replacement_effect = """fetch(`${API_BASE}/api/skill-gap/roles`)
      .then(r => r.json())
      .then(setSupportedRoles)
      .catch(console.error);

    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('portal') === 'owner' || params.get('mode') === 'project_owner') {
        fetchCentreRegister();
      }
    }"""

if target_effect in text:
    text = text.replace(target_effect, replacement_effect, 1)
    print("SUCCESS: Added auto-fetch for Project Owner Register on URL param.")
else:
    print("TARGET EFFECT NOT FOUND")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("SCRIPT COMPLETED")
