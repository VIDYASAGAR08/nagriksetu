import json

with open('audit_full_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== SKILLS WITHOUT TRAINING PROGRAMMES (COUNT: %d) ===' % len(data['skills_without_programs']))
for s in data['skills_without_programs']:
    print(f"Skill ID: {s['skill_id']:3d} | Code: {s['skill_code']:8s} | Name: {s['skill_name']:40s} | Category: {s['category']}")

skills_with_multi_progs = [s for s in data['skills_audit'] if s['programs_count'] > 1]
print(f'\n=== SKILLS WITH MULTIPLE TRAINING PROGRAMMES (COUNT: {len(skills_with_multi_progs)}) ===')
for sm in skills_with_multi_progs:
    print(f"Skill ID: {sm['skill_id']:3d} | Code: {sm['skill_code']:8s} | Name: {sm['skill_name']:35s} | Progs: {sm['programs_count']} | Centres: {sm['associated_centres']}")

skills_with_single_prog = [s for s in data['skills_audit'] if s['programs_count'] == 1]
print(f'\n=== SKILLS WITH EXACTLY 1 TRAINING PROGRAMME (COUNT: {len(skills_with_single_prog)}) ===')
