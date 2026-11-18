import sqlite3

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
c = conn.cursor()
sql = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='update_requests'").fetchone()[0]
print(sql)
