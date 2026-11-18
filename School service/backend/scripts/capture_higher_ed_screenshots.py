import subprocess
import time
import os

EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ARTIFACTS_DIR = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

targets = [
    {
        "url": "http://localhost:5173/schools/COL001",
        "file": "degree_college_msrit_academics.png",
        "window": "1280,2400"
    },
    {
        "url": "http://localhost:5173/schools/COL007",
        "file": "degree_college_mount_carmel_academics.png",
        "window": "1280,2200"
    },
    {
        "url": "http://localhost:5173/schools/COL004",
        "file": "university_pesu_hierarchy.png",
        "window": "1280,2600"
    },
    {
        "url": "http://localhost:5173/schools/COL006",
        "file": "university_st_josephs_hierarchy.png",
        "window": "1280,2600"
    },
    {
        "url": "http://localhost:5173/schools/COL010",
        "file": "university_vtu_hierarchy.png",
        "window": "1280,2600"
    },
]

for t in targets:
    out_path = os.path.join(ARTIFACTS_DIR, t["file"])
    cmd = [
        EDGE_EXE,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={t['window']}",
        "--virtual-time-budget=4000",
        f"--screenshot={out_path}",
        t["url"]
    ]
    print(f"[*] Capturing screenshot for {t['url']} -> {t['file']}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[+] Saved {t['file']} ({size} bytes)")
    else:
        print(f"[!] Failed to save {t['file']}: {res.stderr}")

print("[+] All screenshots captured successfully.")
