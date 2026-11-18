# NagrikSetu: Comprehensive REST API Specifications

**Document Version:** 1.0.0  
**Framework:** FastAPI 0.109+ (Python 3.9+)  
**Total Endpoints:** 140  
**Base URL:** `http://localhost:8000/api`  
**Authentication Scheme:** Bearer JWT (Authorization Header)  

---

## 1. API Domain Overview

The 140 FastAPI endpoints implemented in NagrikSetu are partitioned into 12 functional domains:

| Domain Prefix | Functional Scope | Primary Roles Allowed |
| :--- | :--- | :--- |
| `/api/auth` | Authentication, Token Issuance, Password Reset, Student Activation | Public, Student, Parent, Staff, Admin |
| `/api/schools` | Institutional Directory, Multi-Tier Profiles, Infrastructure & Comparison | Public (Read), Platform Admin (Write) |
| `/api/programs` | Academic Programs, Degrees, PU Combinations, Sections | Public (Read), Academic Admin (Write) |
| `/api/divisions` | Collegiate Divisions, University Faculties, Campus Locations | Public (Read), Institution Admin (Write) |
| `/api/admissions` | Stage 1 Applications, Determinations, Stage 2 Dossier Submissions | Parent, Admissions Officer, Admin |
| `/api/documents` | Verification Desk, Uploads, Authenticated Preview, Accept/Reject | Parent (Upload), Admin/Staff (Review) |
| `/api/students` | 30K Student Roster, Permanent ID Lookup, Demographic Management | Academic Admin, Records Officer |
| `/api/enrollments` | Section Allocations, Annual Transitions, Academic Status | Academic Admin, Staff |
| `/api/attendance` | Daily Classroom Roster Logging, Aggregations & Tally Reports | Classroom Teacher, Academic Admin |
| `/api/examinations`| Term Exams, Grading Configurations, Batch Scorecard Entry | Examination In-Charge, Staff |
| `/api/notifications`| In-App Messaging, Alert Dispatch, Delivery Audit Logging | Authenticated Users (Grounded) |
| `/api/platform` | State Platform Governance, Zero-Token Provisioning, System Audits | Platform Administrator |

---

## 2. Key Endpoint Specifications

### 2.1 Authentication & Student Activation

#### `POST /api/auth/login`
- **Description:** Authenticates a user with email and password, returning JWT bearer token and institution context.
- **Request Body:**
```json
{
  "email": "ksrao@ballari.edu.in",
  "password": "SecurePassword123"
}
```
- **Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "usr_9921",
    "full_name": "K.S Rao",
    "role": "school_admin",
    "institution_id": "SCH019",
    "institution_name": "Ballari Education School"
  }
}
```

#### `POST /api/auth/lookup-student`
- **Description:** Secure database lookup of enrolled student identity using Permanent Student ID prior to account activation.
- **Request Body:**
```json
{
  "permanent_student_id": "NS-SCH019-STD06-166"
}
```
- **Response `200 OK`:**
```json
{
  "found": true,
  "student_name": "Ishaan Verma",
  "institution_id": "SCH019",
  "institution_name": "Ballari Education School",
  "standard": "Standard 6",
  "section": "A",
  "is_activated": false
}
```

---

### 2.2 Admission Lifecycle & Verification Desk

#### `POST /api/admissions/apply`
- **Description:** Submits Stage 1 preliminary admission application from parent portal.
- **Request Body:**
```json
{
  "institution_id": "SCH019",
  "applicant_name": "Aarav Sharma",
  "parent_name": "Vikram Sharma",
  "parent_phone": "9876543210",
  "parent_email": "vikram@example.com",
  "requested_standard": "Standard 1",
  "academic_year": "2026-2027"
}
```
- **Response `201 Created`:**
```json
{
  "application_id": "APP-2026-083",
  "status": "submitted",
  "message": "Stage 1 application successfully submitted."
}
```

#### `POST /api/admissions/{application_id}/action`
- **Description:** Institution administrator executes determination (approve, reject, clarify) on Stage 1 application.
- **Request Body:**
```json
{
  "action": "approve",
  "reviewer_notes": "Preliminary eligibility verified. Proceeding to Stage 2 dossier submission."
}
```
- **Response `200 OK`:**
```json
{
  "application_id": "APP-2026-083",
  "previous_status": "submitted",
  "new_status": "approved",
  "updated_at": "2026-11-04T12:00:00Z"
}
```

#### `POST /api/admissions/documents/{document_id}/verify`
- **Description:** Institution admin accepts and marks an uploaded document as verified.
- **Response `200 OK`:**
```json
{
  "document_id": "DOC-9012",
  "verification_status": "VERIFIED",
  "verified_by": "usr_9921",
  "verified_at": "2026-11-04T12:10:00Z",
  "message": "Document successfully verified."
}
```

#### `POST /api/admissions/documents/{document_id}/reject`
- **Description:** Rejects document with mandatory defect reason and notifies parent for re-upload.
- **Request Body:**
```json
{
  "rejection_reason": "Illegible Scan",
  "rejection_notes": "Marks card image is blurry. Please upload a clear 300 DPI scan."
}
```

---

### 2.3 Academic Programs & Cascading Filters

#### `GET /api/schools/{school_id}/programs`
- **Description:** Retrieves all academic programs configured for an institution with validated combination codes.
- **Response `200 OK`:**
```json
[
  {
    "program_id": "PROG-PU-01",
    "program_name": "Pre-University Science",
    "education_level": "higher_secondary",
    "discipline_or_stream": "Science",
    "combination_code": "PCMB",
    "duration_years": 2
  },
  {
    "program_id": "PROG-PU-02",
    "program_name": "Pre-University Science",
    "education_level": "higher_secondary",
    "discipline_or_stream": "Science",
    "combination_code": "PCMC",
    "duration_years": 2
  }
]
```

---

## 3. Status Codes & Error Handling Standard

The API enforces strict RFC-7807 problem details:
- `200 OK`: Successful resource query or state transition.
- `201 Created`: Successful entity creation (Application, Student, User).
- `400 Bad Request`: Malformed payload, invalid combination code, or duplicate student lookup.
- `401 Unauthorized`: Missing, expired, or invalid JWT token.
- `403 Forbidden`: Mismatched institutional tenancy or insufficient role permissions.
- `404 Not Found`: Target entity not found in active institution scope.
- `422 Unprocessable Entity`: Schema validation errors (Pydantic).
- `500 Internal Server Error`: Unhandled database exception (logged with stack trace).
