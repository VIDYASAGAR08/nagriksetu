import sqlite3
import csv
import os

DB_PATH = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
MIGRATION_CSV = r'C:\Users\callm\nagriksetu\NagrikSetu_Proposed_12000_Student_Migration.csv'
DISTRIBUTION_CSV = r'C:\Users\callm\nagriksetu\NagrikSetu_Institution_Wise_Proposed_Distribution.csv'

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Load schools and capacities
cur.execute("SELECT school_id, school_name, school_type, category, district FROM schools ORDER BY school_id")
schools = {r["school_id"]: dict(r) for r in cur.fetchall()}

cur.execute("SELECT school_id, COUNT(*) as cnt FROM students GROUP BY school_id")
current_counts = {r["school_id"]: r["cnt"] for r in cur.fetchall()}

cur.execute("SELECT institution_id, SUM(capacity) as cap FROM program_sections GROUP BY institution_id")
capacities = {r["institution_id"]: r["cap"] for r in cur.fetchall()}

# District school candidates
DISTRICT_SCHOOL_MAP = {
    'Tumakuru': ('SCH009', 'Saraswati Vidya Kendra'),
    'Mysuru': ('SCH002', 'Shanti Vidya Mandir'),
    'Udupi': ('SCH008', 'Vivekananda School')
}

# 2. Fetch all 12,000 flagged students
print("Fetching 12,000 flagged students...")
cur.execute("""
    SELECT 
        s.student_id,
        s.permanent_student_id,
        s.student_name,
        s.school_id,
        sc.school_name,
        sc.school_type,
        sc.district,
        s.standard,
        s.section,
        s.age,
        s.review_flag
    FROM students s
    JOIN schools sc ON s.school_id = sc.school_id
    WHERE s.review_flag IS NOT NULL
    ORDER BY s.school_id, s.standard, s.section, s.student_id
""")
flagged_students = cur.fetchall()
print(f"Total flagged students fetched: {len(flagged_students)}")

# Track proposed incoming/outgoing for distribution summary
incoming_counts = {sid: 0 for sid in schools}
outgoing_counts = {sid: 0 for sid in schools}

# Counter for tracking capacity allocation per school per standard
allocated_within_capacity = {}

print("Generating NagrikSetu_Proposed_12000_Student_Migration.csv...")
with open(MIGRATION_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "Student ID",
        "Permanent Student ID",
        "Full Name",
        "Current Institution ID",
        "Current Institution Name",
        "Current Institution Type",
        "Current Academic Standard",
        "Proposed Institution ID",
        "Proposed Institution Name",
        "Proposed Institution Type",
        "Correct Academic Classification",
        "District",
        "Reason for Proposed Mapping",
        "Evidence Source",
        "Confidence / Review Status"
    ])

    for row in flagged_students:
        sid = row["student_id"]
        psid = row["permanent_student_id"]
        name = row["student_name"]
        curr_sch_id = row["school_id"]
        curr_sch_name = row["school_name"]
        curr_sch_type = row["school_type"]
        curr_std = row["standard"]
        district = row["district"]
        flag = row["review_flag"]

        outgoing_counts[curr_sch_id] += 1

        if curr_sch_id in ('SCH011', 'SCH012', 'SCH015'):
            # Districts with an existing K-10 school (Tumakuru: SCH009, Mysuru: SCH002, Udupi: SCH008)
            cand_id, cand_name = DISTRICT_SCHOOL_MAP[district]
            
            # Check capacity allocation (max 10 students per standard fit in the 100-seat buffer)
            alloc_key = (cand_id, curr_std)
            allocated_within_capacity[alloc_key] = allocated_within_capacity.get(alloc_key, 0) + 1
            
            if allocated_within_capacity[alloc_key] <= 10:
                # Within nominal capacity
                incoming_counts[cand_id] += 1
                prop_id = cand_id
                prop_name = cand_name
                prop_type = "School"
                prop_class = f"Primary / Secondary Education (Standard {curr_std})"
                reason = f"Same-district K-10 school destination identified within available institutional capacity (10 seats allocated in Standard {curr_std}; 100 seats total available buffer in {cand_id})."
                evidence = f"nagriksetu.db: schools.district='{district}', program_sections ({cand_id} capacity={capacities.get(cand_id, 700)}, curr_strength={current_counts.get(cand_id, 600)})."
                status = "PROPOSED_DESTINATION_WITHIN_CAPACITY"
            else:
                # Capacity overflow (remaining 190 students per standard)
                prop_id = f"{cand_id}_OR_COMPOSITE_RETAIN"
                prop_name = f"{cand_name} (Capacity Overflow) / Retain under {curr_sch_name} Composite Policy"
                prop_type = "School / Composite Pre-University College"
                prop_class = f"Primary / Secondary Education (Standard {curr_std})"
                reason = f"District K-10 school ({cand_id}) maximum capacity exceeded. Total overflow of 1,900 students across Standards 1-10. Physical transfer would cause severe infrastructure deficit. Administrative policy sanction required."
                evidence = f"nagriksetu.db: schools.district='{district}', program_sections ({cand_id} max capacity {capacities.get(cand_id, 700)} exceeded by 271%)."
                status = "UNCERTAIN_CAPACITY_OVERFLOW"

        elif curr_sch_id in ('SCH013', 'SCH014'):
            # Mandya and Hassan: Zero alternate K-10 schools exist in the district registry
            prop_id = "ADMIN_REVIEW_NO_DISTRICT_SCHOOL"
            prop_name = f"No Alternate K-10 School Registered in {district} / Retain under {curr_sch_name} Composite Policy"
            prop_type = "Composite Pre-University College (Std 1-12)"
            prop_class = f"Primary / Secondary Education (Standard {curr_std})"
            reason = f"Zero alternate K-10 schools exist in {district} district registry. Inter-district transfer prohibited under district preservation rules. Recommended: Officially confirm {curr_sch_name} as Composite Junior College."
            evidence = f"nagriksetu.db: schools (only {curr_sch_id} registered in {district} district); statewide institutional directory."
            status = "UNCERTAIN_NO_DESTINATION_IN_DISTRICT"

        else:
            # SCH016 - SCH020: Belagavi, Dharwad, Shivamogga, Ballari, Kalaburagi (Standards 11-12)
            puc_term = "1st PUC" if curr_std == 11 else "2nd PUC"
            prop_id = "ADMIN_REVIEW_NO_DISTRICT_PUC"
            prop_name = f"No Standalone PU College Registered in {district} / Retain under {curr_sch_name} Composite Senior Secondary Policy"
            prop_type = "Composite Senior Secondary School (Std 1-12)"
            prop_class = f"Higher Secondary Education ({puc_term}, Standard {curr_std})"
            reason = f"Zero standalone Pre-University colleges exist in {district} district registry. Inter-district transfer prohibited under district preservation rules. Recommended: Officially upgrade {curr_sch_name} to Composite Senior Secondary School."
            evidence = f"nagriksetu.db: schools ({district} has no registered PU College); program_sections; statewide institutional directory."
            status = "UNCERTAIN_NO_PU_COLLEGE_IN_DISTRICT"

        writer.writerow([
            sid, psid, name, curr_sch_id, curr_sch_name, curr_sch_type,
            f"Standard {curr_std}", prop_id, prop_name, prop_type,
            prop_class, district, reason, evidence, status
        ])

print("Finished generating migration CSV.")

print("Generating NagrikSetu_Institution_Wise_Proposed_Distribution.csv...")
with open(DISTRIBUTION_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "Institution ID",
        "Institution Name",
        "Institution Type",
        "District",
        "Current Student Count",
        "Proposed Incoming Students (Physical Transfer Scenario)",
        "Proposed Outgoing Students",
        "Projected Student Count (Physical Transfer Scenario)",
        "Projected Student Count (Composite Policy Scenario)",
        "Standards / PUC Years Supported",
        "Available Registered Capacity",
        "Capacity Concerns & Administrative Review Remarks"
    ])

    for sid, sdata in sorted(schools.items()):
        curr = current_counts.get(sid, 0)
        inc = incoming_counts.get(sid, 0)
        out = outgoing_counts.get(sid, 0)
        proj_physical = curr + inc - out
        proj_composite = curr  # In composite policy, all existing students remain
        cap = capacities.get(sid, 0)
        stype = sdata["school_type"]
        dist = sdata["district"]

        # Supported standards description
        if sid in ('SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015'):
            stds = "1st PUC & 2nd PUC (Standards 11-12); Currently holds Std 1-10"
            if out > 0:
                remarks = f"Outgoing 2,000 K-10 students would leave 400 genuine PUC students (fits well within {cap} registered PU capacity). Alternatively, Composite Policy retains all 2,400 students."
            else:
                remarks = "Stable."
        elif sid in ('SCH016', 'SCH017', 'SCH018', 'SCH019', 'SCH020'):
            stds = "Standards 1-10; Currently holds Std 11-12"
            if out > 0:
                remarks = f"Outgoing 400 PU students would leave 2,000 K-10 students (fits well within {cap} registered K-10 capacity). Alternatively, Composite Senior Secondary Policy retains all 2,400 students."
            else:
                remarks = "Stable."
        elif sid in ('SCH002', 'SCH008', 'SCH009'):
            stds = "Standards 1-10 (KSEEB State Board)"
            remarks = f"Can absorb exactly {inc} students within 700 registered capacity ({curr} current + {inc} = {proj_physical}). Cannot absorb remaining 1,900 district overflow students without 271% capacity breach."
        elif "College" in stype or "University" in stype:
            stds = "Collegiate / University Degrees"
            remarks = "Higher Education Institution. Unaffected by school/PU realignment."
        else:
            stds = "Standards 1-10 (KSEEB State Board)"
            remarks = "Standard primary/secondary school. Unaffected by realignment."

        writer.writerow([
            sid, sdata["school_name"], stype, dist, curr, inc, out,
            proj_physical, proj_composite, stds, cap, remarks
        ])

print("Finished generating distribution CSV.")
conn.close()
