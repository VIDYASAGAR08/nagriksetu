
import os
import sqlite3

database_path = os.environ.get("DATABASE_PATH", "data/nagriksetu.db")

conn = sqlite3.connect(database_path)

try:
    cursor = conn.execute(
        """
        UPDATE users
        SET school_id = ?
        WHERE email = ? COLLATE NOCASE
          AND role = ?
        """,
        ("SCH001", "callmephalguna@gmail.com", "school_admin"),
    )

    conn.commit()

    print("Updated admin accounts:", cursor.rowcount)

    account = conn.execute(
        """
        SELECT email, role, school_id
        FROM users
        WHERE email = ? COLLATE NOCASE
        """,
        ("callmephalguna@gmail.com",),
    ).fetchone()

    print("Administrator:", account)

finally:
    conn.close()
