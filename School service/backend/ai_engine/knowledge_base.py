"""
NagrikSetu AI Engine - Official Government Knowledge Base
Provides statutory rules, scheme eligibility, and procedural facts for Karnataka Education Services.
Never fabricates rules, amounts, or deadlines.
"""

from typing import Dict, Any, Optional, List

OFFICIAL_SCHEMES_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "rte": {
        "title": "Right to Education (RTE) 25% Reserved Seat Scheme",
        "authority": "Department of School Education and Literacy (DSEL), Government of Karnataka",
        "governing_law": "Right of Children to Free and Compulsory Education Act 2009, Section 12(1)(c)",
        "key_facts": [
            "25% of entry-level seats (LKG or 1st Standard) in private unaided non-minority schools are reserved for children from disadvantaged and economically weaker sections.",
            "Government covers the full tuition reimbursement directly to schools; parents pay zero admission fees.",
            "Eligibility criteria: Family annual income must be below Rs. 3.5 Lakhs for economically weaker section, or child must belong to disadvantaged group (SC/ST, Category 1, HIV affected, children with disabilities, orphan).",
            "Age criteria: Child must have completed 3 years 10 months for LKG or 5 years 10 months to 6 years for Class 1 as of 1st June of the admission academic year.",
            "Application procedure: Online centralized single-window application portal managed by DSEL Karnataka with Aadhaar linkage.",
            "Required documents: Child birth certificate, Aadhaar card of child and parents, valid Caste/Income Certificate issued by Revenue Department (RD number), residential address proof within neighborhood (1 to 3 km)."
        ],
        "important_note": "Under Karnataka RTE Amendment Rules, if a Government or Aided school exists in the neighborhood, RTE private school allocation applies only when government/aided seats are unavailable."
    },
    "ssp_pre_matric": {
        "title": "Karnataka State Scholarship Portal (SSP) - Pre-Matric Scholarship",
        "authority": "Social Welfare, Tribal Welfare, Backward Classes Welfare & Minorities Welfare Departments",
        "target_students": "Students in Standards 1 to 10 belonging to SC, ST, OBC, and Religious Minorities",
        "key_facts": [
            "Provides financial assistance to reduce school dropouts and support educational expenses (books, stationery, uniforms).",
            "Annual family income ceiling: SC/ST up to Rs. 2.50 Lakhs; OBC (Cat-1, 2A, 2B, 3A, 3B) up to Rs. 1.00 Lakh; Minorities up to Rs. 1.00 Lakh.",
            "Minimum academic criteria: Regular attendance and passing preceding class marks (typically 50% for fresh applicants, exemptions for SC/ST).",
            "Direct Benefit Transfer (DBT): Disbursed directly into the student's Aadhaar-seeded bank account.",
            "Mandatory documents: Student SATS number (Student Achievement Tracking System), Revenue Department Caste & Income Certificate (RD Number), student Aadhaar card, bank account linked to NPCI mapper."
        ],
        "application_mode": "Online via Karnataka SSP Portal (ssp.karnataka.gov.in) through school nodal officer."
    },
    "ssp_post_matric": {
        "title": "Karnataka State Scholarship Portal (SSP) - Post-Matric Scholarship",
        "authority": "Government of Karnataka Centralized Scholarship Portal",
        "target_students": "Students pursuing Pre-University (PUC), Diploma, ITI, Undergraduate, Postgraduate and Professional Courses",
        "key_facts": [
            "Covers tuition fee reimbursement, laboratory fees, examination fees, and maintenance allowances.",
            "Includes Vidyasiri (Food and Accommodation Scheme) providing Rs. 15,000 per annum for eligible students not accommodated in government hostels.",
            "Income limits: SC/ST up to Rs. 2.50 Lakhs; Category-1 up to Rs. 2.50 Lakhs; 2A/2B/3A/3B up to Rs. 1.00 Lakh.",
            "E-Attestation required: All uploaded marksheets, fee receipts, and study certificates must be digitally verified by designated college e-attestation officers."
        ],
        "application_mode": "Online via ssp.postmatric.karnataka.gov.in with e-Attestation."
    },
    "nmms": {
        "title": "National Means-cum-Merit Scholarship Scheme (NMMS)",
        "authority": "Ministry of Education & Karnataka KSEAB (Karnataka School Examination and Assessment Board)",
        "target_students": "Meritorious students studying in Government and Aided schools in Standard 8",
        "key_facts": [
            "Scholarship amount: Rs. 12,000 per annum (Rs. 1,000 per month) from Standard 9 through Standard 12.",
            "Selection mechanism: State-level competitive examination comprising Mental Ability Test (MAT) and Scholastic Aptitude Test (SAT).",
            "Eligibility criteria: Minimum 55% marks in Class 7 examination (50% for SC/ST); parental annual income not exceeding Rs. 3.50 Lakhs.",
            "Students enrolled in private schools, Navodaya, or Kendriya Vidyalayas are not eligible."
        ]
    },
    "nutrition_pm_poshan": {
        "title": "PM POSHAN & Ksheera Bhagya Mid-Day Meal Scheme",
        "authority": "Department of School Education and Literacy, Karnataka",
        "target_students": "All students enrolled in Standards 1 to 10 in Government and Government-Aided Schools",
        "key_facts": [
            "Hot cooked mid-day meal provided every working school day meeting calorie and protein nutritional standards.",
            "Ksheera Bhagya: Free nutritious boiled milk distributed 5 days a week.",
            "Egg / Banana / Chikki scheme: Karnataka government provides boiled eggs or bananas/chikki twice a week for all students in Standards 1 to 10 to combat malnutrition and anemia.",
            "Zero cost to students; completely funded by State and Central Governments."
        ]
    },
    "vidya_vikas_textbooks_uniforms": {
        "title": "Karnataka Vidya Vikas Scheme (Free Textbooks & Uniforms)",
        "authority": "Karnataka Textbook Society (KTBS) & Directorate of Primary Education",
        "target_students": "Standards 1 to 10 in Government Schools",
        "key_facts": [
            "Free state curriculum textbooks supplied at the beginning of each academic year to 100% of government school students.",
            "Two sets of stitched school uniforms provided free annually.",
            "One pair of shoes and two pairs of socks provided annually.",
            "Free school bags and notebooks supplied under state welfare allocations."
        ]
    },
    "transfers_and_tc": {
        "title": "School Transfer & Transfer Certificate (TC) Regulatory Guidelines",
        "authority": "Karnataka Education Act 1983 & Karnataka SATS Regulations",
        "key_facts": [
            "Right to Transfer: Every parent has the legal right to request a Transfer Certificate (TC) when moving residence, changing school type, or relocating districts.",
            "Statutory Timeline: School authorities must process and issue the TC within 7 working days of formal parent request.",
            "Fee Dispute Protection: Under High Court and Departmental rulings, schools cannot legally withhold a student's Transfer Certificate or deny TC release due to pending fee disputes.",
            "SATS Online Transfer: Transfer is executed digitally via Karnataka SATS (Student Achievement Tracking System) transferring the student's unique Permanent Student ID seamlessly to the new institution.",
            "Mandatory documents: Application letter by parent/guardian, admission confirmation from receiving school (if inter-state/inter-board), and no-dues clearance for library/sports equipment."
        ]
    },
    "out_of_school_bridge": {
        "title": "Out-of-School Children (OOSC) Re-Entry & Bridge Course Guidelines",
        "authority": "Samagra Shiksha Karnataka",
        "key_facts": [
            "Under Section 4 of the RTE Act, any out-of-school child or dropout must be admitted to an age-appropriate class without entrance examination or penalty.",
            "Special Training Centers (STC) & Bridge Courses: Non-residential and residential bridge centers provide 3 to 12 months accelerated curriculum coaching to prepare children before integrating them into standard classrooms.",
            "Kishori Kendra & Chinnara Angala programs support adolescent girls and migrant children with bridge learning.",
            "Contact: Nearest Block Education Officer (BEO) or Government School Headmaster for direct free enrollment."
        ]
    }
}

def search_official_knowledge(query: str) -> Optional[Dict[str, Any]]:
    """
    Finds the most relevant official knowledge item based on user query keywords.
    """
    q = query.lower()
    
    if any(k in q for k in ["rte", "right to education", "25%", "25 percent", "free quota", "un-aided reservation"]):
        return OFFICIAL_SCHEMES_KNOWLEDGE["rte"]
    elif any(k in q for k in ["nmms", "merit scholarship", "class 8 scholarship", "national means"]):
        return OFFICIAL_SCHEMES_KNOWLEDGE["nmms"]
    elif any(k in q for k in ["pre-matric", "pre matric", "ssp 1-10", "school scholarship", "sc st scholarship", "obc scholarship"]):
        return OFFICIAL_SCHEMES_KNOWLEDGE["ssp_pre_matric"]
    elif any(k in q for k in ["post-matric", "post matric", "college scholarship", "vidyasiri", "puc scholarship", "diploma scholarship"]):
        return OFFICIAL_SCHEMES_KNOWLEDGE["ssp_post_matric"]
    elif any(k in q for k in ["transfer", "tc", "transfer certificate", "school transfer", "relocat", "withhold"]):
        return OFFICIAL_SCHEMES_KNOWLEDGE["transfers_and_tc"]
    elif any(k in q for k in ["out of school", "dropout", "drop out", "bridge course", "re-entry", "chinnara angala", "gap"]):
        return OFFICIAL_SCHEMES_KNOWLEDGE["out_of_school_bridge"]
    elif any(k in q for k in ["food", "lunch", "mid-day", "midday", "pm poshan", "milk", "ksheera bhagya", "nutrition", "egg"]):
        return OFFICIAL_SCHEMES_KNOWLEDGE["nutrition_pm_poshan"]
    elif any(k in q for k in ["textbook", "uniform", "shoes", "free books", "vidya vikas"]):
        return OFFICIAL_SCHEMES_KNOWLEDGE["vidya_vikas_textbooks_uniforms"]
    elif any(k in q for k in ["scholarship", "scheme", "financial assistance", "welfare"]):
        # General scholarship inquiry
        return OFFICIAL_SCHEMES_KNOWLEDGE["ssp_pre_matric"]
    
    return None
