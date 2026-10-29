import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password
from app.api.v1 import auth, citizens, households, admin, chat, health, whatsapp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("civicadmin")


def bootstrap_admin():
    """
    Idempotent initialization of default development administrator.
    Only creates the administrator account if NO admin currently exists.
    Does NOT reset existing passwords on subsequent restarts.
    """
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
        if not existing_admin:
            admin_email = settings.INITIAL_ADMIN_EMAIL.strip().lower()
            logger.info(f"Initializing development administrator account: {admin_email}")
            new_admin = User(
                email=admin_email,
                password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                role=UserRole.ADMIN.value,
                account_status=UserStatus.ACTIVE.value
            )
            db.add(new_admin)
            db.commit()
            logger.info("Development administrator successfully initialized.")
        else:
            logger.info("Administrator account already exists; bootstrap skipped.")
    except Exception as e:
        logger.error(f"Error checking/initializing administrator account: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema exists
    Base.metadata.create_all(bind=engine)
    # Ensure default admin exists
    bootstrap_admin()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Phase 1 Administrative Service microservice providing Citizen & Administrator portals, secure role-based authentication, household management, and audit logging.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS configuration - supports any localhost/127.0.0.1 port in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root-level health probes and versioned probes
app.include_router(health.router)
app.include_router(health.router, prefix=settings.API_V1_STR)

# Versioned API routes under /api/v1
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(citizens.router, prefix=settings.API_V1_STR)
app.include_router(households.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(whatsapp.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "ready": "/ready"
    }
