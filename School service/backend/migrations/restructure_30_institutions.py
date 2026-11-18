import sqlite3
import shutil
import time
import os

DB_PATH = "C:/Users/callm/nagriksetu/backend/data/nagriksetu.db"

def run_restructure():
    print("=" * 70)
    print("NAGRIKSETU: RESTRUCTURING INSTITUTION DIRECTORY TO 30 INSTITUTIONS")
    print("=" * 70)

    # 1. Safety Backup
    ts = int(time.time())
    backup_path = f"{DB_PATH}.backup_restructure_30_{ts}"
    shutil.copyfile(DB_PATH, backup_path)
    print(f"[*] Verified pre-migration backup created: {backup_path}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        conn.execute("BEGIN IMMEDIATE")

        # 2. Add category column to schools if not already present
        cols = [c[1] for c in cur.execute("PRAGMA table_info(schools)").fetchall()]
        if "category" not in cols:
            cur.execute("ALTER TABLE schools ADD COLUMN category TEXT")
            print("[*] Added 'category' column to schools table.")

        # 3. Restructure Category 1: 15 Schools (K-10)
        # SCH001 to SCH010 (10 pure K-10 schools) + SCH016 to SCH020 (5 schools)
        schools_k10_ids = [
            "SCH001", "SCH002", "SCH003", "SCH004", "SCH005",
            "SCH006", "SCH007", "SCH008", "SCH009", "SCH010",
            "SCH016", "SCH017", "SCH018", "SCH019", "SCH020"
        ]
        for sid in schools_k10_ids:
            cur.execute("""
                UPDATE schools
                SET category = 'Schools (K-10)',
                    school_type = 'School'
                WHERE school_id = ?
            """, (sid,))
        print(f"[*] Configured {len(schools_k10_ids)} institutions as Category: 'Schools (K-10)'")

        # 4. Restructure Category 2: 5 PU Colleges (11-12)
        # SCH011 to SCH015
        pu_colleges = [
            ("SCH011", "Tumakuru Model Pre-University College", "Tumakuru"),
            ("SCH012", "Mysuru Government Pre-University College", "Mysuru"),
            ("SCH013", "Mandya Government Pre-University College", "Mandya"),
            ("SCH014", "Hassan Valley Pre-University College", "Hassan"),
            ("SCH015", "Udupi Government Pre-University College", "Udupi")
        ]
        for sid, sname, dist in pu_colleges:
            cur.execute("""
                UPDATE schools
                SET school_name = ?,
                    category = 'PU Colleges (11-12)',
                    school_type = 'PU College',
                    district = ?
                WHERE school_id = ?
            """, (sname, dist, sid))
        print(f"[*] Configured {len(pu_colleges)} institutions as Category: 'PU Colleges (11-12)'")

        # 5. Restructure Category 3: 5 Degree Colleges
        # COL001, COL002, COL003, COL005, COL007
        degree_colleges = [
            ("COL001", "Ramaiah Institute of Technology (MSRIT)"),
            ("COL002", "R.V. College of Engineering (RVCE)"),
            ("COL003", "BMS College of Engineering (BMSCE)"),
            ("COL005", "The National Institute of Engineering (NIE)"),
            ("COL007", "Mount Carmel College (Autonomous)")
        ]
        for cid, cname in degree_colleges:
            cur.execute("""
                UPDATE schools
                SET school_name = ?,
                    category = 'Degree Colleges',
                    school_type = 'Degree College'
                WHERE school_id = ?
            """, (cname, cid))
        print(f"[*] Configured {len(degree_colleges)} institutions as Category: 'Degree Colleges'")

        # 6. Restructure Category 4: 5 Universities
        # COL004, COL006, COL008, COL009, COL010 (VTU)
        universities_existing = [
            ("COL004", "PES University (Ring Road Campus)"),
            ("COL006", "St. Joseph's University"),
            ("COL008", "KLE Technological University (BVBCET)"),
            ("COL009", "University of Mysore (Manasagangotri)")
        ]
        for uid, uname in universities_existing:
            cur.execute("""
                UPDATE schools
                SET school_name = ?,
                    category = 'Universities',
                    school_type = 'University'
                WHERE school_id = ?
            """, (uname, uid))

        # Reclassify COL010 to Visvesvaraya Technological University (VTU)
        cur.execute("""
            UPDATE schools
            SET school_name = 'Visvesvaraya Technological University (VTU)',
                category = 'Universities',
                school_type = 'University',
                district = 'Belagavi',
                description = 'Premier statutory state technical university in Karnataka established under the VTU Act 1994, headquartered in Jnana Sangama Belagavi.',
                website = 'https://vtu.ac.in',
                email = 'registrar@vtu.ac.in',
                affiliation = 'UGC Act 12B Recognized, AICTE Approved, Government of Karnataka',
                recognition = 'NAAC A+ Accredited State University',
                established_year = 1998
            WHERE school_id = 'COL010'
        """)
        print("[*] Configured 5 institutions as Category: 'Universities' (including COL010 VTU)")

        conn.commit()
        print("[*] Transaction committed successfully.")

        # 7. Verification of Category Counts
        cat_counts = cur.execute("SELECT category, count(*) FROM schools GROUP BY category").fetchall()
        print("\n--- FINAL ACTIVE INSTITUTION DISTRIBUTION ---")
        for cat, cnt in cat_counts:
            print(f"  • {cat:<25}: {cnt}")
        
        total_schools = cur.execute("SELECT count(*) FROM schools").fetchone()[0]
        print(f"  TOTAL ACTIVE INSTITUTIONS: {total_schools}")

        # Integrity & Foreign Key checks
        integrity = cur.execute("PRAGMA integrity_check").fetchone()[0]
        fk_violations = cur.execute("PRAGMA foreign_key_check").fetchall()
        print(f"[*] PRAGMA integrity_check: {integrity}")
        print(f"[*] PRAGMA foreign_key_check violations: {len(fk_violations)}")

        # Student baseline check
        student_count = cur.execute("SELECT count(*) FROM students").fetchone()[0]
        enrollment_count = cur.execute("SELECT count(*) FROM enrollments").fetchone()[0]
        print(f"[*] Preserved Students: {student_count} / 30,001")
        print(f"[*] Preserved Enrollments: {enrollment_count} / 30,001")

        assert total_schools == 30, f"Expected 30 schools, found {total_schools}"
        assert student_count == 30001, f"Expected 30001 students, found {student_count}"
        assert enrollment_count == 30001, f"Expected 30001 enrollments, found {enrollment_count}"
        assert integrity == "ok", "Integrity check failed"
        assert len(fk_violations) == 0, f"FK violations found: {fk_violations}"
        print("\n[SUCCESS] All restructure assertions passed!")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Restructure failed, rolled back: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_restructure()
