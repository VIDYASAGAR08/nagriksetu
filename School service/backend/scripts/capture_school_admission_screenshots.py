import subprocess
import os

EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ARTIFACTS_DIR = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

schools_to_capture = [
    {
        "url": "http://localhost:5173/schools/SCH001?apply=true",
        "file": "school_admission_sch001_model_school.png"
    },
    {
        "url": "http://localhost:5173/schools/SCH005?apply=true",
        "file": "school_admission_sch005_green_valley.png"
    },
    {
        "url": "http://localhost:5173/schools/SCH016?apply=true",
        "file": "school_admission_sch016_belagavi.png"
    }
]

for item in schools_to_capture:
    out_path = os.path.join(ARTIFACTS_DIR, item["file"])
    cmd = [
        EDGE_EXE,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1280,1024",
        "--virtual-time-budget=4000",
        f"--screenshot={out_path}",
        item["url"]
    ]
    print(f"[*] Capturing {item['url']} -> {item['file']}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(out_path):
        print(f"[+] Saved {item['file']} ({os.path.getsize(out_path)} bytes)")
    else:
        print(f"[!] Failed to save {item['file']}: {res.stderr}")

print("[+] All school admission screenshots captured.")
