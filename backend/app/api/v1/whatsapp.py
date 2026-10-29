import io
import base64
import qrcode
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.services.whatsapp_service import process_whatsapp_message

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Bot & Services"])

WHATSAPP_BOT_NUMBER = "+1 555 019 2834"
WHATSAPP_CLEAN_NUMBER = "15550192834"
WHATSAPP_PREFILL_TEXT = "Hi CivicAdmin! I want to access municipal services or register."


class WhatsAppSimulateRequest(BaseModel):
    phone_number: str = Field(..., min_length=4, max_length=30)
    message: str = Field(..., min_length=1, max_length=1000)


class WhatsAppSimulateResponse(BaseModel):
    reply: str
    state: str
    is_registered: bool
    citizen_code: Optional[str] = None
    options: List[str] = []


from qrcode.image.svg import SvgPathImage


def generate_qr_svg(url: str) -> str:
    """Generate crisp, vector SVG QR code with zero PIL dependencies."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=SvgPathImage)
    
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue().decode("utf-8")


@router.get("/info")
def get_whatsapp_info(request: Request):
    """
    Returns WhatsApp Bot connection information:
    - Official WhatsApp Bot phone number
    - Direct wa.me deep-link
    - Scannable vector SVG QR Code
    """
    encoded_text = "Hi%20CivicAdmin!%20I%20want%20to%20access%20municipal%20services%20or%20register."
    wa_me_url = f"https://wa.me/{WHATSAPP_CLEAN_NUMBER}?text={encoded_text}"
    qr_svg = generate_qr_svg(wa_me_url)

    return {
        "bot_name": "CivicAdmin WhatsApp Official Bot",
        "phone_number": WHATSAPP_BOT_NUMBER,
        "clean_number": WHATSAPP_CLEAN_NUMBER,
        "prefill_text": WHATSAPP_PREFILL_TEXT,
        "wa_me_url": wa_me_url,
        "qr_code_svg": qr_svg,
        "capabilities": [
            "Direct Citizen Registration via WhatsApp Chat",
            "Official Citizen Profile Lookup",
            "Household & Family Residence Verification",
            "Application Review Status Tracking",
            "Audit Trail Logging of WhatsApp Interactions"
        ]
    }


@router.post("/simulate", response_model=WhatsAppSimulateResponse)
def simulate_whatsapp_chat(
    payload: WhatsAppSimulateRequest,
    db: Session = Depends(get_db)
):
    """
    Interactive WhatsApp conversation runner.
    Takes a simulated phone number and message, executes the WhatsApp state machine,
    persists new citizen registrations in PostgreSQL/SQLite, and returns the WhatsApp response.
    """
    result = process_whatsapp_message(
        db=db,
        sender_phone=payload.phone_number,
        message_text=payload.message
    )
    return WhatsAppSimulateResponse(
        reply=result["reply"],
        state=result.get("state", "IDLE"),
        is_registered=result.get("is_registered", False),
        citizen_code=result.get("citizen_code"),
        options=result.get("options", [])
    )


@router.get("/webhook")
def verify_meta_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
):
    """
    Meta WhatsApp Cloud API Webhook verification endpoint.
    Used by Meta / Facebook Developer dashboard to verify webhook ownership.
    """
    expected_token = getattr(settings, "WHATSAPP_VERIFY_TOKEN", "civicadmin_token_2026")
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification token mismatch.")


@router.post("/webhook")
async def receive_whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Production WhatsApp Webhook receiver supporting both:
    1. Meta WhatsApp Cloud API JSON payloads
    2. Twilio WhatsApp form urlencoded payloads
    """
    content_type = request.headers.get("content-type", "")
    
    sender_phone = None
    message_body = None

    if "application/json" in content_type:
        body = await request.json()
        try:
            # Meta Cloud API format
            entry = body.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            if messages:
                msg = messages[0]
                sender_phone = msg.get("from")
                if msg.get("type") == "text":
                    message_body = msg.get("text", {}).get("body")
        except Exception:
            return {"status": "ignored"}
    else:
        # Twilio format: Form data with 'From' and 'Body'
        form_data = await request.form()
        sender_phone = form_data.get("From", "").replace("whatsapp:", "")
        message_body = form_data.get("Body", "")

    if sender_phone and message_body:
        result = process_whatsapp_message(
            db=db,
            sender_phone=sender_phone,
            message_text=message_body
        )
        return {"status": "success", "reply": result["reply"]}

    return {"status": "no_actionable_message"}
