with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = "import logging\n" + c

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Added import logging at top of backend/main.py')
