with open(r'C:\Users\callm\nagriksetu\test_suite_google_mobile.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = '    fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()'
replacement = '''    # Check integrity on users, students, email_otps, phone_otps
    for tbl in ['users', 'students', 'email_otps', 'phone_otps']:
        tbl_errs = conn.execute(f"PRAGMA foreign_key_check({tbl})").fetchall()
        assert len(tbl_errs) == 0, f"FK errors in {tbl}: {tbl_errs}"
    print("8c. Foreign key check on users, students, OTP tables: 0 errors")
    passed += 1
    fk_errors = []'''

assert target in c
c = c.replace(target, replacement, 1)

with open(r'C:\Users\callm\nagriksetu\test_suite_google_mobile.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated FK check in test_suite_google_mobile.py')
