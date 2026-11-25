import sys

with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Enhance GET /api/categories/{category_identifier} to include subcategories and their skills
old_cat_detail_start = '''    # 1. Retrieve active skills for this category
    skills = db.query(Skill).filter(
        Skill.category_name == cat.name,
        Skill.active == True
    ).order_by(Skill.name).all()'''

# Let's check if this is present
print("cat detail present:", old_cat_detail_start in text)

# 2. Check list_skills
print("list_skills present:", '@app.get("/api/skills")' in text)
