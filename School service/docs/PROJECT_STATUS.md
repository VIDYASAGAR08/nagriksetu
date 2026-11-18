# NagrikSetu — Project Status
*Updated: 2026-10-30 · Phase 2 Architecture*

## Summary

NagrikSetu School Service is a citizen-facing portal for school discovery, parent-child record access, and student correction requests. The backend and database are substantially functional; the frontend is a demonstration-only dashboard that must be replaced with a government-style public portal.

---

## ✅ Completed Features

### Backend (FastAPI)
- `GET /health` — health check ✅
- `GET /` — service status with school/student counts ✅
- `GET /schools` — paginated school list ✅
- `GET /schools/{id}` — single school detail ✅
- `GET /search-schools?keyword=` — keyword search ✅
- `GET /schools/{id}/students?standard=&section=` — filtered student list ✅
- `GET /students/{id}` — public student profile + history ✅
- `GET /schools/{id}/programs` — school programs ✅
- `GET /schools/{id}/achievements` — published achievements ✅
- `POST /auth/login` — JWT login (email or phone) ✅
- `GET /auth/me` — current user info ✅
- `GET /parent/children` — list verified linked children ✅
- `GET /parent/children/{psid}/records` — private academic records ✅
- `POST /parent/update-requests` — submit correction request ✅
- `GET /parent/update-requests` — list own requests ✅
- `GET /school/update-requests` — school's pending requests ✅
- `POST /school/update-requests/{id}/review` — approve/reject ✅
- Argon2 password hashing ✅
- JWT authentication ✅
- Role-based access control (parent, school_staff, school_admin) ✅
- School-level authorization for staff ✅
- Input validation via Pydantic ✅
- Parameterized SQL ✅

### Database
- 15 tables created and seeded ✅
- 20 schools ✅
- 30,000 students ✅
- 30,000 enrollments (AY 2026-2027) ✅
- 2 users (1 parent, 1 school_admin) ✅
- 1 guardian profile ✅
- 1 verified student-guardian link ✅
- 2 pending update requests ✅
- 1 change log entry ✅
- Existing backup: `nagriksetu_backup_before_rebuild.db` ✅

### Frontend (Current State)
- React 19 + Vite 8 build pipeline ✅
- Dashboard page with stat cards ✅
- School directory with search ✅
- Student records table with standard/section filter ✅
- Nginx serving static build on port 5173 ✅

---

## ❌ Missing Features (To Be Built)

### Frontend
- [ ] Government-style public homepage
- [ ] Public school search (no auto-load)
- [ ] Public school profile page
- [ ] Login page
- [ ] Registration page (parent accounts)
- [ ] React Router multi-page navigation
- [ ] Parent dashboard (My Children, Link My Child, Requests)
- [ ] Link My Child form and workflow
- [ ] Correction request submission form
- [ ] Correction request status tracking
- [ ] School staff dashboard
- [ ] Linking request review interface
- [ ] Correction request review interface
- [ ] School administrator dashboard
- [ ] Platform administrator dashboard
- [ ] AI assistant widget
- [ ] Mobile-responsive government header/footer
- [ ] Breadcrumb navigation
- [ ] Pagination component
- [ ] Accessible form components

### Backend
- [ ] `POST /auth/register` — parent registration
- [ ] `POST /auth/logout` — logout
- [ ] `GET /public/schools/search` — public-specific search endpoint
- [ ] `GET /public/schools/{id}` — public-specific profile endpoint
- [ ] `POST /parent/linking-requests` — submit linking request
- [ ] `GET /parent/linking-requests` — list own linking requests
- [ ] `GET /parent/linking-requests/{id}` — get linking request detail
- [ ] `GET /school/linking-requests` — staff view pending linking
- [ ] `POST /school/linking-requests/{id}/review` — staff approve/reject linking
- [ ] `/admin/*` — platform admin endpoints
- [ ] `POST /ai/chat` — AI assistant endpoint
- [ ] General `audit_logs` table and logging
- [ ] `linking_requests` table

### Database
- [ ] `linking_requests` table
- [ ] `audit_logs` general table
- [ ] `users.full_name` column
- [ ] `student_guardians.linking_request_id` column

---

## 🐛 Known Bugs

| # | Location | Description | Severity |
|---|---|---|---|
| 1 | `backend/main.py:300` | `get_school_students` function defined twice; second is dead code (no `@app.get` decorator) | Medium |
| 2 | `backend/main.py:1,607` | `import uuid` duplicated | Low |
| 3 | `.env` | `JWT_SECRET_KEY=PASTE_YOUR_GENERATED_SECRET_HERE` — placeholder value | High |

---

## ⚠️ Security Concerns

| # | Description | Plan |
|---|---|---|
| 1 | JWT secret is a placeholder in `.env` | Replace with cryptographically random value before any production use |
| 2 | No rate limiting on `/auth/login` | Add in Phase 14 (deployment) |
| 3 | Frontend stores JWT in localStorage (XSS risk) | Document limitation; consider httpOnly cookie in production |
| 4 | No email/phone verification on registration | Label as demonstration; implement in Phase 6 |

---

## 🔧 Implementation Phases

| Phase | Description | Status |
|---|---|---|
| 1 | Existing Inspection | ✅ DONE |
| 2 | Architecture Documents | 🔄 IN PROGRESS |
| 3 | Government Design System | ⏳ NEXT |
| 4 | Public Homepage | ⏳ |
| 5 | Public School Discovery | ⏳ |
| 6 | Authentication | ⏳ |
| 7 | Role-Based Authorization | ⏳ |
| 8 | Parent-Child Linking | ⏳ |
| 9 | Student Records | ⏳ |
| 10 | Correction Requests | ⏳ |
| 11 | AI Assistant | ⏳ |
| 12 | Accessibility | ⏳ |
| 13 | Full Testing | ⏳ |
| 14 | Deployment | ⏳ |
| 15 | Final Documentation | ⏳ |

---

## 📋 Checklist

| Item | Status |
|---|---|
| Backend health check passing | ✅ |
| School API returning data | ✅ |
| Student filter (SCH011, Std 1, Sec C) confirmed working | ✅ |
| Database backup exists | ✅ |
| Planning artifacts created | ✅ |
| Architecture document created | ✅ |
| No destructive changes made | ✅ |
| Existing containers untouched | ✅ |
