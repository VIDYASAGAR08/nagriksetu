with open(r"C:\Users\callm\nagriksetu\backend\request_management_service.py", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find("execute-correction")
print(text[pos+1000:pos+3000])
