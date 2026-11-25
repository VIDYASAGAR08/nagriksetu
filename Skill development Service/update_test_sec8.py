path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\test_comprehensive_regression.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """    # Test on Centre 11 (Shivamogga)
    c11_login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "centre.shivamogga@nagriksetu.local", "password": "Shv#j5E!5Ls0!"})
    c11_token = c11_login.json().get("access_token")
    temp_pwd = "Shv#NewPass2026Updated!"
    # Change password
    r_chg = requests.post(
        f"{BASE_URL}/api/auth/change-password",
        json={"current_password": "Shv#j5E!5Ls0!", "new_password": temp_pwd, "confirm_password": temp_pwd},
        headers={"Authorization": f"Bearer {c11_token}"}
    )
    # Verify new password login
    r_verify_new = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "centre.shivamogga@nagriksetu.local", "password": temp_pwd})
    # Restore back to original rotated password
    if r_verify_new.status_code == 200:
        c11_new_token = r_verify_new.json().get("access_token")
        requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={"current_password": temp_pwd, "new_password": "Shv#j5E!5Ls0!", "confirm_password": "Shv#j5E!5Ls0!"},
            headers={"Authorization": f"Bearer {c11_new_token}"}
        )"""

new_block = """    # Test on Centre 11 (Shivamogga)
    c11_login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "centre.shivamogga@nagriksetu.local", "password": "ShivamoggaMal#2026"})
    c11_token = c11_login.json().get("access_token")
    temp_pwd = "Shv#NewPass2026Updated!"
    # Change password
    r_chg = requests.post(
        f"{BASE_URL}/api/auth/change-password",
        json={"current_password": "ShivamoggaMal#2026", "new_password": temp_pwd, "confirm_password": temp_pwd},
        headers={"Authorization": f"Bearer {c11_token}"}
    )
    # Verify new password login
    r_verify_new = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "centre.shivamogga@nagriksetu.local", "password": temp_pwd})
    # Restore back to original permanent password
    if r_verify_new.status_code == 200:
        c11_new_token = r_verify_new.json().get("access_token")
        requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={"current_password": temp_pwd, "new_password": "ShivamoggaMal#2026", "confirm_password": "ShivamoggaMal#2026"},
            headers={"Authorization": f"Bearer {c11_new_token}"}
        )"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated Section 8 in test_comprehensive_regression.py")
else:
    print("Could not find Section 8 in test_comprehensive_regression.py")
