with open(r"C:\Users\callm\nagriksetu\backend\request_management_service.py", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find("request_corrections (")
if pos != -1:
    print(text[pos-100:pos+1200])
