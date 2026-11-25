import re

app_path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add state for selectedSubcategoryId in category_details
# Let's locate activeCategoryCode state
target_state = "const [activeCategoryCode, setActiveCategoryCode] = useState<string>('');"
assert target_state in content, "activeCategoryCode state not found"

new_states = """const [activeCategoryCode, setActiveCategoryCode] = useState<string>('');
  const [selectedSubcategoryId, setSelectedSubcategoryId] = useState<number | null>(null);
  const [adminCatalogueData, setAdminCatalogueData] = useState<any>(null);
  const [adminCatalogueLoading, setAdminCatalogueLoading] = useState<boolean>(false);"""

content = content.replace(target_state, new_states, 1)

# In openCategoryDetails, reset selectedSubcategoryId
target_open_cat = "setActiveCategoryCode(categoryIdentifier);\n    setActiveTab('category_details');"
new_open_cat = "setActiveCategoryCode(categoryIdentifier);\n    setSelectedSubcategoryId(null);\n    setActiveTab('category_details');"
assert target_open_cat in content, "target_open_cat not found"
content = content.replace(target_open_cat, new_open_cat, 1)

# In fetchAdminCatalogue function
admin_fetch_fn = """  const fetchAdminCatalogueSummary = async () => {
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

target_admin_hook = "fetchAdminCentres();\n    }"
new_admin_hook = "fetchAdminCentres();\n      fetchAdminCatalogueSummary();\n    }"
assert target_admin_hook in content, "target_admin_hook not found"
content = content.replace(target_admin_hook, new_admin_hook, 1)

# Add admin_fetch_fn before target_admin_hook
content = content.replace("fetchAdminCentres();", admin_fetch_fn + "\n      fetchAdminCentres();", 1)

print("Part 1: States and fetcher patched.")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)
