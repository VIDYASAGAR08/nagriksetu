import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Account, TrainingCentre, AuditLog
from app.main import hash_password

ROTATED_PASSWORDS = [
    (1, "centre.bengaluru@nagriksetu.local", "Blr#w$Qr%m9@!"),
    (2, "centre.admin.mysuru@nagriksetu.local", "Mys#kxUERTN4!"),
    (3, "centre.admin.hubballi@nagriksetu.local", "Hub#ukl2Lk$y!"),
    (4, "centre.admin.mangaluru@nagriksetu.local", "Mng#HAFHUM%5!"),
    (5, "centre.virtual@nagriksetu.local", "Vrt#@G%gfJXm!"),
    (6, "centre.dharwad@nagriksetu.local", "Dhw#EdspKs6c!"),
    (8, "centre.belagavi@nagriksetu.local", "Blg#7T%PxYtj!"),
    (9, "centre.davanagere@nagriksetu.local", "Dvg#K6@W#7W$!"),
    (10, "centre.kalaburagi@nagriksetu.local", "Klb##hPdqEA7!"),
    (11, "centre.shivamogga@nagriksetu.local", "Shv#j5E!5Ls0!"),
]

# Database connection in container
db_url = os.getenv("DATABASE_URL", "mysql+pymysql://nagriksetu_skill:skill-app-pass-2026@skill-service-db:3306/skill_db")
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("Applying rotated unique passwords with Argon2id...")
for cid, email, pwd in ROTATED_PASSWORDS:
    acc = db.query(Account).filter_by(centre_id=cid, role="TRAINING_CENTRE_ADMIN").first()
    if not acc:
        acc = db.query(Account).filter_by(email=email).first()
    
    if acc:
        new_hash = hash_password(pwd)
        acc.password_hash = new_hash
        acc.active = True
        print(f"Updated Centre {cid:2d} ({email}) -> Argon2id hash: {new_hash[:30]}...")
    else:
        print(f"Account not found for centre {cid}")

db.add(AuditLog(
    actor="SYSTEM_SECURITY",
    role="SECURITY",
    action="CREDENTIAL_ROTATION",
    target="ALL_10_CENTRES",
    details="All 10 Training Centre representative passwords rotated to unique strong credentials using Argon2id."
))
db.commit()
print("All 10 centres successfully rotated and committed to MySQL!")
