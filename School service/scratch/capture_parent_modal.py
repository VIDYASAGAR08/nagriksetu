# -*- coding: utf-8 -*-
import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"

# Login Parent
res_parent = requests.post(f"{base_url}/auth/login", data={"username": "9876543210", "password": "Str0ngPass!2026"})
parent_token = res_parent.json().get("access_token")

# We can create a lightweight helper HTML that sets token, loads parent page, and auto-clicks "View Academic Results & Documents →"
helper_html = f"""<!DOCTYPE html>
<html>
<body>
<script>
  localStorage.setItem('nagriksetu_token', '{parent_token}');
  localStorage.setItem('nagriksetu_user', JSON.stringify({{
    user_id: '46d5077b-ea2d-48f2-8e1d-70c3d728c6b8',
    phone: '9876543210',
    role: 'parent',
    full_name: 'Sri. Ramesh Sharma',
    status: 'active'
  }}));
  window.location.replace('/#/parent');
  setTimeout(() => {{
    const btns = Array.from(document.querySelectorAll('button'));
    const viewBtn = btns.find(b => b.textContent.includes('View Academic Results'));
    if (viewBtn) viewBtn.click();
  }}, 2500);
</script>
</body>
</html>
"""

helper_path = r"C:\Users\callm\nagriksetu\frontend\dist\parent_record_helper.html"
with open(helper_path, "w", encoding="utf-8") as f:
    f.write(helper_html)

# Copy to container
subprocess.run(["docker", "cp", helper_path, "nagriksetu-frontend:/usr/share/nginx/html/parent_record_helper.html"])

out_modal = os.path.join(artifacts_dir, "phase12_parent_child_academic_records_modal.png")
cmd = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1280,1050",
    "--virtual-time-budget=9000",
    f"--screenshot={out_modal}",
    "http://localhost:5173/parent_record_helper.html"
]
print("Capturing Parent Child Academic Modal...")
subprocess.run(cmd, capture_output=True, timeout=35)
print("Saved modal screenshot:", os.path.getsize(out_modal))
