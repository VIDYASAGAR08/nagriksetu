# NagrikSetu School Service — Read-Only Student & Name Audit Report

**Audit Mode**: READ-ONLY  
**Date & Timestamp**: 2026-11-19T21:50:00+05:30  
**Project Path**: `C:\Users\callm\nagriksetu`  
**Database File Audited**: `C:\Users\callm\nagriksetu\backend\data\nagriksetu.db`  
**Container Path**: `/app/data/nagriksetu.db` (Bind Mount)  
**Database Size**: 16,121,856 bytes (~16.1 MB)  
**Backup Reference**: `C:\Users\callm\nagriksetu\backend\data\nagriksetu.db.backup_before_name_fix`

---

## 1. Executive Summary

A comprehensive, read-only audit of the active SQLite database was conducted. The audit verified student identity uniqueness, full name uniqueness (both raw strings and case/whitespace-normalized strings), absence of empty/missing values, and complete preservation of original institution assignments and enrollment relationships against the pre-update database backup.

All 30,003 student records have **100% unique Student IDs**, **100% unique Permanent Student IDs**, and **100% unique full names** across the entire platform. Zero duplicate names, zero duplicate IDs, and zero empty values exist. All original institution assignments, academic years, standards, sections, and active enrollments remain completely preserved.

---

## 2. Core Audit Findings

| Audit Check | Metric / Query | Result | Verification Status |
|---|---|---|---|
| **1. Total Student Records** | `SELECT COUNT(*) FROM students` | **30,003** | Verified |
| **2. Unique Student IDs** | `SELECT COUNT(DISTINCT student_id) FROM students` | **30,003** | 100% Unique |
| **3. Unique Permanent Student IDs** | `SELECT COUNT(DISTINCT permanent_student_id) FROM students` | **30,003** | 100% Unique |
| **4. Unique Student Full Names (Raw)** | `SELECT COUNT(DISTINCT student_name) FROM students` | **30,003** | 100% Unique |
| **4b. Unique Student Names (Normalized)** | `SELECT COUNT(DISTINCT LOWER(TRIM(student_name))) FROM students` | **30,003** | 100% Unique |
| **5. Repeated Student Full Names** | `GROUP BY student_name HAVING count > 1` | **0** | **0 Repeated Names** |
| **5b. Repeated Normalized Names** | `GROUP BY LOWER(TRIM(student_name)) HAVING count > 1` | **0** | **0 Repeated Names** |
| **6. List of Repeated Names** | `HAVING count > 1` | **None** | Empty list |
| **7. Duplicate Student IDs** | `GROUP BY student_id HAVING count > 1` | **0** | **0 Duplicates** |
| **8. Duplicate Permanent Student IDs** | `GROUP BY permanent_student_id HAVING count > 1` | **0** | **0 Duplicates** |
| **9. Missing or Empty Student Names** | `student_name IS NULL OR TRIM(student_name) = ''` | **0** | **0 Missing/Empty** |
| **10. Total Active Enrollments** | `SELECT COUNT(*) FROM enrollments WHERE status = 'active'` | **30,003** | 100% Preserved |
| **10b. Institution Assignment Mismatches** | Comparison with pre-correction backup | **0** | 100% Preserved |
| **10c. Enrollment Record Mismatches** | Comparison with pre-correction backup | **0** | 100% Preserved |

---

## 3. Repeated Full Names List

```
None.
Total repeated full names: 0
Total student records sharing repeated names: 0
```

---

## 4. Institution-Wise Student Distribution

Every educational institution in the database was audited for student headcount, raw name uniqueness, and normalized name uniqueness:

| Institution Code | Institution Name | Category / Tier | Total Students | Unique Names (Raw) | Unique Names (Normalized) | Duplicates |
|---|---|---|---|---|---|---|
| **SCH011** | Tumakuru Model Pre-University College | PU Colleges (11-12) | 2,400 | 2,400 | 2,400 | 0 |
| **SCH012** | Mysuru Government Pre-University College | PU Colleges (11-12) | 2,400 | 2,400 | 2,400 | 0 |
| **SCH013** | Mandya Government Pre-University College | PU Colleges (11-12) | 2,400 | 2,400 | 2,400 | 0 |
| **SCH014** | Hassan Valley Pre-University College | PU Colleges (11-12) | 2,400 | 2,400 | 2,400 | 0 |
| **SCH015** | Udupi Government Pre-University College | PU Colleges (11-12) | 2,400 | 2,400 | 2,400 | 0 |
| **SCH016** | Belagavi Public School | Schools (K-10) | 2,400 | 2,400 | 2,400 | 0 |
| **SCH017** | Dharwad Vidya School | Schools (K-10) | 2,400 | 2,400 | 2,400 | 0 |
| **SCH018** | Shivamogga Model School | Schools (K-10) | 2,400 | 2,400 | 2,400 | 0 |
| **SCH019** | Ballari Education School | Schools (K-10) | 2,400 | 2,400 | 2,400 | 0 |
| **SCH020** | Kalaburagi Public School | Schools (K-10) | 2,400 | 2,400 | 2,400 | 0 |
| **SCH001** | Government Model School | Schools (K-10) | 601 | 601 | 601 | 0 |
| **SCH002** | Shanti Vidya Mandir | Schools (K-10) | 600 | 600 | 600 | 0 |
| **SCH003** | National Public School | Schools (K-10) | 600 | 600 | 600 | 0 |
| **SCH004** | Sri Vidya School | Schools (K-10) | 600 | 600 | 600 | 0 |
| **SCH005** | Green Valley School | Schools (K-10) | 600 | 600 | 600 | 0 |
| **SCH006** | Bharat Education School | Schools (K-10) | 600 | 600 | 600 | 0 |
| **SCH007** | New Horizon School | Schools (K-10) | 600 | 600 | 600 | 0 |
| **SCH008** | Vivekananda School | Schools (K-10) | 600 | 600 | 600 | 0 |
| **SCH009** | Saraswati Vidya Kendra | Schools (K-10) | 600 | 600 | 600 | 0 |
| **SCH010** | Karnataka Public School | Schools (K-10) | 600 | 600 | 600 | 0 |
| **COL003** | BMS College of Engineering (BMSCE) | Degree Colleges | 2 | 2 | 2 | 0 |
| **COL001** | Ramaiah Institute of Technology (MSRIT) | Degree Colleges | 0 | 0 | 0 | 0 |
| **COL002** | R.V. College of Engineering (RVCE) | Degree Colleges | 0 | 0 | 0 | 0 |
| **COL004** | PES University (Ring Road Campus) | Universities | 0 | 0 | 0 | 0 |
| **COL005** | The National Institute of Engineering (NIE) | Degree Colleges | 0 | 0 | 0 | 0 |
| **COL006** | St. Joseph's University | Universities | 0 | 0 | 0 | 0 |
| **COL007** | Mount Carmel College (Autonomous) | Degree Colleges | 0 | 0 | 0 | 0 |
| **COL008** | KLE Technological University (BVBCET) | Universities | 0 | 0 | 0 | 0 |
| **COL009** | University of Mysore (Manasagangotri) | Universities | 0 | 0 | 0 | 0 |
| **COL010** | Visvesvaraya Technological University (VTU) | Universities | 0 | 0 | 0 | 0 |
| **SCH0099**| Vidya Mandir English School | Schools (K-10) | 0 | 0 | 0 | 0 |
| **TOTAL** | — | — | **30,003** | **30,003** | **30,003** | **0** |

---

## 5. Verification Against Pre-Correction Backup

To verify that data preservation rules were strictly adhered to:
1. **Student IDs**: All 30,003 Student IDs present in the backup exist in the current database with identical primary keys.
2. **Permanent Student IDs**: All 30,003 Permanent Student IDs match the backup 1:1.
3. **School Assignments**: Every student's `school_id` assignment is identical to the backup. Zero institution assignment mismatches detected.
4. **Enrollments Table**: All 30,003 enrollment records (`enrollment_id`, `permanent_student_id`, `school_id`, `standard`, `section`, `enrollment_status`) match the backup 1:1.
5. **Parent-Child Guardianship Relationships**: All 20 verified family links in `student_guardians` remain intact with their designated parent accounts, and their children's names were preserved without modification.

---

## 6. Audit Conclusion & Final Answers

- **A. Total student records**: **30,003**
- **B. Total unique names**: **30,003** (30,003 normalized)
- **C. Total repeated names**: **0**
- **D. Total duplicate Student IDs**: **0**
- **E. Total duplicate Permanent Student IDs**: **0**
- **F. Whether the previous name correction appears successful**: **Yes, 100% successful.**
- **G. Whether any further correction is needed**: **No further correction is needed.** The database is clean, consistent, and ready for the Parent Dataset task.
