
import getpass
import uuid

from auth import hash_password
from database import get_connection


def main():
    email = input("Test parent email: ").strip().lower()
    full_name = input("Parent full name: ").strip()
    phone = input("Test parent phone number: ").strip()

    if not email or "@" not in email:
        print("Enter a valid email address.")
        return

    if not full_name:
        print("Enter the parent's name.")
        return

    if not phone:
        print("Phone number is required.")
        return

    password = getpass.getpass("Create password (12+ characters): ")
    confirm = getpass.getpass("Confirm password: ")

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
            """
            SELECT user_id FROM users
            WHERE email = ? COLLATE NOCASE OR phone = ?
            """,
            (email, phone),
        ).fetchone()

        if existing:
            print("That email or phone number is already registered.")
            return

        student = conn.execute(
            """
            SELECT permanent_student_id
            FROM students
            WHERE student_id = ?
            """,
            ("SCH001-STD01-001",),
        ).fetchone()

        if student is None:
            print("Demo student not found. No changes made.")
            return

        user_id = str(uuid.uuid4())
        guardian_id = str(uuid.uuid4())
        link_id = str(uuid.uuid4())

        conn.execute(
            """
            INSERT INTO users (
                user_id, email, phone, password_hash,
                role, school_id, is_active
            )
            VALUES (?, ?, ?, ?, 'parent', NULL, 1)
            """,
            (user_id, email, phone, password_hash),
        )

        conn.execute(
            """
            INSERT INTO guardians (
                guardian_id, user_id, full_name,
                relationship, phone, email
            )
            VALUES (?, ?, ?, 'Parent', ?, ?)
            """,
            (guardian_id, user_id, full_name, phone, email),
        )

        conn.execute(
            """
            INSERT INTO student_guardians (
                student_guardian_id, permanent_student_id,
                guardian_id, can_view_records,
                can_request_updates, is_verified
            )
            VALUES (?, ?, ?, 1, 1, 1)
            """,
            (link_id, student["permanent_student_id"], guardian_id),
        )

        conn.commit()

        print("\nTest parent account created successfully.")
        print("Parent email:", email)
        print("Linked demo student: SCH001-STD01-001")
        print("Parent role: parent")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()
