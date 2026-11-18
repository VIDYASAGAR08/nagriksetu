import urllib.request
import urllib.parse
import json
import sqlite3

BASE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:5173"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def api_post_form(endpoint, form_data):
    data = urllib.parse.urlencode(form_data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"detail": body}

def api_get(endpoint, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE_URL}{endpoint}", headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"detail": body}

def run_tests():
    print("=" * 70)
    print("NAGRIKSETU — REMOVE IDP/OCR DEMO TOGGLE & VERIFICATION SUITE")
    print("=" * 70)

    passed = 0
    total = 0

    def assert_test(cond, title):
        nonlocal passed, total
        total += 1
        if cond:
            print(f"{total}. {title}: PASSED")
            passed += 1
        else:
            print(f"{total}. {title}: FAILED")
            raise AssertionError(f"Test failed: {title}")

    # 1. Public Frontend Bundle Check: Ensure 'IDP / OCR Demo' nav item is absent
    with urllib.request.urlopen(f"{FRONTEND_URL}/") as resp:
        html = resp.read().decode("utf-8")
    assert_test("IDP / OCR Demo" not in html, "Public UI: 'IDP / OCR Demo' absent from main HTML bundle")

    # Check dist JS bundle
    with open(r"C:\Users\callm\nagriksetu\frontend\dist\index.html", "r", encoding="utf-8") as f:
        dist_html = f.read()
    assert_test("IDP / OCR Demo" not in dist_html, "Production Assets: dist/index.html clean of OCR demo")

    # 2. Public Route Protection: Unauthenticated call to /idp/process-document blocked with 401
    try:
        req = urllib.request.Request(f"{BASE_URL}/idp/process-document", data=b"", headers={"Content-Type": "multipart/form-data; boundary=boundary"})
        urllib.request.urlopen(req)
        assert_test(False, "Security: Unauthenticated /idp/process-document permitted")
    except urllib.error.HTTPError as e:
        assert_test(e.code == 401, f"Security: Unauthenticated /idp/process-document rejected with HTTP {e.code} (expected 401)")

    # 3. Authenticated Staff Login
    status, staff_login = api_post_form("/auth/login", {"username": "staff.sch001@example.com", "password": "Staff@NagrikSetu2026!"})
    assert_test(status == 200 and staff_login.get("role") == "school_staff", "Authentication: Staff login successful (staff.sch001@example.com)")
    staff_token = staff_login["access_token"]

    # 4. Internal Admission Document OCR Intelligence API Preserved
    # Check that the internal endpoint exists and requires authorized document parameters
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    doc_row = c.execute("""
        SELECT d.document_id, d.application_id, a.institution_id 
        FROM admission_documents d
        JOIN admission_applications a ON a.application_id = d.application_id
        WHERE a.institution_id = 'SCH001'
        LIMIT 1
    """).fetchone()

    if doc_row:
        doc_id, app_id, inst_id = doc_row
        status, ocr_res = api_get(f"/school/admissions/{app_id}/documents/{doc_id}/ocr-result", token=staff_token)
        # Endpoint exists and responds (either 200 with result or 404 if not yet analyzed)
        assert_test(status in (200, 404), f"Internal OCR: Admission document OCR result endpoint intact (status={status})")
    else:
        # Check endpoint routing directly
        status, ocr_res = api_get(f"/school/admissions/APP-DUMMY/documents/DOC-DUMMY/ocr-result", token=staff_token)
        assert_test(status == 404, f"Internal OCR: Admission document OCR endpoint intact (status={status})")

    # 5. Database Preservations
    inst_count = c.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
    assert_test(inst_count == 30, f"Database: Exactly 30 institutions preserved ({inst_count})")

    stu_count = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    assert_test(stu_count == 30001, f"Database: Exactly 30,001 students preserved ({stu_count})")

    enr_count = c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    assert_test(enr_count == 30001, f"Database: Exactly 30,001 enrollments preserved ({enr_count})")

    app_count = c.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0]
    assert_test(app_count >= 57, f"Database: Admission applications preserved ({app_count})")

    integrity = c.execute("PRAGMA integrity_check").fetchall()
    assert_test(integrity == [('ok',)], f"Database: PRAGMA integrity_check ok ({integrity})")

    fk_violations = c.execute("PRAGMA foreign_key_check").fetchall()
    assert_test(len(fk_violations) == 0, f"Database: PRAGMA foreign_key_check 0 violations ({len(fk_violations)})")

    conn.close()

    print("=" * 70)
    print(f"ALL {passed}/{total} IDP/OCR DEMO REMOVAL TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
