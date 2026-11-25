# NagrikSetu School Service – Parent Request Visibility and Admin Routing Fix Report

**Project:** NagrikSetu School Service  
**Authoritative Path:** `C:\Users\callm\Nagriksetu School Service`  
**Database:** `backend\data\nagriksetu.db`  
**Date:** November 23, 2026  
**Status:** Verified & Resolved  

---

## 1. Executive Summary

This report documents the investigation, root cause diagnosis, code modifications, security validation, and live verification for the issue where requests submitted by parents (specifically `TRK-548751`: **Mobile Number Update** for Dharwad Vidya School **`SCH017`**) were visible in the Parent Portal but failed to appear in the corresponding School Administrator dashboard.

Following the fix:
1. **Mobile Number Update** and other demographic correction requests submitted by parents appear immediately under **Data Correction Requests** in the assigned school administrator's dashboard.
2. **Parent/Guardian Verification Requests** remain strictly in their dedicated sub-tab, preventing mixing of student linking and data correction workflows.
3. Strict institution isolation is enforced on the backend: an administrator can only access and review requests assigned to their institution (`SCH017` cannot view `SCH001` requests, and vice versa).
4. Administrator determinations (Approve / Reject / Clarify) update the live database, log comprehensive audit trails, and instantly reflect across both the School Administrator desk and the Parent Portal.

---

## 2. Root Cause Analysis & Architecture Trace

### 2.1 The Two Disconnected Request Pipelines
When parents submit record modification requests via the modern Parent Portal (`RequesterPortalView.jsx`), the frontend dispatches:
```http
POST /requests/raise
```
This endpoint (defined in [request_management_service.py](file:///C:/Users/callm/Nagriksetu%20School%20Service/backend/request_management_service.py)) stores the request in the **`service_requests`** database table with tracking number `TRK-548751` and status `SUBMITTED`, assigning it to `assigned_institution_id = 'SCH017'`.

However, the School Administrator's **Parent Requests Desk** (`InstitutionParentRequestsDesk.jsx` under sub-tab *Data Correction Requests*) was invoking:
```http
GET /institution/{institution_id}/parent-requests
```
In [backend/main.py](file:///C:/Users/callm/Nagriksetu%20School%20Service/backend/main.py#L14136), this endpoint was querying **only** the legacy `update_requests` table:
```sql
SELECT ur.request_id, ...
FROM update_requests ur
JOIN students s ON s.permanent_student_id = ur.permanent_student_id
WHERE s.school_id = ?
```
Because `TRK-548751` was persisted in `service_requests`, the SQL query returned **0 records** for `SCH017`. Consequently, the administrator dashboard displayed an empty table.

### 2.2 Category Routing Defect
In [request_management_service.py](file:///C:/Users/callm/Nagriksetu%20School%20Service/backend/request_management_service.py#L36), `INSTITUTION_CATEGORIES` did not include `"Mobile Number Update"`, `"Parent / Guardian Information Correction"`, `"Email Address Update"`, and `"Residential Address Update"`. While requests with explicit student IDs were resolved, parent self-targeted updates lacked automatic fallback resolution to their child's enrolled institution.

### 2.3 Status Filter Mismatch in Frontend
In `InstitutionParentRequestsDesk.jsx`, the status filter was matching only exact string equality (e.g. `r.status === 'pending'`). Requests from `service_requests` arrive with statuses such as `'SUBMITTED'`, `'CORRECTED'`, `'ACCEPTED'`, or `'CLARIFICATION_REQUIRED'`. A submitted request was therefore hidden when selecting "Pending Review".

---

## 3. Database State of Request `TRK-548751`

Prior to the fix, the database record was inspected and verified in `nagriksetu.db`:

| Field | Stored Value |
|---|---|
| **Request ID** | `REQ-2026-1A9E7AD9` |
| **Tracking Number** | `TRK-548751` |
| **Category** | `Mobile Number Update` |
| **Title** | `Based on parent personal details` |
| **Description** | `i want to change my phone number to 6361168424` |
| **Priority** | `urgent` |
| **Requester User ID** | `d2be8636-e98e-4a13-8e8a-06f8d006c9ee` (`Phalguna S`) |
| **Requester Phone** | `9638520147` |
| **Affected Student ID** | `SCH172081` |
| **Permanent Student ID** | `NS-SCH017-STD02-014` |
| **Affected Person Name** | `Rohan Kulkarni 14614` |
| **Assigned Institution ID** | `SCH017` |
| **Target Module** | `guardians` |
| **Field Name** | `phone` |
| **Current Value** | `9638520147` |
| **Requested Value** | `6361168424` |
| **Initial Status** | `SUBMITTED` |

Administrator assigned for `SCH017`:
- **User:** `Dharwad Vidya School Administrator` (`dharwad@edu.in`)
- **Institution:** Dharwad Vidya School (`SCH017`)
- **Role:** `school_admin`

---

## 4. Required Fixes Implemented

### 4.1 Backend Unified Parent Requests Endpoint
**File:** [backend/main.py](file:///C:/Users/callm/Nagriksetu%20School%20Service/backend/main.py#L14136-L14240)
- Enhanced `GET /institution/{institution_id}/parent-requests` to query both `service_requests` (routed to this institution) and legacy `update_requests`.
- Standardized columns: `request_id`, `tracking_number`, `permanent_student_id`, `student_name`, `parent_name`, `parent_phone`, `parent_email`, `field_name`, `current_value`, `requested_value`, `reason`, `status`, `submitted_at`, and `category`.
- Implemented robust status mapping for query parameters (`pending`, `approved`, `rejected`, `clarification_requested`).
- Updated `get_institution_dashboard_overview` to count pending requests across both sources.

### 4.2 Backend Determination Review Handler
**File:** [backend/main.py](file:///C:/Users/callm/Nagriksetu%20School%20Service/backend/main.py#L14242-L14395)
- Enhanced `POST /institution/{institution_id}/parent-requests/{request_id}/review` to review `service_requests` and legacy `update_requests`.
- Enforces strict institution authorization: `user["school_id"] == inst_id`.
- On approval of demographic corrections:
  1. Updates `guardians.phone` (or email/address/name) and `users.phone`.
  2. Updates `service_requests.status = 'CORRECTED'` and sets `current_value = requested_value`.
  3. Records entry in `request_corrections`.
  4. Records immutable transition in `request_status_history`.
  5. Records entry in `request_audit_logs` and `platform_audit_logs`.
- Supports rejection and clarification requests with parent notification records.

### 4.3 Institution Categories & Automatic Routing
**File:** [backend/request_management_service.py](file:///C:/Users/callm/Nagriksetu%20School%20Service/backend/request_management_service.py#L36-L53)
- Added `"Mobile Number Update"`, `"Parent / Guardian Information Correction"`, `"Email Address Update"`, and `"Residential Address Update"` to `INSTITUTION_CATEGORIES`.
- Added automatic resolution in `POST /requests/raise` when parent submits for self: auto-detects the child's school via verified guardian links if no institution ID is passed.

### 4.4 Frontend Desk & Status Mapping
**File:** [frontend/src/components/admin/InstitutionParentRequestsDesk.jsx](file:///C:/Users/callm/Nagriksetu%20School%20Service/frontend/src/components/admin/InstitutionParentRequestsDesk.jsx#L250-L265)
- Updated status filtering with grouping helpers:
  - `pending`: matches `pending`, `submitted`, `under_review`
  - `approved`: matches `approved`, `accepted`, `corrected`, `verified`
  - `rejected`: matches `rejected`, `cancelled`
  - `clarification_requested`: matches `clarification_requested`, `clarification_required`, `resubmitted`
- Displays `r.tracking_number || r.request_id` in the table and inspection modal for end-to-end tracking consistency.
- Updated review payload to dispatch `action`, `decision`, `remarks`, and `comment`.

### 4.5 Status Badge Color Mapping
**File:** [frontend/src/components/ui/StatusBadge.jsx](file:///C:/Users/callm/Nagriksetu%20School%20Service/frontend/src/components/ui/StatusBadge.jsx#L4-L22)
- Added color-coded badges for `submitted`, `corrected`, `accepted`, `clarification_required`, `clarification_requested`, `resubmitted`, and `closed`.

---

## 5. Security & Isolation Verification

Backend authorization was tested against multi-institution cross-access attempts:

```text
[Security Check 1] Dharwad Vidya School (SCH017) Admin -> GET /institution/SCH001/parent-requests
Result: HTTP 403 Forbidden (Access Denied: You are not assigned to this institution)

[Security Check 2] Government Model School (SCH001) Admin -> GET /institution/SCH017/parent-requests
Result: HTTP 403 Forbidden (Access Denied: You are not assigned to this institution)
```

No cross-institution data leakage occurs. Security relies entirely on server-side token validation and database query scoping.

---

## 6. End-to-End Test Suite Execution

A 10-point test suite was executed against the running backend:

| # | Test Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | School Admin Login (`SCH017`) | Token issued for `SCH017` | Token issued for `SCH017` | **PASS** |
| 2 | Target Request Visibility | `TRK-548751` in `/parent-requests` | 1 request returned (`TRK-548751`) | **PASS** |
| 3 | Cross-Institution Block (`SCH017` on `SCH001`) | HTTP 403 | HTTP 403 Forbidden | **PASS** |
| 4 | Cross-Institution Block (`SCH001` on `SCH017`) | HTTP 403 | HTTP 403 Forbidden | **PASS** |
| 5 | Linking Requests Separation | `TRK-548751` not in `/linking-requests` | 0 items, no TRK | **PASS** |
| 6 | Admin Determination Review (Approve) | Status 200, status `CORRECTED` | Status 200, `CORRECTED` | **PASS** |
| 7 | DB Persistence in `service_requests` | Status `CORRECTED`, value updated | Status `CORRECTED`, value `6361168424` | **PASS** |
| 8 | DB Persistence in `guardians` & `users` | Phone updated to `6361168424` | `guardians.phone` & `users.phone` updated | **PASS** |
| 9 | Parent Portal Reflection | Status `CORRECTED` on `/requests/my-requests` | Status `CORRECTED` | **PASS** |
| 10 | Status Filter & Dashboard Overview | Filter `approved` includes `TRK-548751` | Filter includes `TRK-548751` | **PASS** |

---

## 7. Visual Browser QA Evidence

Live verification was performed in Chrome on the Dharwad Vidya School Administrator Dashboard (`http://localhost:5173/#/institution-admin?tab=parent_requests`):

1. Logged in as `dharwad@edu.in` / `dharwad@123`.
2. Navigated to **Parent Authorization & Governance**.
3. Selected sub-tab **📝 Data Correction Requests**.
4. Observed `TRK-548751` in the table with student `Rohan Kulkarni 14614`, parent `Phalguna S`, field `phone`, requested value `6361168424`, and status `CORRECTED`.
5. Clicked **Inspect & Review →** to inspect the review modal:

![Parent Request Visibility Verified](file:///C:/Users/callm/.gemini/antigravity/brain/010bed14-ca45-4c39-a172-471440a90a20/parent_request_visibility_verified.png)

---

## 8. Summary of Modified Files

1. [backend/main.py](file:///C:/Users/callm/Nagriksetu%20School%20Service/backend/main.py):
   - Merged `service_requests` and `update_requests` into `GET /institution/{institution_id}/parent-requests`.
   - Updated `POST /institution/{institution_id}/parent-requests/{request_id}/review` to process demographic updates on live tables.
   - Updated `GET /institution/{institution_id}/dashboard-overview` metrics calculation.
2. [backend/request_management_service.py](file:///C:/Users/callm/Nagriksetu%20School%20Service/backend/request_management_service.py):
   - Added parent demographic categories to `INSTITUTION_CATEGORIES`.
   - Added parent verified linked child school resolution fallback.
3. [frontend/src/components/admin/InstitutionParentRequestsDesk.jsx](file:///C:/Users/callm/Nagriksetu%20School%20Service/frontend/src/components/admin/InstitutionParentRequestsDesk.jsx):
   - Displayed tracking ID in table and review modal.
   - Robust status filter matching.
   - Standardized determination payload dispatch.
4. [frontend/src/components/ui/StatusBadge.jsx](file:///C:/Users/callm/Nagriksetu%20School%20Service/frontend/src/components/ui/StatusBadge.jsx):
   - Added color-coded badges for all request lifecycle statuses.
