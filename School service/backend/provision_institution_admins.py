import sqlite3
import uuid
import datetime
import os
from auth import hash_password

db_path = '/app/data/nagriksetu.db' if os.path.exists('/app/data/nagriksetu.db') else r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
print(f"Connecting to DB at: {db_path}")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 1. Add must_change_password column to users if not present
c.execute("PRAGMA table_info(users)")
cols = [r[1] for r in c.fetchall()]
if 'must_change_password' not in cols:
    print("Adding must_change_password column to users table...")
    c.execute("ALTER TABLE users ADD COLUMN must_change_password INTEGER DEFAULT 0")
    conn.commit()
    print("Column must_change_password added.")
else:
    print("Column must_change_password already exists.")

# 2. Master Credentials Mapping by Name and authoritative Live Database ID
# Format: (db_id, institution_name, doc_id, email, temp_password, category)
provision_list = [
    # Schools (14 to create)
    ("SCH001", "Government Model School", "SCH001", "government.model@edu.in", "government@123", "Schools (K-10)"),
    ("SCH002", "Shanti Vidya Mandir", "SCH002", "shanti@edu.in", "shanti@123", "Schools (K-10)"),
    ("SCH003", "National Public School", "SCH003", "national.public@edu.in", "national@123", "Schools (K-10)"),
    ("SCH004", "Sri Vidya School", "SCH004", "sri.vidya@edu.in", "srividya@123", "Schools (K-10)"),
    ("SCH005", "Green Valley School", "SCH005", "green.valley@edu.in", "greenvalley@123", "Schools (K-10)"),
    ("SCH006", "Bharat Education School", "SCH006", "bharat@edu.in", "bharat@123", "Schools (K-10)"),
    ("SCH007", "New Horizon School", "SCH007", "newhorizon@edu.in", "newhorizon@123", "Schools (K-10)"),
    ("SCH008", "Vivekananda School", "SCH008", "vivekananda@edu.in", "vivekananda@123", "Schools (K-10)"),
    ("SCH009", "Saraswati Vidya Kendra", "SCH009", "saraswati@edu.in", "saraswati@123", "Schools (K-10)"),
    ("SCH010", "Karnataka Public School", "SCH010", "karnataka.public@edu.in", "karnataka@123", "Schools (K-10)"),
    ("SCH016", "Belagavi Public School", "SCH016", "belagavi@edu.in", "belagavi@123", "Schools (K-10)"),
    ("SCH017", "Dharwad Vidya School", "SCH017", "dharwad@edu.in", "dharwad@123", "Schools (K-10)"),
    ("SCH018", "Shivamogga Model School", "SCH018", "shivamogga@edu.in", "shivamogga@123", "Schools (K-10)"),
    ("SCH020", "Kalaburagi Public School", "SCH020", "kalaburagi@edu.in", "kalaburagi@123", "Schools (K-10)"),

    # PU Colleges (5 to create)
    ("SCH011", "Tumakuru Model Pre-University College", "SCH011", "tumakuru.pu@edu.in", "tumakuru@123", "PU Colleges (11-12)"),
    ("SCH012", "Mysuru Government Pre-University College", "SCH012", "mysuru.pu@edu.in", "mysuru@123", "PU Colleges (11-12)"),
    ("SCH013", "Mandya Government Pre-University College", "SCH013", "mandya.pu@edu.in", "mandya@123", "PU Colleges (11-12)"),
    ("SCH014", "Hassan Valley Pre-University College", "SCH014", "hassan.pu@edu.in", "hassan@123", "PU Colleges (11-12)"),
    ("SCH015", "Udupi Government Pre-University College", "SCH015", "udupi.pu@edu.in", "udupi@123", "PU Colleges (11-12)"),

    # Higher Education: Degree Colleges (5 to create)
    ("COL001", "Ramaiah Institute of Technology (MSRIT)", "COL001", "ramaiah@edu.in", "ramaiah@123", "Degree Colleges"),
    ("COL002", "R.V. College of Engineering (RVCE)", "COL005", "rvce@edu.in", "rvce@123", "Degree Colleges"),
    ("COL003", "BMS College of Engineering (BMSCE)", "COL003", "bms@edu.in", "bms@123", "Degree Colleges"),
    ("COL005", "The National Institute of Engineering (NIE)", "COL004", "nie@edu.in", "nie@123", "Degree Colleges"),
    ("COL007", "Mount Carmel College (Autonomous)", "COL002", "mountcarmel@edu.in", "mountcarmel@123", "Degree Colleges"),

    # Higher Education: Universities (5 to create)
    ("COL004", "PES University (Ring Road Campus)", "COL007", "pes@edu.in", "pes@123", "Universities"),
    ("COL006", "St. Joseph's University", "COL008", "stjosephs@edu.in", "stjosephs@123", "Universities"),
    ("COL008", "KLE Technological University (BVBCET)", "COL006", "kle.tech@edu.in", "kletech@123", "Universities"),
    ("COL009", "University of Mysore (Manasagangotri)", "COL009", "university.mysore@edu.in", "mysore@123", "Universities"),
    ("COL010", "Visvesvaraya Technological University (VTU)", "COL010", "vtu@edu.in", "vtu@123", "Universities"),
]

# Track actions
created_count = 0
preserved_count = 0
now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for db_id, name, doc_id, email, temp_pwd, cat in provision_list:
    # Check if this institution already has an active administrator account
    existing_user = c.execute("SELECT user_id, email, full_name, role, is_active FROM users WHERE email = ? COLLATE NOCASE", (email,)).fetchone()
    
    if existing_user:
        print(f"[PRESERVED] Email {email} already exists for user {existing_user['user_id']}.")
        user_id = existing_user["user_id"]
        # Ensure active
        c.execute("UPDATE users SET is_active = 1, status = 'active', school_id = ?, role = 'school_admin' WHERE user_id = ?", (db_id, user_id))
        preserved_count += 1
    else:
        # Create new user
        user_id = str(uuid.uuid4())
        pwd_hash = hash_password(temp_pwd)
        c.execute("""
            INSERT INTO users (
                user_id, email, phone, password_hash, role, school_id,
                is_active, created_at, full_name, status, is_email_verified, must_change_password
            ) VALUES (?, ?, NULL, ?, 'school_admin', ?, 1, ?, ?, 'active', 1, 1)
        """, (user_id, email, pwd_hash, db_id, now_str, f"{name} Administrator"))
        created_count += 1
        print(f"[CREATED] Administrator for {db_id} ({name}): {email}")

    # Ensure user_institution_roles has active mapping
    c.execute("DELETE FROM user_institution_roles WHERE user_id = ? AND institution_id = ?", (user_id, db_id))
    c.execute("""
        INSERT INTO user_institution_roles (
            id, user_id, institution_id, role_id, status, created_at, created_by
        ) VALUES (?, ?, ?, 'school_admin', 'active', ?, 'system_provisioning')
    """, (str(uuid.uuid4()), user_id, db_id, now_str))

    # Ensure institution_staff_permissions has full permissions
    c.execute("DELETE FROM institution_staff_permissions WHERE user_id = ? AND institution_id = ?", (user_id, db_id))
    c.execute("""
        INSERT INTO institution_staff_permissions (
            id, user_id, institution_id, role_id, can_view_applications, can_review_details,
            can_request_clarification, can_recommend_decision, can_approve_stage1, can_view_history,
            can_manage_academics, can_manage_students, updated_at, updated_by
        ) VALUES (?, ?, ?, 'school_admin', 1, 1, 1, 1, 1, 1, 1, 1, ?, 'system_provisioning')
    """, (str(uuid.uuid4()), user_id, db_id, now_str))

# Ballari Education School (SCH019)
ballari_admin = c.execute("SELECT user_id, email, full_name, role, school_id, is_active FROM users WHERE email = 'rao@edu.in'").fetchone()
if ballari_admin:
    print(f"[PRESERVED] SCH019 existing administrator {ballari_admin['email']} ('{ballari_admin['full_name']}') preserved.")
    preserved_count += 1
    # Ensure role is school_admin and active
    c.execute("UPDATE users SET is_active = 1, status = 'active', school_id = 'SCH019', role = 'school_admin' WHERE user_id = ?", (ballari_admin["user_id"],))
    c.execute("UPDATE user_institution_roles SET status = 'active', role_id = 'school_admin' WHERE user_id = ? AND institution_id = 'SCH019'", (ballari_admin["user_id"],))

# Also provision ballari@edu.in / ballari@123 if not exists so both credentials work seamlessly
ballari_doc_user = c.execute("SELECT user_id FROM users WHERE email = 'ballari@edu.in'").fetchone()
if not ballari_doc_user:
    b_uid = str(uuid.uuid4())
    b_hash = hash_password("ballari@123")
    c.execute("""
        INSERT INTO users (
            user_id, email, phone, password_hash, role, school_id,
            is_active, created_at, full_name, status, is_email_verified, must_change_password
        ) VALUES (?, 'ballari@edu.in', NULL, ?, 'school_admin', 'SCH019', 1, ?, 'Ballari Education School Administrator', 'active', 1, 1)
    """, (b_uid, b_hash, now_str))
    c.execute("""
        INSERT INTO user_institution_roles (
            id, user_id, institution_id, role_id, status, created_at, created_by
        ) VALUES (?, ?, 'SCH019', 'school_admin', 'active', ?, 'system_provisioning')
    """, (str(uuid.uuid4()), b_uid, now_str))
    c.execute("""
        INSERT INTO institution_staff_permissions (
            id, user_id, institution_id, role_id, can_view_applications, can_review_details,
            can_request_clarification, can_recommend_decision, can_approve_stage1, can_view_history,
            can_manage_academics, can_manage_students, updated_at, updated_by
        ) VALUES (?, ?, 'SCH019', 'school_admin', 1, 1, 1, 1, 1, 1, 1, 1, ?, 'system_provisioning')
    """, (str(uuid.uuid4()), b_uid, now_str))
    print("[CREATED] Additional credential account for SCH019: ballari@edu.in (ballari@123)")

# Check Vidya Mandir English School (SCH0099)
sch099_admin = c.execute("SELECT user_id, email, full_name, role, school_id, is_active FROM users WHERE email = 'admin.sch0099@gmail.com'").fetchone()
if sch099_admin:
    print(f"[PRESERVED] SCH0099 existing administrator {sch099_admin['email']} ('{sch099_admin['full_name']}') preserved.")
    preserved_count += 1

conn.commit()
conn.close()

print(f"\nProvisioning Complete! Created: {created_count}, Preserved: {preserved_count}")
