import subprocess
import html
import os

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
screenshot_dir = r"C:\Users\callm\nagriksetu\screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

tests = [
    {
        "name": "Homepage (Desktop 1440x900)",
        "url": "http://localhost:5173/#/",
        "window_size": "1440,2400",
        "screenshot": os.path.join(screenshot_dir, "phase1_homepage_desktop.png"),
        "expected_strings": [
            "Discover. Learn. Grow.",
            "Explore schools, PU colleges, diploma institutions and universities across Karnataka in one place.",
            "KARNATAKA STATE EDUCATION DISCOVERY PORTAL",
            "Explore Educational Pathways",
            "Standards 1 – 10 (K-10)",
            "Classes 11 – 12 (Higher Secondary)",
            "3-Year Technical Diplomas",
            "Colleges & Universities",
            "Browse by Karnataka District",
            "Bengaluru Urban",
            "Prominent State Institutions",
            "Parent & Guardian Access Portal",
            "How NagrikSetu Works in 3 Simple Steps",
            "vidhana_soudha"
        ]
    },
    {
        "name": "Homepage (Mobile 375x812)",
        "url": "http://localhost:5173/#/",
        "window_size": "375,2400",
        "screenshot": os.path.join(screenshot_dir, "phase1_homepage_mobile.png"),
        "expected_strings": [
            "Discover. Learn. Grow.",
            "Explore Educational Pathways",
            "Search Institutions"
        ]
    },
    {
        "name": "Institutions Directory (Desktop 1440x900)",
        "url": "http://localhost:5173/#/schools",
        "window_size": "1440,2400",
        "screenshot": os.path.join(screenshot_dir, "phase1_directory_desktop.png"),
        "expected_strings": [
            "Educational Institutions Directory",
            "Filter Catalog",
            "All Categories",
            "Schools (K-10)",
            "Degree & Universities",
            "Karnataka District",
            "Showing",
            "Institutions"
        ]
    },
    {
        "name": "Filtered Search - Engineering Colleges",
        "url": "http://localhost:5173/#/schools?category=UNDERGRADUATE",
        "window_size": "1440,2400",
        "screenshot": os.path.join(screenshot_dir, "phase1_directory_filtered.png"),
        "expected_strings": [
            "Educational Institutions Directory",
            "Ramaiah Institute of Technology",
            "R.V. College of Engineering",
            "Category: UNDERGRADUATE"
        ]
    }
]

print("=== STARTING PHASE 1 UI/UX VERIFICATION ===")
all_passed = True

for t in tests:
    print(f"\n--- Testing: {t['name']} ---")
    print(f"URL: {t['url']}")
    
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={t['window_size']}",
        "--virtual-time-budget=6000",
        "--run-all-compositor-stages-before-draw",
        f"--screenshot={t['screenshot']}",
        "--dump-dom",
        t['url']
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    dom = html.unescape(res.stdout)

    passed_count = 0
    for exp in t['expected_strings']:
        if exp in dom:
            print(f"  [PASS] Found: '{exp}'")
            passed_count += 1
        else:
            print(f"  [FAIL] Missing: '{exp}'")
            all_passed = False

    screenshot_exists = os.path.exists(t['screenshot']) and os.path.getsize(t['screenshot']) > 1000
    print(f"  Screenshot Saved: {t['screenshot']} (Size: {os.path.getsize(t['screenshot']) if screenshot_exists else 0} bytes)")
    print(f"  Result: {passed_count}/{len(t['expected_strings'])} strings matched.")

print("\n==========================================")
print(f"OVERALL PHASE 1 UI/UX STATUS: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
print("==========================================")
