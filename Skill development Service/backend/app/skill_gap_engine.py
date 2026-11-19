"""
Transparent Skill Gap Analysis Engine.
Rule-based matching algorithm designed to compare a citizen's existing competencies against
target career profiles and suggest a structured learning path with transparent explanations.
Ready for future integration with the shared NagrikSetu AI recommendation service.
"""
from typing import List, Dict, Any

ROLE_REQUIREMENTS = {
    "Full Stack Python / Web Developer": {
        "required_skills": ["Python Programming", "FastAPI Python Backend Development", "HTML5 & Modern CSS3", "JavaScript Deep Dive (ES6+)", "React.js Frontend Development", "Docker & Containerization"],
        "recommended_order": ["HTML5 & Modern CSS3", "JavaScript Deep Dive (ES6+)", "Python Programming", "FastAPI Python Backend Development", "React.js Frontend Development", "Docker & Containerization"],
        "description": "Engineers end-to-end modern web applications, scalable REST APIs, and responsive citizen-facing interfaces."
    },
    "Enterprise Java Microservices Developer": {
        "required_skills": ["Java Development Fundamentals", "Enterprise Java & Spring Boot", "TypeScript for Modern Applications", "Docker & Containerization", "Kubernetes Administration (CKA Prep)"],
        "recommended_order": ["Java Development Fundamentals", "Enterprise Java & Spring Boot", "Docker & Containerization", "Kubernetes Administration (CKA Prep)"],
        "description": "Architects resilient, high-throughput microservices using Spring Boot, Spring Cloud, and containerized clusters."
    },
    "Data Analyst / Business Intelligence Specialist": {
        "required_skills": ["Data Analysis with Python (Pandas/NumPy)", "Business Intelligence with Power BI", "Advanced Excel for Business Analytics", "Data Storytelling with Tableau", "Data Visualisation (Matplotlib & Seaborn)"],
        "recommended_order": ["Advanced Excel for Business Analytics", "Data Analysis with Python (Pandas/NumPy)", "Data Visualisation (Matplotlib & Seaborn)", "Business Intelligence with Power BI"],
        "description": "Translates complex civic and business metrics into executive dashboards, data stories, and predictive insights."
    },
    "Machine Learning & AI Engineer": {
        "required_skills": ["Python Programming", "Applied Machine Learning with Scikit-Learn", "Deep Learning & Neural Networks with PyTorch", "Generative AI & LLM Prompt Engineering", "Natural Language Processing (NLP)"],
        "recommended_order": ["Python Programming", "Applied Machine Learning with Scikit-Learn", "Deep Learning & Neural Networks with PyTorch", "Natural Language Processing (NLP)", "Generative AI & LLM Prompt Engineering"],
        "description": "Builds and deploys statistical machine learning models, computer vision systems, and generative AI agents."
    },
    "Cloud & DevOps Engineer": {
        "required_skills": ["Linux Command Line & Bash", "AWS Cloud Practitioner Essentials", "Docker & Containerization", "Kubernetes Administration (CKA Prep)", "CI/CD Automation with GitHub Actions", "Infrastructure as Code with Terraform"],
        "recommended_order": ["Linux Command Line & Bash", "AWS Cloud Practitioner Essentials", "Docker & Containerization", "CI/CD Automation with GitHub Actions", "Kubernetes Administration (CKA Prep)", "Infrastructure as Code with Terraform"],
        "description": "Automates cloud infrastructure provisioning, CI/CD pipelines, container orchestration, and multi-region resilience."
    },
    "Software QA & Automation Engineer": {
        "required_skills": ["Manual Software Testing Foundations", "Selenium WebDriver with Java", "API Testing with Postman & Newman", "Performance Testing with Apache JMeter", "Cypress Modern Web Automation"],
        "recommended_order": ["Manual Software Testing Foundations", "API Testing with Postman & Newman", "Selenium WebDriver with Java", "Cypress Modern Web Automation", "Performance Testing with Apache JMeter"],
        "description": "Guarantees mission-critical software reliability through automated regression pipelines, load verification, and bug tracking."
    },
    "Renewable Energy & Solar Technician": {
        "required_skills": ["Domestic Electrician & Home Wiring", "Solar PV Rooftop System Installation", "Electrical Safety Norms"],
        "recommended_order": ["Domestic Electrician & Home Wiring", "Solar PV Rooftop System Installation"],
        "description": "Installs, commissions, and inspects residential and industrial rooftop solar arrays and grid inverters."
    },
    "GST Accountant & Financial Executive": {
        "required_skills": ["Financial Accounting & Bookkeeping", "Tally Prime with GST & E-Way Bills", "Advanced Excel for Business Analytics"],
        "recommended_order": ["Financial Accounting & Bookkeeping", "Tally Prime with GST & E-Way Bills", "Advanced Excel for Business Analytics"],
        "description": "Maintains corporate general ledgers, files statutory GST returns, and generates managerial financial statements."
    }
}

class SkillGapEngine:
    @classmethod
    def get_supported_roles(cls) -> List[Dict[str, str]]:
        return [{"role": role, "description": data["description"]} for role, data in ROLE_REQUIREMENTS.items()]

    @classmethod
    def analyze_gap(cls, target_role: str, user_skills: List[str]) -> Dict[str, Any]:
        role_data = ROLE_REQUIREMENTS.get(target_role)
        if not role_data:
            # Fallback: synthesize target from generic tech role
            role_data = {
                "required_skills": ["Python Programming", "HTML5 & Modern CSS3", "JavaScript Deep Dive (ES6+)", "AWS Cloud Practitioner Essentials"],
                "recommended_order": ["HTML5 & Modern CSS3", "JavaScript Deep Dive (ES6+)", "Python Programming", "AWS Cloud Practitioner Essentials"],
                "description": f"Role requirements for {target_role}."
            }

        required = role_data["required_skills"]
        user_skills_lower = [s.strip().lower() for s in user_skills]

        matching = []
        partial = []
        missing = []

        for req in required:
            r_lower = req.lower()
            if any(r_lower == u for u in user_skills_lower):
                matching.append(req)
            elif any((u in r_lower or r_lower in u) and len(u) > 5 and u != "python" and u != "development" for u in user_skills_lower):
                # Only broad match if specific
                matching.append(req)
            elif any(part in " ".join(user_skills_lower) for part in r_lower.split() if len(part) > 6 and part not in ("python", "backend", "development", "modern")):
                partial.append(req)
            else:
                missing.append(req)

        total_req = len(required)
        match_score = int(((len(matching) * 1.0) + (len(partial) * 0.5)) / total_req * 100) if total_req else 0

        # Suggested courses in recommended order
        recommended_courses = []
        for course in role_data.get("recommended_order", required):
            if course in missing or course in partial:
                recommended_courses.append({
                    "skill_name": course,
                    "reason": f"Essential skill required for {target_role}. Bridges identified knowledge gap.",
                    "priority": "High" if course in missing else "Medium"
                })

        return {
            "target_role": target_role,
            "role_description": role_data["description"],
            "total_required_skills": total_req,
            "matching_skills": matching,
            "partially_matching_skills": partial,
            "missing_skills": missing,
            "skill_gap_score": match_score,
            "readiness_level": "Ready for Interview" if match_score >= 80 else ("Moderate Gap — 1-2 Courses Required" if match_score >= 50 else "High Gap — Comprehensive Foundation Required"),
            "recommended_courses": recommended_courses,
            "engine_type": "Deterministic Rule-Based Analyzer (NagrikSetu Skilling Core v2.0)"
        }
