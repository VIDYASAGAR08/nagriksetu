# NagrikSetu Skill Development Microservice — START HERE

Welcome to the **NagrikSetu Skill Development Microservice** backend handoff package (Member 2).
This service manages the end-to-end vocational training lifecycle:
- Course & Skill Catalog (104 NSQF courses across 10 civic & industry categories).
- Training Centres, Trainers & Batch Capacity Management.
- Citizen Profiles, Skill Portfolios & Application Dossiers.
- Enrolment Lifecycle, Attendance Tracking, Modular Training Progress & Assessment Results.
- Verifiable Digital Certificates with unique cryptographic validation codes.
- Deterministic Skill Gap Analysis Engine with structured course recommendations.
- RabbitMQ Event Publishing on the `nagriksetu.events` exchange.

---

## 1. Prerequisites

- **Python 3.10+** (Python 3.11 / 3.12 / 3.13 supported)
- **MySQL 8.4** (or MySQL 8.0+)
- **RabbitMQ 3.12+** (Optional for local standalone testing; required for full event distribution)
- **Docker & Docker Compose** (Optional, if running via containers)

---

## 2. Quick Setup in 5 Steps

### Step 1: Configure Environment Variables
Copy `.env.example` to `.env` and fill in your database credentials and a secure random JWT secret:
```bash
cp .env.example .env
```
Key configuration items in `.env`:
```ini
# MySQL Configuration
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3308
MYSQL_DATABASE=skill_db
MYSQL_USER=nagriksetu_skill
MYSQL_PASSWORD=your_mysql_password_here

# Security
JWT_SECRET=replace_with_your_own_secure_random_jwt_secret_min_32_chars
ADMIN_EMAIL=skill.admin@nagriksetu.local
ADMIN_PASSWORD=your_secure_admin_password_here

# Message Broker
RABBITMQ_DEFAULT_USER=nagriksetu
RABBITMQ_DEFAULT_PASS=your_rabbitmq_password_here
```

> **IMPORTANT SECURITY NOTE:** The application validates secrets at startup. If `JWT_SECRET` is missing, blank, or left as the placeholder, the application will safely exit with a configuration error.

---

### Step 2: Database Restoration (Strict Schema Isolation)

> **SAFETY WARNING:** The database backup contains `DROP TABLE IF EXISTS` statements. **NEVER** import this backup into an existing shared project database. Always import into a dedicated empty database (e.g. `skill_db`).

#### Option A: Using the Safe Python Restore Script (Recommended)
```bash
cd database
python safe_restore.py --host 127.0.0.1 --port 3308 --user nagriksetu_skill --database skill_db
```

#### Option B: Using the MySQL CLI Directly
```bash
# 1. Create the dedicated database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS skill_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. Import the backup dump
mysql -u nagriksetu_skill -p skill_db < database/skill_db_backup.sql
```

This restores **19 tables** and pre-seeded seed data (104 NSQF training programmes, 520 modules, 208 batches, 10 categories, 5 centres, and 6 trainers).

---

### Step 3: Install Dependencies
```bash
cd backend
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

---

### Step 4: Database Migrations (Alembic)
Schema management is officially handled through Alembic migrations.
To run migrations against your configured database:
```bash
cd backend
alembic upgrade head
```

---

### Step 5: Start the Backend Service

#### Running Locally with Uvicorn:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

#### Running via Docker Compose:
If you prefer running via Docker with the included RabbitMQ container:
```bash
docker compose up -d --build
```

---

## 3. Verify Application Health & Swagger Documentation

Once started, test the service endpoints:
- **Health Check Endpoint:**
  `http://localhost:8003/health`
  Expected response:
  ```json
  {
    "service": "nagriksetu-skill-development",
    "status": "healthy",
    "database": "mysql_8.4",
    "database_status": "connected",
    "version": "2.0.0"
  }
  ```
- **Interactive Swagger Documentation:**
  Open your browser to: `http://localhost:8003/docs`
- **OpenAPI 3.1 JSON Specification:**
  `http://localhost:8003/openapi.json` (Exposes all 46 unique HTTP operations across 41 paths).

---

## 4. Running the Automated Test Suite

The test suite enforces strict database isolation: it verifies that tests execute against `skill_test_db` and **strictly aborts** if pointed toward `skill_db` or production schemas.

```bash
cd backend
# 1. Ensure skill_test_db exists:
# mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS skill_test_db;"

# 2. Run test suite:
pytest tests/test_skill_service.py -v
```
All 9 comprehensive integration and unit tests will execute and pass without mutating any production data.
