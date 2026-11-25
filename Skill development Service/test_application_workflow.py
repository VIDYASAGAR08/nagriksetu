import requests
import json
import pymysql

API_BASE = "http://127.0.0.1:8003/api"

# 1. Connect to MySQL and inspect available test citizens
conn = pymysql.connect(
    host='127.0.0.1',
    port=3308,
    user='nagriksetu_skill',
    password='skill-app-pass-2026',
    database='skill_db',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("SELECT id, email, role, citizen_ref, full_name, phone FROM accounts WHERE role = 'CITIZEN' LIMIT 5")
    citizens = cur.fetchall()
    print("Found test citizens in DB:")
    for c in citizens:
        print(f" - {c['citizen_ref']} ({c['email']})")

    # Pick 3 different programmes belonging to 3 different centres:
    # Prog 1 -> Centre 1 (Bengaluru)
    # Prog 2 -> Centre 2 (Mysuru)
    # Prog 3 -> Centre 3 (Hubballi)
    cur.execute("""
        SELECT tp.id, tp.code, tp.title, tp.centre_id, tc.name as centre_name,
               b.id as batch_id, b.batch_name, b.available_seats, b.total_seats
        FROM training_programs tp
        JOIN training_centres tc ON tp.centre_id = tc.id
        JOIN batches b ON tp.id = b.program_id
        WHERE tp.id IN (1, 2, 3) AND b.available_seats > 0
        GROUP BY tp.id, tp.code, tp.title, tp.centre_id, tc.name, b.id, b.batch_name, b.available_seats, b.total_seats
        ORDER BY tp.id
    """)
    test_programs = cur.fetchall()
    print("\nTest programmes with batches:")
    for p in test_programs:
        print(f"Prog ID {p['id']} ({p['code']}) -> Centre ID {p['centre_id']} ({p['centre_name']}) | Batch ID {p['batch_id']}: {p['available_seats']} seats")

conn.close()
