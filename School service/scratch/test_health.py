import requests
import time

time.sleep(2)
try:
    res = requests.get("http://localhost:8001/health", timeout=5)
    print("Backend health status:", res.status_code, res.json())
except Exception as e:
    print("Backend health error:", e)
