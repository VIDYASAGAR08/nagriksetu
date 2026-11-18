main_path = r"C:\Users\callm\nagriksetu\backend\main.py"
with open(main_path, "r", encoding="utf-8") as f:
    c = f.read()

target = """            record_platform_audit(
                conn,
                event_type="UNAUTHORIZED_INVITATION_CLAIM_ATTEMPT",
                event_category="security",
                institution_id=inst_id,
                actor_user_id=None,
                actor_role="anonymous",
                action=f"Unauthorized claim attempt on {school['school_name']} ({inst_id}) with email '{payload.email}'",
                remarks="Email mismatch on institution invitation claim"
            )"""

replacement = """            record_platform_audit(
                conn,
                event_type="UNAUTHORIZED_INVITATION_CLAIM_ATTEMPT",
                event_category="security",
                institution_id=inst_id,
                actor_user_id=None,
                actor_role="anonymous",
                entity_type="invitation_tokens",
                entity_id=inv["token_id"],
                action=f"Unauthorized claim attempt on {school['school_name']} ({inst_id}) with email '{payload.email}'",
                remarks="Email mismatch on institution invitation claim"
            )"""

assert target in c, "target not found"
c = c.replace(target, replacement, 1)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(c)

print("Fixed record_platform_audit in main.py successfully!")
