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
    # 1. Inspect all 125 programmes: programme centre vs trainer assigned_centre
    cur.execute("""
        SELECT p.id as prog_id, p.code as prog_code, p.title as prog_title, p.centre_id, tc.name as centre_name,
               p.trainer_id, t.name as trainer_name, t.assigned_centre_id as trainer_home_centre,
               home_tc.name as trainer_home_centre_name
        FROM training_programs p
        LEFT JOIN training_centres tc ON p.centre_id = tc.id
        LEFT JOIN trainers t ON p.trainer_id = t.id
        LEFT JOIN training_centres home_tc ON t.assigned_centre_id = home_tc.id
        ORDER BY p.id
    """)
    progs = cur.fetchall()

    same_centre_count = 0
    cross_centre_count = 0
    cross_centre_list = []

    for p in progs:
        if p["centre_id"] == p["trainer_home_centre"]:
            same_centre_count += 1
        else:
            cross_centre_count += 1
            cross_centre_list.append(p)

    print(f"Total programmes analyzed: {len(progs)}")
    print(f"Programmes where trainer home centre == programme centre: {same_centre_count}")
    print(f"Programmes where trainer home centre != programme centre: {cross_centre_count}")

    print("\nSummary of Cross-Centre Assignments:")
    # Group by trainer
    by_trainer = {}
    for p in cross_centre_list:
        tname = p["trainer_name"]
        if tname not in by_trainer:
            by_trainer[tname] = {"home": p["trainer_home_centre_name"], "home_id": p["trainer_home_centre"], "progs": []}
        by_trainer[tname]["progs"].append({"prog_id": p["prog_id"], "prog_code": p["prog_code"], "centre_id": p["centre_id"], "centre_name": p["centre_name"]})

    for tname, data in by_trainer.items():
        print(f"\nTrainer: {tname} (Home Centre: {data['home']} [ID {data['home_id']}])")
        print(f"  Cross-centre programmes count: {len(data['progs'])}")
        centres_assigned = sorted(list(set(f"{prg['centre_name']} (ID {prg['centre_id']})" for prg in data["progs"])))
        print(f"  Visiting/Delivering at centres: {', '.join(centres_assigned[:4])}{'...' if len(centres_assigned) > 4 else ''}")

    # Check Student Portal Programme 19 (ENR-000104)
    cur.execute("""
        SELECT e.id, e.code, e.citizen_name, e.program_id, p.code as prog_code, p.title as prog_title,
               e.centre_id, tc.name as centre_name, p.trainer_id, t.name as trainer_name,
               t.assigned_centre_id as trainer_home_centre, t.qualification
        FROM enrollments e
        JOIN training_programs p ON e.program_id = p.id
        JOIN training_centres tc ON e.centre_id = tc.id
        LEFT JOIN trainers t ON p.trainer_id = t.id
        WHERE e.code = 'ENR-000104'
    """)
    enr_trainer = cur.fetchone()
    print("\nStudent Portal Programme 19 Trainer Assignment for ENR-000104:")
    print(f"  Enrolment: {enr_trainer['code']} ({enr_trainer['citizen_name']})")
    print(f"  Programme: {enr_trainer['prog_title']} [ID {enr_trainer['program_id']}]")
    print(f"  Centre: {enr_trainer['centre_name']} [ID {enr_trainer['centre_id']}]")
    print(f"  Assigned Trainer: {enr_trainer['trainer_name']} (Trainer ID {enr_trainer['trainer_id']})")
    print(f"  Trainer Base/Home Centre: ID {enr_trainer['trainer_home_centre']}")
    print(f"  Qualification: {enr_trainer['qualification']}")

conn.close()
