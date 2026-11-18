# NagrikSetu: Project Defense Presentation Walkthrough & Slide Guide

**Title**: NagrikSetu: A Unified Multi-Tier Digital Education and Institutional Governance Platform for Karnataka  
**Presenter / Candidate**: S Phalguna (`2023UG000171`)  
**Degree**: Bachelor of Technology (Hons.) in Computer Science & Engineering (Data Science)  
**Supervisor**: Shabbeer Basha, Associate Professor  
**Department**: School of Engineering and Technology, Vidyashilp University, Bangalore – 562110  
**Course Code**: Interdisciplinary Project (DATA802) — November 2026  

---

## Deliverable File Links

- **Main Final PowerPoint Presentation (.pptx)**: [NagrikSetu_Project_Presentation_Final.pptx](file:///C:/Users/callm/nagriksetu/docs/final_project_report/NagrikSetu_Project_Presentation_Final.pptx) (Size: **3.92 MB**, 15 Widescreen 16:9 Slides with 17 embedded high-resolution charts & website UI screenshots)
- **Synced Artifact Presentation Copy**: [NagrikSetu_Project_Presentation_Final.pptx](file:///C:/Users/callm/.gemini/antigravity/brain/010bed14-ca45-4c39-a172-471440a90a20/NagrikSetu_Project_Presentation_Final.pptx)
- **Complete Project Report PDF**: [NagrikSetu_Complete_Project_Report.pdf](file:///C:/Users/callm/nagriksetu/docs/final_project_report/NagrikSetu_Complete_Project_Report.pdf) (4.67 MB)
- **Complete Project Report Word**: [NagrikSetu_Complete_Project_Report.docx](file:///C:/Users/callm/nagriksetu/docs/final_project_report/NagrikSetu_Complete_Project_Report.docx) (2.62 MB)
- **Audited Feature Matrix Excel**: [NagrikSetu_Project_Feature_Matrix.xlsx](file:///C:/Users/callm/nagriksetu/docs/final_project_report/NagrikSetu_Project_Feature_Matrix.xlsx) (22.6 KB)

---

## Slide-by-Slide Content & Visual Structure

### Slide 1: Title Slide (Dark Navy Theme)
- **Header**: Vidyashilp University official coat of arms logo.
- **Main Title**: *NagrikSetu: A Unified Multi-Tier Digital Education and Institutional Governance Platform for Karnataka*.
- **Subtitle**: *Interdisciplinary Project Defense (DATA802) • Bachelor of Technology (Hons.) in CSE (Data Science)*.
- **Presenter Metadata**: Candidate **S Phalguna** (`2023UG000171`) | Project Supervisor: **Shabbeer Basha**, Associate Professor.
- **Institution**: School of Engineering and Technology, Vidyashilp University, Bangalore-562110 (November 2026).
- **Deliverables**: PDF (4.67 MB), DOCX (2.62 MB), XLSX Feature Matrix, 140 REST Endpoints.

---

### Slide 2: Problem Statement (Large, Detailed, & Fully Filled)
- **Category Tag**: *MACRO CHALLENGES & ACUTE SYSTEM DEFICITS*
- **Left Column: The Macroscopic Governance Crisis (5 Acute Failure Modes)**:
  1. **Disconnected Institutional Silos**: K-10 schools, PU colleges, polytechnics, and autonomous universities operate on isolated, incompatible software or manual paper records, causing state-wide data blindspots during student transitions.
  2. **Opaque & Repetitive Admission Pipelines**: Parents must physically visit multiple campuses. Manual demographic entries create repetitive paperwork overhead with zero real-time status visibility.
  3. **Fraud-Prone Document Review Desks**: Administrative review desks lack standardized digital magnification (zoom), verified status stamping, and immutable forensic audit trails, leaving institutions vulnerable to credential tampering.
  4. **Rigid Academic Hierarchy Incompatibility**: Generic ERPs fail to model true multi-tier hierarchies: Standard-Sections vs. PU Science/Commerce combinations (PCMB/EBAC) vs. Polytechnic Semesters vs. University Degree divisions.
  5. **High-Friction Student Account Activation**: Enrolled students encounter activation errors due to strict full-name string matching that rejects minor spelling discrepancies instead of verifying official enrolled IDs.
- **Right Column: Quantitative Deficit Analysis & Architecture Comparison Table**:
  - *4.2 Days → Instant*: Average turnaround time for defect notification to parents via in-app alerts vs postal/phone delays.
  - *38% Verification Overhead*: Administrative working hours wasted manually cross-referencing physical paper certificates against student applications.
  - *100% ID Auto-Population*: Complete elimination of student name mismatch failures during account activation via Permanent Student ID lookups.
  - *Zero Security Leakage*: Zero-token administrative onboarding seals credentials without exposing URLs in the DOM or user interfaces.
  - *Direct Architecture Comparison Table*: Institutional Scope, Admissions Flow, Document Audit, Tenancy/Security, and Data Scale contrasted between Legacy systems and NagrikSetu.

---

### Slide 3: Project Aim & Technical Objectives (Filled 2-Column Layout)
- **Primary Aim Card**: Architect, engineer, and empirically verify an enterprise-grade, multi-tier, multi-tenant digital educational information and governance platform tailored to Karnataka's administrative standards.
- **6 Structured Technical Objectives**:
  1. *Citizen Discovery Portal*: Multi-attribute parametric search across 30 institutions, 31 Karnataka districts, 4 tiers, with side-by-side comparison of up to 4 institutions.
  2. *Two-Stage Admission Lifecycle*: Decouple low-friction initial parent application submissions (Stage 1) from detailed demographic and document onboarding (Stage 2).
  3. *Administrative Tri-Action Review Desk*: Authenticated byte-range preview streaming with 50% to 250% zoom controls, atomic single-click verification badge commits, and a mandatory 5-defect rejection taxonomy with parent alerts.
  4. *Multi-Tier Cascading Curricula Engine*: Dynamically validate academic structures across K-10 standards, Pre-University Science/Commerce combinations (PCMB/EBAC), Polytechnic semesters, and University degree faculties without numeric zero bugs.
  5. *Permanent ID Student Identity Activation*: Deterministic 3-step account activation desk querying the master database by Permanent Student ID (`NS-SCH...`), auto-populating official records in read-only mode to prevent spelling mismatches.
  6. *Multi-Tenant RBAC & Forensic Auditability*: Enforce strict institutional boundary isolation (HTTP 403 Forbidden on cross-tenant probes), zero-token administrator onboarding, and dual-layer immutable forensic audit logging (626 platform + 502 institutional logs).

---

### Slide 4: Full-Stack System Architecture & Multi-Tenant Topology
- **Three-Tier Architectural Layout**:
  - **Client Presentation Layer**: React 19 SPA, TailwindCSS 3.4, Lucide-React, 56 modular component files, Public Discovery Portal, Parent Application Desks, Institution Admin Review Desk, Student Activation Desk, and Platform Admin Staff Provisioning.
  - **API Gateway & Service Layer**: FastAPI (Python 3.9+), Asynchronous REST JSON, 140 REST endpoints, Bearer JWT session controller, Bcrypt password hashing, Two-Stage state automata, 50%–250% byte-range streaming preview, and forensic audit logger.
  - **Data Persistence & Storage Layer**: SQLite 3.35+ in Write-Ahead Logging (WAL) mode, 39 normalized relational tables (3NF), 61,842 total relational entity records, 30,003 master student records with compound B-Tree indexing (`idx_enrollments_lookup`), zero orphan foreign keys, and 100% database integrity verified (`PRAGMA integrity_check = ok`).

---

### Slide 5: Institutional Representation & Academic Scale (Includes 2 Embedded Charts)
- **Left Column**:
  - **Embedded Graph 1**: `graph_institutions.png` — Institutional Distribution Across Karnataka (30 Institutions: 15 Primary & Secondary Schools (50.0%), 5 Pre-University Colleges (16.7%), 5 Polytechnic/Degree Colleges (16.7%), 5 Autonomous Universities (16.7%)).
  - Contextual details: Ballari Education School (`SCH019`), Bangalore High School (`SCH001`), Mangaluru PU College (`SCH011`), Visvesvaraya Technological University (`SCH026`).
- **Right Column**:
  - **Embedded Graph 2**: `graph_programs.png` — 140 Academic Programs Breakdown (50 PU Combinations, 48 Undergraduate Degrees, 18 Postgraduate Degrees, 15 School Standards, 9 Ph.D. Disciplines).
  - 455 program sections, zero foreign key violations, 100% 1:1 bi-directional referential integrity across 30,003 student records.

---

### Slide 6: Multi-Tier Cascading Academic Hierarchy (Includes 2 Embedded UI Screenshots)
- **Left Column**:
  - **Pre-University College Hierarchy**: Class (11/12) → Stream (Science/Commerce/Arts) → Combination (PCMB, PCMC, EBAC, HEBA, HEPyS).
  - **Embedded UI Screenshot 1**: `pu_college_stream_combination_filters.png` showing the live selection of stream combinations with automatic subject validation.
- **Right Column**:
  - **University & Degree College Hierarchy**: Division/Faculty (Engineering, Law, Science) → Degree (B.Tech, B.Arch, MCA, MBA) → Semester (1–8) → Section.
  - **Embedded UI Screenshot 2**: `degree_college_cascading_programme_filters.png` displaying the live degree filter and demonstrating resolution of the legacy numeric 0 mapping defect.

---

### Slide 7: Automated Two-Stage Digital Admission Lifecycle (Includes 1 Chart + 1 UI Screenshot)
- **Left Column**:
  - **Embedded Graph 3**: `graph_admissions.png` — Admission Lifecycle Status Progression across 82 applications (40 Stage 1 Submitted, 12 Stage 1 Approved, 6 Clarification Requested, 8 Stage 1 Rejected, 6 Stage 2 Submitted, 6 Documents Uploaded, 4 Enrolled).
  - State machine transition explanation: `submitted → approved → stage2_submitted → documents_uploaded → enrolled`.
- **Right Column**:
  - **Parent Portal Live Status Desk**: Real-time determination tracking, administrator guidance notes, and Stage 2 unlock notification.
  - **Embedded UI Screenshot 3**: `parent_dashboard_admission_status.png` showing the live parent application tracker with real-time status badges.

---

### Slide 8: Stage 2 Detailed Demographic Dossier & Onboarding (Includes UI Screenshot)
- **Left Column**:
  - Deep-dive into Stage 2 onboarding: unlocked only post-approval, captures emergency contacts, secondary guardian info, medical allergies, blood group, prior academic marks, and extracurricular achievements.
  - Multi-file certificate upload (Aadhaar, Transfer Certificate, Marksheets, Caste/Income certificates) and synchronous status transition.
- **Right Column**:
  - **Embedded UI Screenshot 4**: `stage2_dossier_detailed_records.png` showing the full Stage 2 verified records dossier inside the administrative review queue.

---

### Slide 9: Administrative Tri-Action Review Desk (Includes 2 Embedded UI Screenshots)
- **Left Column**:
  - **Verification Dossier & Certificate Roster**: Pending certificates roster with real-time status badges, upload timestamps, and direct action triggers.
  - **Embedded UI Screenshot 5**: `document_actions_dossier_table.png` showing the administrative document actions table.
- **Right Column**:
  - **Authenticated Streaming & 50%–250% Zoom Controls**: Authenticated byte-range preview streaming (`GET /api/documents/{id}/preview`) with granular zoom (50% to 250%), pan, and rotation controls for PDF and image scans.
  - **Embedded UI Screenshot 6**: `document_actions_preview_zoom_modal.png` displaying the interactive document preview zoom modal.

---

### Slide 10: Document Accept & Reject Administrative Controls (Includes 2 Embedded UI Screenshots)
- **Left Column**:
  - **Accept Action Workflow**: Single-click confirmation committing `VERIFIED` status, updating the green badge, decrementing pending review counters, and writing an immutable audit log entry.
  - **Embedded UI Screenshot 7**: `document_actions_accept_modal.png` showing the accept confirmation modal.
- **Right Column**:
  - **Reject Defect Taxonomy Enforcement**: Mandatory defect reason selection (Illegible Scan, Expired Document, Name Mismatch, Missing Signature, Incomplete) + guidance notes, setting status to `REJECTED` and dispatching parent alert.
  - **Embedded UI Screenshot 8**: `document_actions_reject_modal.png` showing the defect taxonomy selection dialog.

---

### Slide 11: Database-Verified Student Account Activation (Includes 3 Embedded UI Screenshots)
- **Three-Step Activation Architecture**:
  - **Step 1: Permanent ID Lookup**: Student enters official Permanent Student ID (`NS-SCH019-STD06-166`). System performs exact B-Tree seek against SQLite database.
    - **Embedded UI Screenshot 9**: `student_activation_step1_lookup.png`.
  - **Step 2: Read-Only Record Auto-Population**: System queries enrolled record and auto-populates official student name, grade, and section as READ-ONLY fields, eliminating spelling mismatch errors.
    - **Embedded UI Screenshot 10**: `student_activation_step2_verified_record.png`.
  - **Step 3: Secure Credential Creation & Dashboard**: Student establishes password encrypted via Bcrypt; account is committed to `users` table and opens the personalized Student Portal dashboard.
    - **Embedded UI Screenshot 11**: `student_activation_step3_portal_dashboard.png`.

---

### Slide 12: High-Scale Database Performance & Roster Management (Includes 1 Chart + 1 UI Screenshot)
- **Left Column**:
  - **Sub-45ms Paginated Query Latency Benchmark**:
  - **Embedded Graph 4**: `graph_latency.png` showing latency scaling from 1,000 to 30,003 records (12ms → 41ms with WAL compound index `idx_enrollments_lookup` vs 820ms for unindexed full table scans).
  - Write-Ahead Logging (WAL) concurrency explanation (zero lock contention between concurrent admin reviews and parent submissions).
- **Right Column**:
  - **Live 30,000-Student Roster Management Desk**:
  - **Embedded UI Screenshot 12**: `school_student_management_desk_std8_secA.png` displaying real-time paginated rendering of student rosters, section capacities, and guardian links.

---

### Slide 13: Institutional Governance, RBAC & Forensic Audit Logging
- **Three Core Pillars**:
  - **Zero-Token Administrator Provisioning**: Platform Admin invites Academic Administrator via dashboard modal; 32-character cryptographic token generated and stored in `invitation_tokens`; **ZERO UI exposure** (raw tokens and URLs are never rendered in the DOM or UI); 60 active invitation tokens managed.
  - **Multi-Tenant Data Isolation (RBAC)**: Every API endpoint validates `institution_id` against `user_institution_roles`; cross-tenant access attempts return HTTP 403 Forbidden; Ballari School (`SCH019`) admins cannot query Bangalore High School (`SCH001`); clean context switching for multi-campus administrators.
  - **Dual-Layer Forensic Audit Trails**: Platform Audit Layer (`platform_audit_logs`: 626 logs) for system configs and invitations; Institutional Audit Layer (`audit_logs`: 502 logs) for document reviews and grading; immutable append-only architecture guaranteeing legal reproducibility.

---

### Slide 14: Technical Maturity, Disclosures & Future Scope
- **Technical Maturity Matrix**:
  - **Fully Implemented (82%)**: Discovery Portal, Two-Stage Admission Pipeline, Tri-Action Review Desk with 50%–250% Zoom, 30,003 Enrolled Student Directory, Cascading Curricula Filters, Permanent ID Student Activation, Zero-Token Invitations, Dual-Layer Audit Logging (1,128 records).
  - **Simulated / Demonstration Features Disclosed (8%)**: AI Assistance Module (`backend/ai_agent.py`) is a deterministic, rule-based in-process Python parser (29 KB) running fully offline (no external cloud LLM API); Document OCR Sandbox (3 endpoints, 2 pre-extracted validation records in DB, manual admin override).
  - **Future Integration Roadmap (10%)**: National DigiLocker Direct API Integration (OAuth 2.0 NAD repository); Online Payment Gateway (Razorpay/BillDesk; `fees` table schema exists with 0 rows); Karnataka State Scholarship Portal SSP DBT Integration (`scholarships` table exists with 0 rows); Telephony SMS / WhatsApp carrier dispatch.

---

### Slide 15: Q&A & Defense Discussion (Dark Navy Theme)
- **Vidyashilp University Official Coat of Arms Logo**.
- **Heading**: *Thank You! Questions, Feedback & Discussion from the Evaluation Committee*.
- **Candidate & Guide Information**: Candidate **S Phalguna** (`2023UG000171`) | Project Supervisor: **Shabbeer Basha**, Associate Professor.
- **Department**: School of Engineering and Technology, Vidyashilp University, Bangalore-562110 (November 2026).
- **Deliverables Citation**: Complete Project Report PDF (4.67 MB), Report DOCX (2.62 MB), Feature Matrix (XLSX), 140 REST API Endpoints.
