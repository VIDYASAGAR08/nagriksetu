import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.execute("UPDATE invitation_tokens SET is_used = 1 WHERE is_used = 0")
conn.execute("UPDATE user_institution_roles SET status = 'revoked' WHERE status = 'invited'")
conn.execute("UPDATE users SET status = 'revoked', school_id = NULL WHERE status = 'invited'")
conn.commit()
print("All pending/exposed tokens revoked successfully!")
conn.close()
