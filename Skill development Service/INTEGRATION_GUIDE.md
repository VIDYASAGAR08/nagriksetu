# NagrikSetu Skill Development Microservice — Integration Guide

This guide details the architecture, API contracts, database schema, RabbitMQ event broker topics, and inter-service integration patterns for the **NagrikSetu Skill Development Microservice** (Member 2).

---

## 1. Microservice Architecture

The Skill Development Service is built as an autonomous, domain-driven microservice in FastAPI and MySQL 8.4:
- **Port:** `8003` (Configurable via `SKILL_BACKEND_PORT`)
- **Default Database:** `skill_db` (MySQL 8.4, isolated schema)
- **Message Broker:** RabbitMQ topic exchange `nagriksetu.events`
- **Security Protocol:** PBKDF2-SHA256 password hashing with HMAC-SHA256 stateless Bearer JWT tokens.

```
                    +------------------------------------+
                    |     Main NagrikSetu Gateway /      |
                    |         Frontend Service           |
                    +-----------------+------------------+
                                      |
                      REST API Calls  | (Port 8003)
                                      v
                    +------------------------------------+
                    |  Skill Development Microservice    |
                    |          (FastAPI 2.0)             |
                    +--------+------------------+--------+
                             |                  |
           Domain State      |                  | Publishes Events
          (CRUD Operations)  |                  | (skill.training.*)
                             v                  v
                    +----------------+  +----------------+
                    |  MySQL 8.4     |  | RabbitMQ Topic |
                    |  (skill_db)    |  | Exchange       |
                    +----------------+  +----------------+
```

---

## 2. API Overview (46 Operations / 41 Unique Paths)

All routes are prefixed under `/api` (plus root `/health`).

### A. Health & System
| Method | Path | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/health` | No | Reports microservice status and live MySQL 8.4 connection status. |

### B. Authentication & Identity
| Method | Path | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/api/auth/register` | No | Registers citizen, creates Account + CitizenProfile, returns JWT. |
| `POST` | `/api/auth/login` | No | Authenticates user credentials, returns JWT with role and citizen ref. |
| `GET` | `/api/auth/me` | Yes (Any) | Returns current authenticated user claims. |

### C. Skill & Course Catalog (NSQF Aligned)
| Method | Path | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/categories` | No | Lists all 10 vocational skill categories with icons and stats. |
| `GET` | `/api/skills` | No | Lists all accredited skills with optional category filter. |
| `GET` | `/api/skills/{code_or_id}` | No | Retrieves detailed skill record and modules by ID or code. |
| `GET` | `/api/programmes` | No | Lists all 104 NSQF training programmes with filter parameters. |
| `GET` | `/api/programmes/{code_or_id}` | No | Retrieves specific training programme and active batches. |
| `GET` | `/api/centres` | No | Lists all 5 certified skilling centres across Karnataka. |
| `GET` | `/api/trainers` | No | Lists certified vocational master trainers. |

### D. Citizen Portfolios & Enrolments
| Method | Path | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/profiles/me` | Yes (Citizen) | Returns authenticated citizen's personal profile and dossier. |
| `PUT` | `/api/profiles/me` | Yes (Citizen) | Updates education, experience, career goal, and category. |
| `POST` | `/api/profiles/me/skills` | Yes (Citizen) | Adds a self-reported or certified skill to citizen profile. |
| `DELETE`| `/api/profiles/me/skills/{skill_id}` | Yes (Citizen) | Removes a skill from citizen profile. |
| `POST` | `/api/enrollments` | Yes (Citizen) | Submits training application for a specific program/batch. |
| `GET` | `/api/enrollments/me` | Yes (Citizen) | Returns all applications and enrolments for current citizen. |
| `GET` | `/api/enrollments/{code_or_id}` | Yes (Citizen/Admin)| Retrieves detailed application dossier and status timeline. |

### E. Assessments, Attendance & Verifiable Certificates
| Method | Path | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/certificates` | Yes (Citizen) | Lists all certificates issued to authenticated citizen. |
| `GET` | `/api/certificates/verify/{certificate_code}`| No (Public) | Public verification endpoint for QR code certificate verification. |

### F. Skill Gap Engine & Job Recommendations
| Method | Path | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/skill-gap/roles` | No | Lists supported career roles with market demand descriptions. |
| `POST` | `/api/skill-gap/analyze` | Optional | Rule-based engine comparing user skills to target role requirements. |
| `GET` | `/api/jobs` | Optional | Queries downstream employment opportunities or cached openings. |
| `POST` | `/api/jobs/{job_id}/save` | Yes (Citizen) | Bookmarks a job opening for current citizen. |
| `GET` | `/api/jobs/saved` | Yes (Citizen) | Returns all bookmarked jobs for authenticated citizen. |

### G. Department Administration Operations (`SKILL_DEPARTMENT_ADMIN`)
| Method | Path | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/admin/dashboard` | Yes (Admin) | Aggregated administrative metrics, counts, and review queues. |
| `GET` | `/api/admin/enrollments` | Yes (Admin) | Paginated list of citizen enrolments with status filter. |
| `PATCH`| `/api/admin/enrollments/{id}/review` | Yes (Admin) | Approves or rejects an enrolment with mandatory officer remarks. |
| `GET` | `/api/admin/enrollments/{id}/attendance`| Yes (Admin) | Retrieves attendance log for an enrolment. |
| `POST` | `/api/admin/enrollments/{id}/attendance`| Yes (Admin) | Records session attendance (Present, Absent, Late). |
| `GET` | `/api/admin/enrollments/{id}/modules` | Yes (Admin) | Lists modular syllabus progress for an enrolment. |
| `PATCH`| `/api/admin/enrollments/{id}/modules` | Yes (Admin) | Updates modular completion percentage. |
| `GET` | `/api/admin/enrollments/{id}/assessments`| Yes (Admin) | Lists practical and theory assessment scores. |
| `POST` | `/api/admin/enrollments/{id}/assessments`| Yes (Admin) | Records exam score, max marks, and passed status. |
| `PATCH`| `/api/admin/enrollments/{id}/progress` | Yes (Admin) | Updates overall progress percentage and status. |
| `GET` | `/api/admin/enrollments/{id}/eligibility` | Yes (Admin) | Checks 80% attendance and module completion eligibility. |
| `POST` | `/api/admin/enrollments/{id}/issue-certificate` | Yes (Admin) | Generates verifiable certificate and triggers RabbitMQ event. |
| `POST` | `/api/admin/skills` | Yes (Admin) | Creates new skill standard. |
| `PUT` | `/api/admin/skills/{skill_id}` | Yes (Admin) | Modifies skill attributes. |
| `DELETE`| `/api/admin/skills/{skill_id}` | Yes (Admin) | Soft-deactivates skill standard. |
| `POST` | `/api/admin/programmes` | Yes (Admin) | Creates NSQF training programme. |
| `POST` | `/api/admin/batches` | Yes (Admin) | Creates training batch for a programme and centre. |
| `PATCH`| `/api/admin/batches/{batch_id}/seats` | Yes (Admin) | Adjusts max seat capacity for a batch. |
| `POST` | `/api/admin/trainers` | Yes (Admin) | Registers certified trainer. |
| `POST` | `/api/admin/centres` | Yes (Admin) | Registers skilling centre. |
| `GET` | `/api/admin/audit` | Yes (Admin) | Retrieves immutable administrative audit trail. |

---

## 3. RabbitMQ Message Broker Integration

The service publishes domain events to the **`nagriksetu.events`** topic exchange.

### Event Topics Published:
1. **`skill.training.enrolled`**
   - **Trigger:** Citizen submits course enrolment.
   - **Payload:**
     ```json
     {
       "event_type": "TRAINING_ENROLLED",
       "producer_service": "skill-development-service",
       "occurred_at": "2026-11-08T12:00:00Z",
       "enrollment_id": 1,
       "application_id": "SKL-ENR-2026-1001",
       "citizen_ref": "CT-KA-2026-0001",
       "program_code": "PRG-IT-001",
       "status": "APPLIED"
     }
     ```
2. **`skill.training.updated`**
   - **Trigger:** Admin approves/rejects application, or progress updates.
   - **Payload:** Includes `application_id`, `new_status`, `reviewer_notes`.
3. **`skill.certificate.issued`**
   - **Trigger:** Course completion & digital certificate issuance.
   - **Payload:** Includes `certificate_code`, `citizen_ref`, `program_name`, `grade`, `issue_date`.

### How Main NagrikSetu Application Consumes Events:
In your consumer microservice (e.g. Employment or Welfare service):
```python
import pika

connection = pika.BlockingConnection(pika.URLParameters("amqp://user:pass@localhost:5672/"))
channel = connection.channel()
channel.exchange_declare(exchange="nagriksetu.events", exchange_type="topic", durable=True)

# Declare consumer queue and bind to skill events
queue_name = channel.queue_declare(queue="employment_skill_intake", durable=True).method.queue
channel.queue_bind(exchange="nagriksetu.events", queue=queue_name, routing_key="skill.#")

def callback(ch, method, properties, body):
    print("Received skill event:", method.routing_key, body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=queue_name, on_message_callback=callback)
channel.start_consuming()
```

---

## 4. Database Schema (19 Tables)

The microservice owns the following tables in its isolated schema:
1. `accounts` — Citizen and administrative user accounts (Argon2id/PBKDF2 salted hashes).
2. `categories` — High-level training industry categories.
3. `skills` — Granular competencies and curriculum standards.
4. `skill_modules` — Weekly / modular breakdown for each skill.
5. `training_centres` — Physical accredited training facilities with GPS locations.
6. `trainers` — Certified vocational instructors.
7. `training_programs` — Complete NSQF aligned training courses.
8. `batches` — Timed classroom cohorts with strict seat capacity.
9. `citizen_profiles` — Citizen skilling dossiers and baseline education.
10. `citizen_skills` — Citizen's self-declared and certified skills.
11. `enrollments` — Master applications and course registrations.
12. `enrollment_status_history` — Immutable audit log of status changes.
13. `attendance_records` — Daily session attendance.
14. `module_progress` — Progress tracking per module.
15. `assessment_results` — Theory and practical examination marks.
16. `certificates` — Verifiable digital certificates with tamper-proof codes.
17. `saved_jobs` — Citizen job bookmarks.
18. `audit_logs` — Administrative governance trail.
19. `alembic_version` — Database migration state.
