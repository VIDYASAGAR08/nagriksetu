# NAGRIKSETU — COMPOSITE INSTITUTION STRUCTURE (SCENARIO B)
## READ-ONLY VERIFICATION & AUDIT REPORT

**Date:** 22 November 2026  
**Audit Scope:** Read-Only Database & System Verification  
**Target Environment:** `nagriksetu.db` & Backup Files  
**Target Institutions:** `SCH011`–`SCH020` (10 Composite Institutions)  
**Total Target Student Population:** 30,003 Students  
**Audit Status:** COMPLETE — READ-ONLY (Zero Records Modified)

---

## EXECUTIVE SUMMARY

A comprehensive, strictly read-only audit of the NagrikSetu database (`backend/data/nagriksetu.db`) and its pre-migration backup was conducted. 

### Key Findings
1. **Migration Execution Status**: `migrate_composite_structure.py` was **NOT EXECUTED**. The migration script exists on disk in `scratch/`, but the live database remains in its pre-migration state.
2. **Database Backup**: A valid, uncorrupted SQLite3 backup exists at `backend/data/backups/nagriksetu_composite_pre_backup_20261122_103046.db` (**413.59 MB**) containing all 30,003 students and associated records.
3. **Record Count Preservation**: Exactly **30,003 student records** are present in the database (0 variance, 0 duplicates, 0 missing core fields).
4. **Data Integrity & Completeness**:
   - 30,003 unique `student_id`s and 30,003 unique `permanent_student_id`s.
   - 30,003 matching enrollment rows.
   - 719,929 student attendance records (100% student coverage).
   - 179,994 academic examination result records (100% student coverage).
   - 120,012 official student dossier documents (100% student coverage).
   - 0 orphan student records (100% of institution references exist in `schools`).
5. **Employment Service**: Untouched and operational on isolated port 8005.
6. **Implementation Status**: **INCOMPLETE** — The migration script has been authored and backed up, but not applied to the database; backend endpoints and frontend admin tabs are pending composite awareness.

---

## AUDIT ITEM 1: CHECK WHETHER `migrate_composite_structure.py` WAS EXECUTED

| Check Item | Observed Value | Expected (Post-Migration) | Status |
| :--- | :--- | :--- | :--- |
| `division_id` column in `students` | `False` (Missing) | `True` | **Not Applied** |
| `academic_division` column in `students` | `False` (Missing) | `True` | **Not Applied** |
| `division_id` column in `enrollments` | `False` (Missing) | `True` | **Not Applied** |
| `academic_division` column in `enrollments` | `False` (Missing) | `True` | **Not Applied** |
| `institution_divisions` for SCH011–SCH020 | **0 rows** | **20 rows** (2 per institution) | **Pending** |
| `schools.school_type` contains "Composite" | **0 institutions** | **10 institutions** | **Pending** |
| Active `review_flag` count in `students` | **12,000 flagged** | **0 flagged** | **Pending** |

> [!IMPORTANT]
> **Audit Conclusion for Item 1:**  
> The migration script `C:\Users\callm\nagriksetu\scratch\migrate_composite_structure.py` **was NOT executed against `nagriksetu.db`**. The database schema and data remain in their initial state with 12,000 flagged records.

---

## AUDIT ITEM 2: COMPOSITE ACADEMIC DIVISIONS FOR SCH011–SCH020

### 1. Institutional Identity & Current Types in `schools` Table
All 10 institutions retain their original identities, names, and identifiers:

| Institution ID | Institution Name | Current Registered Type | Target Composite Type |
| :--- | :--- | :--- | :--- |
| `SCH011` | Tumakuru Model Pre-University College | PU College | Composite School & PU College |
| `SCH012` | Mysuru Government Pre-University College | PU College | Composite School & PU College |
| `SCH013` | Mandya Government Pre-University College | PU College | Composite School & PU College |
| `SCH014` | Hassan Valley Pre-University College | PU College | Composite School & PU College |
| `SCH015` | Udupi Government Pre-University College | PU College | Composite School & PU College |
| `SCH016` | Belagavi Public School | School | Composite School & PU College |
| `SCH017` | Dharwad Vidya School | School | Composite School & PU College |
| `SCH018` | Shivamogga Model School | School | Composite School & PU College |
| `SCH019` | Ballari Education School | School | Composite School & PU College |
| `SCH020` | Kalaburagi Public School | School | Composite School & PU College |

### 2. Division Rows in `institution_divisions`
- **Current Count for SCH011–SCH020:** **0 rows**.
- **Required:** 20 rows (1 `School Division` and 1 `PU Division` per institution).

### 3. Academic Programs in `academic_programs`
- `SCH011`–`SCH015`: **0** K–10 School programs registered (5 required).
- `SCH016`–`SCH020`: Only base school programs exist; **0** PU stream combinations registered (40 required: 8 combinations × 5 institutions).

---

## AUDIT ITEM 3: SCHOOL STANDARDS 1–10 AND PU 1ST/2ND PUC CLASSIFICATIONS

The 24,000 students enrolled across `SCH011`–`SCH020` exhibit the following distribution:

| Institution | Total Students | Standards 1–10 (School) | Standards 11–12 (PU) | Current `puc_year` Values | Classification State |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **SCH011** | 2,400 | 2,000 | 400 | None (2,000), 1st PUC (200), 2nd PUC (200) | 2,000 flagged (Std 1–10 in PU College) |
| **SCH012** | 2,400 | 2,000 | 400 | None (2,000), 1st PUC (200), 2nd PUC (200) | 2,000 flagged (Std 1–10 in PU College) |
| **SCH013** | 2,400 | 2,000 | 400 | None (2,000), 1st PUC (200), 2nd PUC (200) | 2,000 flagged (Std 1–10 in PU College) |
| **SCH014** | 2,400 | 2,000 | 400 | None (2,000), 1st PUC (200), 2nd PUC (200) | 2,000 flagged (Std 1–10 in PU College) |
| **SCH015** | 2,400 | 2,000 | 400 | None (2,000), 1st PUC (200), 2nd PUC (200) | 2,000 flagged (Std 1–10 in PU College) |
| **SCH016** | 2,400 | 2,000 | 400 | None (2,400) | 400 flagged (Std 11–12 in School) |
| **SCH017** | 2,400 | 2,000 | 400 | None (2,400) | 400 flagged (Std 11–12 in School) |
| **SCH018** | 2,400 | 2,000 | 400 | None (2,400) | 400 flagged (Std 11–12 in School) |
| **SCH019** | 2,400 | 2,000 | 400 | None (2,400) | 400 flagged (Std 11–12 in School) |
| **SCH020** | 2,400 | 2,000 | 400 | None (2,400) | 400 flagged (Std 11–12 in School) |
| **Total** | **24,000** | **20,000** | **4,000** | — | **12,000 awaiting resolution** |

---

## AUDIT ITEM 4: PU STREAMS AND SUBJECT COMBINATIONS

### A. Existing PU Students in SCH011–SCH015 (2,000 Students)
These 2,000 students (400 per college: 200 in 1st PUC, 200 in 2nd PUC) already hold canonical Karnataka Department of Pre-University Education (DPUE) stream mappings:

| Standard | PUC Level | Stream | Combination | Count per College | Total across 5 Colleges |
| :---: | :---: | :--- | :---: | :---: | :---: |
| 11 | 1st PUC | Science | PCMB | 50 | 250 |
| 11 | 1st PUC | Science | PCMC | 30 | 150 |
| 11 | 1st PUC | Science | PCME | 20 | 100 |
| 11 | 1st PUC | Commerce | CEBA | 30 | 150 |
| 11 | 1st PUC | Commerce | SEBA | 25 | 125 |
| 11 | 1st PUC | Commerce | HEBA | 20 | 100 |
| 11 | 1st PUC | Commerce | MEBA | 15 | 75 |
| 11 | 1st PUC | Arts / Humanities | HEPS | 10 | 50 |
| 12 | 2nd PUC | Science | PCMB | 50 | 250 |
| 12 | 2nd PUC | Science | PCMC | 30 | 150 |
| 12 | 2nd PUC | Science | PCME | 20 | 100 |
| 12 | 2nd PUC | Commerce | CEBA | 30 | 150 |
| 12 | 2nd PUC | Commerce | SEBA | 25 | 125 |
| 12 | 2nd PUC | Commerce | HEBA | 20 | 100 |
| 12 | 2nd PUC | Commerce | MEBA | 15 | 75 |
| 12 | 2nd PUC | Arts / Humanities | HEPS | 10 | 50 |
| **Subtotal** | | | | **400** | **2,000** |

### B. Flagged PU Students in SCH016–SCH020 (2,000 Students)
- Currently, all 2,000 students have:
  - `stream`: `"Unassigned Higher Secondary (Standards 11-12 in K-10 School)"`
  - `subject_combination`: `"FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS"`
  - `puc_year`: `NULL`
- The migration script assigns them to the exact same 8 canonical combinations adhering to the balanced 100 Science / 90 Commerce / 10 Arts ratio per 200-student cohort.

---

## AUDIT ITEM 5: TOTAL STUDENT COUNT

```
Total Live Students in students Table : 30,003
Required Total Students               : 30,003
Variance                              : 0 (Exact Match)
```

No records have been added, deleted, dropped, or purged.

---

## AUDIT ITEM 6: RECORD PRESERVATION & INTEGRITY AUDIT

| Entity / Table | Total Records | Distinct Student Entities | Coverage | Status |
| :--- | :---: | :---: | :---: | :---: |
| `students` (Student IDs) | 30,003 | 30,003 unique `student_id` | 100.0% | **Verified** |
| `students` (PSIDs) | 30,003 | 30,003 unique `permanent_student_id` | 100.0% | **Verified** |
| `enrollments` | 30,003 | 30,003 unique `permanent_student_id` | 100.0% | **Verified** |
| `student_attendance` | 719,929 | 30,003 unique `permanent_student_id` | 100.0% | **Verified** |
| `academic_results` | 179,994 | 30,003 unique `permanent_student_id` | 100.0% | **Verified** |
| `student_documents` | 120,012 | 30,003 unique `permanent_student_id` | 100.0% | **Verified** |
| `student_guardians` | 32 | 17 distinct children linked | 100.0% | **Verified** |
| Institution FK Integrity | 30,003 | All map to valid `schools.school_id` | 100.0% | **Verified** |

---

## AUDIT ITEM 7: ANOMALY & DISCREPANCY AUDIT

- **Duplicate Student IDs**: **0**
- **Duplicate Permanent Student IDs (PSIDs)**: **0**
- **NULL Core Identifiers**: **0**
- **Orphan Student Records**: **0**
- **Flagged Review Records**: Exactly **12,000 records**:
  - `FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS`: 10,000 students (Standards 1–10 in `SCH011`–`SCH015`).
  - `FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS`: 2,000 students (Standards 11–12 in `SCH016`–`SCH020`).
  - Unflagged normal students: 18,003.

---

## AUDIT ITEM 8: BACKUP FILE VERIFICATION

| Property | Details |
| :--- | :--- |
| **Backup Path** | `C:\Users\callm\nagriksetu\backend\data\backups\nagriksetu_composite_pre_backup_20261122_103046.db` |
| **File Size** | **413.59 MB** (433,676,288 bytes) |
| **Format** | SQLite 3 database |
| **Verification Query** | `SELECT count(*) FROM students` → **30,003** |
| **Integrity Check** | All 31 schools, 30,003 enrollments, 719,929 attendance records, 179,994 exam results, and 120,012 documents successfully verified inside the backup file. |

---

## GAP ANALYSIS: WHAT REMAINS TO COMPLETE SCENARIO B

Because `migrate_composite_structure.py` was authored but not executed, the implementation is currently **INCOMPLETE**. The following tasks remain:

1. **Database Migration Execution (`scratch/migrate_composite_structure.py`)**:
   - Add `division_id` and `academic_division` columns to `students` and `enrollments` (additive schema change).
   - Insert 20 division records into `institution_divisions` (10 School Divisions + 10 PU Divisions for `SCH011`–`SCH020`).
   - Update `schools.school_type` to `Composite School & PU College` for `SCH011`–`SCH020`.
   - Insert 5 K–10 programs for `SCH011`–`SCH015` and 40 PU programs for `SCH016`–`SCH020` into `academic_programs`.
   - Map 10,000 students in `SCH011`–`SCH015` (Standards 1–10) to `School Division` (`academic_division = 'SCHOOL'`, `review_flag = NULL`).
   - Map 2,000 students in `SCH016`–`SCH020` (Standards 11–12) to `PU Division` (`academic_division = 'PU'`, `puc_year = '1st PUC'/'2nd PUC'`, assigned streams, `review_flag = NULL`).
2. **Backend API Routes (`backend/main.py`)**:
   - Update `/institution/{institution_id}/academic-structure` to return `COMPOSITE_INSTITUTION` with both School and PU divisions.
   - Update `/institution/{institution_id}/students` to accept `division_id` / `academic_division` filters.
3. **Frontend UI (`InstitutionStudentManagementDesk.jsx`)**:
   - Provide explicit division selection tabs ("School Division (Std 1–10)" and "PU Division (1st & 2nd PUC)") for Composite Institutions.
4. **Final Verification**:
   - Query DB to verify 0 flagged records and verify live UI in browser.
