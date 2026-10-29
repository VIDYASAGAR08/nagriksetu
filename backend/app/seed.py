"""
Demonstration Database Seed Script for NagrikSetu
Creates administrative hierarchy, fictitious citizens, households, and memberships for university evaluation.
Usage:
    python -m app.seed [--reset]
"""

import sys
from datetime import date
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole, UserStatus
from app.models.household import Household, HouseholdMembership, MembershipStatus
from app.models.citizen import CitizenProfile, ProfileStatus
from app.models.hierarchy import AdministrativeUnit, AdministrativeUnitType, AdministrativeUnitStatus
from app.models.event import OutboxEvent
from app.models.audit import AuditLog
from app.core.security import hash_password
from app.config import settings


def seed_data(reset: bool = False):
    print("=" * 60)
    print("NagrikSetu Administrative Service - Database Seeder")
    print("=" * 60)

    if reset:
        print("⚠️ Reset requested. Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("Creating fresh schema...")
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Administrative Hierarchy (FR-ADM-001)
        hierarchy_data = [
            {
                "identifier": "IN",
                "name": "India (National Republic)",
                "unit_type": AdministrativeUnitType.COUNTRY.value,
                "parent_id": None,
                "status": AdministrativeUnitStatus.ACTIVE.value,
            },
            {
                "identifier": "IN-KA",
                "name": "Karnataka",
                "unit_type": AdministrativeUnitType.STATE.value,
                "parent_code": "IN",
                "status": AdministrativeUnitStatus.ACTIVE.value,
            },
            {
                "identifier": "IN-MH",
                "name": "Maharashtra",
                "unit_type": AdministrativeUnitType.STATE.value,
                "parent_code": "IN",
                "status": AdministrativeUnitStatus.ACTIVE.value,
            },
            {
                "identifier": "IN-KA-BLR",
                "name": "Bengaluru Urban",
                "unit_type": AdministrativeUnitType.DISTRICT.value,
                "parent_code": "IN-KA",
                "status": AdministrativeUnitStatus.ACTIVE.value,
            },
            {
                "identifier": "IN-MH-MUM",
                "name": "Mumbai City",
                "unit_type": AdministrativeUnitType.DISTRICT.value,
                "parent_code": "IN-MH",
                "status": AdministrativeUnitStatus.ACTIVE.value,
            },
            {
                "identifier": "IN-KA-BLR-W150",
                "name": "Ward 150 - Bellandur",
                "unit_type": AdministrativeUnitType.WARD.value,
                "parent_code": "IN-KA-BLR",
                "status": AdministrativeUnitStatus.ACTIVE.value,
            },
        ]

        saved_units = {}
        for u in hierarchy_data:
            existing = db.query(AdministrativeUnit).filter(AdministrativeUnit.identifier == u["identifier"]).first()
            if not existing:
                parent_id = None
                if "parent_code" in u and u["parent_code"] in saved_units:
                    parent_id = saved_units[u["parent_code"]].id
                elif "parent_id" in u:
                    parent_id = u["parent_id"]

                print(f"Creating Administrative Unit: {u['name']} ({u['identifier']})")
                unit = AdministrativeUnit(
                    identifier=u["identifier"],
                    name=u["name"],
                    unit_type=u["unit_type"],
                    parent_id=parent_id,
                    status=u["status"],
                )
                db.add(unit)
                db.flush()
                saved_units[u["identifier"]] = unit
            else:
                saved_units[u["identifier"]] = existing

        # 2. Administrator Accounts (National & Scoped)
        # Root National Admin
        admin_email = settings.INITIAL_ADMIN_EMAIL.strip().lower()
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            print(f"Creating National Administrator: {admin_email}")
            admin = User(
                email=admin_email,
                password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                role=UserRole.ADMIN.value,
                account_status=UserStatus.ACTIVE.value,
                administrative_unit_id=None,  # National unrestricted scope
            )
            db.add(admin)
            db.flush()

        # Scoped Regional Administrator (FR-ADM-021)
        scoped_email = "admin.bengaluru@nagriksetu.gov.in"
        scoped_admin = db.query(User).filter(User.email == scoped_email).first()
        if not scoped_admin and "IN-KA-BLR" in saved_units:
            print(f"Creating Scoped District Administrator: {scoped_email} (Bengaluru Urban)")
            scoped_admin = User(
                email=scoped_email,
                password_hash=hash_password("AdminPass123!@#"),
                role=UserRole.ADMIN.value,
                account_status=UserStatus.ACTIVE.value,
                administrative_unit_id=saved_units["IN-KA-BLR"].id,  # Scoped to Bengaluru Urban
            )
            db.add(scoped_admin)
            db.flush()

        # 3. Seed Households with Area Mappings (FR-ADM-014)
        households_data = [
            {
                "household_code": "HHD-1001-BLR",
                "address_line": "Flat 402, Green Glen Residency, Outer Ring Road",
                "locality": "Bellandur",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560103",
                "administrative_unit_code": "IN-KA-BLR-W150",
                "administrative_notes": "Verified municipal address during 2026 census review."
            },
            {
                "household_code": "HHD-1002-BLR",
                "address_line": "12/A, 3rd Cross, Indiranagar 1st Stage",
                "locality": "Indiranagar",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560038",
                "administrative_unit_code": "IN-KA-BLR",
                "administrative_notes": "Pending updated water connection verification."
            },
            {
                "household_code": "HHD-2001-MUM",
                "address_line": "B-201, Sunshine Heights, Swami Vivekananda Road",
                "locality": "Bandra West",
                "city": "Mumbai",
                "state": "Maharashtra",
                "postal_code": "400050",
                "administrative_unit_code": "IN-MH-MUM",
                "administrative_notes": "Legacy household profile from municipal records."
            }
        ]

        saved_households = {}
        for h_data in households_data:
            existing = db.query(Household).filter(Household.household_code == h_data["household_code"]).first()
            area_id = None
            if h_data.get("administrative_unit_code") in saved_units:
                area_id = saved_units[h_data["administrative_unit_code"]].id

            if not existing:
                print(f"Creating Household: {h_data['household_code']} in {h_data['city']}")
                hh = Household(
                    household_code=h_data["household_code"],
                    address_line=h_data["address_line"],
                    locality=h_data["locality"],
                    city=h_data["city"],
                    state=h_data["state"],
                    postal_code=h_data["postal_code"],
                    administrative_notes=h_data["administrative_notes"],
                    administrative_unit_id=area_id,
                )
                db.add(hh)
                db.flush()
                saved_households[h_data["household_code"]] = hh
            else:
                if not existing.administrative_unit_id and area_id:
                    existing.administrative_unit_id = area_id
                saved_households[h_data["household_code"]] = existing

        # 4. Seed Citizens with Memberships (FR-ADM-006 & FR-ADM-015)
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
                "household_relationship": "Head of Household",
                "administrative_unit_code": "IN-KA-BLR-W150",
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
                "household_relationship": "Spouse",
                "administrative_unit_code": "IN-KA-BLR-W150",
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
                "household_relationship": "Head of Household",
                "administrative_unit_code": "IN-KA-BLR",
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
                "household_relationship": "Member",
                "administrative_unit_code": "IN-MH-MUM",
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
                "household_relationship": None,
                "administrative_unit_code": "IN-MH-MUM",
            }
        ]

        for c_data in citizens_seed:
            existing_user = db.query(User).filter(User.email == c_data["email"]).first()
            area_id = saved_units.get(c_data["administrative_unit_code"]).id if c_data.get("administrative_unit_code") in saved_units else None

            if not existing_user:
                print(f"Creating Citizen User: {c_data['email']}")
                user = User(
                    email=c_data["email"],
                    password_hash=c_data["password_hash"],
                    role=UserRole.CITIZEN.value,
                    account_status=UserStatus.ACTIVE.value,
                    administrative_unit_id=area_id,
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
                    administrative_unit_id=area_id,
                )
                db.add(profile)
                db.flush()

                # Seed Membership History record (FR-ADM-016)
                if hh_id:
                    mem = HouseholdMembership(
                        household_id=hh_id,
                        citizen_id=profile.id,
                        relationship_type=c_data["household_relationship"] or "Member",
                        start_date=date(2025, 1, 1),
                        status=MembershipStatus.ACTIVE.value,
                        notes="Initial census verification registration"
                    )
                    db.add(mem)

        # 5. Commit all changes
        db.commit()
        print("✅ Database seeding completed successfully.")
        print(f"   National Admin : {admin_email} / {settings.INITIAL_ADMIN_PASSWORD}")
        print("   Scoped Admin   : admin.bengaluru@nagriksetu.gov.in / AdminPass123!@# (Bengaluru Urban)")
        print("   Demo Citizen   : aarav.sharma@example.com / CitizenPass123!@")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    should_reset = "--reset" in sys.argv
    seed_data(reset=should_reset)
