import pymysql
import json

conn = pymysql.connect(
    host='127.0.0.1',
    port=3308,
    user='nagriksetu_skill',
    password='skill-app-pass-2026',
    database='skill_db',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("SHOW TABLES;")
    tables = cur.fetchall()
    print("Tables in skill_db:")
    table_names = [list(t.values())[0] for t in tables]
    for name in table_names:
        print(" -", name)

    for t in table_names:
        cur.execute(f"DESCRIBE {t};")
        cols = cur.fetchall()
        print(f"\n=== Schema of {t} ===")
        for col in cols:
            print(f"  {col['Field']} ({col['Type']}) Null={col['Null']} Key={col['Key']}")

conn.close()
