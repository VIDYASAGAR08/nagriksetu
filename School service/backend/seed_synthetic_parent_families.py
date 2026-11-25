"""
seed_synthetic_parent_families.py
Idempotent synthetic parent/guardian generator for NagrikSetu School Service.
Creates 3 families:
- Family 1 (3 children): Father (Ramesh Kumar) & Mother (Lakshmi Kumar)
- Family 2 (2 children): Father (Suresh Patil) & Mother (Deepa Patil)
- Family 3 (1 child): Father (Anand Sharma) & Mother (Priya Sharma)
Both parents have independent login accounts and view all their linked children.
"""

import os
import sys
import sqlite3
import uuid

# Check if auth module is importable for hash_password, otherwise compute hash inside container
try:
    from auth import hash_password
except Exception:
    # Pre-computed Argon2id hash for "Password@123"
    hash_password = lambda p: "$argon2id$v=19$m=65536,t=3,p=4$rY2kP+Y6wP/V6eQ6jM6xkg$J5vC9z+sDqB7xL1m0v+U4pP2gR7vT1wS4aY8dZ9cE2A"

DEFAULT_PASSWORD = "Password@123"

FAMILIES = [
    {
        "family_code": "FAM0001",
        "description": "Family with 3 children (Kumar Family)",
        "parents": [
            {
                "full_name": "Ramesh Kumar",
                "role_in_family": "Father",
                "email": "ramesh.kumar@example.com",
                "phone": "9845011001",
                "address": "104, 3rd Main, Malleshwaram, Bengaluru, Karnataka"
            },
            {
                "full_name": "Lakshmi Kumar",
                "role_in_family": "Mother",
                "email": "lakshmi.kumar@example.com",
                "phone": "9845011002",
                "address": "104, 3rd Main, Malleshwaram, Bengaluru, Karnataka"
            }
        ],
        "children": [
            {"student_id": "SCH01031", "psid": "NS-A0760A0835A448ADA7874F2038A5043E", "name": "Ananya Kumar"},
            {"student_id": "SCH01065", "psid": "NS-D4C6C4C6B30A42D0997A17DAF10381EC", "name": "Arjun Kumar"},
            {"student_id": "SCH01169", "psid": "NS-49151FED94664057B65B5AADE96D6EED", "name": "Diya Kumar"}
        ]
    },
    {
        "family_code": "FAM0002",
        "description": "Family with 2 children (Patil Family)",
        "parents": [
            {
                "full_name": "Suresh Patil",
                "role_in_family": "Father",
                "email": "suresh.patil@example.com",
                "phone": "9845022001",
                "address": "45, 7th Cross, Indiranagar, Bengaluru, Karnataka"
            },
            {
                "full_name": "Deepa Patil",
                "role_in_family": "Mother",
                "email": "deepa.patil@example.com",
                "phone": "9845022002",
                "address": "45, 7th Cross, Indiranagar, Bengaluru, Karnataka"
            }
        ],
        "children": [
            {"student_id": "SCH01006", "psid": "NS-49123DD9E6B5440BB74806813FB2B2E0", "name": "Aarav Patil"},
            {"student_id": "SCH01475", "psid": "NS-7C3AE624C3334C40BFDD171B7D3B7186", "name": "Riya Patil"}
        ]
    },
    {
        "family_code": "FAM0003",
        "description": "Family with 1 child (Sharma Family)",
        "parents": [
            {
                "full_name": "Anand Sharma",
                "role_in_family": "Father",
                "email": "anand.sharma@example.com",
                "phone": "9845033001",
                "address": "12, 1st Cross, Jayanagar, Bengaluru, Karnataka"
            },
            {
                "full_name": "Priya Sharma",
                "role_in_family": "Mother",
                "email": "priya.sharma@example.com",
                "phone": "9845033002",
                "address": "12, 1st Cross, Jayanagar, Bengaluru, Karnataka"
            }
        ],
        "children": [
            {"student_id": "SCH01125", "psid": "NS-FB8336A812DE468FB8E475443CF673EB", "name": "Asha Sharma"}
        ]
    }
]

def get_db_path():
    env_path = os.getenv("DATABASE_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "nagriksetu.db"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "nagriksetu.db"),
        "/app/data/nagriksetu.db",
        "backend/data/nagriksetu.db"
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

def seed_families():
    db_path = get_db_path()
    print(f"[*] Seeding synthetic families into database: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        from auth import hash_password
        hashed_pwd = hash_password(DEFAULT_PASSWORD)
    except Exception:
        # Generate valid argon2 hash using container or pwdlib
        try:
            from pwdlib import PasswordHash
            ph = PasswordHash.recommended()
            hashed_pwd = ph.hash(DEFAULT_PASSWORD)
        except Exception:
            # Fallback to existing argon2 hash from users table
            row = conn.execute("SELECT password_hash FROM users WHERE password_hash IS NOT NULL AND password_hash != '' LIMIT 1").fetchone()
            hashed_pwd = row[0] if row else "$argon2id$v=19$m=65536,t=3,p=4$dummyhash"

    with conn:
        for fam in FAMILIES:
            print(f"\nProcessing {fam['family_code']} — {fam['description']}")
            created_guardians = []

            for p_info in fam["parents"]:
                email = p_info["email"]
                phone = p_info["phone"]
                full_name = p_info["full_name"]
                rel = p_info["role_in_family"]

                # 1. Upsert User Account (Ensure role is parent)
                existing_user = conn.execute(
                    "SELECT user_id, role FROM users WHERE email = ? OR phone = ?", (email, phone)
                ).fetchone()

                if existing_user and existing_user["role"] == "parent":
                    user_id = existing_user["user_id"]
                    conn.execute("""
                        UPDATE users
                        SET full_name = ?, role = 'parent', is_active = 1, is_email_verified = 1
                        WHERE user_id = ?
                    """, (full_name, user_id))
                    print(f"  [+] Updated Parent User: {full_name} ({email}) -> {user_id}")
                else:
                    user_id = str(uuid.uuid4())
                    conn.execute("""
                        INSERT INTO users (
                            user_id, email, phone, password_hash, role,
                            is_active, is_email_verified, full_name, status, created_at
                        ) VALUES (?, ?, ?, ?, 'parent', 1, 1, ?, 'active', CURRENT_TIMESTAMP)
                    """, (user_id, email, phone, hashed_pwd, full_name))
                    print(f"  [+] Created Parent User: {full_name} ({email}) -> {user_id}")

                # 2. Upsert Guardian Record
                existing_guardian = conn.execute(
                    "SELECT guardian_id FROM guardians WHERE user_id = ?", (user_id,)
                ).fetchone()

                if existing_guardian:
                    guardian_id = existing_guardian["guardian_id"]
                    conn.execute("""
                        UPDATE guardians
                        SET full_name = ?, relationship = ?, phone = ?, email = ?, address = ?
                        WHERE guardian_id = ?
                    """, (full_name, rel, phone, email, p_info["address"], guardian_id))
                    print(f"  [+] Updated Guardian: {full_name} ({rel}) -> {guardian_id}")
                else:
                    guardian_id = str(uuid.uuid4())
                    conn.execute("""
                        INSERT INTO guardians (
                            guardian_id, user_id, full_name, relationship,
                            phone, email, address, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (guardian_id, user_id, full_name, rel, phone, email, p_info["address"]))
                    print(f"  [+] Created Guardian: {full_name} ({rel}) -> {guardian_id}")

                created_guardians.append({"guardian_id": guardian_id, "name": full_name, "rel": rel})

            # 3. Link Both Parents to All Children in this Family
            for child in fam["children"]:
                psid = child["psid"]

                # Verify student exists in students table
                stu_row = conn.execute(
                    "SELECT student_id, student_name, standard, section, school_id FROM students WHERE permanent_student_id = ?",
                    (psid,)
                ).fetchone()

                if not stu_row:
                    print(f"  [-] Warning: Student PSID {psid} not found in database! Skipping link.")
                    continue

                for g in created_guardians:
                    gid = g["guardian_id"]
                    link = conn.execute("""
                        SELECT student_guardian_id FROM student_guardians
                        WHERE permanent_student_id = ? AND guardian_id = ?
                    """, (psid, gid)).fetchone()

                    if not link:
                        link_id = str(uuid.uuid4())
                        conn.execute("""
                            INSERT INTO student_guardians (
                                student_guardian_id, permanent_student_id, guardian_id,
                                can_view_records, can_request_updates, is_verified, created_at
                            ) VALUES (?, ?, ?, 1, 1, 1, CURRENT_TIMESTAMP)
                        """, (link_id, psid, gid))
                        print(f"  [+] Linked {g['rel']} {g['name']} -> Child {stu_row['student_name']} ({psid})")
                    else:
                        conn.execute("""
                            UPDATE student_guardians
                            SET can_view_records = 1, can_request_updates = 1, is_verified = 1
                            WHERE permanent_student_id = ? AND guardian_id = ?
                        """, (psid, gid))
                        print(f"  [+] Verified Link: {g['rel']} {g['name']} -> Child {stu_row['student_name']} ({psid})")

    conn.close()
    print("\n[+] Synthetic parent families seeded successfully!")

if __name__ == "__main__":
    seed_families()
