with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Representative registration submit handler
handler_code = """
  const handleRegisterRepresentative = async (e: React.FormEvent) => {
    e.preventDefault();
    if (repPassword !== repConfirmPassword) {
      setRepMsg({ type: 'error', text: 'Password and confirm password do not match.' });
      return;
    }
    if (repPassword.length < 6) {
      setRepMsg({ type: 'error', text: 'Password must be at least 6 characters long.' });
      return;
    }
    setRepSubmitting(true);
    setRepMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/register-centre-representative`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          centre_id: repSelectedCentreId,
          representative_name: repName,
          representative_email: repEmail,
          representative_phone: repPhone,
          password: repPassword
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to register representative account.');
      
      setRepMsg({ type: 'success', text: `Authorized representative account successfully created for ${data.email}. Signing in...` });
      
      // Auto-login into centre workspace
      localStorage.setItem('ns_skill_token', data.access_token);
      localStorage.setItem('ns_skill_role', data.role);
      localStorage.setItem('ns_skill_centre_id', String(data.centre_id));
      localStorage.setItem('ns_skill_email', data.email);
      localStorage.setItem('ns_skill_name', data.full_name || '');
      setToken(data.access_token);
      setUserRole(data.role);
      setCentreId(String(data.centre_id));
      setUserEmail(data.email);
      setUserName(data.full_name || '');
      
      setTimeout(() => {
        setAuthPortalView('none');
        setCentreTab('dashboard');
      }, 1200);
    } catch (err: any) {
      setRepMsg({ type: 'error', text: err.message });
    } finally {
      setRepSubmitting(false);
    }
  };

  const handleOwnerResetPassword = async (e: React.FormEvent) => {
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
  };
"""

target = "const fetchCentreRegister = async () => {"
if target in text and "handleRegisterRepresentative" not in text:
    text = text.replace(target, handler_code + "\n  " + target, 1)
    print("Added handlers successfully")
else:
    print("Handlers already present or target not found")

with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
