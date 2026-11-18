import re

def normalize_dob(dob_str: str) -> str:
    if not dob_str:
        return ""
    s = dob_str.strip()
    m1 = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", s)
    if m1:
        y, m, d = m1.groups()
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
    m2 = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", s)
    if m2:
        d, m, y = m2.groups()
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
    return s

db_dob = "2015-06-15"
print("DB DOB:", db_dob)
print("Input 2015-06-15 match:", normalize_dob("2015-06-15") == normalize_dob(db_dob))
print("Input 15/06/2015 match:", normalize_dob("15/06/2015") == normalize_dob(db_dob))
print("Input 15-06-2015 match:", normalize_dob("15-06-2015") == normalize_dob(db_dob))
print("Input 2015-07-15 match:", normalize_dob("2015-07-15") == normalize_dob(db_dob))
