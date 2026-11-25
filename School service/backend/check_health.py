import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:8000/health') as resp:
        print("Health status:", resp.status, resp.read().decode())
except Exception as e:
    print("Health check error:", e)
