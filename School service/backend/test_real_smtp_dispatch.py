import os
import sys
import email_service

to_addr = os.environ.get("SMTP_FROM_EMAIL")
print(f"Masked recipient: {email_service.mask_email(to_addr)}")

try:
    provider = email_service.get_email_provider()
    res = provider.send_email(
        to_email=to_addr,
        subject="NagrikSetu School Service - SMTP Delivery Test",
        body_text="This is an automated delivery test verifying Gmail SMTP integration on NagrikSetu School Service.",
        body_html="<p>This is an automated delivery test verifying <strong>Gmail SMTP integration</strong> on NagrikSetu School Service.</p>"
    )
    print("DELIVERY_STATUS: SUCCESS")
    print(f"Response: {res}")
except email_service.EmailDeliveryError as e:
    print(f"DELIVERY_STATUS: FAILED")
    print(f"Reason: {e}")
except Exception as e:
    print(f"DELIVERY_STATUS: ERROR")
    print(f"Unexpected: {type(e).__name__}: {e}")
