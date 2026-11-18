import sqlite3
c = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
print([row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
