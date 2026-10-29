# CivicAdmin — Administrative & Citizen Services Platform (Phase 1)

CivicAdmin is a microservice built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.x**, **Pydantic 2.x**, **React 18**, **TypeScript**, and **Tailwind CSS**. It serves as the official Administrative Service within a modular citizen-services architecture.

CivicAdmin provides three integrated, accessible experiences:
1. **Citizen Portal**: Self-service registration, profile management, household privacy-scoped viewing, and a conversational assistant.
2. **WhatsApp Bot & Scannable QR Code**: Scan a QR code to interact or register directly over WhatsApp without needing to browse the website. Features an interactive mobile WhatsApp phone simulator on screen.
3. **Administrator Portal**: Real-time database metrics, citizen registry CRUD, household management, administrative review workflows, and immutable audit logging.

Targeted for **WCAG 2.2 AA Accessibility** and designed for seamless integration behind an **API Gateway**.

---

## Architecture Overview

```
                        ┌──────────────────────────────────────────────┐
                        │              Browser Client                  │
                        │   (React + TypeScript + Vite + Tailwind CSS) │
                        └──────────────┬───────────────────────────────┘
                                       │ HTTP / REST (/api/v1)
                                       │ (Bearer JWT / HttpOnly Cookie)
                                       ▼
                        ┌──────────────────────────────────────────────┐
                        │      FastAPI Administrative Microservice     │
                        │  - Argon2id Password Hashing                 │
                        │  - JWT Expiration & Role Authorization       │
                        │  - Strict Backend Ownership Enforcement      │
                        │  - Audit Logging System                      │
                        └──────────────┬───────────────────────────────┘
                                       │ Parameterized SQL via SQLAlchemy 2.x
                                       ▼
                        ┌──────────────────────────────────────────────┐
                        │        PostgreSQL 16 Database Engine         │
                        │  (Alembic Migrations / Normalized Relational)│
                        └──────────────────────────────────────────────┘
```

---

## Folder Structure

```
.
├── docker-compose.yml             # Multi-container Docker configuration (Postgres + Backend)
├── .env.example                   # Environment configuration template
├── README.md                      # Comprehensive system documentation & evaluation guide
├── backend/
│   ├── Dockerfile                 # Production backend container build
│   ├── requirements.txt           # Python dependency manifests
│   ├── alembic.ini                # Alembic migration configuration
│   ├── alembic/
│   │   ├── env.py                 # Migration runtime connecting models & DB URL
│   │   └── versions/              # Versioned schema migration files
│   ├── app/
│   │   ├── main.py                # FastAPI app initialization, CORS, lifespan bootstrap
│   │   ├── config.py              # Pydantic Settings configuration
│   │   ├── database.py            # SQLAlchemy 2.x engine and session dependency
│   │   ├── seed.py                # Synthetic demo database seeder
│   │   ├── core/
│   │   │   ├── security.py        # Argon2id hashing, password validation, JWT tokens
│   │   │   └── audit.py           # Administrative action audit logging
│   │   ├── models/                # SQLAlchemy relational models
│   │   │   ├── user.py            # User credentials, roles (citizen/admin), statuses
│   │   │   ├── citizen.py         # CitizenProfile (citizen_code, language, demographics)
│   │   │   ├── household.py       # Household (address, locality, city, admin notes)
│   │   │   └── audit.py           # Immutable AuditLog records
│   │   ├── schemas/               # Pydantic 2.x validation models
│   │   └── api/
│   │       ├── deps.py            # Auth dependencies (get_current_user, require_role)
│   │       └── v1/
│   │           ├── auth.py        # /register, /login, /logout, /me
│   │           ├── citizens.py    # Self-service & admin citizen CRUD
│   │           ├── households.py  # Privacy-scoped citizen & admin household CRUD
│   │           ├── admin.py       # Dashboard metrics & audit log viewer
│   │           ├── chat.py        # Conversational assistant endpoint
│   │           └── health.py      # /health & /ready probes
│   └── tests/
│       ├── conftest.py            # Pytest fixtures and in-memory test database
│       ├── test_auth.py           # Authentication, password rules, role isolation
│       ├── test_citizens.py       # Profile CRUD & ownership authorization
│       ├── test_households.py     # Household privacy & assignment tests
│       ├── test_admin.py          # Dashboard counts, audit trail, chat assistant
│       └── test_e2e.py            # Complete 13-step demonstration integration workflow
└── frontend/
    ├── package.json               # Frontend dependencies (React, Vite, Lucide)
    ├── vite.config.ts             # Vite bundler configuration
    ├── tsconfig.json              # TypeScript strict configuration
    ├── tailwind.config.js         # Accessible color tokens & dark/contrast styling
    ├── index.html                 # Accessible HTML5 template with skip-to-content
    └── src/
        ├── context/AuthContext.tsx# Authentication session & accessibility state
        ├── services/api.ts        # Unified API client (API Gateway compatible)
        ├── components/
        │   ├── Navbar.tsx         # Responsive header with accessibility tools
        │   ├── ProtectedRoute.tsx # Route-level authentication & role guard
        │   ├── ConfirmModal.tsx   # WCAG-compliant accessible modal dialog
        │   ├── Badge.tsx          # Dual-coded status badges (text + indicator)
        │   └── Alert.tsx          # ARIA live announcements for screen readers
        └── pages/
            ├── public/            # LandingPage, LoginPage, RegisterPage, AdminLoginPage
            ├── citizen/           # CitizenDashboard, CitizenProfile, CitizenHousehold, CitizenChat
            └── admin/             # AdminDashboard, CitizenManagement, HouseholdManagement, AuditLog
```

---

## Prerequisites

- **Python**: 3.12+
- **Node.js**: v18+ (tested on Node v24)
- **Docker & Docker Compose**: (optional for containerized deployment)

---

## Installation & Local Setup

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed synthetic demonstration data (idempotent)
python -m app.seed
```

### 2. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Verify production build
npm run build
```

---

## How to Run the Applications

### Quick Start (One Command)
Run the automated launcher script from the project root:
```bash
./start_demo.sh
```
This automatically starts:
- **FastAPI Backend** on `http://127.0.0.1:8000`
- **Vite React Frontend** on `http://localhost:5173` with reverse proxy to `/api`

---

### Option A: Manual Two-Terminal Execution

**Terminal 1 — Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base: `http://localhost:8000`
- Interactive Swagger OpenAPI Docs: `http://localhost:8000/docs`
- Health Probe: `http://localhost:8000/health`
- Readiness Probe: `http://localhost:8000/ready`

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```
- Citizen & Admin Web Portal: `http://localhost:5173`

---

### Option B: Docker Compose Deployment

```bash
# Start PostgreSQL database and FastAPI backend
docker compose up --build -d

# Check container status
docker compose ps

# Apply migrations inside container
docker compose exec backend alembic upgrade head

# Seed demo data inside container
docker compose exec backend python -m app.seed
```

---

## Demo Credentials for University Presentation

All demonstration credentials are pre-seeded and development-only:

| User Type | Email Address | Password | Role / Access Details |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@civicportal.gov` | `AdminPass123!@#` | Full administrative control, audit logs, household assignment |
| **Citizen 1** | `aarav.sharma@example.com` | `CitizenPass123!@` | Active status, linked to Bellandur Household |
| **Citizen 2** | `rohit.verma@example.com` | `CitizenPass123!@` | Pending Review status, linked to Indiranagar Household |
| **Citizen 3** | `kavita.deshmukh@example.com`| `CitizenPass123!@` | Active status, no household assigned |

---

## University Presentation Step-by-Step Walkthrough

### Part 1: Public & Citizen Experience
1. Open `http://localhost:5173`.
2. Observe the **Accessibility Bar** at the top: test **High Contrast** mode and **Enlarge Text** mode.
3. Click **Citizen Registration**:
   - Register a new citizen (e.g. `anita.das@example.com`).
   - Notice strict password complexity validation (min 8 chars, uppercase, digits, symbols).
   - Upon completion, notice that public registrations are **automatically assigned the `citizen` role** (preventing privilege escalation).
4. **Citizen Dashboard**:
   - View profile summary, unique citizen code (`CIT-XXXXXXXX`), and pending review status.
5. **My Profile**:
   - Update contact phone or language preference.
   - Notice that internal identifiers, roles, and review status are protected and non-editable.
6. **My Household**:
   - View registered residence. Notice that co-residents' contact numbers/emails and administrative notes are strictly withheld.
7. **Citizen Assistant (WhatsApp-Style Chat)**:
   - Click one of the suggested prompts (e.g., *"View My Profile"* or *"Check Household Details"*).
   - Type queries like `"who lives with me?"` or `"what services are available?"`.
   - Verify that the chat only resolves the authenticated citizen's permitted data.

### Part 2: Security & Role Isolation Verification
1. While logged in as a citizen, manually attempt to visit `http://localhost:5173/admin/dashboard` or `http://localhost:5173/admin/citizens`.
2. Notice the frontend router automatically blocks access and redirects back to `/citizen/dashboard`.
3. Check FastAPI endpoint responses: unauthorized requests return **HTTP 403 Forbidden**.

### Part 3: Administrator Portal Experience
1. Sign out of the citizen account and navigate to `/admin/login`.
2. Click **"Fill Dev Admin Credentials"** and sign in.
3. **Administrator Dashboard**:
   - Review live metrics calculated directly from the database: total citizens, active count, pending review count, and total households.
4. **Citizen Management**:
   - Search by name or citizen code.
   - Filter by status (`pending_review`, `active`, `archived`).
   - Review the newly registered citizen and change their status from `pending_review` to `active`.
5. **Household Management**:
   - Create a new household dwelling with municipal notes.
   - Assign citizens to the household with specific relationships (Head of Household, Spouse, Child, Member).
   - Delete a household and confirm with the accessible confirmation modal (members are safely unassigned without violating relational integrity).
6. **Audit Trail**:
   - View immutable audit log records capturing every creation, update, status change, and household assignment with actor timestamps.

---

## Running the Automated Test Suite

CivicAdmin includes 27 comprehensive automated tests covering authentication, password security, authorization, household privacy, administrative CRUD, and the complete 13-step demonstration workflow.

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest -v
```

All 27 test cases execute against an isolated in-memory test database and do not mutate development or demonstration data.

---

## API Endpoints List (`/api/v1`)

### Authentication & Account Management
- `POST /api/v1/auth/register` — Public citizen registration (strictly assigns `citizen` role)
- `POST /api/v1/auth/login` — Authenticate credentials, issue signed JWT, set HttpOnly session cookie
- `POST /api/v1/auth/logout` — Revoke session cookie
- `GET /api/v1/auth/me` — Return authenticated user information and linked profile

### Citizen Self-Service
- `GET /api/v1/citizens/me` — Retrieve own profile (server derives identity from session)
- `PATCH /api/v1/citizens/me` — Update permitted personal contact fields
- `GET /api/v1/households/me` — Retrieve privacy-scoped household residence and member summaries
- `POST /api/v1/chat/message` — Citizen conversational assistant message processor

### Administrator Operations (Requires `admin` role)
- `GET /api/v1/admin/dashboard` — Live database-derived administrative counters
- `GET /api/v1/admin/audit-logs` — Paginated administrative audit logs
- `GET /api/v1/citizens` — List, search, and filter citizen profiles
- `POST /api/v1/citizens` — Create citizen profile with optional provisioned account
- `GET /api/v1/citizens/{id}` — View complete citizen profile
- `PUT /api/v1/citizens/{id}` — Full update of citizen demographics and household assignment
- `PATCH /api/v1/citizens/{id}/status` — Status review workflow (`pending_review` -> `active` / `archived`)
- `DELETE /api/v1/citizens/{id}` — Delete citizen profile record
- `GET /api/v1/households` — List and search municipal households with administrative notes
- `POST /api/v1/households` — Create new household record
- `GET /api/v1/households/{id}` — View household details, notes, and members
- `PUT /api/v1/households/{id}` — Update household address and notes
- `DELETE /api/v1/households/{id}` — Delete household (safely unlinking members)
- `POST /api/v1/households/{id}/assign` — Assign citizen to household
- `POST /api/v1/households/{id}/unassign/{citizen_id}` — Unassign citizen from household

### System Health
- `GET /health` — Liveness probe
- `GET /ready` — Readiness probe verifying active database connectivity

---

## Accessibility Compliance (WCAG 2.2 AA)

1. **Semantic HTML**: Proper `<header>`, `<nav>`, `<main>`, `<section>`, `<table>`, and `<footer>` tags throughout.
2. **Keyboard Navigation & Focus Management**:
   - Visible outline focus rings (`outline: 2px solid #0270c7`).
   - "Skip to main content" link at top of DOM for keyboard and screen-reader users.
   - Modals trap focus and support dismiss via `Escape` key.
3. **Contrast & Sizing**:
   - Integrated **High Contrast Mode** toggle.
   - Integrated **Enlarge Text Mode** toggle (scales font baseline by 112.5%).
   - All interactive touch and click targets satisfy minimum 44×44px standards.
4. **Accessible Forms & Alerts**:
   - Explicit `<label htmlFor="...">` bindings on all form inputs.
   - Dual-coded status badges with text plus icon indicators.
   - Dynamic asynchronous feedback announced via `role="alert"` and `aria-live="polite"`.

---

## Security Architecture & Known Limitations

### Security Features
- **Argon2id Password Hashing**: Utilizes memory-hard, GPU-resistant parameters.
- **Signed Expiring Tokens**: Signed JWT with HS256 algorithm and explicit expiration lifetimes.
- **Strict Role-Based Access Control**: FastAPI dependency injection (`require_role`) applied to all endpoints.
- **Backend-Enforced Ownership**: No endpoint trusts client-supplied user identifiers for self-service operations.
- **Safe Audit Logging**: Administrative mutations record timestamps and actors while explicitly sanitizing passwords and tokens.

### Honest Limitations & Phase 2 Roadmap
- **External SMS / Email Gateway**: In Phase 1, two-factor authentication (2FA) and real SMS OTP are not integrated; password-based authentication with token verification is used.
- **Rate Limiting**: Throttling is ready for API Gateway deployment (e.g. via Redis/Nginx rate-limiting middleware).
- **Rule-Based Assistant**: The citizen conversational assistant operates deterministically on structured platform data without relying on third-party generative AI models. Future phases will integrate the central AI assistant via API Gateway.
