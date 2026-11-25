import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3308, user='nagriksetu_skill', password='skill-app-pass-2026', database='skill_db')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT id, name FROM subcategories WHERE category_id = 4")
sub_map = {r["name"]: r["id"] for r in cur.fetchall()}

MORE_ENGINEERING_SKILLS = [
    # Electrical & Renewable Power Systems (needs 2 more to reach 5)
    {"sub": "Electrical & Renewable Power Systems", "name": "Electric Vehicle (EV) Charging Station Installation & Safety", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Electrical & Renewable Power Systems", "name": "Industrial Motor Control & PLC Automation", "level": "Intermediate", "weeks": 8, "hours": 50},

    # Mechanical Precision & CNC Machining (needs 3 more to reach 5)
    {"sub": "Mechanical Precision & CNC Machining", "name": "AutoCAD & SolidWorks Engineering Drafting", "level": "Beginner", "weeks": 6, "hours": 40},
    {"sub": "Mechanical Precision & CNC Machining", "name": "CNC Milling Machine Setup & Tooling", "level": "Intermediate", "weeks": 6, "hours": 45},
    {"sub": "Mechanical Precision & CNC Machining", "name": "Geometric Dimensioning & Tolerancing (GD&T) Inspection", "level": "Intermediate", "weeks": 4, "hours": 28},

    # Automotive Engineering & Fleet Maintenance (needs 2 more to reach 5)
    {"sub": "Automotive Engineering & Fleet Maintenance", "name": "Electric Vehicle (EV) Powertrain & Battery Diagnostic Systems", "level": "Intermediate", "weeks": 6, "hours": 45},
    {"sub": "Automotive Engineering & Fleet Maintenance", "name": "Automotive Electronic Control Unit (ECU) Scanning", "level": "Intermediate", "weeks": 4, "hours": 30},

    # HVAC, Fabrication & Welding Trades (needs 3 more to reach 5)
    {"sub": "HVAC, Fabrication & Welding Trades", "name": "Industrial Pipeline Arc Welding (6G Certification Track)", "level": "Advanced", "weeks": 8, "hours": 60},
    {"sub": "HVAC, Fabrication & Welding Trades", "name": "Commercial Chiller & Cold Storage HVAC Maintenance", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "HVAC, Fabrication & Welding Trades", "name": "Sheet Metal Fabrication & Structural Assembly", "level": "Beginner", "weeks": 6, "hours": 40}
]

cur.execute("SELECT MAX(id) as max_id FROM skills")
next_id = cur.fetchone()["max_id"] + 1

for s in MORE_ENGINEERING_SKILLS:
    sub_id = sub_map[s["sub"]]
    code = f"SKL-{next_id:04d}"
    summary = f"Professional industry-aligned engineering trade qualification in {s['name']}."
    details = f"Practical hands-on training, workshop safety, equipment operation and certification in {s['name']}."
    prereq = "Basic technical aptitude and high school pass"
    objectives = f"Develop job-ready technical capabilities in {s['name']} for modern manufacturing and technical trades."
    outcomes = f"Demonstrated ability to perform repairs, assembly, diagnostics and preventive maintenance in {s['name']}."

    cur.execute("""
        INSERT INTO skills (
            id, code, name, category_id, category_name, subcategory_id, subcategory_name,
            level, duration_weeks, duration_hours, summary, details, prerequisites,
            learning_objectives, learning_outcomes, relevant_industries, career_opportunities,
            cert_info, rating, enrolled_count, active
        ) VALUES (
            %s, %s, %s, 4, 'Engineering & Technical Trades', %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, 'Engineering & Manufacturing', 'Certified Technical Specialist',
            'Government of India Skill Qualification Framework (NSQF) aligned certificate',
            4.8, 0, 1
        )
    """, (
        next_id, code, s["name"], sub_id, s["sub"],
        s["level"], s["weeks"], s["hours"], summary, details, prereq,
        objectives, outcomes
    ))
    next_id += 1

conn.commit()
print("Engineering subcategories enriched!")
conn.close()
