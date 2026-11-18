
import random
from database import get_connection, create_tables

random.seed(42)

school_names = [
    "Government Model School",
    "Shanti Vidya Mandir",
    "National Public School",
    "Sri Vidya School",
    "Green Valley School",
    "Bharat Education School",
    "New Horizon School",
    "Vivekananda School",
    "Saraswati Vidya Kendra",
    "Karnataka Public School",
]

first_names = [
    "Aarav", "Ananya", "Arjun", "Asha", "Diya",
    "Ishaan", "Kavya", "Kiran", "Meera", "Nikhil",
    "Pooja", "Rahul", "Riya", "Sanjay", "Sneha",
    "Varun", "Vijay", "Divya", "Manoj", "Priya",
]

last_names = [
    "Sharma", "Patil", "Reddy", "Kumar", "Gowda",
    "Shetty", "Naik", "Joshi", "Verma", "Rao",
]

districts = [
    "Bengaluru Urban", "Mysuru", "Belagavi", "Dharwad",
    "Vijayapura", "Ballari", "Shivamogga", "Udupi",
    "Tumakuru", "Kalaburagi",
]

def seed_data():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # Avoid duplicating records if this script is run again.
    existing = cursor.execute(
        "SELECT COUNT(*) FROM schools"
    ).fetchone()[0]

    if existing > 0:
        print("Schools already exist. No records were changed.")
        conn.close()
        return

    for school_number in range(1, 11):
        school_id = f"SCH{school_number:03d}"

        cursor.execute(
            """
            INSERT INTO schools
            (school_id, school_name, district, state, school_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                school_id,
                school_names[school_number - 1],
                districts[school_number - 1],
                "Karnataka",
                "Government" if school_number % 2 else "Private",
            ),
        )

        for standard in range(1, 11):
            for student_number in range(1, 61):
                student_id = (
                    f"{school_id}-STD{standard:02d}-"
                    f"{student_number:03d}"
                )
                student_name = (
                    f"{random.choice(first_names)} "
                    f"{random.choice(last_names)}"
                )
                age = standard + 5 + random.choice([0, 0, 0, 1])
                section = "A"

                cursor.execute(
                    """
                    INSERT INTO students
                    (student_id, student_name, school_id,
                     standard, section, age)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student_id,
                        student_name,
                        school_id,
                        standard,
                        section,
                        age,
                    ),
                )

    conn.commit()

    school_count = cursor.execute(
        "SELECT COUNT(*) FROM schools"
    ).fetchone()[0]

    student_count = cursor.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    print(f"Schools created: {school_count}")
    print(f"Students created: {student_count}")

    conn.close()

if __name__ == "__main__":
    seed_data()
