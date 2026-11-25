import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3308, user='nagriksetu_skill', password='skill-app-pass-2026', database='skill_db')
cur = conn.cursor(pymysql.cursors.DictCursor)

# 1. Define the 7 Official Main Categories
MAIN_CATEGORIES = [
    {
        "id": 1,
        "code": "CAT-0001",
        "name": "Computer Science & Information Technology",
        "description": "Software development, cloud architecture, AI/ML, data science, networking and cybersecurity.",
        "icon_name": "Cpu"
    },
    {
        "id": 2,
        "code": "CAT-0002",
        "name": "Business & Commerce",
        "description": "Accounting, financial modeling, banking operations, entrepreneurship, project management and retail.",
        "icon_name": "Briefcase"
    },
    {
        "id": 3,
        "code": "CAT-0003",
        "name": "Healthcare",
        "description": "Allied healthcare assistance, pharmacy support, emergency medical services, and health records management.",
        "icon_name": "Activity"
    },
    {
        "id": 4,
        "code": "CAT-0004",
        "name": "Engineering & Technical Trades",
        "description": "Electrical wiring, solar rooftop systems, CNC machining, welding, automotive maintenance and industrial safety.",
        "icon_name": "Wrench"
    },
    {
        "id": 5,
        "code": "CAT-0005",
        "name": "Agriculture & Allied Skills",
        "description": "Organic farming, drip irrigation, livestock management, dairy production and agro-processing.",
        "icon_name": "Sprout"
    },
    {
        "id": 6,
        "code": "CAT-0006",
        "name": "Media & Communication",
        "description": "Digital marketing, graphic design, UI/UX prototyping, content creation, and professional languages.",
        "icon_name": "Share2"
    },
    {
        "id": 7,
        "code": "CAT-0007",
        "name": "Hospitality & Tourism",
        "description": "Front office operations, food safety hygiene, bakery, confectionery, and travel guest services.",
        "icon_name": "Utensils"
    }
]

# Disable foreign key checks temporarily during categories restructure
cur.execute("SET FOREIGN_KEY_CHECKS = 0")

for mc in MAIN_CATEGORIES:
    cur.execute("""
        INSERT INTO categories (id, code, name, description, icon_name)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            description = VALUES(description),
            icon_name = VALUES(icon_name)
    """, (mc["id"], mc["code"], mc["name"], mc["description"], mc["icon_name"]))

# Delete old categories with id > 7 if any exist without breaking
cur.execute("DELETE FROM categories WHERE id > 7")

# 2. Define Subcategories for each Main Category (at least 5 per category)
SUBCATEGORIES = [
    # Cat 1: Computer Science & IT (5 subcategories)
    {"cat_id": 1, "code": "SUB-001", "name": "Programming & Software Development", "desc": "Core application development, algorithms, system software, and enterprise frameworks."},
    {"cat_id": 1, "code": "SUB-002", "name": "Web & Full Stack Engineering", "desc": "Frontend UI, modern JavaScript frameworks, backend APIs, and microservices."},
    {"cat_id": 1, "code": "SUB-003", "name": "Data Science & Artificial Intelligence", "desc": "Data analytics, machine learning, deep learning, NLP, and business intelligence."},
    {"cat_id": 1, "code": "SUB-004", "name": "Cloud Computing & DevOps", "desc": "Cloud infrastructure, containerization, orchestration, and CI/CD automation."},
    {"cat_id": 1, "code": "SUB-005", "name": "Cybersecurity & Network Systems", "desc": "Network engineering, ethical hacking, SOC incident response, and security auditing."},
    {"cat_id": 1, "code": "SUB-006", "name": "Software Quality Assurance & Testing", "desc": "Automation testing, performance testing, Selenium, and API validation."},

    # Cat 2: Business & Commerce (5 subcategories)
    {"cat_id": 2, "code": "SUB-007", "name": "Accounting & Financial Taxation", "desc": "Tally Prime, GST compliance, bookkeeping, and payroll accounting."},
    {"cat_id": 2, "code": "SUB-008", "name": "Banking & Financial Services", "desc": "Retail banking, loan processing, financial modeling, and wealth operations."},
    {"cat_id": 2, "code": "SUB-009", "name": "Entrepreneurship & Small Business", "desc": "Business setup, regulatory compliance, venture funding, and market launch."},
    {"cat_id": 2, "code": "SUB-010", "name": "Project Management & Agile Operations", "desc": "Agile methodologies, Scrum framework, sprint planning, and operations."},
    {"cat_id": 2, "code": "SUB-011", "name": "Retail Management & Merchandising", "desc": "Store inventory, POS operations, visual merchandising, and customer service."},

    # Cat 3: Healthcare (5 subcategories)
    {"cat_id": 3, "code": "SUB-012", "name": "Nursing & Patient Assistance", "desc": "General duty assistance, patient hygiene, bedside support, and vitals monitoring."},
    {"cat_id": 3, "code": "SUB-013", "name": "Pharmacy Support & Dispensing", "desc": "Pharmacy inventory, prescription handling, and retail pharmacy administration."},
    {"cat_id": 3, "code": "SUB-014", "name": "Emergency Medical Services", "desc": "EMT basic, first response, ambulance protocols, and trauma resuscitation."},
    {"cat_id": 3, "code": "SUB-015", "name": "Medical Records & Health Informatics", "desc": "Health records maintenance, medical coding, billing, and EHR management."},
    {"cat_id": 3, "code": "SUB-016", "name": "Diagnostic & Laboratory Assistance", "desc": "Phlebotomy, clinical sample preparation, and diagnostic lab equipment operations."},

    # Cat 4: Engineering & Technical Trades (5 subcategories)
    {"cat_id": 4, "code": "SUB-017", "name": "Electrical & Renewable Power Systems", "desc": "Domestic wiring, industrial panel installation, and solar PV maintenance."},
    {"cat_id": 4, "code": "SUB-018", "name": "Mechanical Precision & CNC Machining", "desc": "CNC turning, milling, CAD/CAM programming, and tooling."},
    {"cat_id": 4, "code": "SUB-019", "name": "Automotive Engineering & Fleet Maintenance", "desc": "Two-wheeler, four-wheeler diagnostics, EV systems, and brake service."},
    {"cat_id": 4, "code": "SUB-020", "name": "HVAC, Fabrication & Welding Trades", "desc": "Refrigeration, AC repair, TIG/MIG welding, and metal fabrication."},
    {"cat_id": 4, "code": "SUB-021", "name": "Construction, Plumbing & Industrial Safety", "desc": "Pipe fitting, sanitary plumbing, masonry, and OSHA workplace safety."},

    # Cat 5: Agriculture & Allied Skills (5 subcategories)
    {"cat_id": 5, "code": "SUB-022", "name": "Organic Agronomy & Soil Management", "desc": "Sustainable crop farming, bio-fertilizers, vermicomposting, and soil testing."},
    {"cat_id": 5, "code": "SUB-023", "name": "Precision Irrigation & Water Technologies", "desc": "Micro-irrigation, automated drip systems, sensor monitoring, and rainwater harvesting."},
    {"cat_id": 5, "code": "SUB-024", "name": "Animal Husbandry & Dairy Management", "desc": "Dairy cattle management, milking hygiene, feed formulation, and poultry operations."},
    {"cat_id": 5, "code": "SUB-025", "name": "Horticulture & Greenhouse Cultivation", "desc": "Floriculture, polyhouse cultivation, nursery management, and pest control."},
    {"cat_id": 5, "code": "SUB-026", "name": "Post-Harvest Handling & Food Processing", "desc": "Cold storage logistics, grain processing, fruit preservation, and packaging."},

    # Cat 6: Media & Communication (5 subcategories)
    {"cat_id": 6, "code": "SUB-027", "name": "Digital Marketing & Growth Strategy", "desc": "SEO, Google Ads, content marketing, performance analytics, and lead generation."},
    {"cat_id": 6, "code": "SUB-028", "name": "Visual Design & UI/UX Experience", "desc": "Graphic communication, brand identity, Figma prototyping, and user journeys."},
    {"cat_id": 6, "code": "SUB-029", "name": "Audio-Visual Production & Editing", "desc": "Video editing, motion graphics, mobile content production, and sound design."},
    {"cat_id": 6, "code": "SUB-030", "name": "Professional Languages & Workplace Communication", "desc": "Professional English, workplace Kannada, functional Hindi, and corporate presentation."},
    {"cat_id": 6, "code": "SUB-031", "name": "Journalism & Content Writing", "desc": "News reporting, copy editing, public relations writing, and scriptwriting."},

    # Cat 7: Hospitality & Tourism (5 subcategories)
    {"cat_id": 7, "code": "SUB-032", "name": "Front Office & Guest Services", "desc": "Hotel reception, room reservation, concierge desk, and guest relations."},
    {"cat_id": 7, "code": "SUB-033", "name": "Culinary Arts & Commercial Bakery", "desc": "Bakery production, pastry arts, commercial confectionery, and culinary hygiene."},
    {"cat_id": 7, "code": "SUB-034", "name": "Food & Beverage Operations", "desc": "Restaurant service, banqueting, bar operations, and table styling."},
    {"cat_id": 7, "code": "SUB-035", "name": "Food Safety, Hygiene & FSSAI Standards", "desc": "HACCP protocols, food inspection, hygiene audits, and storage preservation."},
    {"cat_id": 7, "code": "SUB-036", "name": "Travel Operations & Eco-Tourism", "desc": "Tour guiding, itinerary planning, ecotourism operations, and heritage facilitation."}
]

# Clear existing subcategories and insert fresh
cur.execute("DELETE FROM subcategories")
for sub in SUBCATEGORIES:
    cur.execute("""
        INSERT INTO subcategories (code, category_id, name, description)
        VALUES (%s, %s, %s, %s)
    """, (sub["code"], sub["cat_id"], sub["name"], sub["desc"]))

cur.execute("SET FOREIGN_KEY_CHECKS = 1")
conn.commit()
print(f"Inserted 7 main categories and {len(SUBCATEGORIES)} subcategories successfully!")
conn.close()
