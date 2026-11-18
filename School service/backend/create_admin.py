
import getpass
import uuid

from auth import hash_password
from database import get_connection


def create_admin():
    email = input("Enter administrator email: ").strip().lower()

    if not email or "@" not in email:
        print("Please enter a valid email address.")
        return

    password = getpass.getpass("Create administrator password (12+ characters): ")
    confirm = getpass.getpass("Confirm administrator password: ")

    if password != confirm:
        print("Passwords do not match.")
        return

    try:
        password_hash = hash_password(password)
    except ValueError as error:
        print(error)
        return

    conn = get_connection()

    try:
        existing = conn.execute(
            "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE",
            (email,),
        ).fetchone()

        if existing:
            print("An account with this email already exists.")
            return

        conn.execute(
            """
            INSERT INTO users (
                user_id,
                email,
                phone,
                password_hash,
                role,
                school_id,
                is_active
            )
            VALUES (?, ?, NULL, ?, 'school_admin', NULL, 1)
            """,
            (str(uuid.uuid4()), email, password_hash),
        )

        conn.commit()
        print("Administrator account created successfully.")
        print("Email:", email)
        print("Role: school_admin")

    finally:
        conn.close()


if __name__ == "__main__":
    create_admin()
