with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('logger.warning(', 'logging.getLogger("nagriksetu.auth").warning(')
c = c.replace('logger.error(', 'logging.getLogger("nagriksetu.auth").error(')

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Replaced logger calls in main.py')
