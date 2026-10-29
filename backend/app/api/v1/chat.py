from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.citizen import CitizenProfile
from app.models.household import Household
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.api.deps import get_current_citizen_profile

router = APIRouter(prefix="/chat", tags=["Citizen Assistant"])


@router.post("/message", response_model=ChatMessageResponse)
def handle_chat_message(
    payload: ChatMessageRequest,
    profile: CitizenProfile = Depends(get_current_citizen_profile),
    db: Session = Depends(get_db)
):
    """
    Authenticated citizen conversational assistant.
    - Rule-based natural language processor tailored for public administration.
    - Strictly bound to the authenticated citizen's data and permissions.
    - Never leaks unpermitted household or other citizens' data.
    """
    raw_text = payload.message.strip().lower()
    timestamp = datetime.now(timezone.utc).strftime("%I:%M %p")
    suggested = [
        "View My Profile",
        "Check Household Details",
        "Review Application Status",
        "What services are available?"
    ]
    context_data = None

    # 1. Greeting
    if any(greet in raw_text for greet in ["hi", "hello", "hey", "good morning", "good evening", "namaste"]):
        reply = (
            f"Hello {profile.full_name}! 👋\n\n"
            f"I am your CivicAdmin Assistant. I can help you review your citizen profile, "
            f"check your household registration, or explain available administrative services. "
            f"What would you like assistance with today?"
        )
        return ChatMessageResponse(
            reply=reply,
            sender="assistant",
            timestamp=timestamp,
            suggested_prompts=suggested
        )

    # 2. Profile Details Query
    if any(k in raw_text for k in ["profile", "my details", "who am i", "my code", "citizen code", "about me", "my name"]):
        dob_str = profile.date_of_birth.strftime("%Y-%m-%d") if profile.date_of_birth else "Not provided"
        phone_str = profile.phone_number if profile.phone_number else "Not provided"
        reply = (
            f"📋 **Your Registered Profile Details:**\n\n"
            f"• **Full Name:** {profile.full_name}\n"
            f"• **Citizen Code:** `{profile.citizen_code}`\n"
            f"• **Status:** {profile.profile_status.replace('_', ' ').title()}\n"
            f"• **Phone Number:** {phone_str}\n"
            f"• **Date of Birth:** {dob_str}\n"
            f"• **Preferred Language:** {profile.preferred_language.upper()}\n\n"
            f"You can edit permitted contact details directly from the 'My Profile' tab."
        )
        context_data = {
            "type": "profile",
            "citizen_code": profile.citizen_code,
            "status": profile.profile_status
        }
        return ChatMessageResponse(
            reply=reply,
            sender="assistant",
            timestamp=timestamp,
            suggested_prompts=["Check Household Details", "Review Application Status"],
            context_data=context_data
        )

    # 3. Household Query
    if any(k in raw_text for k in ["household", "address", "family", "members", "who lives with me", "home"]):
        if not profile.household_id:
            reply = (
                "🏠 **Household Status:**\n\n"
                "Your account is not currently linked to a registered household. "
                "An administrative officer will link your household during verification or record processing."
            )
        else:
            household = db.query(Household).filter(Household.id == profile.household_id).first()
            if not household:
                reply = "Your household record could not be retrieved at this time."
            else:
                members = db.query(CitizenProfile).filter(CitizenProfile.household_id == household.id).all()
                member_lines = "\n".join([
                    f"  • {m.full_name} ({m.household_relationship or 'Member'}) - `{m.citizen_code}`"
                    for m in members
                ])
                reply = (
                    f"🏠 **Your Registered Household ({household.household_code}):**\n\n"
                    f"• **Address:** {household.address_line}, {household.locality}\n"
                    f"• **City & State:** {household.city}, {household.state} - {household.postal_code}\n"
                    f"• **Your Role:** {profile.household_relationship or 'Member'}\n\n"
                    f"**Registered Co-Residents ({len(members)} total):**\n"
                    f"{member_lines}"
                )
                context_data = {"type": "household", "household_code": household.household_code}

        return ChatMessageResponse(
            reply=reply,
            sender="assistant",
            timestamp=timestamp,
            suggested_prompts=["View My Profile", "What services are available?"],
            context_data=context_data
        )

    # 4. Status / Review Query
    if any(k in raw_text for k in ["status", "pending", "review", "active", "application status", "verified"]):
        status_readable = profile.profile_status.replace('_', ' ').title()
        if profile.profile_status == "active":
            status_desc = "Your profile is active and in good administrative standing."
        elif profile.profile_status == "pending_review":
            status_desc = (
                "Your profile registration is currently pending administrative review. "
                "Staff will verify your details against official documentation."
            )
        else:
            status_desc = f"Your profile status is currently '{status_readable}'."

        reply = (
            f"🔍 **Application & Profile Status:**\n\n"
            f"• **Current Status:** **{status_readable}**\n"
            f"• **Information:** {status_desc}\n"
            f"• **Citizen Code:** `{profile.citizen_code}`\n\n"
            f"*(Note: Profile status represents internal administrative service tracking and does not constitute official national identity verification.)*"
        )
        return ChatMessageResponse(
            reply=reply,
            sender="assistant",
            timestamp=timestamp,
            suggested_prompts=["View My Profile", "Check Household Details"]
        )

    # 5. Services / Help Query
    if any(k in raw_text for k in ["help", "service", "features", "options", "what can you do", "commands"]):
        reply = (
            "🛠️ **Available Platform Services (Phase 1):**\n\n"
            "1. **Identity & Profile Management:** View your registered identity details, language preferences, and update contact information.\n"
            "2. **Household Records:** Securely view your registered household address and linked family members without exposing private contact credentials.\n"
            "3. **Administrative Assistant:** Chat with me anytime to retrieve records or ask about platform status.\n"
            "4. **Future Microservices:** Integration hooks for education, employment, and social welfare schemes will arrive in upcoming releases via API Gateway.\n\n"
            "Try clicking one of the suggested prompts below!"
        )
        return ChatMessageResponse(
            reply=reply,
            sender="assistant",
            timestamp=timestamp,
            suggested_prompts=suggested
        )

    # 6. Default Fallback
    reply = (
        f"I received: \"{payload.message}\".\n\n"
        f"I can assist you with your citizen profile, household registration, or application review status. "
        f"Please select one of the suggested actions below or type 'help' for guidance."
    )
    return ChatMessageResponse(
        reply=reply,
        sender="assistant",
        timestamp=timestamp,
        suggested_prompts=suggested
    )
