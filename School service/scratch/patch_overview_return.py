path = r'C:\Users\callm\nagriksetu\backend\main.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = """        return {
            "institution": dict(school),
            "overview_cards": {
                "total_students": total_students,
                "total_parents": total_parents,
                "new_admission_applications": new_apps,
                "pending_admission_reviews": pending_admission_reviews,
                "pending_parent_requests": pending_parent_requests,
                "total_academic_programs": total_programs,
                "total_sections": total_sections,
                "authorized_staff_count": staff_count
            },
            "recent_activities": recent_activities
        }"""

replacement = """        return {
            "institution": dict(school),
            "institution_id": school["school_id"],
            "institution_name": school["school_name"],
            "category": school["category"],
            "district": school["district"],
            "state": school["state"],
            "school_type": school["school_type"],
            "affiliation": school["affiliation"],
            "established_year": school["established_year"],
            "total_students": total_students,
            "total_parents": total_parents,
            "new_admission_applications": new_apps,
            "pending_admission_reviews": pending_admission_reviews,
            "pending_parent_requests": pending_parent_requests,
            "total_academic_programs": total_programs,
            "total_sections": total_sections,
            "authorized_staff_count": staff_count,
            "overview_cards": {
                "total_students": total_students,
                "total_parents": total_parents,
                "new_admission_applications": new_apps,
                "pending_admission_reviews": pending_admission_reviews,
                "pending_parent_requests": pending_parent_requests,
                "total_academic_programs": total_programs,
                "total_sections": total_sections,
                "authorized_staff_count": staff_count
            },
            "recent_activities": recent_activities
        }"""

if target in text:
    text = text.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated return dict!")
elif target.replace('\n', '\r\n') in text:
    text = text.replace(target.replace('\n', '\r\n'), replacement.replace('\n', '\r\n'))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated CRLF return dict!")
else:
    print("Target not found")
