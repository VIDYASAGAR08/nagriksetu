import subprocess
import os

EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ARTIFACTS_DIR = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

targets = [
    {
        "url": "http://localhost:5173/schools/SCH001?apply=true",
        "file": "school_lang_pref_sch001.png"
    },
    {
        "url": "http://localhost:5173/schools/SCH006?apply=true",
        "file": "school_lang_pref_sch006.png"
    },
    {
        "url": "http://localhost:5173/schools/SCH018?apply=true",
        "file": "school_lang_pref_sch018.png"
    }
]

for t in targets:
    out_path = os.path.join(ARTIFACTS_DIR, t["file"])
    cmd = [
        EDGE_EXE,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1280,1024",
        "--virtual-time-budget=4000",
        f"--screenshot={out_path}",
        t["url"]
    ]
    print(f"[*] Capturing {t['url']} -> {t['file']}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(out_path):
        print(f"[+] Saved {t['file']} ({os.path.getsize(out_path)} bytes)")
    else:
        print(f"[!] Failed to save {t['file']}: {res.stderr}")

print("[+] All language preference screenshots captured successfully.")
