
import os
import sqlite3
import uuid
from datetime import date

DB_PATH = os.environ["DATABASE_PATH"]

TARGET_SCHOOLS = 20
TARGET_STUDENTS = 30000
NEW_SCHOOLS = 10
STUDENTS_PER_NEW_SCHOOL = 2400
ACADEMIC_YEAR = "2026-2027"

SCHOOL_NAMES = [
    "Tumakuru Model School",
    "Mysuru Public School",
    "Mandya Education School",
    "Hassan Valley School",
    "Udupi Government School",
    "Belagavi Public School",
    "Dharwad Vidya School",
    "Shivamogga Model School",
    "Ballari Education School",
    "Kalaburagi Public School",
]

LANGUAGE_BY_SECTION = {
    "A": "Kannada",
    "B": "Hindi",
    "C": "Sanskrit",
}

FIRST_NAMES = [
    "Aarav", "Ananya", "Arjun", "Asha", "Diya",
    "Ishaan", "Kavya", "Kiran", "Meera", "Nikhil",
    "Pooja", "Rahul", "Riya", "Rohan", "Sneha",
    "Vijay", "Anil", "Divya", "Manoj", "Priya",
]

LAST_NAMES = [
    "Sharma", "Rao", "Patil", "Kumar", "Shetty",
    "Reddy", "Naik", "Gowda", "Das", "Joshi",
    "Kulkarni", "Hegde", "Murthy", "Verma", "Bhat",
]


def student_name(number):
    first = FIRST_NAMES[(number - 1) % len(FIRST_NAMES)]
    last = LAST_NAMES[((number - 1) // len(FIRST_NAMES)) % len(LAST_NAMES)]
    return f"{first} {last} {number:04d}"


def create_school_if_missing(conn, school_number, school_name):
    school_id = f"SCH{school_number:03d}"

    conn.execute(
        """
        INSERT OR IGNORE INTO schools (
            school_id, school_name, district, state, school_type,
            address, description, facilities_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            school_id,
            school_name,
            "Demo District",
            "Karnataka",
            "Government",
            f"{school_name}, Karnataka",
            "Synthetic school record for the NagrikSetu demonstration.",
            '[]',
        ),
    )

    return school_id


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")

    try:
        # All expansion changes are committed together or rolled back.
        conn.execute("BEGIN IMMEDIATE")

        current_schools = conn.execute(
            "SELECT COUNT(*) FROM schools"
        ).fetchone()[0]

        current_students = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        if current_schools > TARGET_SCHOOLS:
            raise RuntimeError(
                f"Found {current_schools} schools; expected no more "
                f"than {TARGET_SCHOOLS}. No changes will be committed."
            )

        if current_students > TARGET_STUDENTS:
            raise RuntimeError(
                f"Found {current_students} students; expected no more "
                f"than {TARGET_STUDENTS}. No changes will be committed."
            )

        # Do not modify the original 10 schools or their students.
        for school_number, school_name in enumerate(
            SCHOOL_NAMES, start=11
        ):
            school_id = create_school_if_missing(
                conn, school_number, school_name
            )

            # 200 students per standard, across standards 1 through 12.
            for standard in range(1, 13):
                for number in range(1, 201):
                    student_id = (
                        f"{school_id}-STD{standard:02d}-{number:03d}"
                    )
                    permanent_id = f"NS-{student_id}"

                    # 67 students in A, 67 in B, and 66 in C.
                    if number <= 67:
                        section = "A"
                    elif number <= 134:
                        section = "B"
                    else:
                        section = "C"

                    language = LANGUAGE_BY_SECTION[section]
                    age = standard + 5

                    # Stable synthetic dates for demonstration records.
                    birth_year = 2026 - age
                    birth_date = date(
                        birth_year, 6, 15
                    ).isoformat()
                    admission_date = "2026-06-01"

                    conn.execute(
                        """
                        INSERT OR IGNORE INTO students (
                            student_id, student_name, school_id,
                            standard, section, age,
                            permanent_student_id, first_language,
                            date_of_birth, gender, admission_date,
                            enrollment_status
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            student_id,
                            student_name(
                                (school_number - 11) * 2400
                                + (standard - 1) * 200
                                + number
                            ),
                            school_id,
                            standard,
                            section,
                            age,
                            permanent_id,
                            language,
                            birth_date,
                            "Not specified",
                            admission_date,
                            "active",
                        ),
                    )

                    # Add an enrollment only when one does not exist.
                    enrollment_exists = conn.execute(
                        """
                        SELECT 1
                        FROM enrollments
                        WHERE permanent_student_id = ?
                          AND school_id = ?
                          AND academic_year = ?
                        """,
                        (permanent_id, school_id, ACADEMIC_YEAR),
                    ).fetchone()

                    if enrollment_exists is None:
                        conn.execute(
                            """
                            INSERT INTO enrollments (
                                enrollment_id, permanent_student_id,
                                school_id, academic_year, standard,
                                section, first_language, admission_date,
                                enrollment_status
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                "ENR-" + uuid.uuid4().hex.upper(),
                                permanent_id,
                                school_id,
                                ACADEMIC_YEAR,
                                standard,
                                section,
                                language,
                                admission_date,
                                "active",
                            ),
                        )

        final_schools = conn.execute(
            "SELECT COUNT(*) FROM schools"
        ).fetchone()[0]

        final_students = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        final_enrollments = conn.execute(
            "SELECT COUNT(*) FROM enrollments"
        ).fetchone()[0]

        standards = [
            row[0]
            for row in conn.execute(
                "SELECT DISTINCT standard FROM students ORDER BY standard"
            )
        ]

        sections = [
            row[0]
            for row in conn.execute(
                "SELECT DISTINCT section FROM students ORDER BY section"
            )
        ]

        print("VALIDATION")
        print("Schools:", final_schools)
        print("Students:", final_students)
        print("Enrollments:", final_enrollments)
        print("Standards:", standards)
        print("Sections:", sections)

        if final_schools != TARGET_SCHOOLS:
            raise RuntimeError(
                f"Expected {TARGET_SCHOOLS} schools, got {final_schools}."
            )

        if final_students != TARGET_STUDENTS:
            raise RuntimeError(
                f"Expected {TARGET_STUDENTS} students, got {final_students}."
            )

        if standards != list(range(1, 13)):
            raise RuntimeError("Not all 12 standards are represented.")

        if not all(section in sections for section in ("A", "B", "C")):
            raise RuntimeError("Sections A, B, and C must be represented.")

        conn.commit()
        print("\nSUCCESS: Dataset expansion committed.")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
