with open("C:/Users/callm/nagriksetu/backend/main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. In list_schools
old_q1 = "s.school_type, s.address, s.established_year,"
new_q1 = "s.school_type, s.category, s.address, s.established_year,"
if old_q1 in content:
    content = content.replace(old_q1, new_q1, 1)
    print("Added s.category to list_schools")

# 2. In get_school
old_q2 = "school_type, address, established_year,"
new_q2 = "school_type, category, address, established_year,"
if old_q2 in content:
    content = content.replace(old_q2, new_q2, 1)
    print("Added category to get_school")

with open("C:/Users/callm/nagriksetu/backend/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py successfully!")
