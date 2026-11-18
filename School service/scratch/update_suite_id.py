with open(r"C:\Users\callm\nagriksetu\scratch\test_phase16_security_suite.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("/parent/children/SCH01125/records", "/parent/children/NS-FB8336A812DE468FB8E475443CF673EB/records")

with open(r"C:\Users\callm\nagriksetu\scratch\test_phase16_security_suite.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated Asha permanent_student_id in test_phase16_security_suite.py")
