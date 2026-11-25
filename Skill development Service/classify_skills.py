import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3308, user='nagriksetu_skill', password='skill-app-pass-2026', database='skill_db')
cur = conn.cursor(pymysql.cursors.DictCursor)

# 1. Fetch subcategory IDs
cur.execute("SELECT id, code, name FROM subcategories")
sub_map = {r["name"]: r["id"] for r in cur.fetchall()}
print(f"Loaded {len(sub_map)} subcategories")

# 2. Map existing 104 skills to their correct main category and subcategory
# Skill ID ranges & classifications:
SKILL_MAP = [
    # Cat 1: Computer Science & IT (Cat ID: 1)
    # SUB: Programming & Software Development
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 1, "Computer Science & Information Technology", "Programming & Software Development"),
    # SUB: Web & Full Stack Engineering
    ([12, 13, 14, 15, 16, 17, 18, 19, 20, 21], 1, "Computer Science & Information Technology", "Web & Full Stack Engineering"),
    # SUB: Data Science & Artificial Intelligence
    ([22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], 1, "Computer Science & Information Technology", "Data Science & Artificial Intelligence"),
    # SUB: Cloud Computing & DevOps
    ([33, 34, 35, 36, 37, 38, 39, 40, 41, 42], 1, "Computer Science & Information Technology", "Cloud Computing & DevOps"),
    # SUB: Cybersecurity & Network Systems
    ([43, 44, 45, 46, 47, 48, 49], 1, "Computer Science & Information Technology", "Cybersecurity & Network Systems"),
    # SUB: Software Quality Assurance & Testing
    ([50, 51, 52, 53, 54, 55, 56], 1, "Computer Science & Information Technology", "Software Quality Assurance & Testing"),

    # Cat 2: Business & Commerce (Cat ID: 2)
    # SUB: Accounting & Financial Taxation
    ([57, 59], 2, "Business & Commerce", "Accounting & Financial Taxation"),
    # SUB: Banking & Financial Services
    ([58, 60, 61], 2, "Business & Commerce", "Banking & Financial Services"),
    # SUB: Entrepreneurship & Small Business
    ([62], 2, "Business & Commerce", "Entrepreneurship & Small Business"),
    # SUB: Project Management & Agile Operations
    ([63, 64], 2, "Business & Commerce", "Project Management & Agile Operations"),
    # SUB: Retail Management & Merchandising
    ([101], 2, "Business & Commerce", "Retail Management & Merchandising"),

    # Cat 3: Healthcare (Cat ID: 3)
    # SUB: Nursing & Patient Assistance
    ([81], 3, "Healthcare", "Nursing & Patient Assistance"),
    # SUB: Pharmacy Support & Dispensing
    ([82], 3, "Healthcare", "Pharmacy Support & Dispensing"),
    # SUB: Emergency Medical Services
    ([83], 3, "Healthcare", "Emergency Medical Services"),
    # SUB: Medical Records & Health Informatics
    ([102], 3, "Healthcare", "Medical Records & Health Informatics"),

    # Cat 4: Engineering & Technical Trades (Cat ID: 4)
    # SUB: Electrical & Renewable Power Systems
    ([72, 73], 4, "Engineering & Technical Trades", "Electrical & Renewable Power Systems"),
    # SUB: Mechanical Precision & CNC Machining
    ([74, 95], 4, "Engineering & Technical Trades", "Mechanical Precision & CNC Machining"),
    # SUB: Automotive Engineering & Fleet Maintenance
    ([76, 77, 93], 4, "Engineering & Technical Trades", "Automotive Engineering & Fleet Maintenance"),
    # SUB: HVAC, Fabrication & Welding Trades
    ([75, 78], 4, "Engineering & Technical Trades", "HVAC, Fabrication & Welding Trades"),
    # SUB: Construction, Plumbing & Industrial Safety
    ([79, 80, 99, 100, 104], 4, "Engineering & Technical Trades", "Construction, Plumbing & Industrial Safety"),

    # Cat 5: Agriculture & Allied Skills (Cat ID: 5)
    # SUB: Organic Agronomy & Soil Management
    ([84], 5, "Agriculture & Allied Skills", "Organic Agronomy & Soil Management"),
    # SUB: Precision Irrigation & Water Technologies
    ([85, 103], 5, "Agriculture & Allied Skills", "Precision Irrigation & Water Technologies"),
    # SUB: Animal Husbandry & Dairy Management
    ([86], 5, "Agriculture & Allied Skills", "Animal Husbandry & Dairy Management"),

    # Cat 6: Media & Communication (Cat ID: 6)
    # SUB: Digital Marketing & Growth Strategy
    ([65, 66, 67, 68], 6, "Media & Communication", "Digital Marketing & Growth Strategy"),
    # SUB: Visual Design & UI/UX Experience
    ([69, 70], 6, "Media & Communication", "Visual Design & UI/UX Experience"),
    # SUB: Audio-Visual Production & Editing
    ([71], 6, "Media & Communication", "Audio-Visual Production & Editing"),
    # SUB: Professional Languages & Workplace Communication
    ([96, 97, 98], 6, "Media & Communication", "Professional Languages & Workplace Communication"),

    # Cat 7: Hospitality & Tourism (Cat ID: 7)
    # SUB: Front Office & Guest Services
    ([87], 7, "Hospitality & Tourism", "Front Office & Guest Services"),
    # SUB: Culinary Arts & Commercial Bakery
    ([89], 7, "Hospitality & Tourism", "Culinary Arts & Commercial Bakery"),
    # SUB: Food Safety, Hygiene & FSSAI Standards
    ([88], 7, "Hospitality & Tourism", "Food Safety, Hygiene & FSSAI Standards"),
    # Other vocational items into respective categories
    ([90], 4, "Engineering & Technical Trades", "Construction, Plumbing & Industrial Safety"), # Apparel/Industrial
    ([91], 7, "Hospitality & Tourism", "Front Office & Guest Services"), # Beauty & Wellness
    ([92], 2, "Business & Commerce", "Retail Management & Merchandising"), # Supply Chain & Warehouse
    ([94], 4, "Engineering & Technical Trades", "Electrical & Renewable Power Systems") # Drone Pilot
]

for ids, cat_id, cat_name, sub_name in SKILL_MAP:
    sub_id = sub_map[sub_name]
    for sid in ids:
        cur.execute("""
            UPDATE skills 
            SET category_id = %s, category_name = %s, subcategory_id = %s, subcategory_name = %s
            WHERE id = %s
        """, (cat_id, cat_name, sub_id, sub_name, sid))

# Skills 105-125 are duplicates created during regression tests -> assign to Cat 1
cur.execute("""
    UPDATE skills
    SET category_id = 1, category_name = 'Computer Science & Information Technology',
        subcategory_id = %s, subcategory_name = 'Cloud Computing & DevOps'
    WHERE id > 104
""", (sub_map["Cloud Computing & DevOps"],))

# 3. Add genuine, realistic skills to under-represented subcategories so each has ~5 relevant skills
ADDITIONAL_SKILLS = [
    # Cat 2: Business & Commerce
    # SUB: Accounting & Financial Taxation (currently has 2: 57, 59)
    {"sub": "Accounting & Financial Taxation", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Corporate Direct & Indirect Tax Auditing", "level": "Intermediate", "weeks": 8, "hours": 48},
    {"sub": "Accounting & Financial Taxation", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Cost Accounting & Variance Budgeting", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Accounting & Financial Taxation", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Payroll Accounting & Statutory Compliance (PF/ESI)", "level": "Beginner", "weeks": 4, "hours": 30},

    # SUB: Banking & Financial Services (currently has 3: 58, 60, 61)
    {"sub": "Banking & Financial Services", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Credit Appraisal & SME Loan Processing", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Banking & Financial Services", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Mutual Funds & Financial Securities Advisory (NISM Prep)", "level": "Intermediate", "weeks": 6, "hours": 40},

    # SUB: Entrepreneurship & Small Business (currently has 1: 62)
    {"sub": "Entrepreneurship & Small Business", "cat_id": 2, "cat_name": "Business & Commerce", "name": "MSME Registration & Government Grant Access", "level": "Beginner", "weeks": 4, "hours": 24},
    {"sub": "Entrepreneurship & Small Business", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Venture Feasibility Analysis & Pitch Deck Creation", "level": "Intermediate", "weeks": 6, "hours": 36},
    {"sub": "Entrepreneurship & Small Business", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Working Capital & Cash Flow Management for Startups", "level": "Intermediate", "weeks": 4, "hours": 30},
    {"sub": "Entrepreneurship & Small Business", "cat_id": 2, "cat_name": "Business & Commerce", "name": "E-Commerce Store Setup & Marketplace Selling", "level": "Beginner", "weeks": 6, "hours": 40},

    # SUB: Project Management & Agile Operations (currently has 2: 63, 64)
    {"sub": "Project Management & Agile Operations", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Jira & Confluence Enterprise Workflow Management", "level": "Beginner", "weeks": 4, "hours": 24},
    {"sub": "Project Management & Agile Operations", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Product Ownership & User Story Mapping", "level": "Intermediate", "weeks": 6, "hours": 36},
    {"sub": "Project Management & Agile Operations", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Risk Management & Quality Governance", "level": "Advanced", "weeks": 6, "hours": 40},

    # SUB: Retail Management & Merchandising (currently has 2: 101, 92)
    {"sub": "Retail Management & Merchandising", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Inventory Optimization & Demand Forecasting", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Retail Management & Merchandising", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Visual Merchandising & Retail Store Layout Design", "level": "Beginner", "weeks": 4, "hours": 28},
    {"sub": "Retail Management & Merchandising", "cat_id": 2, "cat_name": "Business & Commerce", "name": "Customer Relationship Management (CRM) in Retail", "level": "Beginner", "weeks": 4, "hours": 24},

    # Cat 3: Healthcare
    # SUB: Nursing & Patient Assistance (currently has 1: 81)
    {"sub": "Nursing & Patient Assistance", "cat_id": 3, "cat_name": "Healthcare", "name": "Elderly & Geriatric Home Care Assistance", "level": "Beginner", "weeks": 8, "hours": 60},
    {"sub": "Nursing & Patient Assistance", "cat_id": 3, "cat_name": "Healthcare", "name": "Infection Prevention & Hospital Hygiene Control", "level": "Beginner", "weeks": 4, "hours": 30},
    {"sub": "Nursing & Patient Assistance", "cat_id": 3, "cat_name": "Healthcare", "name": "Post-Operative Patient Care & Mobility Support", "level": "Intermediate", "weeks": 6, "hours": 45},
    {"sub": "Nursing & Patient Assistance", "cat_id": 3, "cat_name": "Healthcare", "name": "Palliative Care & Chronic Illness Support", "level": "Intermediate", "weeks": 6, "hours": 40},

    # SUB: Pharmacy Support & Dispensing (currently has 1: 82)
    {"sub": "Pharmacy Support & Dispensing", "cat_id": 3, "cat_name": "Healthcare", "name": "Hospital Pharmacy Inventory & Drug Storage", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Pharmacy Support & Dispensing", "cat_id": 3, "cat_name": "Healthcare", "name": "Pharmacology Basics & Drug Nomenclature", "level": "Beginner", "weeks": 6, "hours": 45},
    {"sub": "Pharmacy Support & Dispensing", "cat_id": 3, "cat_name": "Healthcare", "name": "Over-the-Counter Dispensing & Patient Counseling", "level": "Beginner", "weeks": 4, "hours": 30},
    {"sub": "Pharmacy Support & Dispensing", "cat_id": 3, "cat_name": "Healthcare", "name": "Ayush & Herbal Medicine Inventory Handling", "level": "Beginner", "weeks": 4, "hours": 28},

    # SUB: Emergency Medical Services (currently has 1: 83)
    {"sub": "Emergency Medical Services", "cat_id": 3, "cat_name": "Healthcare", "name": "Basic Life Support (BLS) & CPR Certification", "level": "Beginner", "weeks": 2, "hours": 16},
    {"sub": "Emergency Medical Services", "cat_id": 3, "cat_name": "Healthcare", "name": "Advanced Trauma First Aid & Triage Management", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Emergency Medical Services", "cat_id": 3, "cat_name": "Healthcare", "name": "Disaster Response & Mass Casualty Management", "level": "Intermediate", "weeks": 4, "hours": 30},
    {"sub": "Emergency Medical Services", "cat_id": 3, "cat_name": "Healthcare", "name": "Ambulance Equipment Operation & Patient Extrication", "level": "Beginner", "weeks": 4, "hours": 30},

    # SUB: Medical Records & Health Informatics (currently has 1: 102)
    {"sub": "Medical Records & Health Informatics", "cat_id": 3, "cat_name": "Healthcare", "name": "ICD-10 Clinical Coding & Diagnostics Classification", "level": "Intermediate", "weeks": 6, "hours": 45},
    {"sub": "Medical Records & Health Informatics", "cat_id": 3, "cat_name": "Healthcare", "name": "Ayushman Bharat Digital Mission (ABDM) Integration", "level": "Beginner", "weeks": 4, "hours": 24},
    {"sub": "Medical Records & Health Informatics", "cat_id": 3, "cat_name": "Healthcare", "name": "Hospital Information Management Systems (HIMS)", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Medical Records & Health Informatics", "cat_id": 3, "cat_name": "Healthcare", "name": "Health Insurance Claims Processing & TPA Audit", "level": "Intermediate", "weeks": 6, "hours": 40},

    # SUB: Diagnostic & Laboratory Assistance (currently has 0)
    {"sub": "Diagnostic & Laboratory Assistance", "cat_id": 3, "cat_name": "Healthcare", "name": "Clinical Phlebotomy & Blood Specimen Collection", "level": "Beginner", "weeks": 6, "hours": 45},
    {"sub": "Diagnostic & Laboratory Assistance", "cat_id": 3, "cat_name": "Healthcare", "name": "Clinical Pathology Specimen Preparation", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Diagnostic & Laboratory Assistance", "cat_id": 3, "cat_name": "Healthcare", "name": "Diagnostic Laboratory Safety & Bio-waste Disposal", "level": "Beginner", "weeks": 3, "hours": 20},
    {"sub": "Diagnostic & Laboratory Assistance", "cat_id": 3, "cat_name": "Healthcare", "name": "Point-of-Care Diagnostic Testing (POCT)", "level": "Beginner", "weeks": 4, "hours": 28},
    {"sub": "Diagnostic & Laboratory Assistance", "cat_id": 3, "cat_name": "Healthcare", "name": "ECG Recording & Basic Cardiac Monitoring", "level": "Beginner", "weeks": 4, "hours": 30},

    # Cat 5: Agriculture & Allied Skills
    # SUB: Organic Agronomy & Soil Management (currently has 1: 84)
    {"sub": "Organic Agronomy & Soil Management", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Soil Sampling, Testing & Nutrient Recommendation", "level": "Beginner", "weeks": 4, "hours": 28},
    {"sub": "Organic Agronomy & Soil Management", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Vermicomposting & Bio-Pesticide Production", "level": "Beginner", "weeks": 4, "hours": 24},
    {"sub": "Organic Agronomy & Soil Management", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Natural Farming & Zero Budget Natural Agriculture", "level": "Beginner", "weeks": 6, "hours": 40},
    {"sub": "Organic Agronomy & Soil Management", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Integrated Pest & Weed Management (IPM)", "level": "Intermediate", "weeks": 6, "hours": 40},

    # SUB: Precision Irrigation & Water Technologies (currently has 2: 85, 103)
    {"sub": "Precision Irrigation & Water Technologies", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Solar Water Pump Installation & Maintenance", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Precision Irrigation & Water Technologies", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Agricultural Rainwater Harvesting & Watershed Management", "level": "Beginner", "weeks": 4, "hours": 30},
    {"sub": "Precision Irrigation & Water Technologies", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Automated Sensor-Based Irrigation Systems", "level": "Advanced", "weeks": 6, "hours": 45},

    # SUB: Animal Husbandry & Dairy Management (currently has 1: 86)
    {"sub": "Animal Husbandry & Dairy Management", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Commercial Poultry Broiler & Layer Farming", "level": "Beginner", "weeks": 6, "hours": 40},
    {"sub": "Animal Husbandry & Dairy Management", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Goat & Sheep Rearing for Rural Livelihood", "level": "Beginner", "weeks": 4, "hours": 30},
    {"sub": "Animal Husbandry & Dairy Management", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Clean Milk Production & Cold Chain Logistics", "level": "Beginner", "weeks": 4, "hours": 28},
    {"sub": "Animal Husbandry & Dairy Management", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Veterinary First Aid & Livestock Vaccination", "level": "Intermediate", "weeks": 6, "hours": 45},

    # SUB: Horticulture & Greenhouse Cultivation (currently has 0)
    {"sub": "Horticulture & Greenhouse Cultivation", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Commercial Polyhouse Vegetable Cultivation", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Horticulture & Greenhouse Cultivation", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Floriculture & Commercial Flower Production", "level": "Beginner", "weeks": 6, "hours": 36},
    {"sub": "Horticulture & Greenhouse Cultivation", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Hydroponic & Aeroponic Urban Farming", "level": "Intermediate", "weeks": 6, "hours": 42},
    {"sub": "Horticulture & Greenhouse Cultivation", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Nursery Management & Plant Grafting Techniques", "level": "Beginner", "weeks": 4, "hours": 28},
    {"sub": "Horticulture & Greenhouse Cultivation", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Medicinal & Aromatic Plant Cultivation", "level": "Beginner", "weeks": 6, "hours": 40},

    # SUB: Post-Harvest Handling & Food Processing (currently has 0)
    {"sub": "Post-Harvest Handling & Food Processing", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Fruit & Vegetable Processing & Jam/Pickle Making", "level": "Beginner", "weeks": 6, "hours": 40},
    {"sub": "Post-Harvest Handling & Food Processing", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Grain Milling & Modern Silo Storage Management", "level": "Intermediate", "weeks": 4, "hours": 30},
    {"sub": "Post-Harvest Handling & Food Processing", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Dairy Processing: Paneer, Ghee & Cheese Making", "level": "Beginner", "weeks": 6, "hours": 40},
    {"sub": "Post-Harvest Handling & Food Processing", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Solar Crop Drying & Dehydration Technology", "level": "Beginner", "weeks": 4, "hours": 24},
    {"sub": "Post-Harvest Handling & Food Processing", "cat_id": 5, "cat_name": "Agriculture & Allied Skills", "name": "Agro-Produce Quality Grading & Sorting", "level": "Beginner", "weeks": 4, "hours": 28},

    # Cat 6: Media & Communication
    # SUB: Digital Marketing & Growth Strategy (currently has 4: 65, 66, 67, 68)
    {"sub": "Digital Marketing & Growth Strategy", "cat_id": 6, "cat_name": "Media & Communication", "name": "Email Marketing & Marketing Automation (HubSpot)", "level": "Intermediate", "weeks": 4, "hours": 28},

    # SUB: Visual Design & UI/UX Experience (currently has 2: 69, 70)
    {"sub": "Visual Design & UI/UX Experience", "cat_id": 6, "cat_name": "Media & Communication", "name": "Adobe Illustrator for Vector Illustration & Icons", "level": "Beginner", "weeks": 6, "hours": 36},
    {"sub": "Visual Design & UI/UX Experience", "cat_id": 6, "cat_name": "Media & Communication", "name": "Adobe Photoshop for Photo Editing & Compositing", "level": "Beginner", "weeks": 6, "hours": 40},
    {"sub": "Visual Design & UI/UX Experience", "cat_id": 6, "cat_name": "Media & Communication", "name": "Design Systems & Accessibility-First UI Design", "level": "Advanced", "weeks": 6, "hours": 40},

    # SUB: Audio-Visual Production & Editing (currently has 1: 71)
    {"sub": "Audio-Visual Production & Editing", "cat_id": 6, "cat_name": "Media & Communication", "name": "Adobe Premiere Pro for Documentary & Video Editing", "level": "Intermediate", "weeks": 8, "hours": 50},
    {"sub": "Audio-Visual Production & Editing", "cat_id": 6, "cat_name": "Media & Communication", "name": "Motion Graphics & Visual Effects with After Effects", "level": "Intermediate", "weeks": 8, "hours": 50},
    {"sub": "Audio-Visual Production & Editing", "cat_id": 6, "cat_name": "Media & Communication", "name": "Podcast Production & Studio Audio Engineering", "level": "Beginner", "weeks": 4, "hours": 28},
    {"sub": "Audio-Visual Production & Editing", "cat_id": 6, "cat_name": "Media & Communication", "name": "Drone Cinematography & Aerial Video Capture", "level": "Intermediate", "weeks": 4, "hours": 30},

    # SUB: Professional Languages & Workplace Communication (currently has 3: 96, 97, 98)
    {"sub": "Professional Languages & Workplace Communication", "cat_id": 6, "cat_name": "Media & Communication", "name": "Executive Business Writing & Email Etiquette", "level": "Beginner", "weeks": 4, "hours": 24},
    {"sub": "Professional Languages & Workplace Communication", "cat_id": 6, "cat_name": "Media & Communication", "name": "Public Speaking & Corporate Presentation Skills", "level": "Beginner", "weeks": 4, "hours": 24},

    # SUB: Journalism & Content Writing (currently has 0)
    {"sub": "Journalism & Content Writing", "cat_id": 6, "cat_name": "Media & Communication", "name": "Digital Journalism & Fact-Checking Fundamentals", "level": "Beginner", "weeks": 6, "hours": 36},
    {"sub": "Journalism & Content Writing", "cat_id": 6, "cat_name": "Media & Communication", "name": "SEO Content Writing & Blog Copywriting", "level": "Beginner", "weeks": 4, "hours": 28},
    {"sub": "Journalism & Content Writing", "cat_id": 6, "cat_name": "Media & Communication", "name": "Technical Documentation & API Writing", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Journalism & Content Writing", "cat_id": 6, "cat_name": "Media & Communication", "name": "Social Media Copywriting & Brand Storytelling", "level": "Beginner", "weeks": 4, "hours": 24},
    {"sub": "Journalism & Content Writing", "cat_id": 6, "cat_name": "Media & Communication", "name": "Public Relations Writing & Press Release Crafting", "level": "Intermediate", "weeks": 4, "hours": 28},

    # Cat 7: Hospitality & Tourism
    # SUB: Front Office & Guest Services (currently has 2: 87, 91)
    {"sub": "Front Office & Guest Services", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Hotel Property Management Systems (Opera PMS)", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Front Office & Guest Services", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Concierge Services & Cross-Cultural Guest Relations", "level": "Beginner", "weeks": 4, "hours": 24},
    {"sub": "Front Office & Guest Services", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Housekeeping Management & Hotel Room Styling", "level": "Beginner", "weeks": 6, "hours": 40},

    # SUB: Culinary Arts & Commercial Bakery (currently has 1: 89)
    {"sub": "Culinary Arts & Commercial Bakery", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Continental & Regional Indian Culinary Arts", "level": "Intermediate", "weeks": 8, "hours": 60},
    {"sub": "Culinary Arts & Commercial Bakery", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Artisanal Bread Baking & Sourdough Production", "level": "Intermediate", "weeks": 6, "hours": 45},
    {"sub": "Culinary Arts & Commercial Bakery", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Chocolate Making & Fine Patisserie Confectionery", "level": "Intermediate", "weeks": 6, "hours": 45},
    {"sub": "Culinary Arts & Commercial Bakery", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Commercial Kitchen Knife Skills & Preparation", "level": "Beginner", "weeks": 4, "hours": 30},

    # SUB: Food & Beverage Operations (currently has 0)
    {"sub": "Food & Beverage Operations", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Restaurant Fine Dining Table Service & Etiquette", "level": "Beginner", "weeks": 6, "hours": 40},
    {"sub": "Food & Beverage Operations", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Barista Skills & Specialty Coffee Brewing", "level": "Beginner", "weeks": 4, "hours": 28},
    {"sub": "Food & Beverage Operations", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Banquet Operations & Event Catering Coordination", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Food & Beverage Operations", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Beverage Inventory & Bar Stock Management", "level": "Beginner", "weeks": 4, "hours": 24},
    {"sub": "Food & Beverage Operations", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Fast Food & Quick Service Restaurant (QSR) Operations", "level": "Beginner", "weeks": 4, "hours": 28},

    # SUB: Food Safety, Hygiene & FSSAI Standards (currently has 1: 88)
    {"sub": "Food Safety, Hygiene & FSSAI Standards", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "HACCP Food Safety Management System Implementation", "level": "Intermediate", "weeks": 6, "hours": 40},
    {"sub": "Food Safety, Hygiene & FSSAI Standards", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Commercial Food Storage & Temperature Monitoring", "level": "Beginner", "weeks": 3, "hours": 20},
    {"sub": "Food Safety, Hygiene & FSSAI Standards", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Food Allergy Management & Dietary Labeling", "level": "Beginner", "weeks": 3, "hours": 18},
    {"sub": "Food Safety, Hygiene & FSSAI Standards", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Catering Hygiene Inspection & Audit Compliance", "level": "Intermediate", "weeks": 4, "hours": 28},

    # SUB: Travel Operations & Eco-Tourism (currently has 0)
    {"sub": "Travel Operations & Eco-Tourism", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Karnataka Heritage Tour Guiding & Facilitation", "level": "Beginner", "weeks": 6, "hours": 40},
    {"sub": "Travel Operations & Eco-Tourism", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Travel Itinerary Planning & GDS Air Ticketing", "level": "Intermediate", "weeks": 6, "hours": 45},
    {"sub": "Travel Operations & Eco-Tourism", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Eco-Tourism & Wildlife Safari Camp Coordination", "level": "Beginner", "weeks": 6, "hours": 40},
    {"sub": "Travel Operations & Eco-Tourism", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Adventure Tourism Safety & Trek Leader Standards", "level": "Intermediate", "weeks": 4, "hours": 32},
    {"sub": "Travel Operations & Eco-Tourism", "cat_id": 7, "cat_name": "Hospitality & Tourism", "name": "Homestay Operations & Rural Hospitality Management", "level": "Beginner", "weeks": 4, "hours": 28}
]

cur.execute("SELECT MAX(id) as max_id FROM skills")
next_id = cur.fetchone()["max_id"] + 1

added_cnt = 0
for s in ADDITIONAL_SKILLS:
    sub_id = sub_map[s["sub"]]
    # Check if skill with same name exists
    cur.execute("SELECT id FROM skills WHERE name = %s", (s["name"],))
    if cur.fetchone():
        continue
    code = f"SKL-{next_id:04d}"
    summary = f"Professional industry-aligned skilling course in {s['name']}, certified under NSQF standards."
    details = f"Comprehensive curriculum covering practical laboratory sessions, hands-on industrial projects, and assessments in {s['name']}."
    prereq = "Basic literacy and interest in the technical field"
    objectives = f"Equip trainees with job-ready capabilities in {s['name']} aligned with modern industrial employment requirements."
    outcomes = f"Demonstrated competency in executing standard procedures, equipment handling, and problem solving in {s['name']}."
    industries = s["cat_name"]
    career = f"Junior Specialist / Certified Associate in {s['name']}"

    cur.execute("""
        INSERT INTO skills (
            id, code, name, category_id, category_name, subcategory_id, subcategory_name,
            level, duration_weeks, duration_hours, summary, details, prerequisites,
            learning_objectives, learning_outcomes, relevant_industries, career_opportunities,
            cert_info, rating, enrolled_count, active
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """, (
        next_id, code, s["name"], s["cat_id"], s["cat_name"], sub_id, s["sub"],
        s["level"], s["weeks"], s["hours"], summary, details, prereq,
        objectives, outcomes, industries, career,
        "Government of India Skill Qualification Framework (NSQF) aligned certificate",
        4.8, 0, 1
    ))
    next_id += 1
    added_cnt += 1

conn.commit()
print(f"Skill hierarchy classified! Added {added_cnt} new skills to satisfy 5+ skills per subcategory.")
conn.close()
