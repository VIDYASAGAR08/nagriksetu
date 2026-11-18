import os
import shutil
import subprocess
import time

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\callm\nagriksetu\screenshots"
BRAIN_DIR = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

def kill_edge():
    try:
        subprocess.run(["powershell", "-Command", "Get-Process msedge -ErrorAction SilentlyContinue | Stop-Process -Force"], timeout=5)
    except Exception:
        pass
    time.sleep(0.5)

def capture_target(url, filename, desc=""):
    kill_edge()
    dest_local = os.path.join(SCREENSHOT_DIR, filename)
    dest_brain = os.path.join(BRAIN_DIR, filename)

    print(f"[*] Capturing: {desc} ({filename}) from {url}...")
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,1200",
        f"--screenshot={dest_local}",
        url
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
    except Exception as e:
        print(f"Edge process warning: {e}")

    time.sleep(1)
    if os.path.exists(dest_local):
        shutil.copyfile(dest_local, dest_brain)
        print(f"    -> Saved local: {dest_local}")
        print(f"    -> Copied to Brain: {dest_brain}")
    else:
        print(f"    -> FAILED to capture {filename}")

def main():
    targets = [
        ("http://localhost:5173/#/schools/SCH014", "pu_college_sch014_hassan_profile.png", "SCH014 Hassan Valley PU College Profile"),
        ("http://localhost:5173/#/schools/SCH011", "pu_college_sch011_tumakuru_profile.png", "SCH011 Tumakuru Model PU College Profile"),
        ("http://localhost:5173/#/schools/SCH012", "pu_college_sch012_mysuru_profile.png", "SCH012 Mysuru Govt PU College Profile"),
        ("http://localhost:5173/#/schools/SCH013", "pu_college_sch013_mandya_profile.png", "SCH013 Mandya Govt PU College Profile"),
        ("http://localhost:5173/#/schools/SCH015", "pu_college_sch015_udupi_profile.png", "SCH015 Udupi Govt PU College Profile"),
    ]

    for url, filename, desc in targets:
        capture_target(url, filename, desc)
        time.sleep(1)

    print("\nAll PU college screenshot captures completed.")

if __name__ == "__main__":
    main()
