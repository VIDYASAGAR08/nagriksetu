import urllib.request
import json

url = "http://localhost:8001/auth/login"
data = "username=rao%40edu.in&password=Staff%40NagrikSetu2026!".encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
with urllib.request.urlopen(req) as r:
    res = json.loads(r.read())
    token = res["access_token"]
    print("Token user:", res.get("user"))

req2 = urllib.request.Request("http://localhost:8001/auth/me", headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req2) as r2:
    print("Auth me:", json.loads(r2.read()))
