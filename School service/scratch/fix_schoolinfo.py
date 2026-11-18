# -*- coding: utf-8 -*-
path = r"C:\Users\callm\nagriksetu\frontend\src\pages\staff\StaffDashboard.jsx"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = "institutionName={schoolInfo?.school_name || assignedSchoolId}"
replacement = "institutionName={user?.school_name || assignedSchoolId}"

if target in text:
    text = text.replace(target, replacement, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed schoolInfo reference error!")
else:
    print("Target not found!")
