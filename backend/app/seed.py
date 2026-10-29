"""
Demonstration Database Seed Script
Creates fictitious citizens, households, and relationships for university evaluation.
Usage:
    python -m app.seed [--reset]
"""

import sys
from datetime import date
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole, UserStatus
from app.models.household import Household
from app.models.citizen import CitizenProfile, ProfileStatus
from app.models.audit import AuditLog
from app.core.security import hash_password
from app.config import settings


def seed_data(reset: bool = False):
    print("=" * 60)
    print("CivicAdmin Administrative Service - Database Seeder")
    print("=" * 60)

    if reset:
        print("⚠️ Reset requested. Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("Creating fresh schema...")
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Administrator Account
        admin_email = settings.INITIAL_ADMIN_EMAIL.strip().lower()
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            print(f"Creating Development Admin: {admin_email}")
            admin = User(
                email=admin_email,
                password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                role=UserRole.ADMIN.value,
                account_status=UserStatus.ACTIVE.value
            )
            db.add(admin)
            db.flush()
        else:
            print(f"Admin account ({admin_email}) already present.")

        # 2. Seed Fictitious Households
        households_data = [
            {
                "household_code": "HHD-1001-BLR",
                "address_line": "Flat 402, Green Glen Residency, Outer Ring Road",
                "locality": "Bellandur",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560103",
                "administrative_notes": "Verified municipal address during 2026 census review."
            },
            {
                "household_code": "HHD-1002-BLR",
                "address_line": "12/A, 3rd Cross, Indiranagar 1st Stage",
                "locality": "Indiranagar",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560038",
                "administrative_notes": "Pending updated water connection verification."
            },
            {
                "household_code": "HHD-2001-MUM",
                "address_line": "B-201, Sunshine Heights, Swami Vivekananda Road",
                "locality": "Bandra West",
                "city": "Mumbai",
                "state": "Maharashtra",
                "postal_code": "400050",
                "administrative_notes": "Legacy household profile from municipal records."
            }
        ]

        saved_households = {}
        for h_data in households_data:
            existing = db.query(Household).filter(Household.household_code == h_data["household_code"]).first()
            if not existing:
                print(f"Creating Household: {h_data['household_code']} in {h_data['city']}")
                hh = Household(**h_data)
                db.add(hh)
                db.flush()
                saved_households[h_data["household_code"]] = hh
            else:
                saved_households[h_data["household_code"]] = existing

        # 3. Seed Citizens (with accounts and demo credentials)
        # Demo Citizen Password: "CitizenPass123!@"
        demo_pwd_hash = hash_password("CitizenPass123!@")

        citizens_seed = [
            {
                "email": "aarav.sharma@example.com",
                "password_hash": demo_pwd_hash,
                "full_name": "Aarav Sharma",
                "citizen_code": "CIT-88219011",
                "date_of_birth": date(1991, 5, 14),
                "phone_number": "+91 98765 43210",
                "preferred_language": "en",
                "profile_status": ProfileStatus.ACTIVE.value,
                "household_code": "HHD-1001-BLR",
                "household_relationship": "Head of Household"
            },
            {
                "email": "priya.sharma@example.com",
                "password_hash": demo_pwd_hash,
                "full_name": "Priya Sharma",
                "citizen_code": "CIT-88219012",
                "date_of_birth": date(1993, 8, 22),
                "phone_number": "+91 98765 43211",
                "preferred_language": "en",
                "profile_status": ProfileStatus.ACTIVE.value,
                "household_code": "HHD-1001-BLR",
                "household_relationship": "Spouse"
            },
            {
                "email": "rohit.verma@example.com",
                "password_hash": demo_pwd_hash,
                "full_name": "Rohit Verma",
                "citizen_code": "CIT-77310045",
                "date_of_birth": date(1985, 11, 3),
                "phone_number": "+91 91234 56789",
                "preferred_language": "hi",
                "profile_status": ProfileStatus.PENDING_REVIEW.value,
                "household_code": "HHD-1002-BLR",
                "household_relationship": "Head of Household"
            },
            {
                "email": "ananya.patil@example.com",
                "password_hash": demo_pwd_hash,
                "full_name": "Ananya Patil",
                "citizen_code": "CIT-66421190",
                "date_of_birth": date(1998, 2, 17),
                "phone_number": "+91 99887 76655",
                "preferred_language": "mr",
                "profile_status": ProfileStatus.PENDING_REVIEW.value,
                "household_code": "HHD-2001-MUM",
                "household_relationship": "Member"
            },
            {
                "email": "kavita.deshmukh@example.com",
                "password_hash": demo_pwd_hash,
                "full_name": "Kavita Deshmukh",
                "citizen_code": "CIT-55109923",
                "date_of_birth": date(1974, 12, 30),
                "phone_number": "+91 97654 32109",
                "preferred_language": "en",
                "profile_status": ProfileStatus.ACTIVE.value,
                "household_code": None,
                "household_relationship": None
            }
        ]

        for c_data in citizens_seed:
            existing_user = db.query(User).filter(User.email == c_data["email"]).first()
            if not existing_user:
                print(f"Creating Citizen User: {c_data['email']}")
                user = User(
                    email=c_data["email"],
                    password_hash=c_data["password_hash"],
                    role=UserRole.CITIZEN.value,
                    account_status=UserStatus.ACTIVE.value
                )
                db.add(user)
                db.flush()

                hh_id = None
                if c_data["household_code"] and c_data["household_code"] in saved_households:
                    hh_id = saved_households[c_data["household_code"]].id

                profile = CitizenProfile(
                    user_id=user.id,
                    citizen_code=c_data["citizen_code"],
                    full_name=c_data["full_name"],
                    date_of_birth=c_data["date_of_birth"],
                    phone_number=c_data["phone_number"],
                    preferred_language=c_data["preferred_language"],
                    profile_status=c_data["profile_status"],
                    household_id=hh_id,
                    household_relationship=c_data["household_relationship"],
                )
                db.add(profile)
                print(f"  -> Linked profile: {profile.citizen_code} ({profile.full_name})")
            else:
                print(f"Citizen account {c_data['email']} already exists.")

        # 4. Initial Audit Log
        if not db.query(AuditLog).first():
            audit = AuditLog(
                actor_id=admin.id,
                actor_email=admin.email,
                action="SYSTEM_INIT_SEED",
                resource_type="system",
                resource_id="initialization",
                details='{"message": "Synthetic demonstration dataset initialized."}'
            )
            db.add(audit)

        db.commit()
        print("\n✅ Seed completed successfully!")
        print("\nDemo Accounts for Evaluation:")
        print("  Administrator:")
        print(f"    Email:    {settings.INITIAL_ADMIN_EMAIL}")
        print(f"    Password: {settings.INITIAL_ADMIN_PASSWORD}")
        print("  Citizen 1 (Active, Bellandur Household):")
        print("    Email:    aarav.sharma@example.com")
        print("    Password: CitizenPass123!@")
        print("  Citizen 2 (Pending Review, Indiranagar Household):")
        print("    Email:    rohit.verma@example.com")
        print("    Password: CitizenPass123!@")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error during seed: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    reset_db = "--reset" in sys.argv
    seed_data(reset=reset_db)
