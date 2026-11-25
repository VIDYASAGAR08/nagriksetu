with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. State changes: add ownerAuthToken, ownerKeyInput, ownerAuthenticated, etc.
old_owner_states = """  // Project Owner Password Reset Modal State
  const [ownerResetCentreId, setOwnerResetCentreId] = useState<number | null>(null);
  const [ownerResetSecretKey, setOwnerResetSecretKey] = useState<string>('NagrikSetu@Owner2026!');
  const [ownerResetNewPassword, setOwnerResetNewPassword] = useState<string>('CentreAdmin@2026!');
  const [ownerResetSubmitting, setOwnerResetSubmitting] = useState<boolean>(false);
  const [ownerResetMsg, setOwnerResetMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);"""

new_owner_states = """  // Project Owner Authentication & Protected Management State
  const [ownerAuthToken, setOwnerAuthToken] = useState<string>(localStorage.getItem('ns_skill_owner_token') || '');
  const [ownerKeyInput, setOwnerKeyInput] = useState<string>('');
  const [ownerAuthLoading, setOwnerAuthLoading] = useState<boolean>(false);
  const [ownerAuthMsg, setOwnerAuthMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [ownerResetCentreId, setOwnerResetCentreId] = useState<number | null>(null);
  const [ownerResetNewPassword, setOwnerResetNewPassword] = useState<string>('');
  const [ownerResetSubmitting, setOwnerResetSubmitting] = useState<boolean>(false);
  const [ownerResetMsg, setOwnerResetMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);"""

if old_owner_states in text:
    text = text.replace(old_owner_states, new_owner_states, 1)
    print("Updated owner states in App.tsx")
else:
    print("old_owner_states not found")

# 2. Update fetchCentreRegister to pass ownerAuthToken if present
old_fetch_reg = """  const fetchCentreRegister = async () => {
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
  };"""

new_fetch_reg = """  const fetchCentreRegister = async (tokenOverride?: string) => {
    setCentreRegisterLoading(true);
    const effectiveToken = tokenOverride !== undefined ? tokenOverride : ownerAuthToken;
    try {
      const headers: Record<string, string> = {};
      if (effectiveToken) {
        headers['Authorization'] = `Bearer ${effectiveToken}`;
      }
      const res = await fetch(`${API_BASE}/api/public/centre-register`, { headers });
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

  const handleOwnerAuthenticate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ownerKeyInput.trim()) return;
    setOwnerAuthLoading(true);
    setOwnerAuthMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/project-owner-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ owner_key: ownerKeyInput.trim() })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Authentication failed. Please verify Project Owner Key.');
      localStorage.setItem('ns_skill_owner_token', data.access_token);
      setOwnerAuthToken(data.access_token);
      setOwnerAuthMsg({ type: 'success', text: 'Project Owner verified. Detailed institutional records unlocked.' });
      fetchCentreRegister(data.access_token);
      setOwnerKeyInput('');
    } catch (err: any) {
      setOwnerAuthMsg({ type: 'error', text: err.message });
    } finally {
      setOwnerAuthLoading(false);
    }
  };

  const handleOwnerSignOut = () => {
    localStorage.removeItem('ns_skill_owner_token');
    setOwnerAuthToken('');
    setOwnerAuthMsg(null);
    fetchCentreRegister('');
  };"""

if old_fetch_reg in text:
    text = text.replace(old_fetch_reg, new_fetch_reg, 1)
    print("Updated fetchCentreRegister and added owner auth handlers")
else:
    print("old_fetch_reg not found")

# 3. Update handleOwnerResetPassword to use ownerAuthToken
old_reset_func = """  const handleOwnerResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ownerResetCentreId) return;
    if (ownerResetNewPassword.length < 6) {
      setOwnerResetMsg({ type: 'error', text: 'New password must be at least 6 characters long.' });
      return;
    }
    setOwnerResetSubmitting(true);
    setOwnerResetMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/project-owner-reset-centre-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          centre_id: ownerResetCentreId,
          secret_key: ownerResetSecretKey,
          new_password: ownerResetNewPassword
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Password reset rejected.');
      setOwnerResetMsg({ type: 'success', text: `Success: Demonstration password reset for ${data.centre_name}.` });
      fetchCentreRegister();
      setTimeout(() => {
        setOwnerResetCentreId(null);
        setOwnerResetMsg(null);
      }, 2000);
    } catch (err: any) {
      setOwnerResetMsg({ type: 'error', text: err.message });
    } finally {
      setOwnerResetSubmitting(false);
    }
  };"""

new_reset_func = """  const handleOwnerResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ownerResetCentreId) return;
    if (ownerResetNewPassword.length < 8) {
      setOwnerResetMsg({ type: 'error', text: 'New password must be at least 8 characters long.' });
      return;
    }
    setOwnerResetSubmitting(true);
    setOwnerResetMsg(null);
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (ownerAuthToken) {
        headers['Authorization'] = `Bearer ${ownerAuthToken}`;
      }
      const res = await fetch(`${API_BASE}/api/auth/project-owner-reset-centre-password`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          centre_id: ownerResetCentreId,
          new_password: ownerResetNewPassword
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Password reset rejected.');
      setOwnerResetMsg({ type: 'success', text: `Success: Credentials updated for ${data.centre_name} (${data.registered_email}).` });
      fetchCentreRegister();
      setTimeout(() => {
        setOwnerResetCentreId(null);
        setOwnerResetNewPassword('');
        setOwnerResetMsg(null);
      }, 2000);
    } catch (err: any) {
      setOwnerResetMsg({ type: 'error', text: err.message });
    } finally {
      setOwnerResetSubmitting(false);
    }
  };"""

if old_reset_func in text:
    text = text.replace(old_reset_func, new_reset_func, 1)
    print("Updated handleOwnerResetPassword")
else:
    print("old_reset_func not found")

# 4. Remove any default initial password references
text = text.replace("setLoginPassword('CentreAdmin@2026!');", "setLoginPassword('');")
text = text.replace("setAssignAdminPassword('CentreAdmin@2026!');", "setAssignAdminPassword('');")
text = text.replace("<small style={{ color: '#64748b' }}>Default initial password: CentreAdmin@2026!</small>", "<small style={{ color: '#64748b' }}>Representative sets unique password on self-registration</small>")

with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Saved App.tsx part 1")
