# NagrikSetu Skill Development & Training Centre Management Microservice
## Comprehensive Architecture, API Specification & Deployment Guide

**Version:** 2.0.0 (Production-Ready Final Release)  
**Author:** Final Year Engineering Project Team  
**Platform:** NagrikSetu – AI-Powered Citizen Opportunity, Welfare & Employment Intelligence Platform  
**Target Environment:** Docker, FastAPI, React 18, Vite, MySQL 8.4, RabbitMQ  

---

## 1. Executive Summary & Architecture Overview

NagrikSetu Skill Development is a full-stack, enterprise-grade public service microservice providing career-aligned skill exploration, training centre discovery, admissions management, and verifiable digital certification for citizens across Karnataka.

### System Architecture Diagram

```
+-----------------------------------------------------------------------------------------+
|                                    CLIENT LAYER                                         |
|  React 18 + TypeScript + Vite + Leaflet GPS Maps (Desktop, Tablet, Mobile Responsive)   |
|  - Public Portal & Explore Skills        - Citizen Dashboard & Profile Locker           |
|  - Training Centre Admin Workspace       - Department Platform Admin Desk               |
+-----------------------------------------------------------------------------------------+
                                             |
                                  HTTP / JSON (REST API)
                                             |
+-----------------------------------------------------------------------------------------+
|                                   GATEWAY LAYER                                         |
|  Nginx Reverse Proxy (:5173 / :5178 Gateway)                                           |
|  CORS Whitelisting, Static Asset Delivery, Request Buffering                            |
+-----------------------------------------------------------------------------------------+
                                             |
                                     FastAPI Backend (:8000)
                                             |
+-----------------------------------------------------------------------------------------+
|                                   APPLICATION LAYER                                     |
|  - JWT Authentication & RBAC             - PBKDF2 Password & SHA-256 OTP Engines        |
|  - Dynamic Explore Skills Discovery      - Centre-Scoped Tenant Isolation Manager       |
|  - Attendance & Progress State Machine   - Assessment & Tamper-Proof Certificate Engine |
|  - Skill Gap Matching Engine             - RabbitMQ AMQP Event Publisher                |
+-----------------------------------------------------------------------------------------+
                          |                                           |
               SQLAlchemy ORM (Connection Pool)              pika / AMQP 0-9-1
                          |                                           |
+------------------------------------+             +--------------------------------------+
|          DATABASE LAYER            |             |           MESSAGING LAYER            |
|  MySQL 8.4 Server (:3308)          |             |  RabbitMQ Message Broker (:5672)     |
|  - 18 Training Centres             |             |  Exchange: `nagriksetu.skill.events` |
|  - 118 Skills & 118 Programmes     |             |  Topics: CITIZEN_REGISTERED,         |
|  - 222 Batches & 97 Accounts       |             |          ENROLLMENT_SUBMITTED,       |
|  - 68 Dossiers & 12 Certificates   |             |          CERTIFICATE_ISSUED          |
+------------------------------------+             +--------------------------------------+
```

---

## 2. User Roles & Tenant Isolation Policy

| Role | Access Boundary | Authentication Mechanism | Available Workspaces |
| :--- | :--- | :--- | :--- |
| **`CITIZEN`** | Personal dossiers, skill profile, course catalog, applications. Strictly isolated from other citizens. | Email + Password OR 6-Digit Email OTP | Public Gateway, Explore Skills, My Enrolments, My Profile, Certificates, Gap Analysis |
| **`TRAINING_CENTRE_ADMIN`** | Strictly isolated to the single training centre assigned to their account (`centre_id`). Cannot access or mutate other centres' records. | Email + Password (Assigned via Admin Desk) | Centre Overview, Batches, Student Dossiers, Attendance, Assessments, Faculty, Progress |
| **`SKILL_DEPARTMENT_ADMIN`** / **`GOVERNMENT_ADMIN`** | System-wide oversight across all 18 centres, scheme approvals, audit trails, account provisioning. | Email + Password (Platform Root Credential) | Department Desk, Applications Review, Accredited Centre Management, Analytics, Audit |

---

## 3. Core API Endpoints

### 3.1 Public Discovery & Information
- `GET /health` — Microservice health, MySQL connection status, version.
- `GET /api/categories` — Returns all 10 skilling sectors with aggregate course and batch metrics.
- `GET /api/categories/{id_or_code}` — Returns category details, affiliated skills, training programmes, centres, and active batches.
- `GET /api/skills?page=1&limit=12` — Paginated skill catalogue with keyword and sector filtering.
- `GET /api/programmes` — Accredited training programmes with prerequisites and delivery modes.
- `GET /api/centres` — Training centres with geocoded coordinates, facilities, and contact details.
- `GET /api/trainers` — Certified faculty directory with mentor credentials and schedules.
- `GET /api/certificates` — Publicly verifiable digital credentials with tamper-proof verification hashes.

### 3.2 Authentication & Security
- `POST /api/otp/send` — Dispatches 6-digit OTP code bound to purpose (`LOGIN`, `REGISTRATION`, `PASSWORD_RESET`, `SET_PASSWORD`).
- `POST /api/otp/verify` — Validates code against SHA-256 session hash (5-min expiry, max 5 attempts).
- `POST /api/auth/register` — Citizen registration with mandatory verified OTP and PBKDF2 password setup.
- `POST /api/auth/login` — Dual sign-in supporting password or verified OTP.
- `POST /api/auth/reset-password` — OTP-authenticated password recovery.
- `POST /api/auth/set-password` — Password provisioning for existing passwordless citizen accounts.
- `POST /api/auth/change-password` — Authenticated password rotation requiring current password.

### 3.3 Training Centre Administration (Strict Centre Isolation)
- `GET /api/centre-admin/dashboard` — Overview metrics scoped to authenticated admin's `centre_id`.
- `GET /api/centre-admin/enrollments` — Candidate dossiers applied to this centre's batches.
- `PATCH /api/centre-admin/enrollments/{id}/review` — Accept or Reject application with mandatory reason.
- `GET /api/centre-admin/batches` — Batches scheduled at this centre.
- `POST /api/centre-admin/batches` — Provision new training batch.
- `GET /api/centre-admin/trainers` — Faculty allocated to this centre.

### 3.4 Platform Administration (State-wide Governance)
- `GET /api/admin/dashboard` — State-wide KPIs across all 18 centres and 118 programmes.
- `GET /api/admin/enrollments` — Global application queue with status filtering.
- `PATCH /api/admin/enrollments/{id}/review` — Official department approval/rejection.
- `POST /api/admin/centres/{id}/admin-account` — Provision training centre administrator account.

---

## 4. Docker Deployment Instructions

### Prerequisites
- Docker Engine 24+ & Docker Compose v2+
- Ports: `5173` (Frontend), `8003` (Backend), `3308` (MySQL), `5672`/`15672` (RabbitMQ)

### Commands to Run the Application

```bash
# 1. Clone or extract the project
cd C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL

# 2. Configure environment (copy safe template)
cp .env.example .env

# 3. Start all services in background
docker compose up -d

# 4. Verify running containers
docker compose ps

# 5. Access the web interface
# Web Application: http://localhost:5173 (or http://127.0.0.1:5178 via host gateway)
# Backend Swagger Docs: http://localhost:8003/docs
# RabbitMQ Management: http://localhost:15672 (guest/guest)
```

---

## 5. Verification & Test Execution

```bash
# Execute backend test suite in Docker container
docker exec -w /app -e PYTHONPATH=/app nagriksetu-skill-backend pytest tests/ -v
```
*Result: 9 of 9 unit and integration tests passing in under 4 seconds.*
