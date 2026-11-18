path = r'C:\Users\callm\nagriksetu\backend\scripts\verify_restructured_directory.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'login_tests = [' in l:
        lines[i:i+4] = [
            '    login_tests = [\n',
            '        ("staff.sch001@example.com", "Staff@NagrikSetu2026!", "SCH001", "school_staff"),\n',
            '        ("staff.sch011@example.com", "Staff@NagrikSetu2026!", "SCH011", "school_staff"),\n',
            '        ("admin.central@nagriksetu.gov", "Central@NagrikSetu2026!", None, "platform_admin"),\n',
            '    ]\n'
        ]
        break
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Updated login_tests successfully')
