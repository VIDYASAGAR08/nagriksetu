import urllib.request
import urllib.parse
import json

BASE_URL = "http://localhost:8001"

def login(identifier, password):
    url = f"{BASE_URL}/auth/login"
    data = urllib.parse.urlencode({"username": identifier, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        return json.loads(res.read().decode("utf-8"))

def get_children(token):
    url = f"{BASE_URL}/parent/children"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        return json.loads(res.read().decode("utf-8"))

def get_child_records(token, psid):
    url = f"{BASE_URL}/parent/children/{psid}/records"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")

def test_parents():
    test_cases = [
        ("Family 1 (3 Children) - Father", "ramesh.kumar@example.com", "Password@123", 3),
        ("Family 1 (3 Children) - Mother", "lakshmi.kumar@example.com", "Password@123", 3),
        ("Family 2 (2 Children) - Father", "suresh.patil@example.com", "Password@123", 2),
        ("Family 2 (2 Children) - Mother", "deepa.patil@example.com", "Password@123", 2),
        ("Family 3 (1 Child) - Father", "anand.sharma@example.com", "Password@123", 1),
        ("Family 3 (1 Child) - Mother", "priya.sharma@example.com", "Password@123", 1),
    ]

    tokens = {}
    for label, email, pwd, expected_count in test_cases:
        print(f"\n--- Testing Login: {label} ({email}) ---")
        login_res = login(email, pwd)
        token = login_res.get("access_token")
        user = login_res.get("user", {})
        tokens[email] = token
        print(f"Logged in successfully as: {user.get('full_name')} (Role: {user.get('role')})")

        children = get_children(token)
        print(f"Linked Children Count: {len(children)} (Expected: {expected_count})")
        for ch in children:
            print(f"  • {ch.get('student_name')} | PSID: {ch.get('permanent_student_id')} | Class: {ch.get('standard')}-{ch.get('section')} | School: {ch.get('school_name')}")

        assert len(children) == expected_count, f"Count mismatch for {label}: expected {expected_count}, got {len(children)}"

    # Security Test: Ramesh Kumar attempts to access Anand Sharma's child (Asha Sharma)
    print("\n--- Testing Security: Cross-Family Child Access Attempt ---")
    ramesh_token = tokens["ramesh.kumar@example.com"]
    sharma_psid = "NS-FB8336A812DE468FB8E475443CF673EB" # Asha Sharma
    code, body = get_child_records(ramesh_token, sharma_psid)
    print(f"Access attempt status code: {code} (Expected 404 or 403)")
    print(f"Response: {body}")
    assert code in [403, 404], f"Expected 403/404 on unauthorized child access, got {code}"
    print("[+] Cross-family access BLOCKED securely!")

    # Legitimate Test: Ramesh Kumar accesses own child Ananya Kumar
    ananya_psid = "NS-A0760A0835A448ADA7874F2038A5043E"
    code2, body2 = get_child_records(ramesh_token, ananya_psid)
    print(f"\nLegitimate child record access status: {code2}")
    print(f"Student: {body2.get('student', {}).get('student_name')}")
    assert code2 == 200

    print("\n[+] All Parent Portal authentication, linking and security tests PASSED!")

if __name__ == "__main__":
    test_parents()
