with open(r"C:\Users\callm\nagriksetu\backend\main.py", "r", encoding="utf-8") as f:
    text = f.read()

bad_snippet = """@app.post("/admissions/apply", status_code=status.HTTP_201_CREATED)
def get_optional_current_user"""

good_snippet = """def get_optional_current_user"""

target_func = """def submit_stage1_admission_application("""
decorated_func = """@app.post("/admissions/apply", status_code=status.HTTP_201_CREATED)
def submit_stage1_admission_application("""

# Handle CRLF or LF
text = text.replace(bad_snippet, good_snippet)
if bad_snippet.replace("\n", "\r\n") in text:
    text = text.replace(bad_snippet.replace("\n", "\r\n"), good_snippet)

if decorated_func not in text and decorated_func.replace("\n", "\r\n") not in text:
    text = text.replace(target_func, decorated_func)

with open(r"C:\Users\callm\nagriksetu\backend\main.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fix applied successfully!")
