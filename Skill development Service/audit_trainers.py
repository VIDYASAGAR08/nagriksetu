import pymysql

conn = pymysql.connect(
    host="localhost",
    port=3308,
    user="nagriksetu_skill",
    password="skill-app-pass-2026",
    database="skill_db",
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("SELECT * FROM trainers ORDER BY id")
    trainers = cur.fetchall()
    print(f"Total trainers in DB: {len(trainers)}")
    for t in trainers:
        print(f"\nID: {t['id']} | Code: {t['code']} | Name: {t['name']}")
        print(f"  Assigned Centre ID: {t['assigned_centre_id']}")
        print(f"  Qualification: {t['qualification']}")
        print(f"  Specialisation: {t['specialisation']}")
        print(f"  Experience: {t['experience_years']} years")
        print(f"  Email: {t['contact_email']}")
        print(f"  Availability: {t['availability']}")
        print(f"  Active: {t['active']}")

    # Check which programmes are assigned to trainers
    cur.execute("""
        SELECT p.id as prog_id, p.code as prog_code, p.title as prog_title, p.trainer_id, t.name as trainer_name
        FROM training_programs p
        LEFT JOIN trainers t ON p.trainer_id = t.id
        WHERE p.trainer_id IS NOT NULL
        ORDER BY p.id
    """)
    assigned_progs = cur.fetchall()
    print(f"\nProgrammes with assigned trainers: {len(assigned_progs)}")
    for ap in assigned_progs[:10]:
        print(f"  Prog {ap['prog_code']}: {ap['prog_title']} -> Trainer {ap['trainer_id']} ({ap['trainer_name']})")

conn.close()
