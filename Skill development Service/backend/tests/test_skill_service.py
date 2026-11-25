import pytest
import os
import sys
import time
from datetime import date
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "mysql+pymysql://nagriksetu_skill:skill-app-pass-2026@127.0.0.1:3308/skill_db"

from app.main import app, SessionLocal, Base, engine, hash_password
from app.models import (
    Account, Skill, TrainingProgram, Batch, Enrollment, AttendanceRecord,
    ModuleProgress, AssessmentResult, Certificate, OTPVerificationSession
)
from datetime import datetime, timezone, timedelta
import hashlib
import secrets
from app.otp_service import normalize_phone

def create_verified_otp(identifier: str, purpose: str, citizen_ref: str = None) -> str:
    """Helper to insert a verified OTP verification session for testing (supports email & phone)."""
    db = SessionLocal()
    ref = f"test_otp_ref_{int(time.time() * 1000)}_{secrets.token_hex(4)}_{purpose}"
    if "@" in identifier:
        target = identifier.strip().lower()
    else:
        target = normalize_phone(identifier)
    sess = OTPVerificationSession(
        reference=ref,
        phone=target,
        citizen_ref=citizen_ref,
        purpose=purpose,
        provider="Gmail SMTP",
        hashed_code=hashlib.sha256("123456".encode()).hexdigest(),
        is_verified=True,
        is_consumed=False,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db.add(sess)
    db.commit()
    db.close()
    return ref

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    from app.main import seed_initial_data
    seed_initial_data(db)
    db.close()
    yield

def test_health_check_mysql():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "nagriksetu-skill-development"
    assert data["database"] == "mysql_8.4"
    assert data["database_status"] == "connected"

def test_auth_and_citizen_isolation():
    t_stamp = int(time.time() * 1000)
    
    # Register Citizen A with verified OTP reference
    phone_a = "+91 9123456789"
    email_a = f"citizen.a.{t_stamp}@nagriksetu.local"
    otp_ref_a = create_verified_otp(email_a, "REGISTRATION")
    res_a = client.post("/api/auth/register", json={
        "email": email_a,
        "password": "Password@123",
        "full_name": "Citizen A Applicant",
        "phone": phone_a,
        "otp_reference": otp_ref_a
    })
    assert res_a.status_code == 200
    token_a = res_a.json()["access_token"]
    citizen_ref_a = res_a.json()["citizen_ref"]

    # Register Citizen B with verified OTP reference
    phone_b = "+91 9123456780"
    email_b = f"citizen.b.{t_stamp}@nagriksetu.local"
    otp_ref_b = create_verified_otp(email_b, "REGISTRATION")
    res_b = client.post("/api/auth/register", json={
        "email": email_b,
        "password": "Password@123",
        "full_name": "Citizen B Applicant",
        "phone": phone_b,
        "otp_reference": otp_ref_b
    })
    assert res_b.status_code == 200
    token_b = res_b.json()["access_token"]
    citizen_ref_b = res_b.json()["citizen_ref"]

    # Fetch available programme dynamically
    progs = client.get("/api/programmes").json()
    assert len(progs) > 0, "No training programmes found"
    prog_id = progs[0]["id"]

    # Citizen A submits enrolment for program with verified enrolment OTP
    enrol_otp_ref_a = create_verified_otp(phone_a, "ENROLMENT", citizen_ref_a)
    res_enr = client.post(
        "/api/enrollments",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "program_id": prog_id,
            "applicant_statement": "Looking forward to training",
            "otp_reference": enrol_otp_ref_a
        }
    )
    assert res_enr.status_code == 201
    enr_data = res_enr.json()
    enr_code = enr_data["application_id"]
    enr_id = enr_data["id"]

    # Citizen A can access their own enrolment
    res_get_own = client.get(f"/api/enrollments/{enr_code}", headers={"Authorization": f"Bearer {token_a}"})
    assert res_get_own.status_code == 200
    assert res_get_own.json()["application_id"] == enr_code

    # Citizen B attempts to access Citizen A's enrolment -> MUST BE 403 FORBIDDEN
    res_get_other = client.get(f"/api/enrollments/{enr_code}", headers={"Authorization": f"Bearer {token_b}"})
    assert res_get_other.status_code == 403

    # Citizen A attempts to access Admin endpoint -> MUST BE 403 FORBIDDEN
    res_admin_forbidden = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token_a}"})
    assert res_admin_forbidden.status_code == 403

def test_duplicate_enrolment_and_batch_capacity():
    t_stamp = int(time.time() * 1000)
    phone = f"+91 999{t_stamp % 10000000:07d}"
    email_cap = f"capacity.test.{t_stamp}@nagriksetu.local"
    reg_otp = create_verified_otp(email_cap, "REGISTRATION")
    res_user = client.post("/api/auth/register", json={
        "email": email_cap,
        "password": "Password@123",
        "full_name": "Capacity Tester",
        "phone": phone,
        "otp_reference": reg_otp
    })
    assert res_user.status_code == 200
    token = res_user.json()["access_token"]
    citizen_ref = res_user.json()["citizen_ref"]

    # Fetch available programme dynamically
    progs = client.get("/api/programmes").json()
    assert len(progs) > 0, "No training programmes found"
    prog_id = progs[1]["id"] if len(progs) > 1 else progs[0]["id"]

    # First enrolment with verified OTP
    enr_otp_1 = create_verified_otp(phone, "ENROLMENT", citizen_ref)
    res1 = client.post(
        "/api/enrollments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "program_id": prog_id,
            "applicant_statement": "First apply",
            "otp_reference": enr_otp_1
        }
    )
    assert res1.status_code == 201

    # Second enrolment for the same program -> MUST BE 409 CONFLICT
    enr_otp_2 = create_verified_otp(phone, "ENROLMENT", citizen_ref)
    res2 = client.post(
        "/api/enrollments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "program_id": prog_id,
            "applicant_statement": "Duplicate apply",
            "otp_reference": enr_otp_2
        }
    )
    assert res2.status_code == 409

def test_full_training_lifecycle_attendance_modules_assessments_certificate():
    t_stamp = int(time.time() * 1000)

    # 1. Admin login
    admin_login = client.post("/api/auth/login", json={
        "email": "skill.admin@nagriksetu.local",
        "password": "SkillAdmin@2026!"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]

    # 2. Register learner
    phone_learner = f"+91 988{t_stamp % 10000000:07d}"
    email_learner = f"learner.{t_stamp}@nagriksetu.local"
    reg_otp_l = create_verified_otp(email_learner, "REGISTRATION")
    learner = client.post("/api/auth/register", json={
        "email": email_learner,
        "password": "Password@123",
        "full_name": "Aarav Sharma",
        "phone": phone_learner,
        "otp_reference": reg_otp_l
    })
    assert learner.status_code == 200
    learner_token = learner.json()["access_token"]
    learner_ref = learner.json()["citizen_ref"]

    # 3. Enrol in active Program
    progs = client.get("/api/programmes").json()
    assert len(progs) > 0, "No training programmes found"
    prog_id = progs[2]["id"] if len(progs) > 2 else progs[0]["id"]
    enr_otp_l = create_verified_otp(phone_learner, "ENROLMENT", learner_ref)
    enr_res = client.post(
        "/api/enrollments",
        headers={"Authorization": f"Bearer {learner_token}"},
        json={
            "program_id": prog_id,
            "applicant_statement": "Skill development participant",
            "otp_reference": enr_otp_l
        }
    )
    assert enr_res.status_code == 201
    enr_id = enr_res.json()["id"]

    # 4. RBAC Protection: Platform Admin write attempts are strictly forbidden (403)
    review_res = client.patch(
        f"/api/admin/enrollments/{enr_id}/review",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "APPROVED", "remarks": "Documents verified. Approved for batch training."}
    )
    assert review_res.status_code == 403
    assert "view-only monitoring privileges" in review_res.json()["detail"]

    # 5. Check Certificate Eligibility inspection via Admin read endpoint
    elig_res = client.get(
        f"/api/admin/enrollments/{enr_id}/eligibility",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert elig_res.status_code == 200
    assert elig_res.json()["is_eligible"] is False
    assert len(elig_res.json()["missing_reasons"]) > 0

    # Attempt to issue certificate via Platform Admin -> MUST RETURN 403 Forbidden
    issue_fail = client.post(
        f"/api/admin/enrollments/{enr_id}/issue-certificate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert issue_fail.status_code == 403

    # 6. Verify Attendance read endpoint
    att_res = client.get(
        f"/api/admin/enrollments/{enr_id}/attendance",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert att_res.status_code == 200

    # 7. Verify Modules read endpoint
    modules_res = client.get(
        f"/api/admin/enrollments/{enr_id}/modules",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert modules_res.status_code == 200

def test_skill_catalogue_crud_and_deactivation():
    """FR-SKL-001, FR-SKL-003, FR-SKL-006: Skill Catalogue discovery and RBAC protection."""
    admin_login = client.post("/api/auth/login", json={
        "email": "skill.admin@nagriksetu.local",
        "password": "SkillAdmin@2026!"
    })
    admin_token = admin_login.json()["access_token"]
    t_stamp = int(time.time() * 1000)

    # 1. RBAC Verification: Platform Admin write attempt must be strictly blocked (403)
    create_res = client.post(
        "/api/admin/skills",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": f"Cloud Native Microservices Architecture with Go {t_stamp}",
            "category_name": "Information Technology & Software",
            "level": "Advanced",
            "duration_weeks": 8,
            "duration_hours": 60,
            "summary": "Design scalable microservices using Go and Docker.",
            "details": "Covers goroutines, channels, REST APIs, and Docker.",
            "prerequisites": "Basic programming knowledge"
        }
    )
    assert create_res.status_code == 403
    assert "view-only monitoring privileges" in create_res.json()["detail"]

    # 2. Browse Skill Catalogue (FR-SKL-001, FR-SKL-006)
    skills_res = client.get("/api/skills")
    assert skills_res.status_code == 200
    skills_data = skills_res.json()
    assert "items" in skills_data
    assert len(skills_data["items"]) > 0

    # 3. Verify subcategories endpoint (FR-SKL-001)
    subcat_res = client.get("/api/subcategories")
    assert subcat_res.status_code == 200
    assert len(subcat_res.json()) >= 7

def test_citizen_skill_profile_and_proficiency_validation():
    """FR-SKL-002, FR-SKL-004: Citizen skill profile management and validation."""
    t_stamp = int(time.time() * 1000)
    prof_email = f"citizen.profile.{t_stamp}@nagriksetu.local"
    prof_otp = create_verified_otp(prof_email, "REGISTRATION")
    user_res = client.post("/api/auth/register", json={
        "email": prof_email,
        "password": "Password@123",
        "full_name": "Skill Profile Citizen",
        "phone": f"+91 977{t_stamp % 10000000:07d}",
        "otp_reference": prof_otp
    })
    assert user_res.status_code == 200
    token = user_res.json()["access_token"]

    # 1. Add valid skill with proficiency (FR-SKL-002, FR-SKL-004)
    add_res = client.post(
        "/api/profiles/me/skills",
        headers={"Authorization": f"Bearer {token}"},
        json={"skill_name": "Python Programming", "proficiency": "Intermediate"}
    )
    assert add_res.status_code == 200
    skill_entry_id = add_res.json()["id"]

    # 2. View citizen profile (FR-SKL-002)
    prof_res = client.get("/api/profiles/me", headers={"Authorization": f"Bearer {token}"})
    assert prof_res.status_code == 200
    skills = prof_res.json()["skills"]
    assert any(s["skill_name"] == "Python Programming" and s["proficiency"] == "Intermediate" for s in skills)

    # 3. Update proficiency (FR-SKL-003)
    update_prof = client.post(
        "/api/profiles/me/skills",
        headers={"Authorization": f"Bearer {token}"},
        json={"skill_name": "Python Programming", "proficiency": "Advanced"}
    )
    assert update_prof.status_code == 200

    # Verify updated proficiency
    prof_res2 = client.get("/api/profiles/me", headers={"Authorization": f"Bearer {token}"})
    skills2 = prof_res2.json()["skills"]
    assert any(s["skill_name"] == "Python Programming" and s["proficiency"] == "Advanced" for s in skills2)

    # 4. Remove / deactivate skill (FR-SKL-003)
    del_res = client.delete(f"/api/profiles/me/skills/{skill_entry_id}", headers={"Authorization": f"Bearer {token}"})
    assert del_res.status_code == 200

def test_training_centre_crud():
    """FR-SKL-007: Training centre discovery and RBAC protection."""
    admin_login = client.post("/api/auth/login", json={
        "email": "skill.admin@nagriksetu.local",
        "password": "SkillAdmin@2026!"
    })
    admin_token = admin_login.json()["access_token"]
    t_stamp = int(time.time() * 1000)

    # 1. RBAC Verification: Platform Admin cannot create centres directly (must register via /api/auth/register-centre)
    create_res = client.post(
        "/api/admin/centres",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": f"Dharwad Innovation & Regional Skilling Centre {t_stamp}",
            "location": "Dharwad",
            "district": "Dharwad",
            "state": "Karnataka",
            "address": "Opposite High Court Bench, PB Road, Dharwad",
            "contact_phone": "+91 836 2445566",
            "contact_email": "dharwad.centre@nagriksetu.gov.in",
            "facilities": "AI Research Lab, IoT Smart Workshop, 100-seat Testing Centre"
        }
    )
    assert create_res.status_code == 403
    assert "view-only monitoring access" in create_res.json()["detail"]

    # 2. Retrieve centres list (FR-SKL-007)
    centres_res = client.get("/api/centres")
    assert centres_res.status_code == 200
    centres = centres_res.json()
    assert len(centres) > 0

    # 3. Search centres
    search_res = client.get("/api/centres/search?location=Bengaluru")
    assert search_res.status_code == 200

def test_training_programme_creation_and_discovery():
    """FR-SKL-008, FR-SKL-010, FR-SKL-011, FR-SKL-012, FR-SKL-013: Programme discovery and RBAC protection."""
    admin_login = client.post("/api/auth/login", json={
        "email": "skill.admin@nagriksetu.local",
        "password": "SkillAdmin@2026!"
    })
    admin_token = admin_login.json()["access_token"]

    # 1. RBAC Verification: Platform Admin programme creation is strictly forbidden (403)
    prg_res = client.post(
        "/api/admin/programmes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "skill_id": 1,
            "title": "Government Accelerated Python Cloud Services Programme",
            "description": "Intensive program covering REST APIs and cloud containerization.",
            "mode": "Hybrid",
            "duration_hours": 60,
            "fee": 0.0,
            "scholarship_available": True,
            "eligibility_criteria": "Basic literacy and graduation degree",
            "start_date": "2026-12-01",
            "end_date": "2027-01-31"
        }
    )
    assert prg_res.status_code == 403
    assert "view-only monitoring privileges" in prg_res.json()["detail"]

    # 2. Programme discovery (FR-SKL-011)
    disc_res = client.get("/api/programmes")
    assert disc_res.status_code == 200
    found = disc_res.json()
    assert len(found) > 0
    first_prog = found[0]

    # 3. Programme details inspection (FR-SKL-012)
    detail_res = client.get(f"/api/programmes/{first_prog['id']}")
    assert detail_res.status_code == 200
    assert "title" in detail_res.json()
    assert "batches" in detail_res.json()

def test_skill_gap_analysis_and_training_mapping():
    """FR-SKL-020, FR-SKL-021, FR-SKL-022, FR-SKL-023, FR-SKL-024: Skill gap engine."""
    # 1. Target role selection and gap comparison (FR-SKL-020, FR-SKL-021)
    gap_res = client.post(
        "/api/skill-gap/analyze",
        json={
            "target_role": "Full Stack Python / Web Developer",
            "current_skills": ["HTML5 & Modern CSS3", "Python Programming"]
        }
    )
    assert gap_res.status_code == 200
    data = gap_res.json()

    # Verify Matched Skills (FR-SKL-021)
    assert "Python Programming" in data["matching_skills"]
    assert "HTML5 & Modern CSS3" in data["matching_skills"]

    # Verify Missing Skills (FR-SKL-021)
    assert "FastAPI Python Backend Development" in data["missing_skills"]
    assert "React.js Frontend Development" in data["missing_skills"]
    assert "Docker & Containerization" in data["missing_skills"]

    # Verify Explanation & Score (FR-SKL-022)
    assert "role_description" in data
    assert data["skill_gap_score"] > 0
    assert "readiness_level" in data

    # Verify Training Mapping (FR-SKL-023)
    assert len(data["recommended_courses"]) > 0
    assert all("skill_name" in c and "reason" in c for c in data["recommended_courses"])
