import pytest
from app.models.user import User, UserRole, UserStatus
from app.models.household import Household, HouseholdMembership
from app.models.citizen import CitizenProfile, ProfileStatus
from app.models.records import EducationRecord
from datetime import date


def test_federated_verify_success(client, citizen_user):
    payload = {
        "identifier": citizen_user.email,
        "password": "CitizenPass123!@"
    }
    response = client.post("/api/v1/auth/federated-verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["email"] == citizen_user.email
    assert data["role"] == "citizen"
    assert "user_code" in data
    assert data["user_code"].startswith("USR-")
    assert data["citizen_code"].startswith("CIT-")
    assert "children" in data


def test_federated_verify_invalid_password(client, citizen_user):
    payload = {
        "identifier": citizen_user.email,
        "password": "WrongPassword!@"
    }
    response = client.post("/api/v1/auth/federated-verify", json=payload)
    assert response.status_code == 401


def test_household_children_endpoint(client, db_session, citizen_user, test_household):
    # Link citizen_user to test_household
    profile = citizen_user.citizen_profile
    profile.household_id = test_household.id
    
    # Add a child to the household
    child_profile = CitizenProfile(
        citizen_code="CIT-TESTCHILD01",
        full_name="Baby Citizen",
        date_of_birth=date(2019, 1, 1),
        phone_number=profile.phone_number,
        preferred_language="en",
        profile_status=ProfileStatus.ACTIVE.value,
        household_id=test_household.id,
        household_relationship="Daughter",
        household_role="MEMBER"
    )
    db_session.add(child_profile)
    db_session.flush()

    membership = HouseholdMembership(
        household_id=test_household.id,
        citizen_id=child_profile.id,
        relationship_type="Daughter",
        status="active"
    )
    db_session.add(membership)

    edu = EducationRecord(
        citizen_id=child_profile.id,
        highest_qualification="Primary",
        institution_name="Government Model School",
        student_id="SCH01125",
        permanent_student_id="NS-FB8336A812DE468FB8E475443CF673EB"
    )
    db_session.add(edu)
    db_session.commit()

    response = client.get(f"/api/v1/citizens/household-children?email={citizen_user.email}")
    assert response.status_code == 200
    data = response.json()
    assert data["household_id"] == test_household.id
    assert len(data["children"]) == 1
    assert data["children"][0]["full_name"] == "Baby Citizen"
    assert data["children"][0]["student_id"] == "SCH01125"
    assert data["children"][0]["permanent_student_id"] == "NS-FB8336A812DE468FB8E475443CF673EB"

