import json
import urllib.request

req = urllib.request.urlopen('http://127.0.0.1:8003/api/public/centre-register')
data = json.loads(req.read().decode('utf-8'))
print(f"Total Centres in Register: {len(data)}")
for c in data:
    status_str = "Registered" if c["is_configured"] else "Not Registered"
    print(f"ID: {c['centre_id']:2d} | Code: {c['centre_code']} | Status: {status_str:14s} | Email: {c['registered_email']} | Name: {c['centre_name']}")
