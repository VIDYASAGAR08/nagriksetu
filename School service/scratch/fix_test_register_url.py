file_path = r"C:\Users\callm\nagriksetu\scratch\test_password_length_8.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("/auth/register/parent", "/auth/register")
code = code.replace("assert res_p8.status_code == 200", "assert res_p8.status_code == 201")
code = code.replace("assert res_p10.status_code == 200", "assert res_p10.status_code == 201")
code = code.replace("assert res_p11.status_code == 200", "assert res_p11.status_code == 201")
code = code.replace("assert res_p12.status_code == 200", "assert res_p12.status_code == 201")

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(code)

print("Updated test_password_length_8.py to use /auth/register!")
