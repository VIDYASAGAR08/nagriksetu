import subprocess
import time
import os

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

remaining = [
    (
        "http://localhost:5173/#/schools",
        "cleaned_navigation_schools.png",
        "Explore Institutions Directory Page with Cleaned Navigation"
    ),
    (
        "http://localhost:5173/#/login",
        "cleaned_login_category_selection.png",
        "User Category Selection Screen (Cleaned of Demo References)"
    ),
    (
        "http://localhost:5173/#/ocr-demo",
        "cleaned_ocr_demo_redirect.png",
        "Automatic Redirect of Legacy /ocr-demo Route to /schools Directory"
    ),
]

for url, filename, desc in remaining:
    out_path = os.path.join(artifacts_dir, filename)
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1280,850",
        "--virtual-time-budget=2500",
        f"--screenshot={out_path}",
        url
    ]
    print(f"Capturing: {desc} -> {filename}...")
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=15)
        print(f"Captured {filename}: returncode={res.returncode}")
    except Exception as e:
        print(f"Error capturing {filename}: {e}")
    time.sleep(1)

print("Finished capturing remaining screenshots!")
