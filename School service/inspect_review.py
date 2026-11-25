with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()
m = content.find('@app.post("/school/linking-requests/{request_id}/review")')
if m != -1:
    print(content[m:m+2500])
