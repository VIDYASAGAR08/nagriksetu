# NagrikSetu Project Audit Report
*Generated: 2026-10-30*

---

## 🟢 Container Status

| Container | Name | Port | Status |
|---|---|---|---|
| Frontend | `nagriksetu-frontend` | `0.0.0.0:5173→80/tcp` | ✅ Up |
| Backend | `nagriksetu-backend` | `0.0.0.0:8001→8000/tcp` | ✅ Up |

**Frontend image**: `ff48bb893881` (pre-built Nginx/static, no source bind-mount)  
**Backend image**: `nagriksetu-backend` (Python 3.11-slim + uvicorn)  
**Backend volume**: `C:\Users\callm\nagriksetu\backend\data` → `/app/data` (bind mount, RW)

---

## 📁 Project Structure

```
C:\Users\callm\nagriksetu\
├── .env                     # JWT_SECRET_KEY (placeholder — needs a real value)
├── .gitignore
├── docker-compose.yml
├── backend/
│   ├── Dockerfile           # python:3.11-slim, uvicorn, port 8000
│   ├── requirements.txt     # fastapi, uvicorn, pydantic, PyJWT, pwdlib[argon2]
│   ├── auth.py              # JWT token + argon2 password hashing
│   ├── database.py          # SQLite schema management + migrations
│   ├── main.py              # FastAPI application (848 lines)
│   ├── create_admin.py      # Admin creation utility
│   ├── seed_data.py         # Dataset seeding script
│   ├── expand_dataset.py    # Dataset expansion script
│   ├── inspect_database.py  # DB inspection utility
│   ├── data/
│   │   ├── nagriksetu.db                        # LIVE database
│   │   └── nagriksetu_backup_before_rebuild.db  # Existing backup
│   └── main.py.backup                           # Previous main.py backup
└── frontend/
    ├── Dockerfile           # node:22-alpine build → nginx:alpine serve
    ├── package.json         # React 19, Vite 8, oxlint
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx          # Single-file React app (414 lines)
        ├── App.css          # 629-line stylesheet
        ├── main.jsx         # React entry point
        └── index.css        # Base styles
```

---

## 🗄️ Database State

**Database**: SQLite at `/app/data/nagriksetu.db` (bind-mounted from host)  
**Existing backup**: `nagriksetu_backup_before_rebuild.db` already present

### Table Row Counts

| Table | Count | Notes |
|---|---|---|
| `schools` | **20** | Mix of real districts + demo schools |
| `students` | **30,000** | Full synthetic dataset, all with `permanent_student_id` |
| `users` | **2** | 1 parent + 1 school_admin |
| `guardians` | **1** | Linked to the parent user |
| `student_guardians` | **1** | 1 verified guardian-student link |
| `enrollments` | **30,000** | All in AY 2026-2027, backfilled from students |
| `academic_results` | **0** | No results seeded yet |
| `student_documents` | **0** | No documents seeded |
| `fees` | **0** | No fee records |
| `scholarships` | **0** | No scholarship records |
| `update_requests` | **2** | Existing pending requests |
| `school_change_log` | **1** | One approved change logged |

### Sample Data
- **School**: `SCH001` – Government Model School, Bengaluru Urban
- **Student**: `SCH001-STD01-001` → Asha Sharma (permanent ID: `NS-FB8336A...`)
- **Users**: 1 parent account, 1 school_admin account

---

## 🔧 Backend API Audit (FastAPI v0.128.8)

### Endpoints Implemented

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/login` | None | JWT login (email or phone) |
| `GET` | `/auth/me` | JWT | Current user info |
| `GET` | `/` | None | Service status + counts |
| `GET` | `/health` | None | Health check |
| `GET` | `/schools` | None | Paginated school list |
| `GET` | `/schools/{id}` | None | Single school detail |
| `GET` | `/search-schools` | None | Keyword search |
| `GET` | `/schools/{id}/students` | None | Students by school (standard + section filter) |
| `GET` | `/students/{id}` | None | Public student profile + history |
| `GET` | `/schools/{id}/programs` | None | School programs |
| `GET` | `/schools/{id}/achievements` | None | Published achievements |
| `GET` | `/parent/children` | JWT (parent) | List guardian's children |
| `GET` | `/parent/children/{psid}/records` | JWT (parent) | Private academic records |
| `POST` | `/parent/update-requests` | JWT (parent) | Submit update request |
| `GET` | `/parent/update-requests` | JWT (parent) | List own update requests |
| `GET` | `/school/update-requests` | JWT (staff/admin) | School's pending requests |
| `POST` | `/school/update-requests/{id}/review` | JWT (staff/admin) | Approve/reject request |

### ⚠️ Known Issues in `main.py`
1. **Duplicate function definition** (lines 255–336): `get_school_students` is defined **twice** as a standalone function at line 300 — only the first `@app.get` route at line 255 is registered; the second definition silently shadows it without being a route handler.
2. **`import uuid` appears twice**: once at line 1 and again at line 607 (redundant).

### Security
- JWT with argon2 password hashing ✅
- Permission column whitelist in `get_authorized_child` ✅
- CORS restricted to `localhost:5173` ✅
- `field_name` whitelist for `allowed_fields` in review endpoint ✅
- `JWT_SECRET_KEY` env var enforced (raises `RuntimeError` if missing) ✅
- `.env` has **placeholder value** — `JWT_SECRET_KEY=PASTE_YOUR_GENERATED_SECRET_HERE` ⚠️

---

## 🖥️ Frontend Audit (React 19 + Vite 8)

### Architecture
- **Single-page app** in `App.jsx` (414 lines, all in one file)
- **No router** — custom `activePage` state machine
- **No auth UI** — login, parent portal, school staff portal not yet implemented
- **No state management** beyond `useState`/`useMemo`
- API URL: `http://${window.location.hostname}:8001` (dynamic hostname)

### Pages Implemented
| Page | Feature |
|---|---|
| `dashboard` | Stat cards + 6-school preview grid |
| `directory` | Full school grid + search |
| `students` | Select school → filtered student table (standard + section) |

### Pages NOT Yet Implemented
- Login / authentication flow
- Parent portal (my children, records, update requests)
- School staff portal (pending requests, review)
- Student detail view
- School detail view (programs, achievements)

---

## 🐳 Docker Configuration

```yaml
# docker-compose.yml
backend:  port 8001→8000, bind mount ./backend/data:/app/data
frontend: port 5173→80, no bind mounts (static build baked in)
```

> [!IMPORTANT]
> The frontend is a **static build baked into the image** — no source bind-mount. To update the frontend, the image must be rebuilt and the container restarted.

---

## 📋 Pre-Change Checklist

- [x] Both containers verified running
- [x] Database tables confirmed intact (15 tables)
- [x] Existing backup confirmed at `nagriksetu_backup_before_rebuild.db`
- [x] API health check passing (`/health` → `{"status":"healthy"}`)
- [x] Schools API returning data (`/schools?limit=3` → 3 records)
- [x] No duplicate ports, no stray containers using 5173/8001

---

## ⚠️ Pre-Existing Issues to Fix

1. **Duplicate `get_school_students` function** in `main.py` (dead code)
2. **Redundant `import uuid`** in `main.py`  
3. **Placeholder JWT secret** in `.env` (must be replaced before production use)
4. **Frontend has no auth UI** — login, parent portal, school staff portal all missing
5. **Empty tables**: `academic_results`, `fees`, `scholarships`, `school_programs`, `school_achievements` need seeded data to demonstrate features
