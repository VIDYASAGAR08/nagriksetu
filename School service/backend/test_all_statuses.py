import sqlite3

db_path = '/app/data/nagriksetu.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
from main import get_institution_admin_status_dict

schools = conn.execute("SELECT school_id, school_name, category, district, school_type FROM schools ORDER BY school_id").fetchall()
print(f"Total schools: {len(schools)}")

all_active = True
for s in schools:
    st = get_institution_admin_status_dict(conn, s["school_id"], s)
    status_label = st.get("status")
    btn = st.get("button_label")
    can_login = st.get("can_login")
    if status_label != "ACTIVE" or not can_login:
        all_active = False
        print(f"NOT ACTIVE: {s['school_id']} -> status={status_label}, btn={btn}, can_login={can_login}")
    else:
        print(f"ACTIVE: {s['school_id']} -> {s['school_name']} | btn='{btn}' | can_login={can_login}")

print(f"\nAll 31 institutions ACTIVE and can_login? {all_active}")
conn.close()
