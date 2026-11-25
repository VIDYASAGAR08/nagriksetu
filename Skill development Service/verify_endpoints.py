import urllib.request, json

try:
    with urllib.request.urlopen('http://localhost:8003/api/categories') as resp:
        data = json.loads(resp.read().decode())
        print('Categories count:', len(data))
        for c in data:
            print(f"- {c['name']} (ID {c['id']}): {len(c['subcategories'])} subcategories, {c['skill_count']} skills, {c['offering_centres_count']} centres")
            for sub in c['subcategories'][:2]:
                print(f"    * Sub: {sub['name']} ({sub['skill_count']} skills)")

    print("\n--- Subcategories Endpoint ---")
    with urllib.request.urlopen('http://localhost:8003/api/subcategories') as resp:
        subs = json.loads(resp.read().decode())
        print(f"Total subcategories returned: {len(subs)}")

    print("\n--- Skills with Subcategory Filter ---")
    with urllib.request.urlopen('http://localhost:8003/api/skills?subcategory_id=1&limit=5') as resp:
        skills = json.loads(resp.read().decode())
        print(f"Skills in subcategory 1: {skills['total']} total, first item: {skills['items'][0]['name']} (Sub: {skills['items'][0]['subcategory_name']})")

    print("\n--- Centre Profile with Offered Hierarchy ---")
    with urllib.request.urlopen('http://localhost:8003/api/centres/CTR-0001/profile') as resp:
        prof = json.loads(resp.read().decode())
        print(f"Centre {prof['name']}:")
        print(f"  Offered Categories: {[cat['name'] for cat in prof.get('offered_categories', [])]}")
        print(f"  Offered Subcategories count: {len(prof.get('offered_subcategories', []))}")
        print(f"  Programs count: {len(prof.get('programs', []))}")

    print("\nALL VERIFICATIONS PASSED!")
except Exception as e:
    import traceback
    traceback.print_exc()
