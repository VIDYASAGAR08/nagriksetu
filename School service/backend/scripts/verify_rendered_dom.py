import subprocess
import html

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

test_cases = [
    ("COL001", "Ramaiah Institute of Technology (MSRIT)", True),
    ("SCH001", "Government Model School", True),
    ("COL002", "R.V. College of Engineering (RVCE)", True),
    ("SCH011", "Tumakuru Model School", False)
]

for sid, label, has_divisions in test_cases:
    print(f"\n========================================================")
    print(f"=== DOM Verification for {sid}: {label} ===")
    print(f"========================================================")

    url = f"http://localhost:5173/#/schools/{sid}"
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--virtual-time-budget=6000",
        "--run-all-compositor-stages-before-draw",
        "--dump-dom",
        url
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    dom = html.unescape(res.stdout)

    expected_sections = [
        "About the Institution",
        "Facilities & Infrastructure",
        "Hostel & Residential Accommodation",
        "Transportation & Bus Fleet",
        "Academic Offerings & Programme Structure",
        "Admissions & Fee Guidelines",
        "Verified Institutional Achievements & Accreditations",
        "Enrolled Students Directory"
    ]

    all_passed = True
    for sec in expected_sections:
        present = sec in dom
        status_str = "PASS" if present else "FAIL"
        if not present: all_passed = False
        print(f"[{status_str}] Section: {sec}")

    if has_divisions:
        div_present = "Academic Divisions & Constituent Wings" in dom
        status_str = "PASS" if div_present else "FAIL"
        if not div_present: all_passed = False
        print(f"[{status_str}] Section: Academic Divisions & Constituent Wings")

    print(f"Overall Result for {sid}: {'ALL 10 SECTIONS VERIFIED' if all_passed else 'SOME SECTIONS MISSING'}")
    print(f"Rendered DOM Length: {len(dom)} characters")
