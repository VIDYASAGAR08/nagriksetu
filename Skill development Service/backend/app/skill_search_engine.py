import re
from typing import List, Set, Tuple
from sqlalchemy import or_, and_
from app.models import TrainingProgram, Skill

# Comprehensive Domain & Morphological Term Dictionary
# Connects colloquial, occupational, and technical terms to actual database curricula
UNIVERSAL_MORPHOLOGY_MAP = {
    # Engineering & Technical Trades
    "electrician": ["electrical", "electric", "wiring", "home wiring"],
    "electrical": ["electrician", "electric", "wiring", "home wiring"],
    "electric": ["electrician", "electrical", "wiring"],
    "welder": ["welding", "weld", "metal arc", "tig"],
    "welding": ["welder", "weld", "metal arc", "tig"],
    "weld": ["welder", "welding", "metal arc", "tig"],
    "carpenter": ["carpentry", "woodwork", "architectural woodwork"],
    "carpentry": ["carpenter", "woodwork", "architectural woodwork"],
    "plumber": ["plumbing", "pipe fitting"],
    "plumbing": ["plumber", "pipe fitting"],
    "tailor": ["tailoring", "apparel", "garment", "industrial tailoring"],
    "tailoring": ["tailor", "apparel", "garment", "industrial tailoring"],
    "apparel": ["tailoring", "tailor", "garment"],
    "mason": ["masonry", "construction"],
    "masonry": ["mason", "construction"],
    "construction": ["masonry", "mason"],
    "hvac": ["refrigeration", "air conditioning", "cooling"],
    "refrigeration": ["hvac", "air conditioning"],
    "air conditioning": ["hvac", "refrigeration"],
    "cnc": ["cnc machine", "machining"],
    "mechatronics": ["industrial automation", "plc", "scada", "automation"],
    "automation": ["mechatronics", "industrial automation"],
    "solar": ["solar pv", "rooftop", "photovoltaic"],
    "safety": ["industrial safety", "osha"],

    # Agriculture & Rural Trades
    "farmer": ["farming", "farm", "agriculture", "organic farming"],
    "farming": ["farmer", "farm", "agriculture", "organic farming"],
    "farm": ["farming", "farmer", "agriculture", "organic farming"],
    "agriculture": ["farming", "organic farming", "soil health"],
    "organic": ["organic farming", "soil health"],
    "irrigation": ["micro-irrigation", "drip irrigation"],
    "drip": ["drip irrigation", "micro-irrigation"],
    "dairy": ["livestock", "dairy farming"],
    "livestock": ["dairy farming", "dairy"],

    # Healthcare & Wellness
    "nurse": ["nursing", "general duty assistant", "healthcare", "emt", "medical"],
    "nursing": ["nurse", "general duty assistant", "healthcare", "emt", "medical"],
    "healthcare": ["general duty assistant", "medical", "hospitality", "emt", "pharmacy"],
    "medical": ["general duty assistant", "emt", "emergency medical", "medical records", "healthcare"],
    "hospital": ["healthcare", "hospitality", "general duty assistant"],
    "emt": ["emergency medical technician", "paramedic", "ambulance"],
    "paramedic": ["emt", "emergency medical technician"],
    "pharmacy": ["pharmacy assistant", "pharmacist", "pharmacology"],
    "pharmacist": ["pharmacy assistant", "pharmacy"],
    "wellness": ["beauty", "wellness professional"],
    "beauty": ["beauty & wellness", "wellness"],

    # Food & Hospitality
    "baker": ["baking", "bakery", "confectionery"],
    "baking": ["baker", "bakery", "confectionery"],
    "bakery": ["baking", "baker", "confectionery"],
    "confectionery": ["baking", "baker"],
    "cooking": ["food safety", "commercial baking", "hospitality"],
    "chef": ["commercial baking", "food safety", "hospitality"],
    "food": ["food safety", "fssai", "commercial baking"],
    "fssai": ["food safety", "hygiene"],
    "hospitality": ["front office", "hotel management"],

    # Automotive & Transportation
    "mechanic": ["automotive", "technician", "two-wheeler", "four-wheeler"],
    "automobile": ["automotive", "vehicle", "two-wheeler", "four-wheeler"],
    "automotive": ["automobile", "vehicle", "two-wheeler", "four-wheeler", "maintenance"],
    "driver": ["driving", "commercial vehicle", "fleet"],
    "driving": ["driver", "commercial vehicle", "fleet"],
    "drone": ["drone pilot", "dgca", "uav"],
    "pilot": ["drone pilot"],

    # Business, Finance & Operations
    "accountant": ["accounting", "accounts", "bookkeeping", "tally"],
    "accounting": ["accountant", "accounts", "bookkeeping", "tally"],
    "accounts": ["accounting", "accountant", "bookkeeping", "tally"],
    "tally": ["tally prime", "gst", "accounting"],
    "gst": ["tally prime", "accounting"],
    "banker": ["banking", "retail banking", "retail services"],
    "banking": ["banker", "retail banking", "financial"],
    "finance": ["financial modeling", "accounting", "banking"],
    "financial": ["finance", "financial modeling", "accounting"],
    "excel": ["advanced excel", "spreadsheet", "business analytics"],
    "retail": ["retail store", "store operations", "inventory"],
    "inventory": ["retail store", "supply chain", "warehouse"],
    "supply chain": ["warehouse operations", "logistics", "inventory"],
    "warehouse": ["supply chain", "warehouse operations"],
    "scrum": ["agile", "scrum master", "project management"],
    "agile": ["scrum", "project management"],
    "project management": ["agile", "scrum"],

    # Creative & Design
    "design": ["ui/ux", "graphic design", "figma"],
    "designer": ["ui/ux", "graphic design", "figma"],
    "ui/ux": ["figma", "ui design", "ux design", "user interface"],
    "ui": ["ui/ux", "figma", "user interface"],
    "ux": ["ui/ux", "figma", "user experience"],
    "figma": ["ui/ux", "ui design", "ux design"],
    "graphic": ["graphic design", "visual communication"],
    "video": ["video editing", "content creation"],
    "editing": ["video editing"],

    # Digital Marketing
    "seo": ["search engine optimization", "digital marketing"],
    "marketing": ["digital marketing", "seo", "google ads", "social media"],
    "advertising": ["google ads", "performance marketing", "digital marketing"],
    "ads": ["google ads", "performance marketing"],
    "social media": ["digital marketing", "brand building"],

    # IT, Programming & Computer Science
    "developer": ["software", "programming", "full stack", "web development"],
    "programmer": ["programming", "developer", "software development"],
    "coding": ["programming", "developer", "software"],
    "software": ["programming", "testing", "developer"],
    "testing": ["software testing", "qa", "selenium", "cypress", "automation testing"],
    "qa": ["software testing", "testing", "quality assurance", "selenium"],
    "frontend": ["web development", "react", "html5", "css3", "javascript"],
    "backend": ["node.js", "express", "django", "fastapi", "spring boot", "api"],
    "fullstack": ["full stack", "mern", "web development"],
    "full stack": ["mern", "web development", "frontend", "backend"],
    "api": ["rest api", "fastapi", "node.js", "express", "spring boot", "postman"],
    "cloud": ["aws", "azure", "gcp", "google cloud", "devops", "cloud practitioner"],
    "devops": ["docker", "kubernetes", "ci/cd", "github actions", "terraform", "sre"],
    "containers": ["docker", "kubernetes"],
    "containerization": ["docker", "kubernetes"],
    "security": ["cybersecurity", "ethical hacking", "network security", "infosec"],
    "cyber": ["cybersecurity", "ethical hacking", "penetration testing"],
    "hacking": ["ethical hacking", "penetration testing", "cybersecurity"],
    "pentesting": ["ethical hacking", "penetration testing"],
    "network": ["networking", "cisco", "ccna", "comptia network"],
    "networking": ["network", "cisco", "ccna", "comptia network"],
    "database": ["sql", "data", "backend"],
    "ai": ["artificial intelligence", "machine learning", "deep learning", "generative ai"],
    "ml": ["machine learning", "scikit-learn", "data science"],
    "data science": ["machine learning", "deep learning", "data analysis", "python"],
    "analytics": ["data analytics", "data analysis", "business analytics", "power bi", "tableau"],
    "data analysis": ["data analytics", "pandas", "numpy", "python"],
    "nlp": ["natural language processing", "text analysis"],
    "vision": ["computer vision", "opencv"],
    "llm": ["generative ai", "prompt engineering", "large language models"],
    "genai": ["generative ai", "llm", "prompt engineering"],
    "deep learning": ["neural networks", "pytorch", "artificial intelligence"],
    "machine learning": ["scikit-learn", "artificial intelligence", "data science"]
}

def build_universal_search_terms(query_str: str) -> List[str]:
    """
    Expands a raw search query into canonical and synonym terms
    supporting all database curricula, technical, vocational, and regional trades.
    """
    clean_q = query_str.strip()
    if not clean_q:
        return []
    
    lower_q = clean_q.lower()
    terms_set: Set[str] = {clean_q}

    # Direct phrase matching
    if lower_q in UNIVERSAL_MORPHOLOGY_MAP:
        terms_set.update(UNIVERSAL_MORPHOLOGY_MAP[lower_q])

    # Word-level token inspection and morphological normalization
    raw_tokens = re.findall(r"[\w\+#]+", lower_q)
    for tok in raw_tokens:
        if tok in UNIVERSAL_MORPHOLOGY_MAP:
            terms_set.update(UNIVERSAL_MORPHOLOGY_MAP[tok])
        
        # English morphological suffix stemming:
        # e.g., 'electricians' -> 'electrician', 'plumbers' -> 'plumber', 'welders' -> 'welder'
        # Only query expanded stemmed tokens if they exist in the morphology map (to prevent over-stemming like 'driv' matching 'webdriver')
        if len(tok) >= 5 and tok.endswith("ers"):
            stem = tok[:-3]
            if stem in UNIVERSAL_MORPHOLOGY_MAP:
                terms_set.add(stem)
                terms_set.update(UNIVERSAL_MORPHOLOGY_MAP[stem])
        elif len(tok) >= 4 and tok.endswith("er") and not tok.endswith("docker"):
            stem = tok[:-2]
            if stem in UNIVERSAL_MORPHOLOGY_MAP:
                terms_set.add(stem)
                terms_set.update(UNIVERSAL_MORPHOLOGY_MAP[stem])
        elif len(tok) >= 5 and tok.endswith("ing"):
            stem = tok[:-3]
            if stem in UNIVERSAL_MORPHOLOGY_MAP:
                terms_set.add(stem)
                terms_set.update(UNIVERSAL_MORPHOLOGY_MAP[stem])
        elif len(tok) >= 5 and tok.endswith("s") and not tok.endswith("ss"):
            stem = tok[:-1]
            if stem in UNIVERSAL_MORPHOLOGY_MAP:
                terms_set.add(stem)
                terms_set.update(UNIVERSAL_MORPHOLOGY_MAP[stem])

    return list(terms_set)


def apply_universal_programme_filters(query_obj, search_str: str):
    """
    Applies universal relational matching across TrainingProgram and Skill models,
    with strict linguistic disambiguation for collision-prone acronyms and short names.
    """
    s_clean = search_str.strip()
    if not s_clean:
        return query_obj

    s_lower = s_clean.lower()
    terms = build_universal_search_terms(s_clean)

    filters = []
    for t in terms:
        # Avoid over-broad substring matches on very short tokens like 'ai' or 'c' in long descriptions
        if len(t) <= 2 and t.lower() not in ("c++", "c#", "ui", "ux", "js", "go", "r"):
            filters.extend([
                TrainingProgram.title.ilike(f"%{t} %"),
                TrainingProgram.title.ilike(f"% {t}%"),
                Skill.name.ilike(f"%{t} %"),
                Skill.name.ilike(f"% {t}%"),
                Skill.name.ilike(t)
            ])
        else:
            p = f"%{t}%"
            filters.extend([
                TrainingProgram.title.ilike(p),
                TrainingProgram.description.ilike(p),
                Skill.name.ilike(p),
                Skill.category_name.ilike(p)
            ])

    query_obj = query_obj.join(Skill, TrainingProgram.skill_id == Skill.id).filter(or_(*filters))

    # Strict disambiguation safeguards:
    # 1. C++ must match C++, not general C or C#
    if s_lower == "c++":
        query_obj = query_obj.filter(or_(TrainingProgram.title.ilike("%c++%"), Skill.name.ilike("%c++%")))
    # 2. C Programming must match C foundations, not C++ or C#
    elif s_lower == "c" or s_lower == "c programming":
        query_obj = query_obj.filter(
            or_(TrainingProgram.title.ilike("%c programming%"), Skill.name.ilike("%c programming%")),
            ~TrainingProgram.title.ilike("%c++%"),
            ~TrainingProgram.title.ilike("%c#%")
        )
    # 3. Java must not match JavaScript
    elif "java" in s_lower and "javascript" not in s_lower:
        query_obj = query_obj.filter(
            ~TrainingProgram.title.ilike("%javascript%"),
            ~Skill.name.ilike("%javascript%")
        )
    # 4. JavaScript must not match plain Java
    elif "javascript" in s_lower or s_lower == "js":
        query_obj = query_obj.filter(
            or_(TrainingProgram.title.ilike("%javascript%"), Skill.name.ilike("%javascript%"))
        )
    # 5. Commercial vehicle driving / driver must not match Selenium WebDriver
    elif "driving" in s_lower or "commercial vehicle" in s_lower or s_lower == "driver":
        query_obj = query_obj.filter(
            ~TrainingProgram.title.ilike("%webdriver%"),
            ~Skill.name.ilike("%webdriver%")
        )

    return query_obj
