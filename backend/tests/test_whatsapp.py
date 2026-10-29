from app.models.citizen import CitizenProfile
from app.models.user import User


def test_whatsapp_info_endpoint(client):
    res = client.get("/api/v1/whatsapp/info")
    assert res.status_code == 200
    data = res.json()
    assert "wa_me_url" in data
    assert "qr_code_svg" in data
    assert "<svg" in data["qr_code_svg"]
    assert "555" in data["phone_number"]


def test_whatsapp_citizen_registration_flow(client, db_session):
    phone = "+91 91111 22222"

    # 1. Unregistered user sends "Hello"
    res1 = client.post("/api/v1/whatsapp/simulate", json={"phone_number": phone, "message": "Hello"})
    assert res1.status_code == 200
    assert "Welcome to CivicAdmin" in res1.json()["reply"]
    assert res1.json()["is_registered"] is False

    # 2. User starts registration
    res2 = client.post("/api/v1/whatsapp/simulate", json={"phone_number": phone, "message": "REGISTER"})
    assert res2.status_code == 200
    assert "Full Legal Name" in res2.json()["reply"]
    assert res2.json()["state"] == "AWAITING_NAME"

    # 3. User provides Name
    res3 = client.post("/api/v1/whatsapp/simulate", json={"phone_number": phone, "message": "Sunita Rao"})
    assert res3.status_code == 200
    assert "Email Address" in res3.json()["reply"]
    assert res3.json()["state"] == "AWAITING_EMAIL"

    # 4. User provides Email
    res4 = client.post("/api/v1/whatsapp/simulate", json={"phone_number": phone, "message": "sunita.rao@example.com"})
    assert res4.status_code == 200
    assert "preferred communication language" in res4.json()["reply"]
    assert res4.json()["state"] == "AWAITING_LANGUAGE"

    # 5. User selects Language
    res5 = client.post("/api/v1/whatsapp/simulate", json={"phone_number": phone, "message": "KN"})
    assert res5.status_code == 200
    data5 = res5.json()
    assert "Registration Successful" in data5["reply"]
    assert data5["is_registered"] is True
    assert data5["citizen_code"].startswith("CIT-")

    # 6. Verify User and CitizenProfile exist in DB!
    user = db_session.query(User).filter(User.email == "sunita.rao@example.com").first()
    assert user is not None
    assert user.role == "citizen"
    
    citizen = db_session.query(CitizenProfile).filter(CitizenProfile.user_id == user.id).first()
    assert citizen is not None
    assert citizen.full_name == "Sunita Rao"
    assert citizen.preferred_language == "kn"

    # 7. Check that Sunita can now query her profile on WhatsApp
    res6 = client.post("/api/v1/whatsapp/simulate", json={"phone_number": phone, "message": "1"})
    assert res6.status_code == 200
    assert "Sunita Rao" in res6.json()["reply"]
    assert citizen.citizen_code in res6.json()["reply"]


def test_whatsapp_meta_webhook(client):
    # Test verification challenge
    res = client.get("/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.challenge=11559955&hub.verify_token=civicadmin_token_2026")
    assert res.status_code == 200
    assert res.text == "11559955"

    # Test inbound message
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "919999988888",
                        "type": "text",
                        "text": {"body": "HELP"}
                    }]
                }
            }]
        }]
    }
    res_post = client.post("/api/v1/whatsapp/webhook", json=payload)
    assert res_post.status_code == 200
    assert res_post.json()["status"] == "success"
