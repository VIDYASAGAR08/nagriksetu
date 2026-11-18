import sqlite3
c = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
print([col[1] for col in c.execute('PRAGMA table_info(student_guardians)').fetchall()])
