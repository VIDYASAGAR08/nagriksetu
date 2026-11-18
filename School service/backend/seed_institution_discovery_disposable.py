"""
seed_institution_discovery_disposable.py
Seeds rich institutional profiles, facilities, hostel, transport, admissions, achievements,
and academic divisions on nagriksetu_disposable.db for verification.
"""
import sqlite3
import json
import uuid

DISPOSABLE_DB = 'C:/Users/callm/nagriksetu/backend/data/nagriksetu_disposable.db'

def seed():
    conn = sqlite3.connect(DISPOSABLE_DB)
    c = conn.cursor()

    print("Seeding institutional profile data on disposable DB...")

    # Define rich profile for SCH001 (Government Model School, Malleshwaram)
    sch001_about = {
        "introduction": "Government Model School, Malleshwaram is one of Karnataka's flagship state educational institutions, committed to holistic public education for over six decades.",
        "history": "Established in 1958 under the Karnataka Department of Public Instruction, the school has nurtured generations of scholars, civil servants, and artists with state-subsidised model education.",
        "vision": "To empower every child with foundational literacy, critical inquiry, and civic responsibility in an inclusive, supportive learning atmosphere.",
        "mission": "Provide world-class bilingual education (Kannada and English), cultivate scientific temper, and ensure zero educational dropouts across socio-economic strata.",
        "philosophy": "Child-centric experiential pedagogy bridging conceptual learning with vocational and community awareness under the National Education Framework.",
        "methodology": "Activity-based learning (Nali-Kali for primary, smart-board guided STEM inquiry for middle and secondary grades, and structured co-curricular integration).",
        "academic_environment": "Vibrant 3.5-acre green campus equipped with digital classrooms, state-of-the-art Atal Tinkering Lab, and extensive physical education infrastructure."
    }

    sch001_facilities = {
        "classrooms": {"available": True, "count": 28, "description": "Spacious, well-ventilated classrooms with ergonomic desks, natural daylight, and interactive smartboards."},
        "science_laboratories": {"available": True, "count": 3, "description": "Fully equipped composite Science and Atal Tinkering Labs supporting Physics, Chemistry, and Biology experiments."},
        "computer_laboratories": {"available": True, "count": 2, "description": "45 multimedia PCs running educational Linux distributions with gigabit LAN and broadband access."},
        "library": {"available": True, "count": 1, "description": "Central library housing 12,500+ volumes in Kannada, English, and Hindi, along with children's periodicals and audiobooks."},
        "digital_learning": {"available": True, "description": "Edusat broadcast terminal, digital projector halls, and DIKSHA-linked digital curriculum tablets."},
        "sports_grounds": {"available": True, "description": "Standard 200-meter athletics track, full-sized football/kho-kho field, and volleyball court."},
        "indoor_sports": {"available": True, "description": "Dedicated sports hall for Table Tennis, Chess, Carrom, and Yoga sessions."},
        "auditorium": {"available": True, "capacity": 450, "description": "Dr. Rajkumar Memorial Assembly Hall with modern audio-visual projection and acoustic baffling."},
        "cafeteria": {"available": True, "description": "PM-POSHAN centralised mid-day meal kitchen serving hot, nutritious fortified meals and Ksheera Bhagya milk."},
        "medical_room": {"available": True, "description": "Dedicated first-aid and medical dispensary staffed by a visiting medical officer and trained nurse."},
        "internet": {"available": True, "description": "High-speed 100 Mbps BSNL BharatNet optical fiber connectivity across all administrative and lab blocks."},
        "accessibility": {"available": True, "description": "Accessible ground-floor ramps, tactile paving paths, and barrier-free restrooms for differently-abled students."},
        "safety_security": {"available": True, "description": "32 HD CCTV cameras covering perimeter and hallways, compound wall with round-the-clock security, and fire extinguishers."}
    }

    sch001_hostel = {
        "available": False,
        "description": "Government Model School Malleshwaram is a public day school. Subsidised residential BCM hostel facilities are available within 1.2 km through the Social Welfare Department.",
        "hostel_capacity": 0,
        "boys_hostel": False,
        "girls_hostel": False,
        "contact_person": "School Liaison Desk",
        "contact_phone": "+91 80 2334 1122"
    }

    sch001_transport = {
        "available": True,
        "description": "State transport corporation (BMTC) student bus passes valid across all city routes. Two dedicated dedicated feeder vans operate for feeder municipal wards.",
        "routes": [
            {"route_name": "Route 1: Yeshwanthpur - Malleshwaram 8th Main", "pickup_points": "Yeshwanthpur Circle, Subhashnagar, 18th Cross, School Campus", "timing": "08:15 AM / 03:45 PM"},
            {"route_name": "Route 2: Rajajinagar - Gayathrinagar Loop", "pickup_points": "Rajajinagar Metro, Bashyam Circle, Harishchandra Ghat, School Campus", "timing": "08:20 AM / 03:50 PM"}
        ],
        "contact_phone": "+91 80 2334 1123",
        "accessibility": "BMTC low-floor accessible buses stop directly opposite the main gate."
    }

    sch001_admissions = {
        "eligibility": "Children residing within the school catchment area aged 5+ for Standard 1, and age-appropriate transfers for Standards 2–10.",
        "process": "Direct registration at the school administration office or through the SATS (Student Achievement Tracking System) portal.",
        "fee_structure": "100% tuition-free state education. Free textbooks, two sets of uniforms, mid-day meals, and study materials provided.",
        "application_dates": "Admissions open: March 15 | Last date: June 10 (Rolling admissions for migrant families).",
        "scholarships": "Post-Matric, Pre-Matric, NMMS (National Means-cum-Merit Scholarship), and Pratibha Puraskar cash awards.",
        "required_documents": [
            "Birth Certificate",
            "Aadhar Card of student and parent",
            "Previous School Transfer Certificate (for Grade 2+)",
            "Caste / Income Certificate (if applicable for state scholarship linking)"
        ]
    }

    c.execute('''
        UPDATE schools
        SET logo_url = '/images/logos/sch001_logo.png',
            cover_image_url = '/images/covers/sch001_cover.jpg',
            address = '18th Cross, Margosa Road, Malleshwaram, Bengaluru, Karnataka 560003',
            established_year = 1958,
            public_phone = '+91 80 2334 1122',
            email = 'principal.sch001@karnataka.gov.in',
            website = 'https://sats.karnataka.gov.in/sch001',
            recognition = 'Recognised by Dept. of School Education & Literacy, Govt. of Karnataka (KSEEB Code: 0342)',
            affiliation = 'Karnataka School Examination and Assessment Board (KSEAB)',
            description = 'Premier government model school providing high-standard bilingual education, sports facilities, and Atal Tinkering STEM labs.',
            about_json = ?,
            facilities_details_json = ?,
            hostel_details_json = ?,
            transport_details_json = ?,
            admissions_details_json = ?
        WHERE school_id = 'SCH001'
    ''', (
        json.dumps(sch001_about),
        json.dumps(sch001_facilities),
        json.dumps(sch001_hostel),
        json.dumps(sch001_transport),
        json.dumps(sch001_admissions)
    ))

    # Seed 10 verified achievements for SCH001
    achievements_sch001 = [
        ("State Championship in School Kho-Kho 2025", "Gold Medal in Karnataka State Inter-School Rural & Urban Sports Meet held at Mysuru.", 2025, "State", "Karnataka State Sports Authority", "Sports"),
        ("National Science Congress Finalist", "Student innovative project on smart rain-harvesting selected among top 20 school projects nationally.", 2024, "National", "National Children Science Congress", "Academic"),
        ("District Best Model School Award", "Conferred by Deputy Director of Public Instruction (DDPI) for 100% SSLC board passing rate.", 2024, "District", "DDPI Bengaluru North", "Institutional"),
        ("State Level Pratibha Karanji Folk Dance Winner", "First prize in folk drama depicting Karnataka heritage at Ravindra Kalakshetra.", 2024, "State", "Pratibha Karanji Cultural Festival", "Cultural"),
        ("Atal Tinkering Innovation Marathon Winner", "Awarded ₹1,00,000 research grant for low-cost soil nitrogen detector kit.", 2023, "National", "NITI Aayog Atal Innovation Mission", "Innovation"),
        ("Cleanest School Campus Swachh Vidyalaya Puraskar", "5-star rating for water, sanitation, and waste segregation systems.", 2023, "National", "Ministry of Education, GoI", "Environment"),
        ("State Badminton Singles U-14 Runner Up", "Silver medal in Karnataka School Olympics badminton tournament.", 2023, "State", "School Games Federation of India (SGFI)", "Sports"),
        ("Bilingual Debate Competition Winner", "First place in Inter-School Debating Championship in Kannada and English on Cyber Literacy.", 2022, "District", "Bangalore Literary Society", "Academic"),
        ("Centenary Scout Troop Governor Award", "Seven Bharat Scouts & Guides students received Rajya Puraskar from the Governor of Karnataka.", 2022, "State", "Bharat Scouts & Guides Karnataka", "Social Service"),
        ("Excellence in Digital Classroom Adoption", "Awarded by DSERT for pioneering teacher-led digital lesson module creation.", 2021, "State", "DSERT Karnataka", "Teaching")
    ]

    for title, desc, yr, level, comp, cat in achievements_sch001:
        c.execute('''
            INSERT OR REPLACE INTO school_achievements (
                achievement_id, school_id, title, description, year, award_level,
                competition_name, category, verification_status, is_published
            ) VALUES (?, 'SCH001', ?, ?, ?, ?, ?, ?, 'verified', 1)
        ''', (f"ACH-SCH001-{uuid.uuid4().hex[:8]}", title, desc, yr, level, comp, cat))

    # Also seed Ramaiah Group (COL001) as a multi-division educational group:
    col001_about = {
        "introduction": "Founded in 1962 by the late industrialist and philanthropist Dr. M. S. Ramaiah, the Ramaiah Group is one of India's premier integrated educational conglomerates, fostering excellence across Schooling, Pre-University, Polytechnic, and University Engineering disciplines.",
        "history": "Beginning with the founding of Gokula Education Foundation in 1962, Ramaiah has evolved into an academic city housing world-renowned engineering colleges, multi-specialty hospitals, polytechnics, and schools.",
        "vision": "To be an institution of international repute producing intellectually adept, socially conscious engineers and leaders.",
        "mission": "Deliver outcome-based technical and foundational education, foster interdisciplinary innovation, and advance societal well-being through knowledge and research.",
        "philosophy": "Comprehensive educational pathway from school foundations through doctoral engineering excellence on a singular integrated campus.",
        "methodology": "Outcome-based education (OBE), industry immersion with 400+ multinational partners, hands-on maker spaces, and international credit exchanges.",
        "academic_environment": "A lush 85-acre self-contained academic campus with advanced research centers, incubation parks, sports arenas, and multi-tier student residences."
    }

    col001_facilities = {
        "classrooms": {"available": True, "count": 120, "description": "Air-conditioned amphitheater lecture halls with dual projection, smart digital boards, and live lecture recording."},
        "science_laboratories": {"available": True, "count": 48, "description": "Advanced specialized labs including Nvidia AI Research Center, Robotics Automation Studio, and VLSI Design Lab."},
        "computer_laboratories": {"available": True, "count": 14, "description": "Over 2,200 high-performance workstations connected via 10 Gbps campus fiber backbone."},
        "library": {"available": True, "count": 3, "description": "Central Digital Library housing 150,000+ print volumes, IEEE/Elsevier subscriptions, and 24/7 online access."},
        "digital_learning": {"available": True, "description": "Canvas LMS, cloud virtual computing labs, and immersive VR engineering simulations."},
        "sports_grounds": {"available": True, "description": "Floodlit cricket stadium, synthetic turf football arena, and 400m international athletics track."},
        "indoor_sports": {"available": True, "description": "Multi-court indoor sports complex with wooden badminton courts, basketball arena, and fitness gymnasium."},
        "auditorium": {"available": True, "capacity": 1800, "description": "Apex Auditorium with state-of-the-art concert acoustics and simultaneous multilingual broadcast."},
        "cafeteria": {"available": True, "description": "Seven multi-cuisine food courts, coffee outlets, and health cafes compliant with FSSAI hygiene standards."},
        "medical_room": {"available": True, "description": "24/7 dedicated medical center backed by the adjacent 1,200-bed Ramaiah Memorial Hospital."},
        "internet": {"available": True, "description": "Campus-wide Wi-Fi 6 wireless mesh network with 2 Gbps redundant leased lines."},
        "accessibility": {"available": True, "description": "Elevators in all multistory wings, braille signage, electric mobility carts, and universal wheelchair access."},
        "safety_security": {"available": True, "description": "Centralised command center with 450+ CCTV cameras, boom-barrier access, and 24/7 armed security patrols."}
    }

    col001_hostel = {
        "available": True,
        "description": "Premium on-campus student residences with separate blocks for boys and girls, offering single, twin, and triple-sharing accommodations.",
        "hostel_capacity": 4200,
        "boys_hostel": True,
        "girls_hostel": True,
        "amenities": "High-speed Wi-Fi, solar water heating, biometric security gates, laundromat, gym, and 24-hour reading rooms.",
        "food_dining": "Hygienic dining halls serving North Indian, South Indian, and Continental menus curated by nutritionists.",
        "warden_supervision": "Senior faculty resident wardens, female residential proctors, and strict visitor verification protocols.",
        "contact_phone": "+91 80 2360 7711",
        "contact_email": "hostel.warden@msrit.edu"
    }

    col001_transport = {
        "available": True,
        "description": "Fleet of 35 GPS-tracked air-conditioned and non-air-conditioned institution buses connecting all corners of Greater Bengaluru.",
        "routes": [
            {"route_name": "Route 101: Electronic City - Silk Board - Mathikere", "pickup_points": "Infosys Gate, Silk Board, Koramangala, Indiranagar, Ramaiah Campus", "timing": "07:15 AM / 05:15 PM"},
            {"route_name": "Route 102: Whitefield - KR Puram - Mathikere", "pickup_points": "ITPL, Mahadevapura, Tin Factory, Hebbal, Ramaiah Campus", "timing": "07:20 AM / 05:15 PM"},
            {"route_name": "Route 103: Banashankari - Jayanagar - Mathikere", "pickup_points": "Banashankari TTMC, South End Circle, Majestic, Ramaiah Campus", "timing": "07:30 AM / 05:15 PM"},
            {"route_name": "Route 104: Kengeri - Vijayanagar - Mathikere", "pickup_points": "Kengeri Satellite Town, Chord Road, Rajajinagar, Ramaiah Campus", "timing": "07:35 AM / 05:15 PM"}
        ],
        "contact_phone": "+91 80 2360 0824",
        "accessibility": "Hydraulic wheelchair lifts on designated campus shuttle routes."
    }

    col001_admissions = {
        "eligibility": "B.E./B.Tech: 10+2 with Physics, Mathematics & Chemistry/CS (Min 45% aggregate) + KCET / COMEDK ranking.",
        "process": "State KCET counseling, COMEDK counseling, or institutional merit assessment through official portal.",
        "fee_structure": "Government KCET quota: ₹96,574/yr | COMEDK quota: ₹2,64,000/yr | Institution merit quota: As per state committee norms.",
        "application_dates": "KCET Round 1: June 15 | COMEDK Round 1: July 02 | Academic session commences: August 18.",
        "scholarships": "Post-Matric National Scholarship, AICTE Pragati & Saksham, MSR Memorial Merit Scholarship for top 5% batch performers.",
        "required_documents": [
            "10th Standard Marks Card",
            "12th Standard / PUC Marks Card",
            "KCET / COMEDK Rank Card and Allotment Letter",
            "Transfer Certificate & Migration Certificate",
            "Study / Conduct Certificate (7 years study in Karnataka for state quota)"
        ]
    }

    c.execute('''
        UPDATE schools
        SET is_parent_group = 1,
            campus_name = 'MSR Nagar Main Campus',
            division_name = 'Ramaiah Educational Group',
            recognition = 'Autonomous, Affiliated to VTU, Approved by AICTE, Accredited by NAAC with A+ Grade',
            about_json = ?,
            facilities_details_json = ?,
            hostel_details_json = ?,
            transport_details_json = ?,
            admissions_details_json = ?
        WHERE school_id = 'COL001'
    ''', (
        json.dumps(col001_about),
        json.dumps(col001_facilities),
        json.dumps(col001_hostel),
        json.dumps(col001_transport),
        json.dumps(col001_admissions)
    ))

    # Add Academic Divisions for COL001
    divisions_col001 = [
        ("DIV-COL001-ENG", "COL001", "Ramaiah Institute of Technology", "Engineering College", "Campus Block 1-4, MSR Nagar", "Dr. N. V. R. Naidu", "+91 80 2360 0822", "principal@msrit.edu", "AI & Robotics Labs, Central Library, Research Park, 12 Engineering Branches", "Premier engineering institution offering 12 undergraduate B.E./B.Tech branches and applied research centers.", 1),
        ("DIV-COL001-POLY", "COL001", "Ramaiah Polytechnic", "Diploma Division", "North Wing, Polytechnic Block", "Prof. K. S. Sridhar", "+91 80 2360 1255", "polytechnic@msrit.edu", "Automobile Workshop, CNC Machining Lab, Fluid Mechanics Lab, Electronics Lab", "Offers 3-year government-approved polytechnic diplomas in Computer Science, Automobile, Mechanical, Civil, and Electronics.", 2),
        ("DIV-COL001-PU", "COL001", "Ramaiah Composite Pre-University College", "PU Division", "Heritage Academic Wing", "Dr. H. M. Mallikarjuna", "+91 80 2360 3344", "pu.admissions@msrit.edu", "Modern Science Demonstration Labs, Commerce Smart Classes, Competitive Exam Wing", "Pre-University education in Science (PCMB, PCMC, PCME) and Commerce (SEBA, CEBA, MEBA) with integrated CET coaching.", 3),
        ("DIV-COL001-SCH", "COL001", "Ramaiah Vidyanikethan High School", "School Division", "East Campus Greens", "Smt. Shanta Rathnam", "+91 80 2360 4488", "vidyanikethan@msrit.edu", "Montessori labs, Children Library, Athletic Grounds, STEM Maker Lab", "Standards 1 to 10 providing holistic bilingual education, arts, athletics, and foundational robotics.", 4)
    ]

    for div_id, p_id, d_name, d_type, camp, head, phone, email, fac_sum, desc, order in divisions_col001:
        c.execute('''
            INSERT OR REPLACE INTO institution_divisions (
                division_id, parent_institution_id, division_name, division_type,
                campus_location, head_of_division, contact_phone, contact_email,
                facilities_summary, description, display_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (div_id, p_id, d_name, d_type, camp, head, phone, email, fac_sum, desc, order))

    # Seed 10 verified achievements for COL001
    achievements_col001 = [
        ("NIRF All India Rank 67 in Engineering 2024", "Ranked among top engineering institutions in India by Ministry of Education.", 2024, "National", "NIRF India Rankings", "Institutional"),
        ("NAAC 'A+' Grade Re-Accreditation", "Awarded cumulative grade point average of 3.62 / 4.0 by the National Assessment and Accreditation Council.", 2023, "National", "NAAC", "Accreditation"),
        ("First Prize in Boeing National Aeromodelling Championship", "Ramaiah student aeronautics team won national championship with autonomous UAV design.", 2024, "National", "Boeing India", "Innovation"),
        ("Smart India Hackathon (SIH) National Winner", "CSE Department team won ₹1,00,000 for AI-driven railway track anomaly detection system.", 2023, "National", "Ministry of Education & AICTE", "Hackathon"),
        ("IEEE Outstanding Student Branch Award", "Recognised by IEEE Bangalore Section for organizing 45+ technical workshops and hackathons.", 2024, "State", "IEEE Region 10", "Academic"),
        ("SAE BAJA All-Terrain Vehicle Endurance Champions", "Mechanical and Automobile engineering students built all-terrain buggy ranking 1st in endurance.", 2023, "National", "Society of Automotive Engineers", "Engineering"),
        ("AICTE Clean and Green Campus Award", "Gold category recognition for 1.2 MW rooftop solar generation and zero-liquid-discharge water recycling.", 2023, "National", "AICTE New Delhi", "Environment"),
        ("VTU Overall Athletics Championship Trophy", "Won 14 Gold medals in Visvesvaraya Technological University Inter-Collegiate Athletics Meet.", 2024, "State", "VTU Sports Board", "Sports"),
        ("DST-FIST Research Infrastructure Grant of ₹2.5 Crore", "Sanctioned by Department of Science & Technology for Advanced Materials Characterisation Lab.", 2022, "National", "DST Government of India", "Research"),
        ("Formula Student Electric Car Design Award", "Ranked 2nd nationally for student-designed high-voltage electric race car powertrain.", 2024, "National", "Formula Student India", "Innovation")
    ]

    for title, desc, yr, level, comp, cat in achievements_col001:
        c.execute('''
            INSERT OR REPLACE INTO school_achievements (
                achievement_id, school_id, title, description, year, award_level,
                competition_name, category, verification_status, is_published
            ) VALUES (?, 'COL001', ?, ?, ?, ?, ?, ?, 'verified', 1)
        ''', (f"ACH-COL001-{uuid.uuid4().hex[:8]}", title, desc, yr, level, comp, cat))

    conn.commit()
    print("Verification of seeded data on disposable DB:")
    print("Divisions count:", c.execute('SELECT count(*) FROM institution_divisions').fetchone()[0])
    print("Achievements count:", c.execute('SELECT count(*) FROM school_achievements').fetchone()[0])
    print("Integrity check:", c.execute('PRAGMA integrity_check').fetchall())
    print("FK check:", c.execute('PRAGMA foreign_key_check').fetchall())
    conn.close()

if __name__ == '__main__':
    seed()
