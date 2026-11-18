import os
import shutil
import subprocess
import time

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\callm\nagriksetu\screenshots"
BRAIN_DIR = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def kill_edge():
    try:
        subprocess.run(["powershell", "-Command", "Get-Process msedge -ErrorAction SilentlyContinue | Stop-Process -Force"], timeout=5)
    except Exception:
        pass
    time.sleep(0.5)

def capture_target(url, filename):
    kill_edge()
    dest_local = os.path.join(SCREENSHOT_DIR, filename)
    dest_brain = os.path.join(BRAIN_DIR, filename)

    print(f"[*] Capturing {filename} from {url}...")
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,1050",
        f"--screenshot={dest_local}",
        url
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
        print(f"    -> Failed to capture {filename}")

def capture_all():
    # 1. Empty Initial State
    capture_target("http://localhost:5173/#/ocr-demo", "phase10_ocr_empty_initial_state.png")

    # 2. Uploaded Document Ready for OCR
    capture_target("http://localhost:5173/#/ocr-demo?test_view=ready", "phase10_ocr_uploaded_ready.png")

    # 3. OCR Extracted Result with Traceability, Review & Confirmation Gate
    capture_target("http://localhost:5173/#/ocr-demo?test_view=result", "phase10_ocr_extracted_result.png")

if __name__ == "__main__":
    capture_all()
