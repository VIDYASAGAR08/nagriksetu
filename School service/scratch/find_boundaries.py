path = r'C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'INSTITUTION HEADER BANNER' in line:
        start_header = i
    if 'PRIMARY SECTION TABS' in line:
        start_tabs = i
    if 'TAB 1: ADMISSION APPLICATION MANAGEMENT' in line:
        start_tab1 = i
    if 'ACADEMIC MANAGEMENT & SUPERVISION TAB' in line:
        start_academics = i

print(f"Header start: line {start_header+1}")
print(f"Tabs start: line {start_tabs+1}")
print(f"Tab 1 (applications) start: line {start_tab1+1}")
print(f"Academics tab start: line {start_academics+1}")
