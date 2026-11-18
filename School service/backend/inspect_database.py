import sqlite3

db_path = "data/nagriksetu.db"
connection = sqlite3.connect(db_path)

print("Database tables:")
tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()

for table in tables:
    print("-", table[0])

connection.close()
