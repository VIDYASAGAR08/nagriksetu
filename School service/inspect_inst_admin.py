with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

print("--- InstitutionAdminDashboard.jsx ---")
for line in text.splitlines():
    if any(k in line for k in ['activeTab', 'tab', 'Linking', 'linking', 'requests', 'Request', 'render']):
        print(' ', line[:120])
