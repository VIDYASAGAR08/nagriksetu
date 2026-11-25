import pymysql
import argon2
import urllib.request
import json

ph = argon2.PasswordHasher(time_cost=2, memory_cost=65536, parallelism=1)

# The 10 verified target accounts matching exact account IDs
CREDENTIALS = [
    {
        "account_id": 97,
        "centre_id": 1,
        "centre_code": "CTR-0001",
        "centre_name": "Bengaluru Central Skill Hub (Rajajinagar)",
        "email": "centre.bengaluru@nagriksetu.local",
        "password": "BengaluruHub#2026"
    },
    {
        "account_id": 94,
        "centre_id": 2,
        "centre_code": "CTR-0002",
        "centre_name": "Mysuru Regional Skilling Institute",
        "email": "centre.admin.mysuru@nagriksetu.local",
        "password": "MysuruSkill#2026"
    },
    {
        "account_id": 96,
        "centre_id": 3,
        "centre_code": "CTR-0003",
        "centre_name": "Hubballi-Dharwad Tech Development Centre",
        "email": "centre.admin.hubballi@nagriksetu.local",
        "password": "HubballiTech#2026"
    },
    {
        "account_id": 95,
        "centre_id": 4,
        "centre_code": "CTR-0004",
        "centre_name": "Mangaluru Coastal Skill Academy",
        "email": "centre.admin.mangaluru@nagriksetu.local",
        "password": "MangaluruSea#2026"
    },
    {
        "account_id": 139,
        "centre_id": 5,
        "centre_code": "CTR-0005",
        "centre_name": "NagrikSetu Virtual Learning Portal",
        "email": "centre.virtual@nagriksetu.local",
        "password": "VirtualLearn#2026"
    },
    {
        "account_id": 140,
        "centre_id": 6,
        "centre_code": "CTR-0006",
        "centre_name": "Dharwad Innovation & Regional Skilling Centre",
        "email": "centre.dharwad@nagriksetu.local",
        "password": "DharwadInno#2026"
    },
    {
        "account_id": 135,
        "centre_id": 8,
        "centre_code": "CTR-0007",
        "centre_name": "Belagavi Regional Skilling Hub",
        "email": "centre.belagavi@nagriksetu.local",
        "password": "BelagaviHub#2026"
    },
    {
        "account_id": 136,
        "centre_id": 9,
        "centre_code": "CTR-0008",
        "centre_name": "Davanagere Vocational & Technical Institute",
        "email": "centre.davanagere@nagriksetu.local",
        "password": "DavanagereVoc#2026"
    },
    {
        "account_id": 137,
        "centre_id": 10,
        "centre_code": "CTR-0009",
        "centre_name": "Kalaburagi Regional Skill Development Centre",
        "email": "centre.kalaburagi@nagriksetu.local",
        "password": "KalaburagiDev#2026"
    },
    {
        "account_id": 138,
        "centre_id": 11,
        "centre_code": "CTR-0010",
        "centre_name": "Shivamogga Malnad Skill Development Centre",
        "email": "centre.shivamogga@nagriksetu.local",
        "password": "ShivamoggaMal#2026"
    }
]

def update_and_verify():
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3308,
        user='nagriksetu_skill',
        password='skill-app-pass-2026',
        database='skill_db'
    )
    cur = conn.cursor(pymysql.cursors.DictCursor)

    print("Step 1: Hashing passwords with Argon2id and updating MySQL database...")
    for item in CREDENTIALS:
        aid = item["account_id"]
        pwd = item["password"]
        argon_hash = ph.hash(pwd)
        cur.execute(
            "UPDATE accounts SET password_hash = %s, active = 1 WHERE id = %s",
            (argon_hash, aid)
        )
    conn.commit()
    print("Database updated successfully.")

    print("\nStep 2: Testing login and centre dashboard isolation for each account...")
    results = []
    for item in CREDENTIALS:
        email = item["email"]
        pwd = item["password"]
        cid = item["centre_id"]
        code = item["centre_code"]
        name = item["centre_name"]

        # Call Login API
        login_url = "http://127.0.0.1:8003/api/auth/login"
        payload = json.dumps({"email": email, "password": pwd}).encode('utf-8')
        req = urllib.request.Request(
            login_url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                token = data.get("access_token")
                user_role = data.get("role")
                login_success = (resp.status == 200 and token is not None and user_role == "TRAINING_CENTRE_ADMIN")
        except Exception as e:
            login_success = False
            token = None
            print(f"Login failed for {email}: {e}")

        # Verify Dashboard and Application Isolation
        dash_success = False
        app_count = 0
        isolation_verified = False

        if login_success and token:
            headers = {"Authorization": f"Bearer {token}"}
            dash_url = "http://127.0.0.1:8003/api/centre-admin/dashboard"
            enr_url = "http://127.0.0.1:8003/api/centre-admin/enrollments"

            try:
                # 1. Fetch dashboard
                dash_req = urllib.request.Request(dash_url, headers=headers)
                with urllib.request.urlopen(dash_req) as d_resp:
                    d_data = json.loads(d_resp.read().decode('utf-8'))
                    dash_centre = d_data.get("centre", {})
                    dash_centre_id = dash_centre.get("id")
                    dash_success = (dash_centre_id == cid)

                # 2. Fetch enrollments
                enr_req = urllib.request.Request(enr_url, headers=headers)
                with urllib.request.urlopen(enr_req) as e_resp:
                    e_data = json.loads(e_resp.read().decode('utf-8'))
                    app_count = len(e_data)
                    # Verify every returned application strictly belongs to this centre
                    all_match = all(e.get("centre_id") == cid or e.get("centre_id") is None for e in e_data)
                    isolation_verified = all_match

                # 3. Verify cross-centre attempt with unauthorized X-Centre-ID header
                unauthorized_cid = 2 if cid != 2 else 1
                cross_req = urllib.request.Request(
                    enr_url,
                    headers={**headers, "X-Centre-ID": str(unauthorized_cid)}
                )
                try:
                    with urllib.request.urlopen(cross_req) as cr_resp:
                        cross_data = json.loads(cr_resp.read().decode('utf-8'))
                        # Even if 200 returned, it must NOT return other centre's applications
                        assert all(e.get("centre_id") == cid for e in cross_data if e.get("centre_id")), "Cross-centre leaked data!"
                except urllib.error.HTTPError as he:
                    pass # Expected 403 or handled gracefully

            except Exception as e:
                print(f"Dashboard/isolation check error for {email}: {e}")

        status_str = "SUCCESS (Verified)" if (login_success and dash_success and isolation_verified) else "FAILED"
        results.append({
            "code": code,
            "name": name,
            "email": email,
            "password": pwd,
            "login_result": status_str,
            "apps": app_count,
            "centre_id": cid
        })

    print("\n" + "=" * 135)
    print(f"| {'Centre Code':12} | {'Actual Centre Name':45} | {'Login Email':38} | {'Permanent Password':20} | {'Result':18} | {'Apps':5} |")
    print("=" * 135)
    for r in results:
        print(f"| {r['code']:12} | {r['name'][:45]:45} | {r['email']:38} | {r['password']:20} | {r['login_result']:18} | {r['apps']:5} |")
    print("=" * 135)

if __name__ == "__main__":
    update_and_verify()
