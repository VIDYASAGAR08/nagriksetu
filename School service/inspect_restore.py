with open(r'C:\Users\callm\nagriksetu\backend\main.py.from_image', 'r', encoding='utf-8') as f:
    text = f.read()

m = text.find('@app.get("/parent/children")')
print("parent/children at:", m)
if m != -1:
    print(text[m:m+1200])
