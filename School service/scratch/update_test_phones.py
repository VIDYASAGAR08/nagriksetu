file_path = r"C:\Users\callm\nagriksetu\scratch\test_three_level_gap.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace('"phone": "9876000001"', f'"phone": "98{uuid.uuid4().int % 89999999 + 10000000}"')
code = code.replace('"candidate_phone": "9845011223"', f'"candidate_phone": "98{uuid.uuid4().int % 89999999 + 10000000}"')

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(code)

print("Updated test_three_level_gap.py phone numbers!")
