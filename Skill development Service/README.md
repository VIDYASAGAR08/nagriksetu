# NagrikSetu Skill Development Microservice
## Production-Grade Digital Public Infrastructure (DPI) for Citizen Skilling & Career Placement

---

### 1. Project Overview
NagrikSetu Skill Development is a full-stack, enterprise-grade civic microservice aligned with the **National Skills Qualifications Framework (NSQF)** and the **Ministry of Skill Development and Entrepreneurship (MSDE)** standards.

It bridges the youth employability lifecycle across:
- **NSQF-Aligned Course Discovery:** 104+ technical and vocational skills mapped to training centres and accredited faculty.
- **Smart Citizen Skilling Dossier:** Profile management with Aadhaar-aligned name standards and automated form pre-filling.
- **Dynamic Skill Gap Analyzer:** Algorithm comparing current proficiencies against target industrial roles to calculate gap scores and recommended learning orders.
- **Bilingual Interface:** Full end-to-end localization in English and Kannada (ಕನ್ನಡ) with instant switching and session persistence.
- **Verified Document & Resume Locker:** FastAPI multipart upload handling resume and educational credential storage with mime/size validation.
- **Tamper-Proof Certification:** Verification engine providing verifiable credentials and downloadable standard PDF certificates with credential codes.
- **Career & Employment Portal:** Full in-portal job application pipeline, saved opportunity bookmarks, and real-time status tracking.
- **Asynchronous Architecture:** Event-driven RabbitMQ message broker for decoupled notification processing and comprehensive administrative audit logging.

---

### 2. Technology Stack
- **Frontend:** React 18, TypeScript, Vite, Tailwind-compatible CSS design system, Lucide icons, `i18next` & `react-i18next`.
- **Backend:** Python 3.11, FastAPI, SQLAlchemy ORM, Pydantic v2, PyMySQL, PyJWT, Python-Multipart.
- **Database:** MySQL 8.4 Enterprise Relational Database (`skill_db`, port 3308).
- **Messaging:** RabbitMQ 3-Management message broker (AMQP port 5672, HTTP UI port 15672).
- **Deployment:** Docker & Docker Compose with multi-stage production builds and Nginx reverse proxy.

---

### 3. Repository & Folder Structure
```text
NagrikSetu_SkillDevelopment_Final/
├── backend/
│   ├── app/
│   │   ├── main.py               # Core FastAPI endpoints & authentication
│   │   ├── models.py             # SQLAlchemy models (Accounts, Programs, Docs, etc.)
│   │   ├── schemas.py            # Pydantic v2 validation contracts
│   │   ├── employment_adapter.py # Career opportunities & job engine
│   │   ├── event_publisher.py    # RabbitMQ event publisher
│   │   ├── seed_data.py          # Database seeding scripts
│   │   └── skill_gap_engine.py   # Skill gap analysis & recommendation engine
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   ├── safe_restore.py
│   └── skill_db_backup.sql
├── frontend/
│   ├── src/
│   │   ├── locales/
│   │   │   ├── en.json           # English localization dictionary
│   │   │   └── kn.json           # Kannada localization dictionary
│   │   ├── App.tsx               # Main React component
│   │   ├── i18n.ts               # i18next configuration (en/kn)
│   │   ├── main.tsx              # Application entry point
│   │   └── style.css             # National portal visual design system
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docker-compose.yml
└── README.md
```

---

### 4. Default Ports & Service Endpoints
| Component | URL / Port | Credentials / Purpose |
| :--- | :--- | :--- |
| **Frontend Web Portal** | `http://localhost:5173` | Citizen & Admin Interface |
| **Backend REST API** | `http://localhost:8003` | FastAPI Microservice Engine |
| **Interactive Swagger Docs** | `http://localhost:8003/docs` | OpenAPI 3.0 Documentation |
| **Backend Health Check** | `http://localhost:8003/health` | Automated System & DB Health |
| **RabbitMQ Management** | `http://localhost:15672` | User: `guest` / Pass: `guest` |
| **MySQL 8.4 Database** | `localhost:3308` | User: `nagriksetu_skill` / DB: `skill_db` |

---

### 5. Quickstart & Docker Execution Commands

To build and run all services in detached mode:
```bash
docker compose up -d --build
```

To view real-time container logs:
```bash
docker compose logs -f
```

To stop all services safely without losing database records:
```bash
docker compose down
```

---

### 6. Authentication Details
- **Administrator Account:**
  - Email: `skill.admin@nagriksetu.local`
  - Password: `SkillAdmin@2026!`
  - Role: `SKILL_DEPARTMENT_ADMIN`
- **Citizen Account (Demo / Live):**
  - Email: `puneet213@gmail.com` (or create a new citizen account via the registration modal)
  - Role: `CITIZEN`

---

### 7. End-to-End Verification Suite
A comprehensive automated test script is provided in the repository. Run:
```bash
python scratch/e2e_full_verification.py
```
This script validates:
1. Backend & database connectivity.
2. Administrator login and metrics retrieval.
3. Citizen account creation and JWT issuance.
4. Profile completion and skill declaration.
5. Skill gap analysis engine execution.
6. In-portal career opportunity application with duplicate prevention.
7. Multipart document upload to persistent storage.
8. In-app notifications persistence and read-marking.
9. Cryptographic certificate verification and binary PDF generation.

---

### 8. Real-World Training Centre Discovery System (Real GPS, Universal Search & Custom Radius)
The Skill Development microservice includes real-time location-based centre discovery across any supported Indian city, locality, PIN code, or landmark:
- **Universal Geocoding & Location Search:** Resolves any locality (e.g. `CV Raman Nagar, Bengaluru`, `Kaggadasapura`, `Whitefield`, `Indiranagar`, `Mysuru`, `Chennai`, `Hyderabad`, `Mumbai`, `Delhi`) into exact geographical coordinates via Google Geocoding or OpenStreetMap Nominatim.
- **Genuine Places Provider Integration:**
  - **Google Places API (New):** Connects to Google Cloud Places Text Search, Nearby Search, and Place Details via backend. Configure `GOOGLE_PLACES_API_KEY` in `.env`.
  - **OpenStreetMap & DPI Real-World Directory:** Built-in fallback ensuring 100% operational discovery with real establishments (vocational institutes, IT/software academies, ITIs, NSDC centres, polytechnics) even when Google credentials are not set.
- **Fully Dynamic Custom Radius:** Users can type ANY custom radius in kilometres (e.g. `1 km`, `2.5 km`, `7 km`, `15 km`, `25 km`, `100 km`) or use the interactive slider.
- **Precise Haversine Distance:** Mathematically calculates straight-line distances from the origin coordinates and sorts results nearest to farthest.
- **Interactive Leaflet & OpenStreetMap:** Displays real markers with distinct pins for the origin point (blue), official NagrikSetu centres (orange), and real-world discovered institutes (teal), complete with ratings, facilities, phone numbers, websites, and turn-by-turn directions.
- **API Endpoints:**
  - `GET /api/centres/search?location={location}&radius_km={radius}`
  - `GET /api/centres/nearby?latitude={lat}&longitude={lon}&radius_km={radius}`
  - `GET /api/centres/details/{place_id}`

#### Google Places API Configuration (Optional)
To enable live Google Cloud Places queries:
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Places API (New)** and **Geocoding API**.
3. Generate an API Key under Credentials.
4. Add to your `.env` file:
   ```env
   GOOGLE_PLACES_API_KEY=your_actual_google_api_key_here
   ```
5. Restart backend services. If omitted, the system seamlessly uses the OpenStreetMap DPI places engine.

