import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole, UserStatus
from app.models.citizen import CitizenProfile, ProfileStatus
from app.models.household import Household
from app.core.security import hash_password, create_access_token

# Isolated SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    user = User(
        email="test_admin@civicportal.gov",
        password_hash=hash_password("AdminPass123!@#"),
        role=UserRole.ADMIN.value,
        account_status=UserStatus.ACTIVE.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    return create_access_token({"sub": str(admin_user.id), "role": admin_user.role})


@pytest.fixture
def citizen_user(db_session):
    user = User(
        email="citizen1@example.com",
        password_hash=hash_password("CitizenPass123!@"),
        role=UserRole.CITIZEN.value,
        account_status=UserStatus.ACTIVE.value,
    )
    db_session.add(user)
    db_session.flush()

    profile = CitizenProfile(
        user_id=user.id,
        citizen_code="CIT-TEST0001",
        full_name="Citizen One",
        date_of_birth=date(1990, 1, 1),
        phone_number="+91 99999 11111",
        preferred_language="en",
        profile_status=ProfileStatus.ACTIVE.value,
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def citizen_token(citizen_user):
    return create_access_token({"sub": str(citizen_user.id), "role": citizen_user.role})


@pytest.fixture
def second_citizen_user(db_session):
    user = User(
        email="citizen2@example.com",
        password_hash=hash_password("CitizenPass123!@"),
        role=UserRole.CITIZEN.value,
        account_status=UserStatus.ACTIVE.value,
    )
    db_session.add(user)
    db_session.flush()

    profile = CitizenProfile(
        user_id=user.id,
        citizen_code="CIT-TEST0002",
        full_name="Citizen Two",
        date_of_birth=date(1995, 5, 5),
        phone_number="+91 99999 22222",
        preferred_language="hi",
        profile_status=ProfileStatus.ACTIVE.value,
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_household(db_session):
    hh = Household(
        household_code="HHD-TEST0001",
        address_line="100 Test St",
        locality="Test Nagar",
        city="Bengaluru",
        state="Karnataka",
        postal_code="560001",
        administrative_notes="Secret notes for admin eyes only"
    )
    db_session.add(hh)
    db_session.commit()
    db_session.refresh(hh)
    return hh
