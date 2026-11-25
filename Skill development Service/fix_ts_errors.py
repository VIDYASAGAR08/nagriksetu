app_path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix adminTab type definition to include 'hierarchy'
old_admin_state = "const [adminTab, setAdminTab] = useState<'applications' | 'skills' | 'programmes' | 'centres'>('applications');"
new_admin_state = "const [adminTab, setAdminTab] = useState<'applications' | 'skills' | 'programmes' | 'centres' | 'hierarchy'>('applications');"
assert old_admin_state in content, "old_admin_state not found"
content = content.replace(old_admin_state, new_admin_state, 1)

# 2. Add fetchAdminCatalogueSummary definition next to fetchAdminCentres
target_fetch_centres = "const fetchAdminCentres = async () => {"
fetch_catalogue_fn = """const fetchAdminCatalogueSummary = async () => {
    if (!token) return;
    setAdminCatalogueLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/admin/catalogue-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAdminCatalogueData(data);
      }
    } catch (e) {
      console.error('Failed to load admin catalogue summary', e);
    } finally {
      setAdminCatalogueLoading(false);
    }
  };

  """

assert target_fetch_centres in content, "target_fetch_centres not found"
content = content.replace(target_fetch_centres, fetch_catalogue_fn + target_fetch_centres, 1)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: adminTab type and fetchAdminCatalogueSummary function placed correctly!")
