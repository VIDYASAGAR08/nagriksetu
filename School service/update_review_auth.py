with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = '''    if user["role"] not in ("school_staff", "school_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School staff access required.",
        )
    if not user.get("school_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to a school.",
        )'''

replace1 = '''    if user["role"] not in ("school_staff", "school_admin", "platform_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School staff access required.",
        )
    if not user.get("school_id") and user["role"] != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to a school.",
        )'''

assert target1 in text, "target1 not found"
text = text.replace(target1, replace1, 1)

target2 = '''        if lr["school_id"] != user["school_id"]:'''
replace2 = '''        if user["role"] != "platform_admin" and lr["school_id"] != user.get("school_id"):'''

assert target2 in text, "target2 not found"
text = text.replace(target2, replace2, 1)

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated review_school_linking_request auth successfully!")
