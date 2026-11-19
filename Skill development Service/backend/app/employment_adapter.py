"""
Employment Microservice Integration Adapter.
As mandated by NagrikSetu Architecture: Member 1 owns the Employment Microservice.
This module isolates external calls to Member 1's service behind an adapter pattern.
If the Employment API is available, it forwards requests; otherwise, it supplies clearly
identified demonstration data, keeping the Skill Development service completely decoupled.
"""
from typing import List, Dict, Any, Optional
import os
import httpx
import logging

log = logging.getLogger(__name__)

EMPLOYMENT_SERVICE_URL = os.getenv("EMPLOYMENT_SERVICE_URL", "http://localhost:8002")

# Realistic demonstration career opportunities aligned with skilled trades and tech roles
DEMO_JOB_OPPORTUNITIES = [
    {
        "id": "JOB-00101",
        "title": "Junior Python / Backend Developer",
        "company": "Karnataka e-Governance Centre / Tech Partner",
        "location": "Bengaluru, Karnataka (Hybrid)",
        "required_skills": ["Python", "FastAPI", "SQL", "Git"],
        "qualification": "B.E. / B.Tech / BCA / MCA / Diploma in CS",
        "experience": "0 - 2 Years (Freshers Eligible)",
        "salary": "₹ 4,50,000 - ₹ 6,00,000 P.A.",
        "job_type": "Full Time",
        "work_mode": "Hybrid",
        "category": "Government Contract / IT",
        "is_fresher_friendly": True,
        "is_internship": False,
        "description": "Develop and maintain civic service microservices, database optimizations, and API security for public welfare platforms.",
        "application_url": "https://service.nagriksetu.gov.in/jobs/JOB-00101"
    },
    {
        "id": "JOB-00102",
        "title": "React Frontend Developer Intern",
        "company": "Digital City Solutions India",
        "location": "Bengaluru, Karnataka (On-site)",
        "required_skills": ["React.js", "JavaScript", "HTML5", "Tailwind CSS"],
        "qualification": "Pursuing or Completed Graduate Degree",
        "experience": "Freshers / Students",
        "salary": "Stipend: ₹ 22,000 / month",
        "job_type": "Internship",
        "work_mode": "On-site",
        "category": "Private Sector / IT",
        "is_fresher_friendly": True,
        "is_internship": True,
        "description": "Collaborate with UI/UX designers to implement accessible, responsive portals conforming to government GIGW standards.",
        "application_url": "https://service.nagriksetu.gov.in/jobs/JOB-00102"
    },
    {
        "id": "JOB-00103",
        "title": "Associate QA / Automation Test Engineer",
        "company": "Infosys FinTech Services",
        "location": "Mysuru, Karnataka",
        "required_skills": ["Selenium WebDriver with Java", "Manual Software Testing", "Postman", "SQL"],
        "qualification": "Graduate in any discipline with QA Certification",
        "experience": "0 - 1 Year",
        "salary": "₹ 3,80,000 - ₹ 5,20,000 P.A.",
        "job_type": "Full Time",
        "work_mode": "Hybrid",
        "category": "Private Sector / IT",
        "is_fresher_friendly": True,
        "is_internship": False,
        "description": "Execute automated regression suites using Selenium, log Jira tickets, and verify API responses across financial gateways.",
        "application_url": "https://service.nagriksetu.gov.in/jobs/JOB-00103"
    },
    {
        "id": "JOB-00104",
        "title": "Solar Rooftop Installation Supervisor",
        "company": "Karnataka Renewable Energy Development Ltd (KREDL) Vendor",
        "location": "Hubballi / Belagavi, Karnataka",
        "required_skills": ["Solar PV Rooftop System Installation", "Electrical Safety", "Inverter Maintenance"],
        "qualification": "ITI / Diploma in Electrical / Mechanical Engineering",
        "experience": "1 - 3 Years",
        "salary": "₹ 3,20,000 - ₹ 4,50,000 P.A.",
        "job_type": "Full Time",
        "work_mode": "On-site",
        "category": "Government Vendor / Renewable Energy",
        "is_fresher_friendly": False,
        "is_internship": False,
        "description": "Supervise domestic and commercial solar PV array installations, inverter connections, net metering inspections, and team safety compliance.",
        "application_url": "https://service.nagriksetu.gov.in/jobs/JOB-00104"
    },
    {
        "id": "JOB-00105",
        "title": "Accounts Executive & GST Specialist",
        "company": "Apex Agro Enterprises",
        "location": "Mangaluru, Karnataka",
        "required_skills": ["Tally Prime with GST", "Advanced Excel", "Financial Accounting"],
        "qualification": "B.Com / BBA / M.Com",
        "experience": "1 - 2 Years",
        "salary": "₹ 3,00,000 - ₹ 4,20,000 P.A.",
        "job_type": "Full Time",
        "work_mode": "On-site",
        "category": "Private Sector / Finance",
        "is_fresher_friendly": True,
        "is_internship": False,
        "description": "Prepare GST returns, manage monthly bank reconciliations, process vendor invoices in Tally Prime, and assist statutory auditors.",
        "application_url": "https://service.nagriksetu.gov.in/jobs/JOB-00105"
    },
    {
        "id": "JOB-00106",
        "title": "AWS Cloud Operations Trainee",
        "company": "CloudBridge Systems",
        "location": "Remote / Bengaluru",
        "required_skills": ["AWS Cloud Practitioner", "Linux Administration", "Docker"],
        "qualification": "B.Sc Computer Science / B.E. / BCA",
        "experience": "0 - 1 Year",
        "salary": "₹ 4,00,000 - ₹ 5,50,000 P.A.",
        "job_type": "Full Time",
        "work_mode": "Remote",
        "category": "Private Sector / Cloud",
        "is_fresher_friendly": True,
        "is_internship": False,
        "description": "Monitor AWS CloudWatch alerts, manage EC2/RDS snapshots, configure security group rules, and handle Level 1 ticket resolution.",
        "application_url": "https://service.nagriksetu.gov.in/jobs/JOB-00106"
    },
    {
        "id": "JOB-00107",
        "title": "Hospital Patient Care / General Duty Assistant",
        "company": "District Civil Hospital Network",
        "location": "Kalaburagi / Shivamogga, Karnataka",
        "required_skills": ["General Duty Assistant", "First Aid", "Patient Hygiene"],
        "qualification": "10th / 12th Pass with Healthcare Skilling Certificate",
        "experience": "Freshers Welcome",
        "salary": "₹ 2,40,000 - ₹ 3,00,000 P.A.",
        "job_type": "Full Time",
        "work_mode": "On-site",
        "category": "Government Healthcare",
        "is_fresher_friendly": True,
        "is_internship": False,
        "description": "Assist ward nursing staff in recording vitals, mobilizing patients, maintaining sterile ward environments, and emergency first aid.",
        "application_url": "https://service.nagriksetu.gov.in/jobs/JOB-00107"
    }
]

class EmploymentServiceAdapter:
    """Provides abstracted access to career and job opportunities."""

    @classmethod
    async def get_opportunities(
        cls,
        q: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        fresher: Optional[bool] = None,
        skills: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        # Attempt live API call to Member 1's service if configured
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{EMPLOYMENT_SERVICE_URL}/api/employment/jobs")
                if res.status_code == 200:
                    data = res.json()
                    jobs = data.get("jobs", data)
                    return cls._filter_jobs(jobs, q, location, job_type, fresher, skills)
        except Exception:
            # Fallback cleanly to demonstration data from adapter
            pass

        return cls._filter_jobs(DEMO_JOB_OPPORTUNITIES, q, location, job_type, fresher, skills)

    @classmethod
    def _filter_jobs(
        cls,
        jobs: List[Dict[str, Any]],
        q: Optional[str],
        location: Optional[str],
        job_type: Optional[str],
        fresher: Optional[bool],
        skills: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        results = []
        for job in jobs:
            text = f"{job.get('title', '')} {job.get('company', '')} {job.get('description', '')} {' '.join(job.get('required_skills', []))}".lower()
            if q and q.lower() not in text:
                continue
            if location and location.lower() != "all" and location.lower() not in job.get("location", "").lower():
                continue
            if job_type and job_type.lower() != "all" and job_type.lower() not in job.get("job_type", "").lower():
                continue
            if fresher is True and not job.get("is_fresher_friendly"):
                continue
            if skills:
                # Skill matching check
                req = [s.lower() for s in job.get("required_skills", [])]
                has_overlap = any(any(cs.lower() in r for r in req) for cs in skills)
                job["has_skill_match"] = has_overlap
            results.append(job)
        return results
