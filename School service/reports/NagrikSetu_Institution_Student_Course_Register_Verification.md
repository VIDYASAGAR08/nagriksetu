# NagrikSetu – Complete Institution-wise Student and Course Enrollment Register
## Comprehensive Audit & Verification Report

---

### Executive Summary

In accordance with official registry oversight protocols, a complete read-only audit of the **NagrikSetu School Service** live database (`backend/data/nagriksetu.db`) was performed. Using the verified database as the single source of truth, an authoritative, presentation-ready multi-sheet Excel register has been generated:

- **Generated Workbook**: [`NagrikSetu_Institution_Wise_Student_Course_Enrollment_Register.xlsx`](file:///C:/Users/callm/nagriksetu/reports/NagrikSetu_Institution_Wise_Student_Course_Enrollment_Register.xlsx)
- **File Location**: `C:\Users\callm\nagriksetu\reports\`
- **File Size**: **6.35 MB**
- **Total Worksheets**: **7 Worksheets**
- **Total Students Reconciled**: Exactly **30,003** records (100% matched with 0 loss and 0 duplicates).
- **Total Institutions Reconciled**: **31 Registered Institutions** across Karnataka (including 10 institutions currently carrying 0 active enrollments).
- **Employment Service Isolation**: Kept completely isolated and untouched (Port `8005` unmodified).
- **Database Safety**: Read-only extraction. Zero database records, tables, enrollments, or relationships were modified.

---

### 1. Structural Overview of the Excel Workbook

The Excel workbook contains 7 dedicated worksheets, formatted with frozen header panes, auto-filters, professional color schemes, clean borders, custom column widths, and zero merged cells in the detailed registers:

| Sheet # | Worksheet Title | Row Count | Primary Purpose & Contents |
| :---: | :--- | :---: | :--- |
| **Sheet 1** | `Institution Directory` | 33 rows | Master directory of all 31 registered institutions in Karnataka (Schools, PU Colleges, Degree Colleges, Universities). Displays category, type, district, taluk, physical address, total registered students, active enrollments, academic divisions, and operational status. Includes total sum row. |
| **Sheet 2** | `Complete Student Register` | 30,004 rows | Comprehensive master ledger of all 30,003 students. Contains Serial Number, Student ID, PSID, Student Name, Institution ID, Institution Name, District, Academic Division, Course/Programme, Standard/Class/Level, Section, Stream, Subject Combination, Academic Year, and Enrollment Status. Unmapped records highlighted with red/amber alert styling. |
| **Sheet 3** | `Institution-wise Student List` | 30,004 rows | Clean, grouped student roster organized institution-by-institution for rapid filtering by School ID, School Name, and District. |
| **Sheet 4** | `Course Enrollment Register` | 30,004 rows | Official academic course ledger capturing Student ID, Name, Institution, Program ID (`academic_programs`), Course Name, Division, Class, Stream, Subject Combination, Department, Year/Semester, Academic Year, and Status. |
| **Sheet 5** | `Course Summary` | 304 rows | Aggregated matrix breaking down student counts by Institution ID, Name, Course Name, Academic Division, Standard/PUC Year, and Stream. Reconciles exactly to 30,003 students. |
| **Sheet 6** | `Academic Classification` | 68 rows | Structured taxonomy separating School Education (Standards 1–10), Pre-University Education (1st/2nd PUC with PCMB/PCMC/CEBA/etc.), Higher Education (B.E. Civil Engineering), and Unresolved Mismatch Subtotals. |
| **Sheet 7** | `Unmapped Review Records` | 12,002 rows | Dedicated ledger of the 12,000 flagged mismatch records (10,000 in PU Colleges SCH011–SCH015 and 2,000 in K-10 Schools SCH016–SCH020) awaiting Composite Institution Scenario B policy execution. Clearly notes existing classification, identified issue, and review status. |

---

### 2. Institution Directory Breakdown (All 31 Institutions)

The live database contains **31 institutions** across Karnataka. All institutions—including the 10 colleges and schools with zero current enrollments—are fully accounted for:

| # | Institution ID | Institution Name | Category | Type | District | Total Students | Active Enrollments | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 1 | `SCH001` | Government Model School | Schools (K-10) | School | Bengaluru Urban | 601 | 601 | Active (Mapped) |
| 2 | `SCH002` | Shanti Vidya Mandir | Schools (K-10) | School | Bengaluru Urban | 600 | 600 | Active (Mapped) |
| 3 | `SCH003` | National Public School | Schools (K-10) | School | Bengaluru Urban | 600 | 600 | Active (Mapped) |
| 4 | `SCH004` | Sri Vidya School | Schools (K-10) | School | Mysuru | 600 | 600 | Active (Mapped) |
| 5 | `SCH005` | Green Valley School | Schools (K-10) | School | Mysuru | 600 | 600 | Active (Mapped) |
| 6 | `SCH006` | Bharat Education School | Schools (K-10) | School | Tumakuru | 600 | 600 | Active (Mapped) |
| 7 | `SCH007` | New Horizon School | Schools (K-10) | School | Tumakuru | 600 | 600 | Active (Mapped) |
| 8 | `SCH008` | Vivekananda School | Schools (K-10) | School | Mandya | 600 | 600 | Active (Mapped) |
| 9 | `SCH009` | Saraswati Vidya Kendra | Schools (K-10) | School | Mandya | 600 | 600 | Active (Mapped) |
| 10 | `SCH010` | Karnataka Public School | Schools (K-10) | School | Hassan | 600 | 600 | Active (Mapped) |
| 11 | `SCH011` | Tumakuru Model Pre-University College | PU Colleges (11-12) | PU College | Tumakuru | 2,400 | 2,400 | Active (Mixed) |
| 12 | `SCH012` | Mysuru Government Pre-University College | PU Colleges (11-12) | PU College | Mysuru | 2,400 | 2,400 | Active (Mixed) |
| 13 | `SCH013` | Mandya Government Pre-University College | PU Colleges (11-12) | PU College | Mandya | 2,400 | 2,400 | Active (Mixed) |
| 14 | `SCH014` | Hassan Valley Pre-University College | PU Colleges (11-12) | PU College | Hassan | 2,400 | 2,400 | Active (Mixed) |
| 15 | `SCH015` | Udupi Government Pre-University College | PU Colleges (11-12) | PU College | Udupi | 2,400 | 2,400 | Active (Mixed) |
| 16 | `SCH016` | Belagavi Public School | Schools (K-10) | School | Belagavi | 2,400 | 2,400 | Active (Mixed) |
| 17 | `SCH017` | Dharwad Vidya School | Schools (K-10) | School | Dharwad | 2,400 | 2,400 | Active (Mixed) |
| 18 | `SCH018` | Shivamogga Model School | Schools (K-10) | School | Shivamogga | 2,400 | 2,400 | Active (Mixed) |
| 19 | `SCH019` | Ballari Education School | Schools (K-10) | School | Ballari | 2,400 | 2,400 | Active (Mixed) |
| 20 | `SCH020` | Kalaburagi Public School | Schools (K-10) | School | Kalaburagi | 2,400 | 2,400 | Active (Mixed) |
| 21 | `COL001` | Ramaiah Institute of Technology (MSRIT) | Degree Colleges | Degree College | Bengaluru Urban | 0 | 0 | Registered (Zero) |
| 22 | `COL002` | R.V. College of Engineering (RVCE) | Degree Colleges | Degree College | Bengaluru Urban | 0 | 0 | Registered (Zero) |
| 23 | `COL003` | BMS College of Engineering (BMSCE) | Degree Colleges | Degree College | Bengaluru Urban | 2 | 2 | Active (Mapped) |
| 24 | `COL004` | PES University (Ring Road Campus) | Universities | University | Bengaluru Urban | 0 | 0 | Registered (Zero) |
| 25 | `COL005` | The National Institute of Engineering (NIE) | Degree Colleges | Degree College | Mysuru | 0 | 0 | Registered (Zero) |
| 26 | `COL006` | St. Joseph's University | Universities | University | Bengaluru Urban | 0 | 0 | Registered (Zero) |
| 27 | `COL007` | Mount Carmel College (Autonomous) | Degree Colleges | Degree College | Bengaluru Urban | 0 | 0 | Registered (Zero) |
| 28 | `COL008` | KLE Technological University (BVBCET) | Universities | University | Dharwad | 0 | 0 | Registered (Zero) |
| 29 | `COL009` | University of Mysore (Manasagangotri) | Universities | University | Mysuru | 0 | 0 | Registered (Zero) |
| 30 | `COL010` | Visvesvaraya Technological University (VTU) | Universities | University | Belagavi | 0 | 0 | Registered (Zero) |
| 31 | `SCH0099` | Vidya Mandir English School | Schools (K-10) | Primary School | Bengaluru Urban | 0 | 0 | Registered (Zero) |
| **TOTAL** | — | **31 Registered Institutions** | — | — | **Karnataka State** | **30,003** | **30,003** | **100% Reconciled** |

---

### 3. Academic Programme & Course Summary

| Category / Academic Domain | Academic Division | Program ID / Course Code | Programme Name | Student Count |
| :--- | :--- | :--- | :--- | :---: |
| **School Education** | Primary & Secondary (Std 1–10) | `PROG-SCH001-K10` to `PROG-SCH010-K10` | Karnataka State School Education (Std 1–10) | 6,001 |
| **School Education** | Primary & Secondary (Std 1–10) | `PROG-SCH016-K10` to `PROG-SCH020-K10` | Karnataka State School Education (Std 1–10) | 10,000 |
| **Pre-University (PUC)** | Pre-University (Science) | `PROG-SCH011-PCMB` to `PROG-SCH015-PCMB` | Pre-University (PCMB Combination) | 500 |
| **Pre-University (PUC)** | Pre-University (Science) | `PROG-SCH011-PCMC` to `PROG-SCH015-PCMC` | Pre-University (PCMC Combination) | 300 |
| **Pre-University (PUC)** | Pre-University (Science) | `PROG-SCH011-PCME` to `PROG-SCH015-PCME` | Pre-University (PCME Combination) | 200 |
| **Pre-University (PUC)** | Pre-University (Commerce) | `PROG-SCH011-CEBA` to `PROG-SCH015-CEBA` | Pre-University (CEBA Combination) | 300 |
| **Pre-University (PUC)** | Pre-University (Commerce) | `PROG-SCH011-SEBA` to `PROG-SCH015-SEBA` | Pre-University (SEBA Combination) | 250 |
| **Pre-University (PUC)** | Pre-University (Commerce) | `PROG-SCH011-HEBA` to `PROG-SCH015-HEBA` | Pre-University (HEBA Combination) | 200 |
| **Pre-University (PUC)** | Pre-University (Commerce) | `PROG-SCH011-MEBA` to `PROG-SCH015-MEBA` | Pre-University (MEBA Combination) | 150 |
| **Pre-University (PUC)** | Pre-University (Arts) | `PROG-SCH011-HEPS` to `PROG-SCH015-HEPS` | Pre-University (HEPS Combination) | 100 |
| **Higher Education** | Engineering & Tech (UG) | `PROG-COL003-UG-02` | B.E. in Civil Engineering (Semester 1) | 2 |
| **Unmapped Group A** | Unresolved (Std 1–10 in PU) | `UNMAPPED-SCH-IN-PUC` | Unassigned - Review Required (Standards 1–10 in SCH011–SCH015) | 10,000 |
| **Unmapped Group B** | Unresolved (Std 11–12 in School) | `UNMAPPED-PUC-IN-K10` | Unassigned - Review Required (Standards 11–12 in SCH016–SCH020) | 2,000 |
| **GRAND TOTAL** | — | — | **All Academic Programs & Unmapped Ledgers** | **30,003** |

---

### 4. Unmapped & Review Records Investigation (12,000 Records)

As confirmed by direct database inspection, **Scenario B (Composite Institution Migration)** has not yet been executed on the live database. In accordance with strict audit instructions, missing information has **not** been synthetically invented or forcefully mapped:

1. **Group A: 10,000 Students in PU Colleges (`SCH011`–`SCH015`) carrying Standards 1–10**:
   - **Records**: 2,000 students per institution across 5 institutions = 10,000 students.
   - **Database State**: `standard` is between 1 and 10; `puc_year` is `NULL`; `program_id` is `NULL`; `degree` is `NULL`; `stream` carries `'Unassigned Primary/Secondary (Standards 1-10 in PU College)'`.
   - **Issue Identified**: Mismatched Institutional Assignment. Primary and secondary school-level students are assigned to Pre-University Colleges without valid PU Programme assignment.
   - **Reporting**: Exported with full transparency in Sheet 2, Sheet 3, Sheet 4, Sheet 5, Sheet 6, and exhaustively itemized row-by-row in **Sheet 7 (Unmapped Review Records)**.

2. **Group B: 2,000 Students in K-10 Schools (`SCH016`–`SCH020`) carrying Standards 11–12**:
   - **Records**: 400 students per institution across 5 institutions = 2,000 students.
   - **Database State**: `standard` is 11 or 12; `puc_year` is `NULL`; `program_id` is `NULL`; `degree` is `NULL`; `stream` carries `'Unassigned Higher Secondary (Standards 11-12 in K-10 School)'`.
   - **Issue Identified**: Mismatched Institutional Assignment. Higher secondary students (11th and 12th level) are assigned to K-10 Schools without valid School curriculum assignment.
   - **Reporting**: Exported with full transparency in Sheet 2, Sheet 3, Sheet 4, Sheet 5, Sheet 6, and exhaustively itemized row-by-row in **Sheet 7 (Unmapped Review Records)**.

---

### 5. Data Integrity, Uniqueness & Quality Assertions

An automated verification script (`verify_excel_workbook.py`) was executed on the generated Excel workbook:

```
[✓] Loading workbook: C:\Users\callm\nagriksetu\reports\NagrikSetu_Institution_Wise_Student_Course_Enrollment_Register.xlsx
[✓] All 7 Worksheets Present: TRUE
[✓] Sheet 1 (Institution Directory): 33 rows (31 institutions + 1 header + 1 total)
    -> Sum Registered Students: 30,003 | Sum Active Enrollments: 30,003
[✓] Sheet 2 (Complete Student Register): Exactly 30,003 student rows (plus header)
    -> Unique Student IDs: 30,003 (0 duplicates, 0 missing)
    -> Unique PSIDs: 30,003 (0 duplicates, 0 missing)
[✓] Sheet 3 (Institution-wise Student List): Exactly 30,003 student rows
[✓] Sheet 4 (Course Enrollment Register): Exactly 30,003 student rows
[✓] Sheet 5 (Course Summary): 304 rows, Reconciled Grand Total: 30,003 students
[✓] Sheet 6 (Academic Classification): All subtotals reconcile to 30,003 students
[✓] Sheet 7 (Unmapped Review Records): Exactly 12,000 rows
[✓] Database Count Reconciliation: 30,003 live DB students == 30,003 Excel student rows (100% Match)
```

- **Student ID Uniqueness**: 30,003 unique IDs out of 30,003 records. Zero duplicates.
- **Permanent Student ID (PSID) Uniqueness**: 30,003 unique PSIDs out of 30,003 records. Zero duplicates.
- **Institution ID Referential Integrity**: 100% of student `school_id` values match registered institutions in `schools`.
- **Enrollment Consistency**: All 30,003 students have valid records in `enrollments` with `academic_year = '2026-2027'` and `enrollment_status = 'active'`.

---

### 6. Deliverable Files Summary

1. **Excel Register**:
   - Path: [`C:\Users\callm\nagriksetu\reports\NagrikSetu_Institution_Wise_Student_Course_Enrollment_Register.xlsx`](file:///C:/Users/callm/nagriksetu/reports/NagrikSetu_Institution_Wise_Student_Course_Enrollment_Register.xlsx)
   - Size: **6.35 MB**
   - Format: OpenXML Spreadsheet (`.xlsx`) with 7 styled worksheets.
2. **Audit & Verification Report**:
   - Path: [`C:\Users\callm\nagriksetu\reports\NagrikSetu_Institution_Student_Course_Register_Verification.md`](file:///C:/Users/callm/nagriksetu/reports/NagrikSetu_Institution_Student_Course_Register_Verification.md)
   - Size: Full markdown verification audit report.
