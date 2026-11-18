import subprocess
import time
import os

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

screenshots = [
    # 1. Cleaned Header & Navigation on Home Page
    (
        "http://localhost:5173/#/",
        "cleaned_navigation_home.png",
        "Cleaned NagrikSetu Main Navigation on Home Page (No IDP/OCR Demo)"
    ),
    # 2. Cleaned Navigation on Explore Institutions Directory Page
    (
        "http://localhost:5173/#/schools",
        "cleaned_navigation_schools.png",
        "Explore Institutions Directory Page with Cleaned Navigation"
    ),
    # 3. User Category Selection Screen
    (
        "http://localhost:5173/#/login",
        "cleaned_login_category_selection.png",
        "User Category Selection Screen (Cleaned of Demo References)"
    ),
    # 4. Redirect of Legacy /ocr-demo Route to /schools
    (
        "http://localhost:5173/#/ocr-demo",
        "cleaned_ocr_demo_redirect.png",
        "Automatic Redirect of Legacy /ocr-demo Route to /schools Directory"
    ),
]

for url, filename, desc in screenshots:
    out_path = os.path.join(artifacts_dir, filename)
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1280,850",
        "--virtual-time-budget=6000",
        f"--screenshot={out_path}",
        url
    ]
    print(f"Capturing: {desc} -> {filename}...")
    subprocess.run(cmd, capture_output=True, timeout=30)
    time.sleep(1)

print("All screenshots captured successfully!")
