"""
Patch script to update backend routes in main.py:
1. GET /api/categories/{category_identifier}:
   - Include subcategories list with their skills and offering centres.
2. GET /api/subcategories and GET /api/subcategories/{subcategory_id}:
   - Subcategory listing & details with associated skills and registered offering centres.
3. GET /api/skills:
   - Add subcategory_id and subcategory query params, filter accordingly.
   - Return subcategory_id and subcategory_name on each item.
4. GET /api/skills/{code_or_id}:
   - Return subcategory_id and subcategory_name.
5. GET /api/centres/{centre_id}/profile:
   - Return offered_categories and offered_subcategories distinctly based on the actual programmes the centre offers.
6. GET /api/admin/dashboard:
   - Include total_subcategories and catalogue breakdown.
7. GET /api/admin/catalogue-summary:
   - Comprehensive read-only view of the 7 main categories, 36 subcategories, skills with programmes vs without, centres offering each, active batches.
"""

main_path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py'
with open(main_path, 'r', encoding='utf-8') as f:
    code = f.read()

# -----------------------------------------------------------------------------
# 1. Update GET /api/categories/{category_identifier}
# -----------------------------------------------------------------------------
old_cat_detail = '''    # 1. Retrieve active skills for this category
    skills = db.query(Skill).filter(
        Skill.category_name == cat.name,
        Skill.active == True
    ).order_by(Skill.name).all()

    skill_ids = [s.id for s in skills]
    skills_data = []
    for s in skills:
        modules = db.query(SkillModule).filter(SkillModule.skill_id == s.id).order_by(SkillModule.module_order).all()
        skills_data.append({
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "level": s.level,
            "summary": s.summary,
            "description": s.details or s.summary,
            "category_name": s.category_name,
            "duration_hours": s.duration_hours,
            "duration_weeks": s.duration_weeks,
            "certification_name": s.cert_info,
            "enrolled_count": s.enrolled_count,
            "rating": s.rating,
            "modules": [
                {
                    "id": m.id,
                    "order": m.module_order,
                    "title": m.title,
                    "description": m.description,
                    "practical_assignments": m.practical_assignments
                } for m in modules
            ]
        })'''

new_cat_detail = '''    # 1. Retrieve subcategories for this category
    subcategories = db.query(Subcategory).filter(Subcategory.category_id == cat.id).order_by(Subcategory.id).all()
    subcategories_data = []

    # 2. Retrieve active skills for this category
    skills = db.query(Skill).filter(
        or_(Skill.category_id == cat.id, Skill.category_name == cat.name),
        Skill.active == True
    ).order_by(Skill.name).all()

    skill_ids = [s.id for s in skills]
    skills_data = []
    for s in skills:
        modules = db.query(SkillModule).filter(SkillModule.skill_id == s.id).order_by(SkillModule.module_order).all()
        skills_data.append({
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "level": s.level,
            "summary": s.summary,
            "description": s.details or s.summary,
            "category_id": s.category_id,
            "category_name": s.category_name,
            "subcategory_id": s.subcategory_id,
            "subcategory_name": s.subcategory_name,
            "duration_hours": s.duration_hours,
            "duration_weeks": s.duration_weeks,
            "certification_name": s.cert_info,
            "enrolled_count": s.enrolled_count,
            "rating": s.rating,
            "modules": [
                {
                    "id": m.id,
                    "order": m.module_order,
                    "title": m.title,
                    "description": m.description,
                    "practical_assignments": m.practical_assignments
                } for m in modules
            ]
        })

    for sub in subcategories:
        sub_skills = [sk for sk in skills_data if sk.get("subcategory_id") == sub.id]
        subcategories_data.append({
            "id": sub.id,
            "code": sub.code,
            "name": sub.name,
            "description": sub.description,
            "icon_name": sub.icon_name,
            "skill_count": len(sub_skills),
            "skills": sub_skills
        })'''

assert old_cat_detail in code, "old_cat_detail not found in code"
code = code.replace(old_cat_detail, new_cat_detail, 1)

# In the return payload of get_category_details, include subcategories
old_cat_return = '''        "stats": {
            "total_skills": len(skills_data),
            "total_programmes": len(programmes_data),
            "total_centres": len(centres_dict)
        },
        "skills": skills_data,'''

new_cat_return = '''        "stats": {
            "total_subcategories": len(subcategories_data),
            "total_skills": len(skills_data),
            "total_programmes": len(programmes_data),
            "total_centres": len(centres_dict)
        },
        "subcategories": subcategories_data,
        "skills": skills_data,'''

assert old_cat_return in code, "old_cat_return not found in code"
code = code.replace(old_cat_return, new_cat_return, 1)

# -----------------------------------------------------------------------------
# 2. Add GET /api/subcategories and GET /api/subcategories/{subcategory_id}
# -----------------------------------------------------------------------------
subcategories_endpoints = '''@app.get("/api/subcategories")
def list_subcategories(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Subcategory)
    if category_id:
        query = query.filter(Subcategory.category_id == category_id)
    subs = query.order_by(Subcategory.id).all()
    result = []
    for s in subs:
        sk_count = db.query(Skill).filter(Skill.subcategory_id == s.id, Skill.active == True).count()
        cat = db.query(Category).filter(Category.id == s.category_id).first()
        result.append({
            "id": s.id,
            "code": s.code,
            "category_id": s.category_id,
            "category_name": cat.name if cat else "",
            "name": s.name,
            "description": s.description,
            "icon_name": s.icon_name,
            "skill_count": sk_count
        })
    return result

@app.get("/api/subcategories/{subcategory_id}")
def get_subcategory_details(subcategory_id: int, db: Session = Depends(get_db)):
    sub = db.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    cat = db.query(Category).filter(Category.id == sub.category_id).first()
    skills = db.query(Skill).filter(Skill.subcategory_id == sub.id, Skill.active == True).order_by(Skill.name).all()
    skill_ids = [s.id for s in skills]

    # Find offering centres for these skills
    offering_centres = []
    if skill_ids:
        raw_centres = db.query(TrainingCentre).join(
            TrainingProgram, TrainingProgram.centre_id == TrainingCentre.id
        ).filter(
            TrainingProgram.skill_id.in_(skill_ids),
            TrainingCentre.active == True
        ).distinct().all()
        for c in raw_centres:
            offering_centres.append({
                "id": c.id,
                "code": c.code,
                "name": c.name,
                "district": c.district,
                "location": c.location
            })

    return {
        "id": sub.id,
        "code": sub.code,
        "category_id": sub.category_id,
        "category_name": cat.name if cat else "",
        "name": sub.name,
        "description": sub.description,
        "icon_name": sub.icon_name,
        "skills": [
            {
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "level": s.level,
                "summary": s.summary,
                "duration_hours": s.duration_hours,
                "duration_weeks": s.duration_weeks,
                "category_id": s.category_id,
                "category_name": s.category_name,
                "subcategory_id": s.subcategory_id,
                "subcategory_name": s.subcategory_name,
                "rating": s.rating,
                "enrolled_count": s.enrolled_count
            }
            for s in skills
        ],
        "offering_centres": offering_centres
    }

'''

# Insert before @app.get("/api/skills")
target_skills_header = '@app.get("/api/skills")\ndef list_skills('
assert target_skills_header in code, "target_skills_header not found in code"
code = code.replace(target_skills_header, subcategories_endpoints + target_skills_header, 1)

# -----------------------------------------------------------------------------
# 3. Update GET /api/skills parameters and items
# -----------------------------------------------------------------------------
old_list_skills_params = '''@app.get("/api/skills")
def list_skills(
    q: Optional[str] = None,
    category: Optional[str] = None,
    level: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
    sort_by: Optional[str] = "popular",
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Skill).filter(Skill.active == True)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(Skill.name.ilike(term), Skill.summary.ilike(term), Skill.category_name.ilike(term)))
    if category and category.lower() != "all":
        cat_term = category.strip()
        query = query.filter(Skill.category_name.ilike(f"%{cat_term}%"))'''

new_list_skills_params = '''@app.get("/api/skills")
def list_skills(
    q: Optional[str] = None,
    category: Optional[str] = None,
    subcategory_id: Optional[int] = None,
    subcategory: Optional[str] = None,
    level: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
    sort_by: Optional[str] = "popular",
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Skill).filter(Skill.active == True)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(
            Skill.name.ilike(term),
            Skill.summary.ilike(term),
            Skill.category_name.ilike(term),
            Skill.subcategory_name.ilike(term)
        ))
    if category and category.lower() != "all":
        cat_term = category.strip()
        query = query.filter(Skill.category_name.ilike(f"%{cat_term}%"))
    if subcategory_id:
        query = query.filter(Skill.subcategory_id == subcategory_id)
    if subcategory and subcategory.lower() != "all":
        sub_term = subcategory.strip()
        query = query.filter(Skill.subcategory_name.ilike(f"%{sub_term}%"))'''

assert old_list_skills_params in code, "old_list_skills_params not found"
code = code.replace(old_list_skills_params, new_list_skills_params, 1)

# Include subcategory_id and subcategory_name in list_skills items
old_skill_item = '''            {
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "category_id": s.category_id,
                "category_name": s.category_name,
                "level": s.level,'''

new_skill_item = '''            {
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "category_id": s.category_id,
                "category_name": s.category_name,
                "subcategory_id": s.subcategory_id,
                "subcategory_name": s.subcategory_name,
                "level": s.level,'''

assert old_skill_item in code, "old_skill_item not found"
code = code.replace(old_skill_item, new_skill_item, 1)

# -----------------------------------------------------------------------------
# 4. Include subcategory in get_skill_details
# -----------------------------------------------------------------------------
old_detail_item = '''    return {
        "id": skill.id,
        "code": skill.code,
        "name": skill.name,
        "category_name": skill.category_name,'''

new_detail_item = '''    return {
        "id": skill.id,
        "code": skill.code,
        "name": skill.name,
        "category_id": skill.category_id,
        "category_name": skill.category_name,
        "subcategory_id": skill.subcategory_id,
        "subcategory_name": skill.subcategory_name,'''

assert old_detail_item in code, "old_detail_item not found"
code = code.replace(old_detail_item, new_detail_item, 1)

# -----------------------------------------------------------------------------
# 5. Enhance GET /api/centres/{centre_id}/profile with offered categories & subcategories
# -----------------------------------------------------------------------------
old_centre_progs = '''    # Live programmes offered by this centre
    progs = db.query(TrainingProgram).options(
        joinedload(TrainingProgram.skill),
        joinedload(TrainingProgram.batches)
    ).filter(TrainingProgram.centre_id == c.id).all()'''

new_centre_progs = '''    # Live programmes offered by this centre
    progs = db.query(TrainingProgram).options(
        joinedload(TrainingProgram.skill),
        joinedload(TrainingProgram.batches)
    ).filter(TrainingProgram.centre_id == c.id).all()

    # Determine genuine distinct categories and subcategories offered by this centre
    offered_cats_dict = {}
    offered_subs_dict = {}
    for p in progs:
        if p.skill:
            if p.skill.category_name and p.skill.category_name not in offered_cats_dict:
                offered_cats_dict[p.skill.category_name] = {
                    "id": p.skill.category_id,
                    "name": p.skill.category_name,
                    "program_count": 0
                }
            if p.skill.category_name:
                offered_cats_dict[p.skill.category_name]["program_count"] += 1

            if p.skill.subcategory_name and p.skill.subcategory_name not in offered_subs_dict:
                offered_subs_dict[p.skill.subcategory_name] = {
                    "id": p.skill.subcategory_id,
                    "name": p.skill.subcategory_name,
                    "category_name": p.skill.category_name,
                    "program_count": 0
                }
            if p.skill.subcategory_name:
                offered_subs_dict[p.skill.subcategory_name]["program_count"] += 1'''

assert old_centre_progs in code, "old_centre_progs not found"
code = code.replace(old_centre_progs, new_centre_progs, 1)

old_centre_return = '''        "programs": [
            {
                "id": p.id,
                "code": p.code,
                "title": p.title,
                "description": p.description,
                "mode": p.mode,
                "duration_hours": p.duration_hours,
                "fee": p.fee,
                "scholarship_available": p.scholarship_available,
                "eligibility_criteria": p.eligibility_criteria,
                "skill_name": p.skill.name if p.skill else p.title,'''

new_centre_return = '''        "offered_categories": list(offered_cats_dict.values()),
        "offered_subcategories": list(offered_subs_dict.values()),
        "programs": [
            {
                "id": p.id,
                "code": p.code,
                "title": p.title,
                "description": p.description,
                "mode": p.mode,
                "duration_hours": p.duration_hours,
                "fee": p.fee,
                "scholarship_available": p.scholarship_available,
                "eligibility_criteria": p.eligibility_criteria,
                "skill_id": p.skill_id,
                "skill_name": p.skill.name if p.skill else p.title,
                "category_name": p.skill.category_name if p.skill else None,
                "subcategory_name": p.skill.subcategory_name if p.skill else None,'''

assert old_centre_return in code, "old_centre_return not found"
code = code.replace(old_centre_return, new_centre_return, 1)

# -----------------------------------------------------------------------------
# 6. Enhance Admin Dashboard & Add /api/admin/catalogue-summary
# -----------------------------------------------------------------------------
old_admin_stats = '''    total_skills = db.query(Skill).count()
    total_categories = db.query(Category).count()
    total_programs = db.query(TrainingProgram).count()'''

new_admin_stats = '''    total_skills = db.query(Skill).count()
    total_categories = db.query(Category).count()
    total_subcategories = db.query(Subcategory).count()
    total_programs = db.query(TrainingProgram).count()'''

assert old_admin_stats in code, "old_admin_stats not found"
code = code.replace(old_admin_stats, new_admin_stats, 1)

old_admin_stat_dict = '''        "stats": {
            "total_skills": total_skills,
            "total_categories": total_categories,
            "total_programs": total_programs,'''

new_admin_stat_dict = '''        "stats": {
            "total_skills": total_skills,
            "total_categories": total_categories,
            "total_subcategories": total_subcategories,
            "total_programs": total_programs,'''

assert old_admin_stat_dict in code, "old_admin_stat_dict not found"
code = code.replace(old_admin_stat_dict, new_admin_stat_dict, 1)

# Add GET /api/admin/catalogue-summary right before @app.get("/api/admin/enrollments")
admin_cat_endpoint = '''@app.get("/api/admin/catalogue-summary")
def get_admin_catalogue_summary(admin: Account = Depends(require_admin), db: Session = Depends(get_db)):
    """
    Read-only endpoint providing Platform Admins full visibility into the skill hierarchy:
    7 main categories, 36 subcategories, skills, programme offerings by centre, and batch capacity.
    """
    categories = db.query(Category).order_by(Category.id).all()
    hierarchy_data = []

    for cat in categories:
        subs = db.query(Subcategory).filter(Subcategory.category_id == cat.id).order_by(Subcategory.id).all()
        subs_data = []
        cat_skill_count = 0
        cat_prog_count = 0

        for sub in subs:
            skills = db.query(Skill).filter(Skill.subcategory_id == sub.id, Skill.active == True).order_by(Skill.name).all()
            cat_skill_count += len(skills)
            skills_data = []
            for sk in skills:
                progs = db.query(TrainingProgram).filter(TrainingProgram.skill_id == sk.id).all()
                cat_prog_count += len(progs)
                centres_offering = []
                for p in progs:
                    if p.centre:
                        centres_offering.append({
                            "centre_id": p.centre.id,
                            "centre_name": p.centre.name,
                            "district": p.centre.district,
                            "program_code": p.code,
                            "mode": p.mode
                        })
                skills_data.append({
                    "skill_id": sk.id,
                    "skill_code": sk.code,
                    "skill_name": sk.name,
                    "level": sk.level,
                    "duration_hours": sk.duration_hours,
                    "has_programmes": len(progs) > 0,
                    "programmes_count": len(progs),
                    "centres_offering": centres_offering
                })

            subs_data.append({
                "subcategory_id": sub.id,
                "subcategory_code": sub.code,
                "subcategory_name": sub.name,
                "skills_count": len(skills),
                "skills": skills_data
            })

        hierarchy_data.append({
            "category_id": cat.id,
            "category_code": cat.code,
            "category_name": cat.name,
            "subcategories_count": len(subs),
            "total_skills": cat_skill_count,
            "total_programmes": cat_prog_count,
            "subcategories": subs_data
        })

    return {
        "total_categories": len(categories),
        "total_subcategories": sum(c["subcategories_count"] for c in hierarchy_data),
        "total_skills": sum(c["total_skills"] for c in hierarchy_data),
        "categories": hierarchy_data
    }

'''

target_admin_enrollments = '@app.get("/api/admin/enrollments")'
assert target_admin_enrollments in code, "target_admin_enrollments not found"
code = code.replace(target_admin_enrollments, admin_cat_endpoint + target_admin_enrollments, 1)

with open(main_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("SUCCESS: backend/app/main.py patched successfully with all hierarchy endpoints!")
