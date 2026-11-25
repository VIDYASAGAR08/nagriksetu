import sqlite3
import os

db_path = 'data/nagriksetu.db' if os.path.exists('data/nagriksetu.db') else 'backend/data/nagriksetu.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'")
for row in cur.fetchall():
    print(f"Index: {row[0]} on {row[1]}")
conn.close()

