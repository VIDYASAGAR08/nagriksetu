import os
import shutil
import subprocess
import time

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\callm\nagriksetu\screenshots"
BRAIN_DIR = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def capture():
    # Kill existing msedge instances if any
    try:
        subprocess.run(["powershell", "-Command", "Get-Process msedge -ErrorAction SilentlyContinue | Stop-Process -Force"], timeout=5)
    except Exception:
        pass

    dest_local = os.path.join(SCREENSHOT_DIR, "phase9_ai_assistant_grounded.png")
    dest_brain = os.path.join(BRAIN_DIR, "phase9_ai_assistant_grounded.png")

    target_url = "http://localhost:5173/#/?open_ai=sample"

    print("[*] Capturing Phase 9 Grounded AI Assistant Screen...")
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,1050",
        f"--screenshot={dest_local}",
        target_url
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
    except Exception as e:
        print(f"Edge warning: {e}")

    time.sleep(1)
    if os.path.exists(dest_local):
        shutil.copyfile(dest_local, dest_brain)
        print(f"    -> Saved: {dest_local}")
        print(f"    -> Copied to Brain: {dest_brain}")
    else:
        print("    -> Failed to capture screenshot")

if __name__ == "__main__":
    capture()
