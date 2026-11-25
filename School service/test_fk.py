import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

# Get valid user and school
u = c.execute("SELECT user_id FROM users WHERE role = 'parent' LIMIT 1").fetchone()[0]
s = c.execute("SELECT school_id FROM schools LIMIT 1").fetchone()[0]

test_id = "test-check-status-valid-id"
c.execute("""
INSERT INTO linking_requests (
    request_id, parent_user_id, school_id, student_ref, relationship_type, request_status
) VALUES (?, ?, ?, 'ST123', 'Father', 'clarification_required')
""", (test_id, u, s))
conn.commit()
print("Successfully inserted clarification_required status with valid FK!")

# Now test updating to pending_review
c.execute("UPDATE linking_requests SET request_status = 'pending_review' WHERE request_id = ?", (test_id,))
conn.commit()
print("Successfully updated to pending_review!")

# Delete test row
c.execute("DELETE FROM linking_requests WHERE request_id = ?", (test_id,))
conn.commit()

# Verify total students
st_count = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
print(f"Verified students count: {st_count}")
assert st_count == 30003

conn.close()
print("All constraint tests passed!")
