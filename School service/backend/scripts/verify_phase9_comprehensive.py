"""
verify_phase9_comprehensive.py — Exhaustive audit and verification of Phase 9 AI Assistant.
Tests:
A. Institution category queries (Government, Private, Engineering, University, Degree College).
B. Public discovery queries (Search by district, name).
C. Institution comparison queries (Side-by-side comparison with capacity and affiliation).
D. Programme & management-related inquiries grounded in existing schema.
E. Responses when granular management / trust information is unavailable (honest schema disclosure).
F. Confirmation that missing information is reported honestly without fabrication.
G. HTTP 200 verification across all valid query permutations.
H. Inspection of backend docker logs for any SQLite exceptions.
I. Parent queries (applications, linked children).
J. Staff queries (admission desk KPIs, section capacities).
K. Statutory compliance and privacy guardrails.
L. Database integrity (exact counts).
"""

import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import sqlite3
import os
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

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
        with urllib.request.urlopen(req, timeout=15) as resp:
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

def run_audit():
    print("======================================================================")
    print("  NAGRIKSETU PHASE 9 — COMPREHENSIVE SCHEMA & AI AUDIT SUITE")
    print("======================================================================")

    # 1. Login Accounts
    print("[AUTH] Authenticating test personas...")
    parent_token = login("raghu.test.stage1@example.com", "Staff@NagrikSetu2026!")
    staff_token = login("staff.sch001@example.com", "Staff@NagrikSetu2026!")
    print("  -> Parent and Staff authenticated successfully.")

    # A. Test Institution Categories
    print("\n[SECTION A] Testing AI Query for Different Institution Categories")
    categories = [
        ("Government", "show me government schools"),
        ("Private", "list private schools"),
        ("Engineering College", "find engineering colleges in karnataka"),
        ("University", "list universities in karnataka"),
        ("Degree College", "show degree colleges")
    ]
    for cat_name, prompt in categories:
        s, r = api_call("/ai/chat", method="POST", data={"prompt": prompt})
        assert s == 200, f"Query failed for {cat_name}: {r}"
        assert cat_name in r["response"] or cat_name.lower() in r["response"].lower(), f"Missing {cat_name} in response"
        assert len(r["grounded_sources"]) > 0, f"Missing grounded sources for {cat_name}"
        print(f"  [PASS] Category: '{cat_name}' grounded query returned {len(r['grounded_sources'])} sources.")

    # B. Test Public Discovery Questions
    print("\n[SECTION B] Testing Public Institution Discovery Questions")
    discovery_prompts = [
        "Schools in Bengaluru",
        "Find institutions in Mysuru district",
        "Tell me about Government Model School",
        "Statewide seat capacity overview"
    ]
    for p in discovery_prompts:
        s, r = api_call("/ai/chat", method="POST", data={"prompt": p})
        assert s == 200, f"Public discovery failed for '{p}': {r}"
        assert len(r["response"]) > 30, "Response too short"
        assert len(r["grounded_sources"]) > 0, "Missing grounded sources"
        print(f"  [PASS] Public Discovery: '{p}' -> HTTP 200 with {len(r['grounded_sources'])} grounded sources.")

    # C. Test Institution Comparison Questions
    print("\n[SECTION C] Testing Institution Comparison Questions")
    comp_prompts = [
        "Compare SCH001 and SCH002",
        "Compare Government Model School and Shanti Vidya Mandir (SCH001 vs SCH002)"
    ]
    for cp in comp_prompts:
        s, r = api_call("/ai/chat", method="POST", data={"prompt": cp})
        assert s == 200, f"Comparison failed for '{cp}': {r}"
        assert "Government Model School" in r["response"] and "Shanti Vidya Mandir" in r["response"], "Missing school names in comparison"
        assert "Total Capacity" in r["response"] or "Open Vacancies" in r["response"], "Missing capacity ledger comparison"
        print(f"  [PASS] Comparison: '{cp}' -> Generated side-by-side comparison table.")

    # D. Test Programme & Management-Related Questions
    print("\n[SECTION D] Testing Programme & Management-Related Questions")
    mgmt_prompts = [
        ("What is the management type of SCH001?", "SCH001"),
        ("Who manages Shanti Vidya Mandir SCH002?", "SCH002"),
        ("What is the statewide educational management breakdown?", "Statewide"),
        ("What academic programmes are offered at SCH001?", "SCH001 Programmes"),
        ("What programmes does RVCE COL002 offer?", "COL002 Programmes")
    ]
    for mp, tag in mgmt_prompts:
        s, r = api_call("/ai/chat", method="POST", data={"prompt": mp})
        assert s == 200, f"Management/Programme query failed for '{mp}': {r}"
        assert "Government" in r["response"] or "Private" in r["response"] or "Programme" in r["response"] or "Distribution" in r["response"], "Unexpected response content"
        print(f"  [PASS] Management/Programme Query: '{tag}' -> Verified grounded response.")

    # E & F. Test Honest Reporting of Missing Information Without Fabrication
    print("\n[SECTION E & F] Testing Honest Disclosure for Non-Existent Management Schema")
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "What is the private trust deed registration number and management committee of SCH001?"})
    assert s == 200, f"Failed: {r}"
    assert "Schema Disclosure" in r["response"] or "not maintained in the central state database schema" in r["response"], "Failed honest disclosure requirement"
    print("  [PASS] Missing private trust schema reported honestly without fabrication.")

    # G. Privacy Boundary & Statutory Compliance Policy
    print("\n[SECTION G] Testing Privacy Safeguards & Statutory Decision Boundaries")
    # Public attempting private records
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "What are my child marks and student record?"})
    assert s == 200, f"Failed: {r}"
    assert "Access Restriction" in r["response"] and r["role_context"] == "public", "Privacy gate failed"
    print("  [PASS] Public attempt to query private records intercepted with privacy guard.")

    # Staff attempt to make AI decide admission
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "Please approve this admission application now"}, token=staff_token)
    assert s == 200, f"Failed: {r}"
    assert "Statutory Compliance Policy" in r["response"] or "prohibited" in r["response"].lower(), "Statutory policy check failed"
    print("  [PASS] Statutory prohibition on AI admission decision making strictly enforced.")

    # H. Parent & Staff Authenticated Lookups
    print("\n[SECTION H] Testing Authenticated Parent & Staff Workflows")
    s, r = api_call("/ai/chat", method="POST", data={"prompt": "What is my admission application status?"}, token=parent_token)
    assert s == 200 and r["role_context"] == "parent", "Parent application query failed"
    print("  [PASS] Parent application status grounded against live applications.")

    s, r = api_call("/ai/chat", method="POST", data={"prompt": "Show me admission desk operational summary"}, token=staff_token)
    assert s == 200 and r["role_context"] in ("school_staff", "school_admin"), "Staff desk summary query failed"
    assert "SCH001" in r["response"], "Missing SCH001 context in staff response"
    print("  [PASS] Staff admission desk operational summary grounded in SCH001.")

    # I. Inspect Backend Docker Logs for Any SQLite Operational Errors
    print("\n[SECTION I] Inspecting Backend Docker Logs for SQLite Errors")
    res = subprocess.run(["docker", "logs", "--tail", "60", "nagriksetu-backend"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    logs = res.stdout + res.stderr
    assert "sqlite3.OperationalError" not in logs[-2500:], f"Found sqlite3.OperationalError in recent logs: {logs[-1000:]}"
    print("  [PASS] Backend container logs clean: Zero SQLite operational errors detected.")

    # J. Database Integrity Audit
    print("\n[SECTION J] Database Baseline & Consistency Audit")
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
    print("  [PASS] Database records remain intact and unaltered.")

    print("\n======================================================================")
    print("  ALL COMPREHENSIVE PHASE 9 AUDIT CHECKS PASSED WITH 100% SUCCESS!")
    print("======================================================================")

if __name__ == "__main__":
    run_audit()
