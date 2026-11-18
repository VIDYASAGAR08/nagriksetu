import urllib.request
import json

base_url = "http://localhost:8001"

for sid in ["COL001", "SCH001", "COL002", "SCH011"]:
    print(f"\n=== Testing {sid} ===")
    req = urllib.request.urlopen(f"{base_url}/schools/{sid}")
    data = json.loads(req.read().decode("utf-8"))
    print("School Name:", data.get("school_name"))
    print("Affiliation:", data.get("affiliation"))
    print("About Vision:", (data.get("about") or {}).get("vision", "")[:60] + "...")
    print("Facilities count:", len(data.get("facilities") or {}))
    print("Hostel Available:", (data.get("hostel") or {}).get("available"))
    print("Transport Available:", (data.get("transport") or {}).get("available"))

    req_ach = urllib.request.urlopen(f"{base_url}/schools/{sid}/achievements")
    ach = json.loads(req_ach.read().decode("utf-8"))
    print("Achievements count:", len(ach))
    if ach:
        print("Sample Achievement:", ach[0].get("title"), f"({ach[0].get('year')})")

    req_div = urllib.request.urlopen(f"{base_url}/schools/{sid}/divisions")
    divs = json.loads(req_div.read().decode("utf-8"))
    print("Divisions count:", len(divs))
    if divs:
        print("Sample Division:", divs[0].get("division_name"))

    req_prog = urllib.request.urlopen(f"{base_url}/schools/{sid}/programs")
    progs = json.loads(req_prog.read().decode("utf-8"))
    print("Programs count:", len(progs))
    if progs:
        print("Sample Program:", progs[0].get("program_name"))

print("\nAll API tests completed successfully!")
