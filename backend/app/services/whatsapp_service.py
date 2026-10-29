import uuid
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.user import User, UserRole, UserStatus
from app.models.citizen import CitizenProfile, ProfileStatus
from app.models.household import Household
from app.core.security import hash_password
from app.core.audit import record_audit_log

# In-memory session tracking for active conversational registrations
# Key: normalized phone number -> State dict
_registration_sessions: Dict[str, Dict[str, Any]] = {}


def generate_citizen_code() -> str:
    return f"CIT-{uuid.uuid4().hex[:8].upper()}"


def normalize_phone(phone: str) -> str:
    """Normalize phone numbers to digits only with leading plus if available."""
    cleaned = re.sub(r"[^\d+]", "", phone.strip())
    return cleaned


def process_whatsapp_message(
    db: Session,
    sender_phone: str,
    message_text: str
) -> Dict[str, Any]:
    """
    Core state machine for processing inbound WhatsApp messages.
    Supports citizen self-registration, profile lookup, household inspection,
    and review status checks directly via WhatsApp without needing the website.
    """
    clean_phone = normalize_phone(sender_phone)
    text = message_text.strip()
    lower_text = text.lower()

    # 1. Check if phone is already linked to a registered Citizen Profile
    citizen = db.query(CitizenProfile).filter(
        (CitizenProfile.phone_number == clean_phone) |
        (CitizenProfile.phone_number == sender_phone.strip())
    ).first()

    # If the user is already registered in the database:
    if citizen:
        return _handle_registered_citizen(db, citizen, text, lower_text)

    # If user is NOT registered yet, check active registration session
    session = _registration_sessions.get(clean_phone)
    if session:
        return _handle_registration_steps(db, clean_phone, session, text)

    # Initial greeting for an unregistered phone number
    if any(k in lower_text for k in ["register", "start", "join", "signup", "1"]):
        _registration_sessions[clean_phone] = {
            "step": "AWAITING_NAME",
            "phone": clean_phone,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        reply = (
            "🏛️ *NagrikSetu Citizen WhatsApp Registration*\n\n"
            "Welcome! I will help you register as a citizen in our official citizen registry.\n\n"
            "Please reply with your *Full Legal Name* (as shown on official government ID):"
        )
        return {
            "reply": reply,
            "state": "AWAITING_NAME",
            "is_registered": False,
            "options": []
        }

    # Default greeting for unregistered user
    reply = (
        "🏛️ *Welcome to NagrikSetu Citizen WhatsApp Services!*\n\n"
        "Your phone number is not yet registered in the citizen registry.\n\n"
        "You can register directly here without visiting the website!\n\n"
        "👉 Reply *REGISTER* (or *1*) to start citizen registration.\n"
        "👉 Reply *HELP* to learn about available citizen services."
    )
    return {
        "reply": reply,
        "state": "IDLE",
        "is_registered": False,
        "options": ["REGISTER", "HELP"]
    }


def _handle_registration_steps(
    db: Session,
    clean_phone: str,
    session: Dict[str, Any],
    text: str
) -> Dict[str, Any]:
    step = session.get("step")

    # Step 1: Receiving Full Legal Name
    if step == "AWAITING_NAME":
        name = text.strip()
        if len(name) < 2:
            return {
                "reply": "⚠️ Full name must be at least 2 characters. Please reply with your Full Legal Name:",
                "state": "AWAITING_NAME",
                "is_registered": False
            }
        session["full_name"] = name
        session["step"] = "AWAITING_EMAIL"
        reply = (
            f"Thank you, *{name}*! ✍️\n\n"
            f"Please reply with your *Email Address* (used for administrative notices and status updates):"
        )
        return {
            "reply": reply,
            "state": "AWAITING_EMAIL",
            "is_registered": False
        }

    # Step 2: Receiving Email Address
    if step == "AWAITING_EMAIL":
        email = text.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return {
                "reply": "⚠️ That doesn't look like a valid email. Please reply with a valid Email Address (e.g., name@example.com):",
                "state": "AWAITING_EMAIL",
                "is_registered": False
            }
        # Check if email is already taken
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return {
                "reply": "⚠️ An account with this email already exists in NagrikSetu. Please provide a different email address:",
                "state": "AWAITING_EMAIL",
                "is_registered": False
            }

        session["email"] = email
        session["step"] = "AWAITING_LANGUAGE"
        reply = (
            "Got it! 🌐 What is your *preferred communication language*?\n\n"
            "Reply with one of the codes:\n"
            "• *EN* - English\n"
            "• *HI* - Hindi (हिंदी)\n"
            "• *KN* - Kannada (ಕನ್ನಡ)\n"
            "• *TA* - Tamil (தமிழ்)\n"
            "• *TE* - Telugu (తెలుగు)\n"
            "• *MR* - Marathi (मराठी)"
        )
        return {
            "reply": reply,
            "state": "AWAITING_LANGUAGE",
            "is_registered": False,
            "options": ["EN", "HI", "KN", "TA", "TE", "MR"]
        }

    # Step 3: Receiving Language and Finalizing Database Insertion
    if step == "AWAITING_LANGUAGE":
        lang = text.strip().lower()
        if lang not in ["en", "hi", "kn", "ta", "te", "mr"]:
            lang = "en"

        full_name = session["full_name"]
        email = session["email"]

        # Atomically create User + CitizenProfile in database
        # Temporary secure password hash for account (citizen can also log in online)
        temp_pwd_hash = hash_password("WhatsAppPass123!@")
        new_user = User(
            email=email,
            password_hash=temp_pwd_hash,
            role=UserRole.CITIZEN.value,
            account_status=UserStatus.ACTIVE.value,
        )
        db.add(new_user)
        db.flush()

        citizen_code = generate_citizen_code()
        while db.query(CitizenProfile).filter(CitizenProfile.citizen_code == citizen_code).first():
            citizen_code = generate_citizen_code()

        new_profile = CitizenProfile(
            user_id=new_user.id,
            citizen_code=citizen_code,
            full_name=full_name,
            phone_number=clean_phone,
            preferred_language=lang,
            profile_status=ProfileStatus.PENDING_REVIEW.value,
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        # Clear session
        del _registration_sessions[clean_phone]

        # Audit log entry
        record_audit_log(
            db=db,
            actor=new_user,
            action="WHATSAPP_CITIZEN_REGISTRATION",
            resource_type="citizen",
            resource_id=citizen_code,
            details={"phone": clean_phone, "channel": "whatsapp"}
        )

        reply = (
            f"🎉 *Registration Successful on NagrikSetu!*\n\n"
            f"Your citizen record has been successfully registered directly from WhatsApp:\n\n"
            f"• *Citizen Code:* `{citizen_code}`\n"
            f"• *Full Name:* {full_name}\n"
            f"• *Registered Phone:* {clean_phone}\n"
            f"• *Email:* {email}\n"
            f"• *Status:* Pending Review ⏳\n"
            f"• *Language:* {lang.upper()}\n\n"
            f"You can now manage your records anytime from WhatsApp!\n"
            f"Reply with *MENU* to see available commands."
        )
        return {
            "reply": reply,
            "state": "COMPLETED",
            "is_registered": True,
            "citizen_code": citizen_code,
            "options": ["1. View Profile", "2. Check Household", "3. Check Status"]
        }

    return {"reply": "Please reply *REGISTER* to start.", "state": "IDLE", "is_registered": False}


def _handle_registered_citizen(
    db: Session,
    citizen: CitizenProfile,
    text: str,
    lower_text: str
) -> Dict[str, Any]:
    """Processes commands from an already-registered citizen."""
    
    # Profile command (1 or 'profile')
    if lower_text in ["1", "profile", "my profile", "who am i", "my details"]:
        reply = (
            f"📋 *Your Official Citizen Profile:*\n\n"
            f"• *Citizen Code:* `{citizen.citizen_code}`\n"
            f"• *Full Name:* {citizen.full_name}\n"
            f"• *Phone Number:* {citizen.phone_number or 'Not provided'}\n"
            f"• *Language:* {citizen.preferred_language.upper()}\n"
            f"• *Status:* {citizen.profile_status.replace('_', ' ').title()}\n"
            f"• *Registered On:* {citizen.created_at.strftime('%Y-%m-%d')}\n\n"
            f"Reply *MENU* to return to the main options."
        )
        return {
            "reply": reply,
            "state": "MENU",
            "is_registered": True,
            "citizen_code": citizen.citizen_code,
            "options": ["2. Check Household", "3. Check Status", "MENU"]
        }

    # Household command (2 or 'household')
    if lower_text in ["2", "household", "my household", "address", "family", "home"]:
        if not citizen.household_id:
            reply = (
                "🏠 *Household Status:*\n\n"
                "You are not currently linked to a registered municipal dwelling.\n"
                "An administrative officer will assign your household upon document verification."
            )
        else:
            hh = db.query(Household).filter(Household.id == citizen.household_id).first()
            if not hh:
                reply = "Household record not found."
            else:
                members = db.query(CitizenProfile).filter(CitizenProfile.household_id == hh.id).all()
                member_lines = "\n".join([
                    f"  • {m.full_name} ({m.household_relationship or 'Member'}) - `{m.citizen_code}`"
                    for m in members
                ])
                reply = (
                    f"🏠 *Registered Household ({hh.household_code}):*\n\n"
                    f"• *Address:* {hh.address_line}, {hh.locality}\n"
                    f"• *City:* {hh.city}, {hh.state} - {hh.postal_code}\n"
                    f"• *Your Role:* {citizen.household_relationship or 'Member'}\n\n"
                    f"*Verified Household Members ({len(members)}):*\n"
                    f"{member_lines}\n\n"
                    f"*(Confidential notes & co-resident contacts withheld for privacy)*"
                )
        return {
            "reply": reply,
            "state": "MENU",
            "is_registered": True,
            "citizen_code": citizen.citizen_code,
            "options": ["1. View Profile", "3. Check Status", "MENU"]
        }

    # Review status command (3 or 'status')
    if lower_text in ["3", "status", "review", "application status", "verified"]:
        status_readable = citizen.profile_status.replace('_', ' ').title()
        if citizen.profile_status == "active":
            status_desc = "Your profile is active and in good administrative standing."
        elif citizen.profile_status == "pending_review":
            status_desc = "Your profile is currently pending administrative verification by municipal staff."
        else:
            status_desc = f"Your profile status is '{status_readable}'."

        reply = (
            f"🔍 *Official Review Status:*\n\n"
            f"• *Citizen Code:* `{citizen.citizen_code}`\n"
            f"• *Status:* *{status_readable}*\n"
            f"• *Details:* {status_desc}\n\n"
            f"*(Note: Internal service tracking; does not constitute official national identity verification)*"
        )
        return {
            "reply": reply,
            "state": "MENU",
            "is_registered": True,
            "citizen_code": citizen.citizen_code,
            "options": ["1. View Profile", "2. Check Household", "MENU"]
        }

    # Default / Menu / Greeting
    reply = (
        f"👋 *Hello {citizen.full_name}!*\n"
        f"Citizen Code: `{citizen.citizen_code}`\n\n"
        f"Welcome to *NagrikSetu Citizen WhatsApp Bot*.\n"
        f"Reply with a number or keyword:\n\n"
        f"*1* 📋 View My Profile\n"
        f"*2* 🏠 Check Household Details\n"
        f"*3* 🔍 Application Review Status\n"
        f"*4* ❓ Platform Services Info"
    )
    return {
        "reply": reply,
        "state": "MENU",
        "is_registered": True,
        "citizen_code": citizen.citizen_code,
        "options": ["1. View Profile", "2. Check Household", "3. Check Status", "4. Services Info"]
    }
