import urllib.request
import urllib.parse
import json
import uuid

BASE_URL = "http://localhost:8001"

def post_json(endpoint, data):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def post_form(endpoint, form_data):
    data_bytes = urllib.parse.urlencode(form_data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=data_bytes,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def test_registration_suite():
    print("Testing Registration Suite for Formal Redesign...")
    pwd = "GovFormalPass@2026"

    # 1. Email registration
    email = f"formal.gov.{uuid.uuid4().hex[:6]}@karnataka.gov.in"
    code, res = post_json("/auth/register", {
        "full_name": "Dr. Rameshwar Rao",
        "email": email,
        "phone": None,
        "password": pwd,
        "confirm_password": pwd
    })
    print("1. Email Registration:", code, res.get("user_id"))
    assert code == 201
    assert "access_token" in res

    # 2. Mobile registration
    phone = f"98{str(uuid.uuid4().int)[:8]}"
    code, res = post_json("/auth/register", {
        "full_name": "Smt. Shailaja Devi",
        "email": None,
        "phone": phone,
        "password": pwd,
        "confirm_password": pwd
    })
    print("2. Mobile Registration:", code, res.get("user_id"))
    assert code == 201
    assert "access_token" in res

    # 3. Email login
    code, res = post_form("/auth/login", {"username": email, "password": pwd})
    print("3. Email Login:", code, res.get("role"))
    assert code == 200 and res.get("role") == "parent"

    # 4. Mobile login
    code, res = post_form("/auth/login", {"username": phone, "password": pwd})
    print("4. Mobile Login:", code, res.get("role"))
    assert code == 200 and res.get("role") == "parent"

    # 5. Duplicate email rejection
    code, res = post_json("/auth/register", {
        "full_name": "Duplicate Test",
        "email": email,
        "phone": None,
        "password": pwd,
        "confirm_password": pwd
    })
    print("5. Duplicate Email Rejection:", code)
    assert code == 409

    # 6. Duplicate phone rejection
    code, res = post_json("/auth/register", {
        "full_name": "Duplicate Test",
        "email": None,
        "phone": phone,
        "password": pwd,
        "confirm_password": pwd
    })
    print("6. Duplicate Phone Rejection:", code)
    assert code == 409

    print("ALL REGISTRATION API TESTS PASSED!")

if __name__ == "__main__":
    test_registration_suite()
