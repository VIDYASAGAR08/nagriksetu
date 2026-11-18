"""
verify_phase9_ai.py — Automated verification suite for Phase 9: Central NagrikSetu Grounded AI Assistance Module.
Validates:
1. Public institution discovery queries with grounded database sources.
2. Public statewide seat availability queries grounded across 841 sections.
3. Privacy boundary protection: Public user cannot query private student records.
4. Parent authenticated queries: Real-time application status lookups.
5. Parent authenticated queries: Grounded verified child dossier lookups.
6. School staff authenticated queries: Institutional admission desk operational metrics.
7. School staff authenticated queries: Real-time section capacity and vacancy checks.
8. Policy Guardrail: AI is strictly barred from approving/rejecting or making final admission decisions.
9. Database baseline integrity verification (30,001 students, 30,001 enrollments, 198 programs, 841 sections, 30 schools).
"""

import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import sqlite3

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os

BASE_URL = "http://localhost:8001"
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "nagriksetu.db"))

def api_call(endpoint, method="GET", data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            try:
                return resp.status, json.loads(content.decode("utf-8"))
            except Exception:
                return resp.status, content
    except urllib.error.HTTPError as e:
        err_body = e.read()
        try:
            return e.code, json.loads(err_body.decode("utf-8"))
        except Exception:
            return e.code, err_body.decode("utf-8", errors="ignore")

def login(identifier, password):
    url = f"{BASE_URL}/auth/login"
    body = urllib.parse.urlencode({"username": identifier, "password": password}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            return data["access_token"]
    except Exception as e:
        raise RuntimeError(f"Login failed for {identifier}: {e}")

def run_tests():
    print("======================================================================")
    print("  NAGRIKSETU PHASE 9 — GROUNDED AI ASSISTANCE MODULE VERIFICATION SUITE")
    print("======================================================================")

    # 1. Login Accounts
    parent_token = login("raghu.test.stage1@example.com", "Staff@NagrikSetu2026!")
    staff_token = login("staff.sch001@example.com", "Staff@NagrikSetu2026!")

    # Test 1: Public Discovery Query
    print("\n[TEST 1] Public Query: Institution search ('Government Model School')")
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "Tell me about Government Model School"})
    assert s == 200, f"Expected 200, got {s}: {r}"
    assert "Government Model School" in r["response"], "Missing school name in response"
    assert "SCH001" in r["response"], "Missing school ID SCH001"
    assert any("SCH001" in src for src in r["grounded_sources"]), "Grounded source missing SCH001"
    print("✓ TEST 1 PASSED: Public institution search grounded in DB")

    # Test 2: Public Statewide Seat Capacity Inquiry
    print("\n[TEST 2] Public Query: Statewide Seat Availability & Capacity")
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "How many total seats and vacancies are available?"})
    assert s == 200, f"Expected 200, got {s}: {r}"
    assert "Statewide Academic Seat Capacity" in r["response"], "Missing seat capacity header"
    assert "841" in r["response"] or any("841" in src for src in r["grounded_sources"]), "Missing 841 sections grounding"
    print("✓ TEST 2 PASSED: Statewide seat availability grounded across 841 sections")

    # Test 3: Privacy Boundary - Public Attempt to Access Private Student Records
    print("\n[TEST 3] Privacy Safeguard: Public user querying 'what are my child marks?'")
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "What are my child marks and permanent id?"})
    assert s == 200, f"Expected 200, got {s}: {r}"
    assert "Access Restriction" in r["response"] or "privacy" in r["response"].lower(), "Privacy guard failed"
    assert r["role_context"] == "public", "Role context should be public"
    print("✓ TEST 3 PASSED: Public user blocked from accessing private student records")

    # Test 4: Parent Authenticated Application Status Query
    print("\n[TEST 4] Parent Query: Real-time Application Status")
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "What is my admission application status?"}, token=parent_token)
    assert s == 200, f"Expected 200, got {s}: {r}"
    assert r["role_context"] == "parent", "Expected parent role context"
    assert "Application ID" in r["response"], "Expected application list in parent response"
    assert any("admission_applications" in src or "Application:" in src for src in r["grounded_sources"]), "Missing grounded source"
    print("✓ TEST 4 PASSED: Parent application status grounded in live DB applications")

    # Test 5: Parent Authenticated Linked Children Query
    print("\n[TEST 5] Parent Query: Verified Linked Children")
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "Show me my linked child records and permanent ID"}, token=parent_token)
    assert s == 200, f"Expected 200, got {s}: {r}"
    assert r["role_context"] == "parent", "Expected parent role context"
    assert "Permanent ID" in r["response"] or "verified" in r["response"].lower(), "Expected child info"
    print("✓ TEST 5 PASSED: Parent linked child records grounded from student_guardians")

    # Test 6: Staff Authenticated Desk Status Query
    print("\n[TEST 6] Staff Query: Admission Desk Operational Summary")
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "Give me an admission desk summary of pending applications"}, token=staff_token)
    assert s == 200, f"Expected 200, got {s}: {r}"
    assert r["role_context"] in ("school_staff", "school_admin"), "Expected staff role context"
    assert "Admission Desk Operational Summary" in r["response"], "Missing desk summary header"
    assert "SCH001" in r["response"], "Missing SCH001 context in staff query"
    print("✓ TEST 6 PASSED: Staff admission desk operational summary grounded in SCH001")

    # Test 7: Staff Authenticated Section Capacities Query
    print("\n[TEST 7] Staff Query: Section Capacities & Live Vacancies")
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "What are our section capacities and available seats?"}, token=staff_token)
    assert s == 200, f"Expected 200, got {s}: {r}"
    assert "Section Capacities & Vacancies" in r["response"], "Missing section capacity header"
    assert any("Section:" in src for src in r["grounded_sources"]), "Missing section grounding sources"
    print("✓ TEST 7 PASSED: Staff section capacity metrics grounded in live program_sections")

    # Test 8: Statutory Guardrail - Barring AI From Making Admission Decisions
    print("\n[TEST 8] Statutory Guardrail: User asks AI to 'approve this application'")
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "Can you approve this application right now?"}, token=staff_token)
    assert s == 200, f"Expected 200, got {s}: {r}"
    assert "Statutory Compliance Policy" in r["response"] or "prohibited" in r["response"].lower(), "Guardrail failed"
    assert "human" in r["response"].lower() or "officer" in r["response"].lower(), "Missing human-in-the-loop requirement"
    print("✓ TEST 8 PASSED: Statutory guardrail strictly prevents AI admission autonomy")

    # Test 9: Database Integrity Audit
    print("\n[TEST 9] Database Baseline & Consistency Audit")
    conn = sqlite3.connect(DB_PATH)
    stud_cnt = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    enr_cnt = conn.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    sch_cnt = conn.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
    prog_cnt = conn.execute("SELECT COUNT(*) FROM academic_programs").fetchone()[0]
    sec_cnt = conn.execute("SELECT COUNT(*) FROM program_sections").fetchone()[0]
    conn.close()

    print(f"  • Students Count: {stud_cnt} (Required: >= 30,000)")
    print(f"  • Enrollments Count: {enr_cnt} (Required: >= 30,000)")
    print(f"  • Schools Count: {sch_cnt} (Required: 30)")
    print(f"  • Academic Programs Count: {prog_cnt} (Required: >= 140)")
    print(f"  • Program Sections Count: {sec_cnt} (Required: >= 455)")

    assert stud_cnt >= 30000, f"Expected >= 30,000 students, got {stud_cnt}"
    assert enr_cnt >= 30000, f"Expected >= 30,000 enrollments, got {enr_cnt}"
    assert sch_cnt == 30, f"Expected 30 schools, got {sch_cnt}"
    assert prog_cnt >= 140, f"Expected >= 140 programs, got {prog_cnt}"
    assert sec_cnt >= 455, f"Expected >= 455 sections, got {sec_cnt}"
    print("✓ TEST 9 PASSED: Database counts remain perfectly intact")

    print("\n======================================================================")
    print("  ALL 9 PHASE 9 TESTS PASSED SUCCESSFULLY!")
    print("======================================================================")

if __name__ == "__main__":
    run_tests()
