import subprocess
import html
import os
import shutil
import urllib.request
import json

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
screenshot_dir = r"C:\Users\callm\nagriksetu\screenshots"
brain_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
os.makedirs(screenshot_dir, exist_ok=True)

# 1. Test Backend Endpoints
print("=== VERIFYING BACKEND APIS ===")
# A. Seat availability for SCH001
try:
    res = urllib.request.urlopen("http://localhost:8001/schools/SCH001/seat-availability")
    sch_data = json.loads(res.read())
    print(f"  [PASS] SCH001 Seat Availability: Capacity={sch_data['total_sanctioned_capacity']}, Current={sch_data['total_current_strength']}, Available={sch_data['total_available_seats']}")
except Exception as e:
    print(f"  [FAIL] SCH001 Seat Availability: {e}")

# B. Seat availability for COL001
try:
    res = urllib.request.urlopen("http://localhost:8001/schools/COL001/seat-availability")
    col_data = json.loads(res.read())
    print(f"  [PASS] COL001 Seat Availability: Capacity={col_data['total_sanctioned_capacity']}, Current={col_data['total_current_strength']}, Available={col_data['total_available_seats']}")
except Exception as e:
    print(f"  [FAIL] COL001 Seat Availability: {e}")

# C. Multi-School Compare Endpoint
try:
    req = urllib.request.Request(
        "http://localhost:8001/schools/compare",
        data=json.dumps({"school_ids": ["COL001", "COL002", "COL003"]}).encode(),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    compare_data = json.loads(res.read())
    print(f"  [PASS] POST /schools/compare returned {len(compare_data)} institutions: {[x['school_id'] for x in compare_data]}")
except Exception as e:
    print(f"  [FAIL] POST /schools/compare: {e}")

# 2. Test Frontend Renderings & Screenshots with Edge Headless
tests = [
    {
        "name": "Homepage Hero & AI Entry (Desktop 1440x900)",
        "url": "http://localhost:5173/#/",
        "window_size": "1440,2000",
        "file_name": "phase2_homepage_hero_desktop.png",
        "expected_strings": [
            "Discover. Learn. Grow.",
            "Find the right educational institution for your child's future.",
            "KARNATAKA STATE EDUCATION DISCOVERY PORTAL",
            "Ask AI Assistant",
            "NagrikSetu is a transparent public educational discovery",
            "Search Institutions"
        ]
    },
    {
        "name": "Homepage Responsive View (Mobile 375x812)",
        "url": "http://localhost:5173/#/",
        "window_size": "375,1800",
        "file_name": "phase2_homepage_hero_mobile.png",
        "expected_strings": [
            "Discover. Learn. Grow.",
            "Find the right educational institution for your child's future.",
            "Ask AI Assistant"
        ]
    },
    {
        "name": "Directory with Live Seats & Compare (Desktop 1440x1200)",
        "url": "http://localhost:5173/#/schools",
        "window_size": "1440,2400",
        "file_name": "phase2_directory_seats_compare.png",
        "expected_strings": [
            "Educational Institutions Directory",
            "Filter Catalog",
            "Programme / Specialisation",
            "Show Only Open Admissions",
            "+ Compare",
            "Seats Open"
        ]
    },
    {
        "name": "School Details Live Seat Quotas (SCH001)",
        "url": "http://localhost:5173/#/schools/SCH001",
        "window_size": "1440,2600",
        "file_name": "phase2_school_details_seat_quota.png",
        "expected_strings": [
            "Government Model School",
            "Live Seat Availability & Quota",
            "Sanctioned Capacity",
            "Current Enrolment",
            "Available Seats",
            "Apply for Initial Admission"
        ]
    },
    {
        "name": "College Details Live Seat Quotas (COL001)",
        "url": "http://localhost:5173/#/schools/COL001",
        "window_size": "1440,2600",
        "file_name": "phase2_college_details_seat_quota.png",
        "expected_strings": [
            "Ramaiah Institute of Technology",
            "Live Seat Availability & Quota",
            "Sanctioned Capacity",
            "Available Seats"
        ]
    }
]

print("\n=== STARTING BROWSER TESTING & SCREENSHOT CAPTURE ===")
all_passed = True

for t in tests:
    print(f"\n--- Testing: {t['name']} ---")
    dest_path = os.path.join(screenshot_dir, t['file_name'])
    brain_path = os.path.join(brain_dir, t['file_name'])
    
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={t['window_size']}",
        "--virtual-time-budget=6000",
        "--run-all-compositor-stages-before-draw",
        f"--screenshot={dest_path}",
        "--dump-dom",
        t['url']
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    dom = html.unescape(res.stdout)

    matched = 0
    for exp in t['expected_strings']:
        if exp in dom:
            print(f"  [PASS] Found: '{exp}'")
            matched += 1
        else:
            print(f"  [FAIL] Missing: '{exp}'")
            all_passed = False

    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        shutil.copyfile(dest_path, brain_path)
        print(f"  Screenshot Saved & Synced: {t['file_name']} ({os.path.getsize(dest_path)} bytes)")
    else:
        print(f"  [WARN] Screenshot not generated for {t['name']}")

print("\n==========================================")
print(f"OVERALL PHASE 2 STATUS: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
print("==========================================")
