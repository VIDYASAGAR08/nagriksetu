import sys
sys.path.append(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend')
from app.places_registry import AUTHENTIC_REAL_WORLD_CENTRES

print(f"Total authentic institutes: {len(AUTHENTIC_REAL_WORLD_CENTRES)}")
emptrg_count = 0
for inst in AUTHENTIC_REAL_WORLD_CENTRES:
    w = inst.get('website', '')
    if 'emptrg.karnataka.gov.in' in w:
        emptrg_count += 1
        name = inst.get('name', '')[:45]
        iid = inst.get('id', '')
        print(f"{iid:25} | {name:45} | {w}")

print(f"\nInstitutes with emptrg.karnataka.gov.in: {emptrg_count}")
