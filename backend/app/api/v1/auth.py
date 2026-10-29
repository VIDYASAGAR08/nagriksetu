import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
)
from app.models.user import User, UserRole, UserStatus
from app.models.citizen import CitizenProfile, ProfileStatus
from app.schemas.auth import (
    CitizenRegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    AuthMeResponse,
)
from app.schemas.citizen import CitizenProfileResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def generate_citizen_code() -> str:
    """Generate a clean, unique citizen identifier."""
    return f"CIT-{uuid.uuid4().hex[:8].upper()}"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_citizen(
    payload: CitizenRegisterRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Public citizen registration.
    - Public registrations are ALWAYS assigned the 'citizen' role.
    - Role escalation is strictly prevented.
    - Password complexity is enforced.
    - An atomic user account and linked citizen profile are created.
    """
    # 1. Validate password confirmation
    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password and confirmation password do not match."
        )

    # 2. Check password complexity policy
    strength_error = validate_password_strength(payload.password)
    if strength_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strength_error
        )

    # 3. Check for duplicate email
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists."
        )

    # 4. Hash password with Argon2
    hashed_pwd = hash_password(payload.password)

    # 5. Create user record strictly with 'citizen' role
    new_user = User(
        email=payload.email,
        password_hash=hashed_pwd,
        role=UserRole.CITIZEN.value,
        account_status=UserStatus.ACTIVE.value,
    )
    db.add(new_user)
    db.flush()  # Flush to obtain new_user.id

    # 6. Create initial citizen profile linked to the user
    citizen_code = generate_citizen_code()
    # Ensure citizen code is unique
    while db.query(CitizenProfile).filter(CitizenProfile.citizen_code == citizen_code).first():
        citizen_code = generate_citizen_code()

    new_profile = CitizenProfile(
        user_id=new_user.id,
        citizen_code=citizen_code,
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        preferred_language=payload.preferred_language or "en",
        profile_status=ProfileStatus.PENDING_REVIEW.value,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_user)

    # 7. Issue signed authentication token
    token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})

    # Set secure HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production"
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticate user credentials (citizen or administrator).
    Issues JWT bearer token and sets HttpOnly cookie for session persistence.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if user.account_status != UserStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is currently {user.account_status}. Please contact an administrator."
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production"
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
def logout(response: Response):
    """Clear session authentication cookie."""
    response.delete_cookie(key="access_token", samesite="lax")
    return {"message": "Successfully logged out."}


@router.get("/me", response_model=AuthMeResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details of currently authenticated user and associated profile."""
    profile_data = None
    if current_user.citizen_profile:
        profile_data = CitizenProfileResponse.model_validate(current_user.citizen_profile).model_dump()

    return AuthMeResponse(
        user=UserResponse.model_validate(current_user),
        citizen_profile=profile_data
    )
