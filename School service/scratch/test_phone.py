import sqlite3
conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
cur.execute("SELECT user_id, email, phone, role FROM users WHERE phone = '9876543210'")
print("Users with phone 9876543210:", cur.fetchall())
