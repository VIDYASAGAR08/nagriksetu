with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = "next_num = db.query(Enrollment).count() + 1"
replacement = """from sqlalchemy import func
    max_id = db.query(func.max(Enrollment.id)).scalar() or 0
    next_num = max(max_id + 1, db.query(Enrollment).count() + 1)
    while db.query(Enrollment).filter_by(code=f"ENR-{next_num:06d}").first():
        next_num += 1"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: Unique enrollment code logic updated")
else:
    print("ERROR: Target not found")
