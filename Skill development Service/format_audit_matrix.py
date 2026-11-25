import json

with open("audit_full_dump.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Group programs by Centre
centres = {}
for p in data["programs_audit"]:
    cid = p["centre_id"]
    cname = p["centre_name"]
    ccode = p["centre_code"]
    cdist = p["centre_district"]
    cstate = p["centre_state"]
    if cid not in centres:
        centres[cid] = {
            "id": cid,
            "code": ccode,
            "name": cname,
            "district": cdist,
            "state": cstate,
            "programs": []
        }
    centres[cid]["programs"].append(p)

print(f"Total centres with programs: {len(centres)}")
for cid in sorted(centres.keys()):
    c = centres[cid]
    print(f"\nCentre #{cid} ({c['code']} - {c['name']}, {c['district']}, {c['state']}): {len(c['programs'])} programmes")
    for prog in c["programs"]:
        print(f"  [{prog['program_code']}] ID:{prog['program_id']} | '{prog['program_title']}' | Skill: {prog['skill_code']} - '{prog['skill_name']}' | Batches: {prog['batch_count']}")
