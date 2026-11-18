# NagrikSetu — Master Pre-Implementation Plan
*Locked in before any code changes · 2026-10-30*

---

## 1. IMPLEMENTATION ROADMAP

### Phase Dependencies

```
Phase 1 (Audit)         ✅ DONE
Phase 2 (Architecture)  → must precede all code
Phase 3 (Design System) → must precede Phase 4
Phase 4 (Homepage)      → depends on Phase 3, 6
Phase 5 (School Search) → depends on Phase 4
Phase 6 (Auth)          → depends on Phase 4; backend independent
Phase 7 (AuthZ)         → depends on Phase 6
Phase 8 (Parent-Child)  → depends on Phase 7
Phase 9 (Student Records) → depends on Phase 7
Phase 10 (Corrections)  → depends on Phase 8, 9
Phase 11 (AI Assistant) → depends on Phase 6
Phase 12 (Accessibility) → parallel to Phase 11
Phase 13 (Testing)      → depends on Phase 10
Phase 14 (Deployment)   → depends on Phase 13
Phase 15 (Docs)         → depends on Phase 14
```

### Phase Breakdown

| Phase | Title | Key Deliverables | Status |
|---|---|---|---|
| 1 | Existing Inspection | Audit report, backup confirmation | ✅ DONE |
| 2 | Architecture | ARCHITECTURE.md, DATABASE.md, API.md | 🔄 IN PROGRESS |
| 3 | Design System | CSS variables, reusable components, gov-style header/footer | ⏳ |
| 4 | Public Homepage | New citizen-facing entry, school search (no auto-load), nav | ⏳ |
| 5 | Public School Discovery | Search results, public school profile, no private data | ⏳ |
| 6 | Authentication | Register, Login, Logout, JWT, protected routes | ⏳ |
| 7 | Role-Based AuthZ | Backend permission guards, school-level restrictions | ⏳ |
| 8 | Parent-Child Linking | Link My Child flow, staff verification, approval/rejection | ⏳ |
| 9 | Student Records | Protected access, mandatory std+section, pagination | ⏳ |
| 10 | Correction Requests | Parent submission, staff review, audit log, DB consistency | ⏳ |
| 11 | AI Assistant | Rule-based guide, role-aware, no private data leakage | ⏳ |
| 12 | Accessibility | Semantic HTML, keyboard nav, contrast, GIGW principles | ⏳ |
| 13 | Testing | Backend pytest, frontend smoke tests, integration, Docker | ⏳ |
| 14 | Deployment | Env config, Docker rebuild verification, health checks | ⏳ |
| 15 | Documentation | All docs/\*.md files complete and accurate | ⏳ |

### Frontend Architecture Decision
- Add `react-router-dom` v7 for multi-page routing
- Component hierarchy: pages/ + components/ + contexts/ + hooks/ + utils/
- Auth context (`AuthContext.jsx`) wraps entire app
- Public routes: `/`, `/schools`, `/schools/:id`, `/login`, `/register`
- Protected routes: `/dashboard`, `/parent/*`, `/staff/*`, `/admin/*`
- Existing dashboard functionality moved to `/staff/students`

### Backend Architecture Decision
- Keep monolithic FastAPI; split `main.py` into APIRouter modules
- New files: `routers/public.py`, `routers/auth_routes.py`, `routers/parent.py`, `routers/staff.py`, `routers/admin.py`
- `main.py` becomes the mount point for all routers
- `database.py` gets additive migration functions only
- Dockerfile updated to COPY the entire backend directory

---

## 2. DATABASE MIGRATION PLAN

### Guiding Constraints
- ✅ Zero data loss (20 schools, 30,000 students, 2 users, 1 guardian, etc.)
- ✅ Additive only — no DROP TABLE, no DROP COLUMN, no DELETE
- ✅ All migrations via `database.py:create_tables()` using `ADD COLUMN IF NOT EXISTS`
- ✅ New tables created with `CREATE TABLE IF NOT EXISTS`
- ✅ Database backup verified BEFORE container rebuild
- ✅ Rollback: restore backup file and restart container

### Mapping: Spec Tables → Existing Tables

| Spec Table | Existing Table | Action |
|---|---|---|
| `users` | `users` | Add `full_name` column |
| `parent_student_relationships` | `student_guardians` | Extend with `linking_request_id` FK |
| `linking_requests` | *(none)* | **CREATE NEW** |
| `correction_requests` | `update_requests` | Map existing; add `requester_user_id` alias view |
| `audit_logs` | `school_change_log` (partial) | **CREATE NEW** general audit_logs table |

### New Tables to Create

#### `linking_requests`
```sql
CREATE TABLE IF NOT EXISTS linking_requests (
    request_id       TEXT PRIMARY KEY,
    parent_user_id   TEXT NOT NULL,
    school_id        TEXT NOT NULL,
    student_ref      TEXT,             -- student name/ID reference (NOT verified ID)
    relationship_type TEXT NOT NULL,
    additional_info  TEXT,
    request_status   TEXT NOT NULL DEFAULT 'pending'
        CHECK (request_status IN ('pending','approved','rejected','cancelled')),
    reviewer_id      TEXT,
    reviewer_comment TEXT,
    created_at       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at      TEXT,
    FOREIGN KEY (parent_user_id) REFERENCES users(user_id),
    FOREIGN KEY (school_id)      REFERENCES schools(school_id),
    FOREIGN KEY (reviewer_id)    REFERENCES users(user_id)
);
```

#### `audit_logs`
```sql
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id      TEXT PRIMARY KEY,
    actor_user_id TEXT,
    action        TEXT NOT NULL,
    entity_type   TEXT NOT NULL,
    entity_id     TEXT,
    ip_address    TEXT,
    metadata_json TEXT,
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actor_user_id) REFERENCES users(user_id)
);
```

### Column Additions (Additive)

| Table | Column | Definition | Reason |
|---|---|---|---|
| `users` | `full_name` | `TEXT` | Spec requires full_name; existing rows get NULL |
| `student_guardians` | `linking_request_id` | `TEXT` | FK back to linking_requests |
| `update_requests` | `requester_user_id` | `TEXT` | Alias for guardian-submitted; existing rows NULL |

### Migration Order
1. Back up `nagriksetu.db` → `nagriksetu_pre_phase3_<timestamp>.db`
2. Add `full_name` column to `users`
3. Create `linking_requests` table
4. Add `linking_request_id` column to `student_guardians`
5. Create `audit_logs` table
6. Add `requester_user_id` to `update_requests`
7. Rebuild backend Docker image
8. Verify via `/health` endpoint
9. Verify existing counts unchanged

### Rollback Steps
1. Stop backend container: `docker compose stop backend`
2. Copy backup over live DB: `copy nagriksetu_pre_phase3_<ts>.db nagriksetu.db`
3. Restart with previous image or rebuild

---

## 3. API PLAN

### Prefix Convention
- `/public/*` — No auth, returns only approved public fields
- `/auth/*` — Auth management
- `/parent/*` — Requires JWT + role=parent
- `/school/*` — Requires JWT + role in (school_staff, school_admin)
- `/admin/*` — Requires JWT + role=platform_admin

### Preserve Existing (NO CHANGES)
| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/health` | None | Keep as-is |
| GET | `/` | None | Keep as-is |
| GET | `/schools` | None | Keep as-is |
| GET | `/schools/{id}` | None | Keep as-is |
| GET | `/schools/{id}/students` | None | Keep as-is |
| GET | `/schools/{id}/programs` | None | Keep as-is |
| GET | `/schools/{id}/achievements` | None | Keep as-is |
| GET | `/students/{id}` | None | Keep as-is |
| GET | `/search-schools` | None | Keep for backward compat |
| POST | `/auth/login` | None | Keep as-is |
| GET | `/auth/me` | JWT | Keep as-is |
| GET | `/parent/children` | JWT parent | Keep as-is |
| GET | `/parent/children/{psid}/records` | JWT parent | Keep as-is |
| POST | `/parent/update-requests` | JWT parent | Keep as-is |
| GET | `/parent/update-requests` | JWT parent | Keep as-is |
| GET | `/school/update-requests` | JWT staff | Keep as-is |
| POST | `/school/update-requests/{id}/review` | JWT staff | Keep as-is |

### New Endpoints — Public
| Method | Path | Auth | Response |
|---|---|---|---|
| GET | `/public/schools/search?q=&limit=&offset=` | None | `[{school_id, school_name, district, state, school_type, address}]` |
| GET | `/public/schools/{school_id}` | None | `{school_id, school_name, district, state, school_type, address, established_year, description, public_phone, website, facilities}` |

### New Endpoints — Authentication
| Method | Path | Auth | Body | Response |
|---|---|---|---|---|
| POST | `/auth/register` | None | `{full_name, email, phone, password}` | `{user_id, message}` |
| POST | `/auth/logout` | JWT | — | `{message}` |

### New Endpoints — Parent
| Method | Path | Auth | Body / Params | Response |
|---|---|---|---|---|
| POST | `/parent/linking-requests` | JWT parent | `{school_id, student_ref, relationship_type, additional_info}` | `{request_id, status}` |
| GET | `/parent/linking-requests` | JWT parent | — | `[{request_id, school_id, status, created_at, reviewed_at, reviewer_comment}]` |
| GET | `/parent/linking-requests/{id}` | JWT parent | — | `{request details}` |

### New Endpoints — School Staff
| Method | Path | Auth | Body / Params | Response |
|---|---|---|---|---|
| GET | `/school/linking-requests` | JWT staff | `?status=pending` | `[{request_id, parent_name, student_ref, relationship_type, created_at}]` |
| GET | `/school/linking-requests/{id}` | JWT staff | — | `{full request detail}` |
| POST | `/school/linking-requests/{id}/review` | JWT staff | `{decision, permanent_student_id?, reviewer_comment}` | `{request_id, status}` |

### New Endpoints — Admin
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/admin/users` | JWT admin | List all users (paginated) |
| POST | `/admin/users` | JWT admin | Provision school_staff or school_admin account |
| PATCH | `/admin/users/{id}/role` | JWT admin | Change role |
| GET | `/admin/schools` | JWT admin | Full school list with private fields |
| POST | `/admin/schools` | JWT admin | Register a new school |
| GET | `/admin/audit-logs` | JWT admin | Paginated audit log |
| GET | `/admin/stats` | JWT admin | Platform statistics |

### Error Response Format (Standard)
```json
{"detail": "Human-readable error message"}
```
HTTP status codes: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Validation Error, 500 Internal Server Error.

---

## 4. ROLE-PERMISSION MATRIX

| Operation | public | parent | school_staff | school_admin | platform_admin |
|---|:---:|:---:|:---:|:---:|:---:|
| Search schools (public) | ✅ | ✅ | ✅ | ✅ | ✅ |
| View public school profile | ✅ | ✅ | ✅ | ✅ | ✅ |
| Register (parent account only) | ✅ | — | — | — | — |
| Login | ✅ | ✅ | ✅ | ✅ | ✅ |
| View own profile | — | ✅ | ✅ | ✅ | ✅ |
| Submit linking request | — | ✅ | — | — | — |
| View own linking requests | — | ✅ | — | — | — |
| View own linked children | — | ✅ | — | — | — |
| View child's private records | — | ✅ (verified) | — | — | ✅ |
| Submit correction request | — | ✅ (verified) | — | — | — |
| View own correction requests | — | ✅ | — | — | — |
| View school's student list | — | — | ✅ (assigned) | ✅ (assigned) | ✅ |
| Review linking requests | — | — | ✅ (assigned) | ✅ (assigned) | ✅ |
| Approve/reject linking | — | — | ✅ (assigned) | ✅ (assigned) | ✅ |
| Review correction requests | — | — | ✅ (assigned) | ✅ (assigned) | ✅ |
| Approve/reject corrections | — | — | ✅ (assigned) | ✅ (assigned) | ✅ |
| View school change log | — | — | ✅ (assigned) | ✅ (assigned) | ✅ |
| Manage school info | — | — | — | ✅ (assigned) | ✅ |
| Manage staff accounts | — | — | — | ✅ (assigned) | ✅ |
| Register school (platform) | — | — | — | — | ✅ |
| Manage all users | — | — | — | — | ✅ |
| View all audit logs | — | — | — | — | ✅ |
| Assign/change roles | — | — | — | — | ✅ |

### School-Level Isolation Rules
- `school_staff` and `school_admin` can ONLY access data for `users.school_id = their school_id`
- This is enforced in every backend endpoint that touches student/request data
- Frontend hiding of buttons is NOT sufficient — backend must check every time
- `platform_admin` bypasses school-level isolation but still requires JWT

### Blocked Combinations
- A parent cannot approve their own linking request
- A parent cannot edit official student records directly
- `school_staff` cannot elevate their own role
- Public registration only creates `parent` accounts; `school_staff`/`school_admin`/`platform_admin` are provisioned by admin

---

## 5. SECURITY PLAN

### Authentication
- **Algorithm**: Argon2 (pwdlib) for password hashing — already in use ✅
- **Tokens**: HS256 JWT, 30-minute expiry — already in use ✅
- **Secret**: `JWT_SECRET_KEY` from environment variable — already enforced ✅
- **Storage**: Bearer token in `Authorization` header; frontend stores in memory/localStorage
- **Registration**: `/auth/register` creates `role=parent` ONLY; no public admin/staff registration
- **Password minimum**: 12 characters — already enforced ✅

### Authorization (Backend)
- Every protected endpoint calls `get_current_user()` → fetches from DB → validates `is_active`
- Role checks use explicit `if user["role"] not in (...)` guards
- School-level checks compare `user["school_id"]` against resource's school
- Parent-child access validated via `student_guardians.is_verified = 1`
- `get_authorized_child()` whitelist prevents SQL injection on column names ✅

### Input Validation
- All inputs use Pydantic models with `min_length`, `max_length`, pattern constraints
- SQL uses parameterized queries throughout — no f-string interpolation with user data
- The only f-string SQL is `get_authorized_child()` which uses a hardcoded whitelist ✅
- File uploads not supported in Phase 1

### Secrets Management
- `JWT_SECRET_KEY` in `.env`, passed to container via `docker-compose.yml` env block
- `.env` file is in `.gitignore` — confirmed
- No secrets in frontend JavaScript bundles
- AI API key (if used) goes in backend environment only

### Rate Limiting
- Phase 1: document the need; implement at Nginx level or via middleware in Phase 14
- Login endpoint should be protected from brute force (to be implemented)

### Audit Logging
- All write operations (approve, reject, update student) write to `audit_logs` table
- Existing operations already write to `school_change_log` — keep both
- Audit logs include: `actor_user_id`, `action`, `entity_type`, `entity_id`, `created_at`

### Safe Error Responses
- Never return stack traces in production (`debug=False` default in FastAPI prod)
- Error messages must not reveal internal state, table names, or user enumeration info
- Authentication errors use generic "Incorrect username or password" message ✅

### CORS
- Restrict to `http://localhost:5173` in development
- Update to actual domain in production
- Already configured ✅

---

## 6. BACKUP PLAN

### Pre-Migration Backup (Phase 3 Trigger)
```
Source:  C:\Users\callm\nagriksetu\backend\data\nagriksetu.db
Target:  C:\Users\callm\nagriksetu\backend\data\nagriksetu_pre_phase3_<timestamp>.db
Method:  PowerShell Copy-Item (container stopped or SQLite WAL checkpoint first)
Verify:  Open backup with python3 -c "import sqlite3; ..." and count rows
```

### Existing Backup (Already Present)
- `nagriksetu_backup_before_rebuild.db` ✅ — confirmed in audit

### Per-Phase Backup Policy
| Phase | Backup Required? | Reason |
|---|---|---|
| 2 (Arch docs) | No | No code/DB changes |
| 3 (Design System) | Frontend only | DB unchanged |
| 4 (Homepage) | Frontend rebuild | DB unchanged |
| 5 (School Search) | Backend rebuild | New DB tables |
| 6 (Auth) | **Yes — DB backup** | Adds users columns |
| 8 (Parent-Child) | **Yes — DB backup** | New linking_requests table |
| 10 (Corrections) | **Yes — DB backup** | audit_logs table, record updates |
| 13 (Testing) | No (reads only) | No DB modification |

### Rollback Procedure
1. `docker compose stop backend`
2. `Copy-Item nagriksetu_pre_phase3_<ts>.db nagriksetu.db`
3. If code changes need reverting: git restore or copy .backup files
4. `docker compose build backend`
5. `docker compose up -d backend`
6. `curl http://localhost:8001/health` → must return `{"status":"healthy"}`
7. Verify record counts via inspect script

### Backup Verification Script
```python
import sqlite3
conn = sqlite3.connect('/path/to/backup.db')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
counts = {t[0]: conn.execute(f'SELECT COUNT(*) FROM {t[0]}').fetchone()[0] for t in tables}
print(counts)
# Expected: schools=20, students=30000, enrollments=30000, users=2
conn.close()
```
