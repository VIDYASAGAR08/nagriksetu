with open(r"C:\Users\callm\nagriksetu\scratch\test_phase16_security_suite.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    "SELECT application_id, institution_id FROM admission_applications WHERE status = 'approved' LIMIT 1",
    "SELECT application_id, institution_id FROM admission_applications WHERE institution_id = 'SCH001' AND status = 'approved' LIMIT 1"
)

with open(r"C:\Users\callm\nagriksetu\scratch\test_phase16_security_suite.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated app query in test_phase16_security_suite.py")
