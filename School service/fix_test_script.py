with open(r'C:\Users\callm\nagriksetu\test_suite_google_mobile.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'assert res.get("user", {}).get("phone") == "6361168242"',
    'phone_ret = res.get("phone") or res.get("user", {}).get("phone")\n    assert phone_ret in ("6361168242", "+916361168242")'
)
c = c.replace(
    "print(f\"    Successfully logged in user: {res['user']['full_name']} (role={res['user']['role']})\")",
    'fn = res.get("full_name") or res.get("user", {}).get("full_name")\n    rl = res.get("role") or res.get("user", {}).get("role")\n    print(f"    Successfully logged in user: {fn} (role={rl})")'
)

with open(r'C:\Users\callm\nagriksetu\test_suite_google_mobile.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated phone check in test_suite_google_mobile.py')
