import sqlite3
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

conn = sqlite3.connect('/app/data/nagriksetu.db')
cur = conn.cursor()
cur.execute('SELECT password_hash FROM users WHERE email = "admin.sch019@gmail.com";')
h = cur.fetchone()[0]

for pwd in ['Admin19', 'Admin@19', 'Admin@19!', 'Admin19!', 'Admin19@', '7418529630', 'Admin@NagrikSetu2026!', 'Admin@SCH019!']:
    try:
        if password_hash.verify(pwd, h):
            print('MATCH FOUND:', pwd)
            break
    except Exception as e:
        print('Error:', e)
else:
    print('No match in candidate list.')
