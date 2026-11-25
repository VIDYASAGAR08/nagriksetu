with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

old_type = "const [authPortalView, setAuthPortalView] = useState<'none' | 'select_role' | 'login_citizen' | 'login_centre' | 'login_admin' | 'register_citizen' | 'forgot_password' | 'set_password'>('none');"
new_type = "const [authPortalView, setAuthPortalView] = useState<'none' | 'select_role' | 'login_citizen' | 'login_centre' | 'login_admin' | 'register_citizen' | 'register_centre_rep' | 'project_owner_register' | 'forgot_password' | 'set_password'>('none');"

if old_type in text:
    text = text.replace(old_type, new_type, 1)
    print("Updated authPortalView type successfully")
else:
    print("ERROR: old_type not found in text")

# New state hooks for Centre Register & Owner Reset
hooks_to_insert = """
  // Project Owner Centre Account Register & Representative Setup State
  const [centreRegisterList, setCentreRegisterList] = useState<any[]>([]);
  const [centreRegisterLoading, setCentreRegisterLoading] = useState<boolean>(false);
  const [repSelectedCentreId, setRepSelectedCentreId] = useState<number>(1);
  const [repName, setRepName] = useState<string>('');
  const [repEmail, setRepEmail] = useState<string>('');
  const [repPhone, setRepPhone] = useState<string>('');
  const [repPassword, setRepPassword] = useState<string>('');
  const [repConfirmPassword, setRepConfirmPassword] = useState<string>('');
  const [repSubmitting, setRepSubmitting] = useState<boolean>(false);
  const [repMsg, setRepMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Project Owner Password Reset Modal State
  const [ownerResetCentreId, setOwnerResetCentreId] = useState<number | null>(null);
  const [ownerResetSecretKey, setOwnerResetSecretKey] = useState<string>('NagrikSetu@Owner2026!');
  const [ownerResetNewPassword, setOwnerResetNewPassword] = useState<string>('CentreAdmin@2026!');
  const [ownerResetSubmitting, setOwnerResetSubmitting] = useState<boolean>(false);
  const [ownerResetMsg, setOwnerResetMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchCentreRegister = async () => {
    setCentreRegisterLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/public/centre-register`);
      if (res.ok) {
        const data = await res.json();
        setCentreRegisterList(data);
      }
    } catch (err) {
      console.error('Failed to load centre register', err);
    } finally {
      setCentreRegisterLoading(false);
    }
  };
"""

target_after_type = new_type
if target_after_type in text and "const [centreRegisterList" not in text:
    text = text.replace(target_after_type, target_after_type + "\n" + hooks_to_insert, 1)
    print("Inserted state hooks successfully")

with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
