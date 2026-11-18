"""
test_disposable_migration.py
Tests database schema changes, population of admission contacts, and update_requests expansion
on the disposable database copy without touching live data.
"""
import sqlite3
import hashlib
import uuid

DISPOSABLE_DB = 'C:/Users/callm/nagriksetu/backend/data/nagriksetu_disposable.db'

def run_disposable_migration():
    conn = sqlite3.connect(DISPOSABLE_DB)
    c = conn.cursor()

    # Step 1: Create student_admission_contacts
    c.execute('''
        CREATE TABLE IF NOT EXISTS student_admission_contacts (
            admission_contact_id TEXT PRIMARY KEY,
            permanent_student_id TEXT NOT NULL,
            school_id TEXT NOT NULL,
            father_name TEXT,
            father_phone TEXT NOT NULL,
            father_email TEXT,
            mother_name TEXT,
            mother_phone TEXT NOT NULL,
            mother_email TEXT,
            residential_address TEXT,
            emergency_contact_name TEXT,
            emergency_contact_phone TEXT,
            emergency_contact_relation TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (permanent_student_id) REFERENCES students(permanent_student_id) ON DELETE CASCADE,
            FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE,
            UNIQUE (permanent_student_id)
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_adm_contacts_psid ON student_admission_contacts(permanent_student_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_adm_contacts_fphone ON student_admission_contacts(father_phone)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_adm_contacts_mphone ON student_admission_contacts(mother_phone)')

    # Step 2: Create parent_otp_verifications
    c.execute('''
        CREATE TABLE IF NOT EXISTS parent_otp_verifications (
            session_id TEXT PRIMARY KEY,
            permanent_student_id TEXT NOT NULL,
            contact_role TEXT NOT NULL CHECK (contact_role IN ('father', 'mother', 'secondary_guardian')),
            phone TEXT NOT NULL,
            otp_hash TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 5,
            expires_at TEXT NOT NULL,
            is_verified INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (permanent_student_id) REFERENCES students(permanent_student_id) ON DELETE CASCADE
        )
    ''')

    # Step 3: Migrate update_requests to support all 6 statuses and new columns
    c.execute('PRAGMA foreign_keys = OFF')
    c.execute('BEGIN TRANSACTION')

    c.execute('''
        CREATE TABLE new_update_requests (
            request_id TEXT PRIMARY KEY,
            permanent_student_id TEXT NOT NULL,
            guardian_id TEXT NOT NULL,
            school_id TEXT,
            parent_user_id TEXT,
            request_type TEXT NOT NULL CHECK (
                request_type IN ('request_change', 'report_change', 'contact_change', 'address_change', 'emergency_contact_change')
            ),
            field_name TEXT NOT NULL,
            old_value TEXT,
            proposed_value TEXT NOT NULL,
            reason TEXT,
            supporting_document_id TEXT,
            supporting_document_url TEXT,
            supporting_document_name TEXT,
            status TEXT NOT NULL DEFAULT 'submitted'
                CHECK (status IN (
                    'submitted', 'pending', 'under_review', 'additional_info_required', 'approved', 'rejected', 'cancelled'
                )),
            reviewed_by_user_id TEXT,
            review_comment TEXT,
            submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TEXT,
            FOREIGN KEY (permanent_student_id) REFERENCES students(permanent_student_id),
            FOREIGN KEY (guardian_id) REFERENCES guardians(guardian_id),
            FOREIGN KEY (school_id) REFERENCES schools(school_id),
            FOREIGN KEY (parent_user_id) REFERENCES users(user_id),
            FOREIGN KEY (supporting_document_id) REFERENCES student_documents(document_id),
            FOREIGN KEY (reviewed_by_user_id) REFERENCES users(user_id)
        )
    ''')

    # Copy existing records
    c.execute('''
        INSERT INTO new_update_requests (
            request_id, permanent_student_id, guardian_id, request_type,
            field_name, old_value, proposed_value, reason,
            supporting_document_id, status, reviewed_by_user_id,
            review_comment, submitted_at, reviewed_at
        )
        SELECT request_id, permanent_student_id, guardian_id, request_type,
               field_name, old_value, proposed_value, reason,
               supporting_document_id, status, reviewed_by_user_id,
               review_comment, submitted_at, reviewed_at
        FROM update_requests
    ''')

    c.execute('DROP TABLE update_requests')
    c.execute('ALTER TABLE new_update_requests RENAME TO update_requests')
    c.execute('COMMIT')
    c.execute('PRAGMA foreign_keys = ON')

    # Step 4: Populate student_admission_contacts for students
    # Deterministic generation for all 30,000 students
    print("Populating admission contacts for students...")
    students = c.execute('SELECT student_id, permanent_student_id, student_name, school_id FROM students').fetchall()
    
    father_surnames = ["Kumar", "Rao", "Gowda", "Patil", "Shetty", "Hegde", "Murthy", "Prasad", "Naik", "Reddy"]
    father_firstnames = ["Ramesh", "Suresh", "Manjunath", "Venkatesh", "Anand", "Nagaraj", "Santosh", "Prakash", "Vijay", "Krishna"]
    mother_firstnames = ["Sunitha", "Lakshmi", "Shailaja", "Geetha", "Parvathi", "Radha", "Meenakshi", "Sujatha", "Roopa", "Anitha"]
    areas = ["Malleshwaram", "Jayanagar", "Indiranagar", "Rajajinagar", "Basavanagudi", "Koramangala", "Hebbal", "Vijayanagar"]

    batch = []
    for s_id, psid, s_name, sch_id in students:
        # Use student_id to deterministically derive contacts
        h = int(hashlib.md5(s_id.encode()).hexdigest(), 16)
        
        f_first = father_firstnames[h % len(father_firstnames)]
        f_last = father_surnames[(h // 10) % len(father_surnames)]
        f_name = f"{f_first} {f_last}"
        # Father phone: 98450xxxxx
        f_phone = f"9845{h % 1000000:06d}"
        
        m_first = mother_firstnames[(h // 100) % len(mother_firstnames)]
        m_name = f"{m_first} {f_last}"
        # Mother phone: 97410xxxxx (distinct from father)
        m_phone = f"9741{(h // 7) % 1000000:06d}"
        
        area = areas[(h // 50) % len(areas)]
        addr = f"#{h % 200 + 1}, {h % 15 + 1}th Cross, {area}, Bengaluru, Karnataka 560{h % 90 + 10:02d}"
        
        cid = f"ADM-CONT-{s_id}"
        batch.append((
            cid, psid, sch_id,
            f_name, f_phone, f"father.{s_id.lower()}@example.com",
            m_name, m_phone, f"mother.{s_id.lower()}@example.com",
            addr,
            f_name, f_phone, "Father"
        ))

    c.executemany('''
        INSERT OR REPLACE INTO student_admission_contacts (
            admission_contact_id, permanent_student_id, school_id,
            father_name, father_phone, father_email,
            mother_name, mother_phone, mother_email,
            residential_address,
            emergency_contact_name, emergency_contact_phone, emergency_contact_relation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', batch)
    conn.commit()

    # Step 5: Verification on disposable DB
    integrity = c.execute('PRAGMA integrity_check').fetchall()
    fk_check = c.execute('PRAGMA foreign_key_check').fetchall()
    stu_count = c.execute('SELECT count(*) FROM students').fetchone()[0]
    adm_count = c.execute('SELECT count(*) FROM student_admission_contacts').fetchone()[0]
    req_count = c.execute('SELECT count(*) FROM update_requests').fetchone()[0]

    print("=== DISPOSABLE TEST RESULTS ===")
    print("Integrity check:", integrity)
    print("Foreign key check:", fk_check)
    print("Students intact:", stu_count)
    print("Admission contacts created:", adm_count)
    print("Update requests intact:", req_count)
    
    assert integrity == [('ok',)], "Integrity check failed"
    assert fk_check == [], f"FK violations: {fk_check}"
    assert stu_count == 30000, "Student count altered"
    assert adm_count == 30000, "Admission contacts count mismatch"

    # Sample contact check
    sample = c.execute('SELECT * FROM student_admission_contacts LIMIT 1').fetchone()
    print("Sample admission contact:", sample)

    conn.close()
    print("\n[SUCCESS] Disposable migration verified with 100% success!")

if __name__ == '__main__':
    run_disposable_migration()
