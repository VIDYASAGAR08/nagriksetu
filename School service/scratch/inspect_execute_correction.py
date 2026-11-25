with open(r"C:\Users\callm\nagriksetu\backend\request_management_service.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
pos = text.find("execute-correction")
if pos != -1:
    print(text[pos-100:pos+1600])
