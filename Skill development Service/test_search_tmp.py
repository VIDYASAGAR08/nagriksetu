import requests

for loc in ["Whitefield", "Kaggadasapura", "Jalahalli"]:
    res = requests.get(f"http://127.0.0.1:8003/api/centres/search?location={loc}")
    print(f"=== Search: {loc} (Status: {res.status_code}) ===")
    if res.status_code == 200:
        data = res.json()
        print("Resolved:", data.get("resolved_address"))
        centres = data.get("centres", [])
        print(f"Found count: {len(centres)}")
        for c in centres[:5]:
            print(f"  * {c.get('name')} | Dist: {c.get('distance_km')} km | Locality: {c.get('locality')} | Source: {c.get('source')} | URL: {c.get('website')}")
    else:
        print(res.json())
