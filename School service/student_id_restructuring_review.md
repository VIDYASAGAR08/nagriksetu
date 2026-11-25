# NagrikSetu – Centralised Student ID Restructuring Review & Migration Plan (Phase 1)

**Document Type:** Phase 1 Architectural Audit, ID Mapping Report & Migration Plan  
**Project Path:** `C:\Users\callm\nagriksetu`  
**Database Audited:** `C:\Users\callm\nagriksetu\backend\data\nagriksetu.db` (SQLite)  
**Mapping CSV Generated:** `C:\Users\callm\nagriksetu\student_id_restructuring_mapping.csv`  
**Audit Timestamp:** 2026-11-19T22:45:00+05:30  
**Phase Status:** PHASE 1 COMPLETE — NO DATABASE MODIFICATIONS HAVE BEEN APPLIED. AWAITING EXPLICIT USER APPROVAL.

---

## 1. Executive Summary

This report establishes the centralized, academic programme- and stream-based Student ID restructuring system for the NagrikSetu School Service platform. In accordance with the Phase 1 specification:
1. The active SQLite database was audited in **read-only mode**. Total student count is verified at **exactly 30,003 students**.
2. All 31 institutions (Schools, Pre-University Colleges, Degree Colleges, and Universities) were inspected.
3. Every table schema, foreign-key dependency, and application reference to `student_id` was identified across the backend codebase.
4. A complete 30,003-row mapping CSV (`student_id_restructuring_mapping.csv`) has been generated. Every single student in the database is represented with **zero duplicates**, **zero omissions**, and **complete data integrity**.
5. All records with missing admission dates or unassigned academic streams have been systematically identified, categorized, and flagged for explicit administrative review.
6. A transactional Phase 2 execution and rollback plan has been prepared.

---

## 2. Baseline Database Verification

| Entity / Metric | Current Database Baseline | Verification Status |
|---|---|---|
| **Total Institutions in `schools`** | **31** (15 Schools, 5 PU Colleges, 5 Degree Colleges, 5 Universities, 1 Primary School) | Verified |
| **Total Student Records (`students`)** | **30,003** | Verified |
| **Total Active Enrollments (`enrollments`)** | **30,003** | Verified (100% active, AY 2026-2027) |
| **Unique Existing Student IDs** | **30,003** | 100% Unique |
| **Unique Permanent Student IDs (`PSID`)** | **30,003** | 100% Unique (Zero duplicates) |
| **Parent-Child Linkages (`student_guardians`)** | **20** verified family links | Preserved intact |
| **Registered User Accounts (`users`)** | **43** accounts | Preserved intact |
| **Users with `student_id` attribute** | **6** student user accounts | Identified for sync |
| **Admission Applications with `enrolled_student_id`** | **3** applications (1 School, 2 College) | Preserved intact |

---

## 3. Student ID Formats & Policy Rules

### A. Pre-University (PU) College Students
* **Format:** `STREAM_PREFIX + ADMISSION_YEAR + 4-DIGIT_SEQUENCE`
* **Admission Year Format:** 2-digit admission year (`26` for 2026).
* **Numbering Rule:** The 4-digit sequence is **centralised and shared across all PU colleges** offering that stream. Numbering starts at `0001` per stream and increments continuously across institutions without resetting per college.
* **Standard PU Stream Prefixes:**
  * `PCMB`: Physics, Chemistry, Mathematics, Biology (`PCMB260001`...)
  * `PCMC`: Physics, Chemistry, Mathematics, Computer Science (`PCMC260001`...)
  * `PCME`: Physics, Chemistry, Mathematics, Electronics (`PCME260001`...)
  * `CEBA`: Computer Science, Economics, Business Studies, Accountancy (`CEBA260001`...)
  * `SEBA`: Statistics, Economics, Business Studies, Accountancy (`SEBA260001`...)
  * `EBAC`: Economics, Business Studies, Accountancy, Computer Applications (`EBAC260001`...)
  * `HEBA`: History, Economics, Business Studies, Accountancy (`HEBA260001`...)
  * `MEBA`: Mathematics, Economics, Business Studies, Accountancy (`MEBA260001`...)
  * `HEPS`: History, Economics, Political Science, Sociology (`HEPS260001`...)
  * `VOCIT`: Vocational IT, Electronics & Commerce (`VOCIT260001`...)

### B. Degree College Students
* **Format:** `PROGRAMME_PREFIX + ADMISSION_YEAR + 4-DIGIT_SEQUENCE`
* **Numbering Rule:** Independent continuous sequence per programme shared across all colleges.
* **Standard Programme Prefixes:**
  * `BE`: Bachelor of Engineering (`BE260001`...)
  * `BTECH`: Bachelor of Technology (`BTECH260001`...)
  * `BCA`: Bachelor of Computer Applications (`BCA260001`...)
  * `BSCS`: B.Sc Computer Science (`BSCS260001`...)
  * `BSDS`: B.Sc Data Science (`BSDS260001`...)
  * `BCOM`: Bachelor of Commerce (`BCOM260001`...)
  * `BBA`: Bachelor of Business Administration (`BBA260001`...)
  * `BA`: Bachelor of Arts (`BA260001`...)
  * `BSC`: Bachelor of Science (`BSC260001`...)
  * `BPHARM`: Bachelor of Pharmacy (`BPHARM260001`...)
  * `BARCH`: Bachelor of Architecture (`BARCH260001`...)
  * `BSW`: Bachelor of Social Work (`BSW260001`...)

### C. University Students
* **Format:** `PROGRAMME_PREFIX + ADMISSION_YEAR + 4-DIGIT_SEQUENCE`
* **Master Postgraduate & Doctoral Prefixes:**
  * `MTECH`: Master of Technology (`MTECH260001`...)
  * `MBA`: Master of Business Administration (`MBA260001`...)
  * `MCA`: Master of Computer Applications (`MCA260001`...)
  * `MSC`: Master of Science (`MSC260001`...)
  * `MCOM`: Master of Commerce (`MCOM260001`...)
  * `MA`: Master of Arts (`MA260001`...)
  * `PHD`: Doctor of Philosophy (`PHD260001`...)

### D. School Students (K-10)
* **Format:** `YYYY + SEQUENCE` (e.g., `20260001` onwards)
* **Numbering Rule:** Continuous, non-overlapping range allocated across schools based on headcount.
* **Sequence Length Consideration:** When school student counts exceed 9,999, the sequence portion expands from 4 digits (`0001`–`9999`) to 5 digits (`10000`–`99999`) to prevent sequence exhaustion and preserve continuous monotonic ordering across the platform.

---

## 4. Master Academic Programme & Prefix Mapping Table

The complete catalogue of academic programmes across all 31 institutions in the NagrikSetu platform:

| Academic Level | Category / Discipline | Degree / Stream | Code / Combination | Central Prefix | Sequence Starts At |
|---|---|---|---|---|---|
| **PU College** | Science | Pre-University (PCMB) | PCMB | `PCMB` | `PCMB260001` |
| **PU College** | Science | Pre-University (PCMC) | PCMC | `PCMC` | `PCMC260001` |
| **PU College** | Science | Pre-University (PCME) | PCME | `PCME` | `PCME260001` |
| **PU College** | Commerce | Pre-University (CEBA) | CEBA | `CEBA` | `CEBA260001` |
| **PU College** | Commerce | Pre-University (SEBA) | SEBA | `SEBA` | `SEBA260001` |
| **PU College** | Commerce | Pre-University (EBAC) | EBAC | `EBAC` | `EBAC260001` |
| **PU College** | Commerce | Pre-University (HEBA) | HEBA | `HEBA` | `HEBA260001` |
| **PU College** | Commerce | Pre-University (MEBA) | MEBA | `MEBA` | `MEBA260001` |
| **PU College** | Arts | Pre-University (HEPS) | HEPS | `HEPS` | `HEPS260001` |
| **PU College** | Vocational | Pre-University (VOC-IT) | VOC-IT | `VOCIT` | `VOCIT260001` |
| **Degree / Univ** | Engineering | Bachelor of Engineering | BE | `BE` | `BE260001` |
| **Degree / Univ** | Engineering | Bachelor of Technology | B.Tech | `BTECH` | `BTECH260001` |
| **Degree / Univ** | Computer App | Bachelor of Computer Applications | BCA | `BCA` | `BCA260001` |
| **Degree / Univ** | Science | B.Sc Computer Science | BSCS | `BSCS` | `BSCS260001` |
| **Degree / Univ** | Science | B.Sc Data Science | BSDS | `BSDS` | `BSDS260001` |
| **Degree / Univ** | Commerce | Bachelor of Commerce | B.Com | `BCOM` | `BCOM260001` |
| **Degree / Univ** | Management | Bachelor of Business Administration | BBA | `BBA` | `BBA260001` |
| **Degree / Univ** | Arts / Humanities | Bachelor of Arts | BA | `BA` | `BA260001` |
| **Degree / Univ** | Sciences | Bachelor of Science | B.Sc | `BSC` | `BSC260001` |
| **Degree / Univ** | Pharmacy | Bachelor of Pharmacy | B.Pharm | `BPHARM` | `BPHARM260001` |
| **Degree / Univ** | Architecture | Bachelor of Architecture | B.Arch | `BARCH` | `BARCH260001` |
| **Degree / Univ** | Social Work | Bachelor of Social Work | BSW | `BSW` | `BSW260001` |
| **Postgraduate** | Engineering | Master of Technology | M.Tech | `MTECH` | `MTECH260001` |
| **Postgraduate** | Management | Master of Business Administration | MBA | `MBA` | `MBA260001` |
| **Postgraduate** | Computer App | Master of Computer Applications | MCA | `MCA` | `MCA260001` |
| **Postgraduate** | Sciences | Master of Science | M.Sc | `MSC` | `MSC260001` |
| **Postgraduate** | Commerce | Master of Commerce | M.Com | `MCOM` | `MCOM260001` |
| **Postgraduate** | Arts | Master of Arts | MA | `MA` | `MA260001` |
| **Doctoral** | Research | Doctor of Philosophy | Ph.D. | `PHD` | `PHD260001` |
| **School (K-10)** | General | Karnataka State Board (Std 1-10) | KSEEB-CORE | `2026` | `20260001` |

---

## 5. Institution-Wise Student Distribution & Allocation Baseline

The 30,003 students currently residing in the database are distributed across 21 institutions (10 institutions currently hold 0 students):

| Institution ID | Institution Name | Category / Type | Total Students | Standards | Admission Date Status | Proposed ID Range | Mapping Status |
|---|---|---|---|---|---|---|---|
| **COL003** | BMS College of Engineering (BMSCE) | Degree College | 2 | 1 (Year 1) | Verified (2026-11-01) | `BE260001` – `BE260002` | `MAPPED_VERIFIED` |
| **SCH001** | Government Model School | Schools (K-10) | 601 | 1 to 10 | 1 Verified, 600 NULL | `20260001` – `20260601` | 1 `MAPPED_VERIFIED`, 600 `FLAGGED_REVIEW_ADMISSION_DATE_NULL` |
| **SCH002** | Shanti Vidya Mandir | Schools (K-10) | 600 | 1 to 10 | NULL (AY 2026-27) | `20260602` – `20261201` | `FLAGGED_REVIEW_ADMISSION_DATE_NULL` |
| **SCH003** | National Public School | Schools (K-10) | 600 | 1 to 10 | NULL (AY 2026-27) | `20261202` – `20261801` | `FLAGGED_REVIEW_ADMISSION_DATE_NULL` |
| **SCH004** | Sri Vidya School | Schools (K-10) | 600 | 1 to 10 | NULL (AY 2026-27) | `20261802` – `20262401` | `FLAGGED_REVIEW_ADMISSION_DATE_NULL` |
| **SCH005** | Green Valley School | Schools (K-10) | 600 | 1 to 10 | NULL (AY 2026-27) | `20262402` – `20263001` | `FLAGGED_REVIEW_ADMISSION_DATE_NULL` |
| **SCH006** | Bharat Education School | Schools (K-10) | 600 | 1 to 10 | NULL (AY 2026-27) | `20263002` – `20263601` | `FLAGGED_REVIEW_ADMISSION_DATE_NULL` |
| **SCH007** | New Horizon School | Schools (K-10) | 600 | 1 to 10 | NULL (AY 2026-27) | `20263602` – `20264201` | `FLAGGED_REVIEW_ADMISSION_DATE_NULL` |
| **SCH008** | Vivekananda School | Schools (K-10) | 600 | 1 to 10 | NULL (AY 2026-27) | `20264202` – `20264801` | `FLAGGED_REVIEW_ADMISSION_DATE_NULL` |
| **SCH009** | Saraswati Vidya Kendra | Schools (K-10) | 600 | 1 to 10 | NULL (AY 2026-27) | `20264802` – `20265401` | `FLAGGED_REVIEW_ADMISSION_DATE_NULL` |
| **SCH010** | Karnataka Public School | Schools (K-10) | 600 | 1 to 10 | NULL (AY 2026-27) | `20265402` – `20266001` | `FLAGGED_REVIEW_ADMISSION_DATE_NULL` |
| **SCH016** | Belagavi Public School | Schools (K-10) | 2,400 | 1 to 12 | Verified (2026-06-01) | `20266002` – `20268401` | 2,000 `MAPPED_VERIFIED_SCHOOL_STUDENTS`, 400 `FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS` |
| **SCH017** | Dharwad Vidya School | Schools (K-10) | 2,400 | 1 to 12 | Verified (2026-06-01) | `20268402` – `202610801` | 2,000 `MAPPED_VERIFIED_SCHOOL_STUDENTS`, 400 `FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS` |
| **SCH018** | Shivamogga Model School | Schools (K-10) | 2,400 | 1 to 12 | Verified (2026-06-01) | `202610802` – `202613201` | 2,000 `MAPPED_VERIFIED_SCHOOL_STUDENTS`, 400 `FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS` |
| **SCH019** | Ballari Education School | Schools (K-10) | 2,400 | 1 to 12 | Verified (2026-06-01) | `202613202` – `202615601` | 2,000 `MAPPED_VERIFIED_SCHOOL_STUDENTS`, 400 `FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS` |
| **SCH020** | Kalaburagi Public School | Schools (K-10) | 2,400 | 1 to 12 | Verified (2026-06-01) | `202615602` – `202618001` | 2,000 `MAPPED_VERIFIED_SCHOOL_STUDENTS`, 400 `FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS` |
| **SCH011** | Tumakuru Model PU College | PU Colleges (11-12) | 2,400 | 1 to 12 | Verified (2026-06-01) | `202618002` – `202620001` (Std 1-10)<br>`PU260001` – `PU260400` (Std 11-12) | 2,000 `FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS`, 400 `FLAGGED_REVIEW_PU_STREAM_UNASSIGNED` |
| **SCH012** | Mysuru Government PU College | PU Colleges (11-12) | 2,400 | 1 to 12 | Verified (2026-06-01) | `202620002` – `202622001` (Std 1-10)<br>`PU260401` – `PU260800` (Std 11-12) | 2,000 `FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS`, 400 `FLAGGED_REVIEW_PU_STREAM_UNASSIGNED` |
| **SCH013** | Mandya Government PU College | PU Colleges (11-12) | 2,400 | 1 to 12 | Verified (2026-06-01) | `202622002` – `202624001` (Std 1-10)<br>`PU260801` – `PU261200` (Std 11-12) | 2,000 `FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS`, 400 `FLAGGED_REVIEW_PU_STREAM_UNASSIGNED` |
| **SCH014** | Hassan Valley PU College | PU Colleges (11-12) | 2,400 | 1 to 12 | Verified (2026-06-01) | `202624002` – `202626001` (Std 1-10)<br>`PU261201` – `PU261600` (Std 11-12) | 2,000 `FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS`, 400 `FLAGGED_REVIEW_PU_STREAM_UNASSIGNED` |
| **SCH015** | Udupi Government PU College | PU Colleges (11-12) | 2,400 | 1 to 12 | Verified (2026-06-01) | `202626002` – `202628001` (Std 1-10)<br>`PU261601` – `PU262000` (Std 11-12) | 2,000 `FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS`, 400 `FLAGGED_REVIEW_PU_STREAM_UNASSIGNED` |
| **COL001, COL002, COL004–COL010, SCH0099** | Remaining 10 Institutions | Degree / Univ / School | 0 | — | N/A | Available from `0001` | Clean Ready State |
| **TOTAL** | **31 Institutions** | — | **30,003** | — | — | **30,003 Unique Proposed IDs** | **Zero Duplicates** |

---

## 6. Audit of Missing Data, Edge Cases & Data Inconsistencies

During Phase 1 database inspection, five major structural data anomalies were detected in the legacy database. In accordance with the prompt requirement (*"Identify records with missing programme or admission-year information. Report any records that cannot be safely mapped"*), these are documented below:

### Issue 1: Missing `admission_date` for 6,000 School Students (SCH001–SCH010)
* **Finding:** In `SCH001` to `SCH010`, exactly 6,000 student records have `students.admission_date = NULL` and `enrollments.admission_date = NULL`. (Only 1 student in SCH001 has an explicit date `2026-11-01`).
* **Existing Reality:** However, all 6,000 records have `enrollments.academic_year = '2026-2027'`.
* **Proposed Handling:** In the mapping CSV, these students are proposed under the 2026 numeric sequence (`20260002` to `20266001`) based on their verified academic year `2026-2027`, and their status is explicitly marked as `FLAGGED_REVIEW_ADMISSION_DATE_NULL`.

### Issue 2: PU Colleges Containing Standards 1 to 10 (10,000 Students in SCH011–SCH015)
* **Finding:** `SCH011` to `SCH015` are classified as `PU Colleges (11-12)` in `schools.category` and `schools.school_type`. However, each college contains 200 students in each standard from Standard 1 to Standard 10 (total 10,000 students across the 5 PU colleges).
* **Existing Reality:** In `academic_programs`, PU colleges only offer higher secondary programmes (standards 11 and 12). There are no registered K-10 programmes for PU colleges.
* **Proposed Handling:** In the mapping CSV, these 10,000 students are proposed under the continuous school numeric sequence (`202618002`–`202628001`) with status `FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS` and programme labeled as `Unassigned Primary/Secondary (Standards 1-10 in PU College)`.

### Issue 3: PU Students with Unassigned Academic Streams (2,000 Students in SCH011–SCH015)
* **Finding:** For the 2,000 higher secondary students in `SCH011` to `SCH015` (Standards 11 & 12), `enrollments.stream` is `NULL` and `enrollments.subject_combination` is `NULL`. The students are currently divided into sections `A` (67 students), `B` (67 students), and `C` (66 students).
* **Existing Reality:** While `academic_programs` defines 10 specific streams (`PCMB`, `PCMC`, `PCME`, `CEBA`, `SEBA`, `EBAC`, `HEPS`, `VOC-IT`, `HEBA`, `MEBA`), individual student rows were never assigned to specific streams during synthetic seeding.
* **Proposed Handling:** Because assigning individual students to `PCMB` vs `PCMC` without record backing would be synthetic invention, the Phase 1 mapping CSV assigns a centralized Pre-University sequence (`PU260001` to `PU262000`) and marks status as `FLAGGED_REVIEW_PU_STREAM_UNASSIGNED`. If the user approves assigning sections A, B, C to specific streams (e.g., A=PCMB, B=PCMC, C=HEBA), this can be executed cleanly in Phase 2.

### Issue 4: K-10 Schools Containing Standards 11 and 12 (2,000 Students in SCH016–SCH020)
* **Finding:** `SCH016` to `SCH020` are categorized as `Schools (K-10)` in `schools.category`, yet each contains 200 students in Standard 11 and 200 students in Standard 12 (total 2,000 students).
* **Existing Reality:** In `academic_programs`, these institutions only have `PROG-SCH016-K10` to `PROG-SCH020-K10` (Standards 1-10). They have no registered PU programmes, and `enrollments.stream` is `NULL`.
* **Proposed Handling:** Proposed with continuous numeric IDs and flagged as `FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS`.

### Issue 5: School Sequence Length Beyond 9,999 Students
* **Finding:** When continuous numbering is applied across all school students (Standards 1-10 across SCH001-SCH010 and SCH016-SCH020 = 16,001 students), the sequence exceeds 4 digits (`0001` to `9999`).
* **Existing Reality:** A strict 4-digit sequence caps at 9,999 students.
* **Proposed Handling:** The sequence portion expands to 5 digits (`10000` to `28001`) starting at student 10,000 (`202610000`), maintaining strictly monotonic, unique, non-overlapping IDs.

---

## 7. Mapping CSV Verification Metrics

The mapping CSV `C:\Users\callm\nagriksetu\student_id_restructuring_mapping.csv` was verified using automated Python validation:

* **Total Rows Written:** 30,003 student records (+ 1 header row).
* **Existing Student IDs:** Exactly 30,003 unique values (0 duplicates, 0 missing).
* **Permanent Student IDs:** Exactly 30,003 unique values (0 duplicates, 0 missing).
* **Proposed New Student IDs:** Exactly 30,003 unique values (**0 duplicates, 0 collisions**).
* **CSV File Size:** 6,391,116 bytes (~6.39 MB).

### Mapping Status Breakdown:

```
  MAPPED_VERIFIED                              :         3  (COL003: 2, SCH001: 1)
  FLAGGED_REVIEW_ADMISSION_DATE_NULL           :     6,000  (SCH001-SCH010 K-10)
  MAPPED_VERIFIED_SCHOOL_STUDENTS              :    10,000  (SCH016-SCH020 Std 1-10)
  FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS    :     2,000  (SCH016-SCH020 Std 11-12)
  FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS:   10,000  (SCH011-SCH015 Std 1-10)
  FLAGGED_REVIEW_PU_STREAM_UNASSIGNED          :     2,000  (SCH011-SCH015 Std 11-12)
  --------------------------------------------------------------------------------
  TOTAL VERIFIED STUDENTS                      :    30,003
```

---

## 8. Database Foreign-Key Dependencies & Impact Analysis

An exhaustive audit of foreign keys, table columns, and Python backend code (`backend/main.py`) identified every component linked to `student_id`:

### A. Database Table References:
1. `students.student_id`: Primary identifier for display, student login, and search.
2. `users.student_id`: 6 student user accounts currently hold `student_id`:
   - `student.asha@example.com` (`SCH01125`)
   - `kiran.kumar@student.nagriksetu.gov` (`SCH01246`)
   - `student1@nagriksetu.gov` (`SCH01004`)
   - `ishaan.verma@example.com` (`SCH19956`)
   - `student.sch19049@nagriksetu.portal` (`SCH19049`)
   - `student.sch19029@nagriksetu.portal` (`SCH19029`)
   *Phase 2 Action:* Synchronize `users.student_id` with the student's new `student_id`.
3. `linking_requests.student_ref`: Stores submitted reference (such as `COL03001`, `COL03002`, `NS-...`).
   *Phase 2 Action:* Update `student_ref` where it matches an existing `student_id`.
4. Relational Integrity (`enrollments`, `student_guardians`, `academic_results`, `student_attendance`, `fees`):
   - All relational tables in NagrikSetu use `permanent_student_id` as the relational foreign key, NOT `student_id`.
   - Because `permanent_student_id` is **strictly preserved and untouched**, all academic results, attendance logs, fee receipts, and parent-child guardianship relationships remain **100% intact with zero relational disruption**.

### B. Application Code Endpoints in `main.py`:
- `GET /students/{student_id}`: Lookups use `student_id = ? OR permanent_student_id = ?`. Will immediately support new IDs.
- `GET /parent/lookup-student`: Autocomplete and ID searches search `s.student_id LIKE ?`. Will immediately autocomplete new IDs.
- `GET /institution/{institution_id}/students`: Directory tables display `student_id`. Will immediately render restructured IDs.
- `POST /auth/login`: Student login matching `student_id = ?` will authenticate with new IDs once `users.student_id` is synchronized.

---

## 9. Phase 2 Transactional Execution Plan

Upon receiving explicit user approval, Phase 2 will execute according to the following strict, zero-downtime protocol:

1. **Step 1 – Pre-Migration Verified Backup:**
   - Create a binary snapshot copy of the database:
     `C:\Users\callm\nagriksetu\backend\data\nagriksetu.db.backup_before_id_restructure`
   - Verify backup file readability and row count (`30,003`).

2. **Step 2 – Atomic Transaction Execution (`BEGIN IMMEDIATE`):**
   - Execute bulk update of `students.student_id` from `student_id_restructuring_mapping.csv` within a single SQLite transaction.
   - Update `users.student_id` for matching student user accounts.
   - Update `linking_requests.student_ref` where existing IDs match.

3. **Step 3 – Automated Post-Migration Verification:**
   - Verify `PRAGMA integrity_check` = `ok`.
   - Verify `PRAGMA foreign_key_check` = 0 violations.
   - Verify `SELECT COUNT(*) FROM students` = `30,003`.
   - Verify `SELECT COUNT(DISTINCT student_id) FROM students` = `30,003` (0 duplicates).
   - Verify `SELECT COUNT(DISTINCT permanent_student_id) FROM students` = `30,003` (0 duplicates).
   - Verify parent-child links in `student_guardians` (all 20 relationships intact).
   - Verify enrollments and academic records unchanged.

4. **Step 4 – Rollback Guarantee:**
   - If any verification check fails or an exception occurs, the transaction is immediately rolled back (`ROLLBACK`), and the database is restored from the pre-migration backup.

5. **Step 5 – Final Deliverable:**
   - Compile and generate `NagrikSetu_Student_ID_Structure_and_Migration_Report.docx` inside `C:\Users\callm\nagriksetu\`.

---

## 10. Phase 1 Completion & Request for Approval

**Phase 1 is now complete.**
- No database changes have been made.
- The mapping CSV is saved at `C:\Users\callm\nagriksetu\student_id_restructuring_mapping.csv`.
- The audit and review plan is saved at `C:\Users\callm\nagriksetu\student_id_restructuring_review.md`.

### Decisions Required Before Phase 2 Execution:
1. **PU College Stream Assignment (SCH011–SCH015, Standards 11-12, 2,000 students):**
   - *Option A (Recommended):* Allocate the 2,000 higher secondary students across the prominent PU streams based on section (`Section A` -> `PCMB`, `Section B` -> `PCMC`, `Section C` -> `HEBA`/`CEBA`).
   - *Option B:* Keep the provisional centralized PU prefix (`PU260001` to `PU262000`) until manual stream assignments are imported.
2. **K-10 Students in PU Colleges (SCH011–SCH015, Standards 1-10, 10,000 students):**
   - Confirm retaining numeric school sequence IDs (`202618002`–`202628001`) with administrative flag.
3. **Approval to Proceed:**
   - Please review the mapping CSV and provide your explicit confirmation to proceed with **Phase 2 (Database Migration & Report Generation)**.
