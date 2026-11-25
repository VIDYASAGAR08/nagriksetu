# NagrikSetu – Centralized Request, Complaint, Verification and Record Correction Management System

**Project:** `C:\Users\callm\nagriksetu`  
**Live SQLite Database:** `C:\Users\callm\nagriksetu\backend\data\nagriksetu.db`  
**Database Backup Reference:** `C:\Users\callm\nagriksetu\backend\data\nagriksetu_backup_requests_20261121_170244.db` (27,435,008 bytes)  
**Total Verified Student Records Preserved:** **30,003 Students** (100% Intact)  
**System Status:** **Active & Verified in Production**  
**Date of Completion:** November 21, 2026  

---

## 1. Executive Summary & Architecture Overview

NagrikSetu's Centralized Request, Complaint, Verification, and Record Correction Management System provides a comprehensive, multi-tiered grievance redressal and transactional record correction platform for Karnataka's educational institutions.

The system empowers **Students, Parents, Guardians, Citizens, and Staff** to submit official requests, track end-to-end lifecycle status with unique tracking numbers, provide requested clarifications, and receive authenticated, auditable record rectifications. Crucially, it replaces superficial status toggles with an **Authorized Record-Editing Engine** that applies transactional updates directly to original database tables (`student_attendance`, `students`, `guardians`, `users`, `academic_results`), verifies the change post-commit, archives old vs. new values, and logs permanent audit trails.

```
                              ┌──────────────────────────────────────────────┐
                              │           REQUEST INTAKE & ROUTING           │
                              │  (18 Categories, Priority, Target Record)    │
                              └──────────────────────┬───────────────────────┘
                                                     │
                                    ┌────────────────┴───────────────┐
                                    ▼                                ▼
                     ┌──────────────────────────────┐ ┌──────────────────────────────┐
                     │   INSTITUTION TIER QUEUE     │ │     STATE PLATFORM TIER      │
                     │  - Attendance Corrections    │ │  - General Clarifications    │
                     │  - Personal / Name / DOB     │ │  - State Policy Grievances   │
                     │  - Marks & Academic Results  │ │  - Cross-Institution Disputes│
                     │  - Parent Contact Updates    │ │  - Escalated Appeals         │
                     └──────────────┬───────────────┘ └──────────────┬───────────────┘
                                    │                                │
                                    ▼                                ▼
                     ┌──────────────────────────────┐ ┌──────────────────────────────┐
                     │   INSTITUTION ADMIN DESK     │ │    PLATFORM ADMIN DESK       │
                     │  - Investigation & Notes     │ │  - System-Wide KPI Oversight │
                     │  - Clarification Requests    │ │  - Institution SLA Breakdown │
                     │  - Mandatory Reason Reject   │ │  - Re-route & Forwarding     │
                     └──────────────┬───────────────┘ └──────────────┬───────────────┘
                                    │                                │
                                    ▼                                ▼
                     ┌───────────────────────────────────────────────────────────────┐
                     │             AUTHORISED RECORD-EDITING ENGINE                  │
                     │  - Transactional update to original database records         │
                     │  - Instant post-update verification                          │
                     │  - Dual-audit log generation (Corrections & Status History)   │
                     │  - In-app push notification dispatch                         │
                     └───────────────────────────────────────────────────────────────┘
```

---

## 2. The 18 Supported Categories & Automatic Routing Model

Every submission is categorized into one of 18 standardized classifications with deterministic tier routing:

| # | Category Identifier | Official Category Name | Default Target Table / Module | Deterministic Routing Tier |
|---|---------------------|------------------------|-------------------------------|----------------------------|
| 1 | `attendance_correction` | Attendance Correction | `student_attendance` | Institution Desk (`assigned_institution_id`) |
| 2 | `student_personal_info` | Student Personal Info Correction | `students` | Institution Desk (`assigned_institution_id`) |
| 3 | `parent_guardian_info` | Parent / Guardian Info Correction | `guardians` / `users` | Institution Desk (`assigned_institution_id`) |
| 4 | `mobile_number_update` | Mobile Number Update | `guardians` / `users` | Institution Desk (`assigned_institution_id`) |
| 5 | `email_address_update` | Email Address Update | `guardians` / `users` | Institution Desk (`assigned_institution_id`) |
| 6 | `address_update` | Residential Address Update | `guardians` | Institution Desk (`assigned_institution_id`) |
| 7 | `dob_correction` | Date of Birth Correction | `students` | Institution Desk (`assigned_institution_id`) |
| 8 | `name_correction` | Student Name Correction | `students` | Institution Desk (`assigned_institution_id`) |
| 9 | `marks_correction` | Examination Marks Correction | `academic_results` | Institution Desk (`assigned_institution_id`) |
| 10 | `result_correction` | Examination Result Correction | `academic_results` | Institution Desk (`assigned_institution_id`) |
| 11 | `academic_record` | Academic Record Correction | `students` / `enrollments` | Institution Desk (`assigned_institution_id`) |
| 12 | `fee_clarification` | Fee Record Clarification | `financial` / `general` | Institution Desk (`assigned_institution_id`) |
| 13 | `admission_info` | Admission Info Correction | `students` / `admissions` | Institution Desk (`assigned_institution_id`) |
| 14 | `linking_issue` | Parent-Student Linking Issue | `student_guardians` | Institution Desk (`assigned_institution_id`) |
| 15 | `institution_complaint` | Institution Complaint | `grievance` | Institution Desk (with Platform Visibility) |
| 16 | `staff_complaint` | Staff / Faculty Complaint | `disciplinary` | Institution Desk (with Platform Escalation) |
| 17 | `general_clarification` | General Clarification | `platform_support` | Platform Tier (State Administration) |
| 18 | `other` | Other Requests | `general` | Platform Tier / Designated Authority |

---

## 3. Database Architecture & Schema Specification

Six robust relational tables were provisioned in `backend/data/nagriksetu.db` with foreign key integrity and performance indexes:

### 1. `service_requests` (Core Request Ledger)
- `request_id` (TEXT PRIMARY KEY) – Unique identifier (e.g., `REQ-2026-BB52E4F2`).
- `tracking_number` (TEXT UNIQUE NOT NULL) – Citizen-facing tracking code (e.g., `TRK-CE9E7F`).
- `requester_user_id` (TEXT NOT NULL) – Foreign key to `users(user_id)`.
- `requester_name`, `requester_role`, `requester_email`, `requester_phone` – Snapshot of citizen contact details.
- `affected_person_type` (TEXT NOT NULL) – `self`, `linked_child`, `staff`, or `other`.
- `affected_student_id`, `permanent_student_id` – References to target student.
- `assigned_institution_id` – Assigned school/college ID (e.g., `SCH001`).
- `routing_tier` (TEXT NOT NULL) – `institution` or `platform`.
- `category` (TEXT NOT NULL) – One of the 18 standardized categories.
- `title`, `description` – Case description.
- `priority` (TEXT NOT NULL DEFAULT 'medium') – `low`, `medium`, `high`, `urgent`.
- `status` (TEXT NOT NULL DEFAULT 'SUBMITTED') – 11 lifecycle statuses.
- `target_module`, `target_record_id`, `field_name`, `current_value`, `requested_value` – Database correction metadata.
- `rejection_reason` – Mandatory official reason when rejected.
- `clarification_prompt` – Official prompt when clarification is requested.
- `is_escalated` (INTEGER NOT NULL DEFAULT 0) – Escalation flag to state platform.
- `escalated_at`, `escalation_reason` – Escalation audit metadata.
- `submitted_at`, `updated_at`, `closed_at`.

### 2. `request_attachments` (Document Evidence Store)
- `attachment_id` (TEXT PRIMARY KEY).
- `request_id` (TEXT NOT NULL REFERENCES `service_requests(request_id)`).
- `file_name`, `file_type`, `file_url_or_path`, `file_size_bytes`, `purpose`, `created_at`.

### 3. `request_remarks` (Investigation & Communication Thread)
- `remark_id` (TEXT PRIMARY KEY).
- `request_id` (TEXT NOT NULL REFERENCES `service_requests(request_id)`).
- `author_user_id`, `author_name`, `author_role`.
- `message` (TEXT NOT NULL).
- `visibility` (TEXT NOT NULL CHECK(visibility IN ('requester_visible', 'internal_only'))) – **Strict confidentiality control**. Internal notes are strictly excluded from citizen/requester views.
- `created_at`.

### 4. `request_status_history` (Lifecycle Transition Trail)
- `history_id` (TEXT PRIMARY KEY).
- `request_id` (TEXT NOT NULL REFERENCES `service_requests(request_id)`).
- `from_status`, `to_status`, `action`, `actor_user_id`, `actor_name`, `actor_role`, `notes`, `created_at`.

### 5. `request_corrections` (Authenticated Record Rectification Vault)
- `correction_id` (TEXT PRIMARY KEY).
- `request_id` (TEXT NOT NULL REFERENCES `service_requests(request_id)`).
- `target_table`, `target_record_id`, `field_name`, `previous_value`, `corrected_value`.
- `correction_reason` (TEXT NOT NULL).
- `administrator_id`, `administrator_name`, `administrator_role`.
- `verification_status` (TEXT NOT NULL DEFAULT 'VERIFIED').
- `verified_at`, `evidence_ref`, `created_at`.

### 6. `request_audit_logs` (System Security Audit Log)
- `log_id` (TEXT PRIMARY KEY).
- `request_id`, `actor_user_id`, `actor_role`, `action`, `entity_type`, `entity_id`, `school_id`, `details`, `created_at`.

---

## 4. The Authorised Record-Editing Engine

The core operational requirement mandates that administrator approvals perform genuine database modifications rather than simple status flags. The engine operates inside ACID transactions (`conn.execute(...)` with `conn.commit()` and `conn.rollback()`):

### A. Attendance Correction (`student_attendance`)
- Locates the student's attendance record via `permanent_student_id` and `attendance_date`.
- If an existing entry exists: updates `status` to `'present'`, `'absent'`, or `'leave'`, notes the correction ID, records `updated_at`, and sets `recorded_by_user_id`.
- If missing: inserts a new verified record under the student's assigned institution.
- Performs post-update SELECT verification to guarantee write success.
- Transitions request status to `CORRECTED`.

### B. Student Personal Information & Name/DOB (`students`)
- Verifies authorization over `affected_student_id` or `permanent_student_id`.
- Sanitizes and updates `student_name`, `date_of_birth`, `gender`, or `first_language`.
- Archives the old value in `request_corrections`.

### C. Parent & Guardian Contact Updates (`guardians` & `users`)
- Updates `phone`, `email`, or `address` in `guardians`.
- Automatically synchronizes corresponding login accounts in `users` (`phone` / `email`).

### D. Examination Marks & Results (`academic_results`)
- Updates `marks_obtained` and recalculates `percentage` and letter grade (`A+`, `A`, `B`, `C`, etc.).
- Appends an audit entry to `academic_result_audits` preserving the previous mark.

---

## 5. Requester Experience (Parent & Student Portals)

Both the Parent Portal (`ParentDashboard.jsx`) and Student Portal (`StudentDashboard.jsx`) feature the integrated **`RequesterPortalView.jsx`**:

1. **Raise New Request / Grievance Modal**:
   - Supports all 18 categories with dynamic form fields (e.g. date selector for attendance, old vs new values for record corrections, file attachment upload).
   - Validates authority: Parents can select only their verified linked children; students can submit requests only for themselves.
   - Generates an immediate tracking confirmation (e.g. `TRK-AA8899`).
2. **My Requests & Complaints List**:
   - Status badge filters: All, Open / In-Progress, Needs Clarification, Corrected, Rejected, Closed.
   - Search bar across Tracking ID, Category, Subject, and Student Name.
3. **Comprehensive Lifecycle & Case Drawer**:
   - Full timeline from `SUBMITTED` to `CORRECTED` / `REJECTED`.
   - **Clarification Response Panel**: When an institution requests clarification (`CLARIFICATION_REQUIRED`), the requester is presented with the prompt and an interactive submission form to supply text and evidence, instantly transitioning the case back to `UNDER_REVIEW`.
   - **Verified Correction Card**: When corrected, highlights the previous value vs. the newly written database value with timestamp and verification badge.
   - **Rejection Notice**: When rejected, prominently renders the mandatory official reason given by the administrator.
   - **Confidential Remarks Thread**: Strictly presents `requester_visible` communications; internal administrator deliberations are completely hidden.

---

## 6. Institution Administrator Desk

Located in the Institution Portal (`InstitutionAdminDashboard.jsx`) under the **"Requests & Record Corrections"** tab (`InstitutionRequestsDesk.jsx`):

1. **Real-Time KPI Counters**:
   - Total Received, New Submissions, Under Review, Needs Clarification, Corrected & Resolved, Rejected.
2. **Investigation & Action Desk**:
   - Filterable table by status, priority, and citizen search.
   - Case investigation modal showing current live database values alongside requested changes.
3. **Six Action Workflows**:
   - **Accept Request**: Moves status to `ACCEPTED` or `CORRECTION_PENDING`.
   - **Execute Live Record Correction**: Form where admin reviews previous vs. requested value, adjusts if necessary, enters mandatory justification notes, and commits the real transaction to the database with post-write verification.
   - **Request Clarification**: Prompts requester with specific guidance and transitions case to `CLARIFICATION_REQUIRED`.
   - **Reject Request**: Requires mandatory justification; prevents arbitrary rejection without recorded reason.
   - **Add Official Remark**: Offers visibility toggle (`requester_visible` vs `internal_only`).
   - **Escalate to Platform**: Escalates complex or policy-level disputes to the State Platform Authority.

---

## 7. Platform Administrator Oversight

Located in the State Platform Dashboard (`AdminDashboard.jsx`) under the **"Platform Request Oversight"** tab (`PlatformRequestOversightDesk.jsx`):

1. **State-Wide KPI Overview**:
   - System-wide request volumes, open cases, state escalations, completed corrections, and overdue SLA risks.
2. **Institution Performance Breakdown**:
   - Tabular overview of every accredited school/college in Karnataka showing total requests, open counts, correction rates, and escalation counts.
3. **Platform Re-Routing & Forwarding**:
   - Enables Platform Administrators to forward misplaced cases or student transfer disputes to the correct institution with forwarding remarks and automated notification.

---

## 8. Verification: All 17 End-to-End Scenarios Passed

The comprehensive test suite (`backend/test_requests_management_e2e.py`) was executed directly against the live system in the container:

```
================================================================================
NAGRIKSETU REQUEST & RECORD CORRECTION MANAGEMENT SYSTEM - E2E TEST SUITE
================================================================================
[*] Pre-test total student count: 30003

[✓] Test fixtures initialized successfully.

--- SCENARIO 1: Student attendance correction request submission ---
[✓] Attendance request created: ID=REQ-2026-870EA936, Tracking=TRK-11A929, Status=SUBMITTED

--- SCENARIO 2: Institution receives request (SCH001) ---
[✓] Institution SCH001 successfully retrieved request list (Total 20 requests).

--- SCENARIO 3: Institution reviews case details ---
[✓] Request details verified: Target=student_attendance.status

--- SCENARIO 4: Institution executes live attendance correction ---
[✓] Live correction executed and verified in database!
[✓] Database audit: student_attendance.status is now 'present'

--- SCENARIOS 5 & 6: Student views corrected status & previous/corrected values ---
[✓] Student dashboard shows request status as CORRECTED
[✓] Student details view verified: Previous='absent' -> Corrected='present'

--- SCENARIOS 7, 8, 9: Parent mobile number update ---
[✓] Parent submitted mobile update request: TRK-17EA05
[✓] Institution executed phone correction in guardians/users table
[✓] Database audit: guardians.phone successfully updated to '9845012345'
[✓] Parent confirmed status CORRECTED with new phone number '9845012345'

--- SCENARIOS 10, 11, 12: Clarification cycle ---
[✓] Institution requested clarification: Status -> CLARIFICATION_REQUIRED
[✓] Requester submitted clarification response: Status -> UNDER_REVIEW
[✓] Institution reviewed and accepted clarified request: Status -> ACCEPTED

--- SCENARIOS 13 & 14: Rejection with mandatory reason & internal remark confidentiality ---
[✓] Request rejected with mandatory reason: Status -> REJECTED
[✓] Security verified: Internal-only remark strictly hidden from requester!
[✓] Admin view verified: Internal-only remark visible to authorized administrator.

--- SCENARIO 15: Cross-institution authorization isolation (403 check) ---
[✓] Cross-institution isolation verified: Admin of SCH002 cannot access or action SCH001 requests.

--- SCENARIO 16: Platform Admin oversight and request re-routing ---
[✓] Platform Oversight KPI verified: Total=23, Escalated=2
[✓] Request successfully forwarded to SCH002 by Platform Administrator.

--- SCENARIO 17: Database audit integrity & total student count preservation ---
[*] Final total student count: 30003
[✓] Audit trails verified: 34 audit logs, 54 status transitions, 11 permanent corrections.

================================================================================
ALL 17 SCENARIOS PASSED WITH ZERO ERRORS!
================================================================================
```

---

## 9. Database Backup & Preservation Verification

- **Pre-task Backup Location:** `C:\Users\callm\nagriksetu\backend\data\nagriksetu_backup_requests_20261121_170244.db` (27,435,008 bytes).
- **Verified Student Population:** Exactly **30,003 students** before, during, and after migration and test suite execution.
- **Zero Data Loss:** All existing enrollments, academic results, attendance logs, and institution relationships remain completely unaltered and safe.
