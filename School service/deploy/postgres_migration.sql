-- ====================================================================
-- NAGRIKSETU POSTGRESQL PRODUCTION MIGRATION SCRIPT
-- Generated at UTC: 2026-11-03T06:51:03.757734
-- Source: SQLite 3.x -> Target: PostgreSQL 14+ / 16
-- ====================================================================

BEGIN;

SET client_encoding = 'UTF8';

SET standard_conforming_strings = on;

-- Table: academic_programs (Row count: 140)
CREATE TABLE IF NOT EXISTS "academic_programs" (
    "program_id" TEXT,
    "institution_id" TEXT NOT NULL,
    "education_level" TEXT NOT NULL,
    "program_name" TEXT NOT NULL,
    "degree_type" TEXT NOT NULL DEFAULT 'None',
    "discipline_or_stream" TEXT,
    "combination_code" TEXT,
    "faculty_name" TEXT,
    "department_name" TEXT,
    "duration_years" BIGINT NOT NULL DEFAULT 1,
    "is_active" BIGINT NOT NULL DEFAULT 1,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_academic_programs PRIMARY KEY ("program_id")
);

-- Table: academic_result_audits (Row count: 6)
CREATE TABLE IF NOT EXISTS "academic_result_audits" (
    "audit_id" TEXT,
    "result_id" TEXT NOT NULL,
    "previous_marks" NUMERIC,
    "new_marks" NUMERIC,
    "previous_max_marks" NUMERIC,
    "new_max_marks" NUMERIC,
    "reason_for_change" TEXT NOT NULL,
    "modified_by_user_id" TEXT NOT NULL,
    "modified_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_academic_result_audits PRIMARY KEY ("audit_id")
);

-- Table: academic_results (Row count: 17)
CREATE TABLE IF NOT EXISTS "academic_results" (
    "result_id" TEXT,
    "enrollment_id" TEXT NOT NULL,
    "subject_name" TEXT NOT NULL,
    "exam_name" TEXT NOT NULL,
    "marks_obtained" NUMERIC NOT NULL,
    "maximum_marks" NUMERIC NOT NULL,
    "academic_year" TEXT NOT NULL,
    "exam_date" TEXT,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "permanent_student_id" TEXT,
    "exam_id" TEXT,
    "grade" TEXT,
    "percentage" NUMERIC,
    "recorded_by_user_id" TEXT,
    "updated_at" TEXT,
    CONSTRAINT pk_academic_results PRIMARY KEY ("result_id")
);

-- Table: admission_applications (Row count: 60)
CREATE TABLE IF NOT EXISTS "admission_applications" (
    "application_id" VARCHAR,
    "institution_id" VARCHAR NOT NULL,
    "division_id" VARCHAR DEFAULT NULL,
    "parent_user_id" VARCHAR DEFAULT NULL,
    "applicant_name" VARCHAR NOT NULL,
    "parent_name" VARCHAR NOT NULL,
    "parent_phone" VARCHAR NOT NULL,
    "parent_email" VARCHAR,
    "residential_address" TEXT NOT NULL,
    "academic_year" VARCHAR NOT NULL,
    "education_level" VARCHAR NOT NULL,
    "requested_standard" BIGINT DEFAULT NULL,
    "requested_program_id" VARCHAR DEFAULT NULL,
    "first_language_preference" VARCHAR DEFAULT NULL,
    "stream_preference" VARCHAR DEFAULT NULL,
    "combination_code" VARCHAR DEFAULT NULL,
    "status" VARCHAR NOT NULL DEFAULT 'submitted',
    "reviewer_user_id" VARCHAR DEFAULT NULL,
    "rejection_reason" TEXT DEFAULT NULL,
    "rejection_explanation" TEXT DEFAULT NULL,
    "institution_contact_phone" VARCHAR DEFAULT NULL,
    "clarification_request" TEXT DEFAULT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "second_language_preference" VARCHAR DEFAULT NULL,
    "enrolled_student_id" TEXT,
    "enrolled_at" TEXT,
    CONSTRAINT pk_admission_applications PRIMARY KEY ("application_id")
);

-- Table: admission_detailed_submissions (Row count: 7)
CREATE TABLE IF NOT EXISTS "admission_detailed_submissions" (
    "submission_id" VARCHAR,
    "application_id" VARCHAR NOT NULL,
    "date_of_birth" TEXT,
    "gender" VARCHAR,
    "blood_group" VARCHAR,
    "previous_institution_name" VARCHAR,
    "previous_institution_location" VARCHAR,
    "previous_standard_or_degree" VARCHAR,
    "previous_board" VARCHAR,
    "previous_marks_percentage" NUMERIC,
    "emergency_contact_name" VARCHAR,
    "emergency_contact_phone" VARCHAR,
    "custom_fields_json" TEXT,
    "status" VARCHAR NOT NULL DEFAULT 'submitted',
    "submitted_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_admission_detailed_submissions PRIMARY KEY ("submission_id")
);

-- Table: admission_documents (Row count: 25)
CREATE TABLE IF NOT EXISTS "admission_documents" (
    "document_id" VARCHAR,
    "application_id" VARCHAR NOT NULL,
    "document_type" VARCHAR NOT NULL,
    "file_name" VARCHAR NOT NULL,
    "file_path" VARCHAR NOT NULL,
    "file_size_bytes" BIGINT NOT NULL,
    "mime_type" VARCHAR NOT NULL,
    "verification_status" VARCHAR DEFAULT 'pending',
    "uploaded_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "verified_by_user_id" VARCHAR DEFAULT NULL,
    "verified_at" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    "verification_notes" TEXT DEFAULT NULL,
    CONSTRAINT pk_admission_documents PRIMARY KEY ("document_id")
);

-- Table: admission_status_history (Row count: 114)
CREATE TABLE IF NOT EXISTS "admission_status_history" (
    "history_id" VARCHAR,
    "application_id" VARCHAR NOT NULL,
    "previous_status" VARCHAR,
    "new_status" VARCHAR NOT NULL,
    "action_by_user_id" VARCHAR NOT NULL,
    "action_note" TEXT,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_admission_status_history PRIMARY KEY ("history_id")
);

-- Table: audit_logs (Row count: 298)
CREATE TABLE IF NOT EXISTS "audit_logs" (
    "audit_id" TEXT,
    "actor_user_id" TEXT,
    "actor_role" TEXT,
    "action" TEXT NOT NULL,
    "entity_type" TEXT NOT NULL,
    "entity_id" TEXT,
    "school_id" TEXT,
    "ip_address" TEXT,
    "metadata_json" TEXT NOT NULL DEFAULT '{}',
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_audit_logs PRIMARY KEY ("audit_id")
);

-- Table: collegiate_enrollments (Row count: 0)
CREATE TABLE IF NOT EXISTS "collegiate_enrollments" (
    "enrollment_id" TEXT,
    "permanent_student_id" TEXT NOT NULL,
    "institution_id" TEXT NOT NULL,
    "program_id" TEXT NOT NULL,
    "academic_year" TEXT NOT NULL,
    "current_year_or_term" BIGINT NOT NULL,
    "section" TEXT NOT NULL DEFAULT 'A',
    "enrollment_status" TEXT NOT NULL DEFAULT 'active',
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_collegiate_enrollments PRIMARY KEY ("enrollment_id")
);

-- Table: document_ocr_extractions (Row count: 2)
CREATE TABLE IF NOT EXISTS "document_ocr_extractions" (
    "extraction_id" TEXT,
    "document_id" TEXT NOT NULL,
    "application_id" TEXT NOT NULL,
    "raw_text" TEXT NOT NULL,
    "ocr_engine" TEXT NOT NULL,
    "average_confidence" NUMERIC NOT NULL,
    "extracted_entities_json" TEXT NOT NULL,
    "match_status" TEXT NOT NULL DEFAULT 'unreviewed',
    "discrepancy_notes" TEXT,
    "extracted_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_document_ocr_extractions PRIMARY KEY ("extraction_id")
);

-- Table: enrollments (Row count: 30001)
CREATE TABLE IF NOT EXISTS "enrollments" (
    "enrollment_id" TEXT,
    "permanent_student_id" TEXT NOT NULL,
    "school_id" TEXT NOT NULL,
    "academic_year" TEXT NOT NULL,
    "standard" BIGINT NOT NULL,
    "section" TEXT NOT NULL,
    "first_language" TEXT NOT NULL,
    "stream" TEXT,
    "subject_combination" TEXT,
    "admission_date" TEXT,
    "leaving_date" TEXT,
    "enrollment_status" TEXT NOT NULL DEFAULT 'active',
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_enrollments PRIMARY KEY ("enrollment_id")
);

-- Table: examinations (Row count: 38)
CREATE TABLE IF NOT EXISTS "examinations" (
    "exam_id" TEXT,
    "institution_id" TEXT NOT NULL,
    "academic_year" TEXT NOT NULL DEFAULT '2026-2027',
    "exam_name" TEXT NOT NULL,
    "standard_or_level" TEXT NOT NULL,
    "start_date" TEXT,
    "end_date" TEXT,
    "status" TEXT NOT NULL DEFAULT 'scheduled',
    "description" TEXT,
    "created_by_user_id" TEXT NOT NULL,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_examinations PRIMARY KEY ("exam_id")
);

-- Table: fees (Row count: 0)
CREATE TABLE IF NOT EXISTS "fees" (
    "fee_id" TEXT,
    "permanent_student_id" TEXT NOT NULL,
    "school_id" TEXT NOT NULL,
    "academic_year" TEXT NOT NULL,
    "fee_type" TEXT NOT NULL,
    "amount_due" NUMERIC NOT NULL,
    "amount_paid" NUMERIC NOT NULL DEFAULT 0,
    "due_date" TEXT,
    "payment_status" TEXT NOT NULL DEFAULT 'pending',
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_fees PRIMARY KEY ("fee_id")
);

-- Table: guardians (Row count: 16)
CREATE TABLE IF NOT EXISTS "guardians" (
    "guardian_id" TEXT,
    "user_id" TEXT,
    "full_name" TEXT NOT NULL,
    "relationship" TEXT NOT NULL,
    "phone" TEXT NOT NULL,
    "email" TEXT,
    "address" TEXT,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_guardians PRIMARY KEY ("guardian_id")
);

-- Table: institution_announcements (Row count: 25)
CREATE TABLE IF NOT EXISTS "institution_announcements" (
    "announcement_id" TEXT,
    "institution_id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "target_audience" TEXT NOT NULL DEFAULT 'all',
    "published_date" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_user_id" TEXT NOT NULL,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_institution_announcements PRIMARY KEY ("announcement_id")
);

-- Table: institution_divisions (Row count: 28)
CREATE TABLE IF NOT EXISTS "institution_divisions" (
    "division_id" VARCHAR,
    "parent_institution_id" VARCHAR NOT NULL,
    "division_name" VARCHAR NOT NULL,
    "division_type" VARCHAR NOT NULL,
    "campus_location" VARCHAR NOT NULL,
    "head_of_division" VARCHAR,
    "contact_phone" VARCHAR,
    "contact_email" VARCHAR,
    "facilities_summary" TEXT,
    "description" TEXT,
    "display_order" BIGINT DEFAULT 1,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_institution_divisions PRIMARY KEY ("division_id")
);

-- Table: institution_staff_permissions (Row count: 23)
CREATE TABLE IF NOT EXISTS "institution_staff_permissions" (
    "id" TEXT,
    "user_id" TEXT NOT NULL,
    "institution_id" TEXT NOT NULL,
    "role_id" TEXT NOT NULL,
    "can_view_applications" BIGINT NOT NULL DEFAULT 0,
    "can_review_details" BIGINT NOT NULL DEFAULT 0,
    "can_request_clarification" BIGINT NOT NULL DEFAULT 0,
    "can_recommend_decision" BIGINT NOT NULL DEFAULT 0,
    "can_approve_stage1" BIGINT NOT NULL DEFAULT 0,
    "can_view_history" BIGINT NOT NULL DEFAULT 0,
    "can_manage_academics" BIGINT NOT NULL DEFAULT 0,
    "can_manage_students" BIGINT NOT NULL DEFAULT 0,
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_by" TEXT,
    CONSTRAINT pk_institution_staff_permissions PRIMARY KEY ("id")
);

-- Table: invitation_tokens (Row count: 26)
CREATE TABLE IF NOT EXISTS "invitation_tokens" (
    "token_id" TEXT,
    "token_hash" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "institution_id" TEXT NOT NULL,
    "role_id" TEXT NOT NULL,
    "expires_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "is_used" BIGINT DEFAULT 0,
    "used_at" TIMESTAMP WITH TIME ZONE,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "created_by" TEXT,
    CONSTRAINT pk_invitation_tokens PRIMARY KEY ("token_id")
);

-- Table: linking_requests (Row count: 5)
CREATE TABLE IF NOT EXISTS "linking_requests" (
    "request_id" TEXT,
    "parent_user_id" TEXT NOT NULL,
    "school_id" TEXT NOT NULL,
    "student_ref" TEXT NOT NULL,
    "relationship_type" TEXT NOT NULL,
    "verification_doc_id" TEXT,
    "additional_notes" TEXT,
    "request_status" TEXT NOT NULL DEFAULT 'pending',
    "reviewer_user_id" TEXT,
    "reviewer_comment" TEXT,
    "permanent_student_id" TEXT,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "reviewed_at" TEXT,
    CONSTRAINT pk_linking_requests PRIMARY KEY ("request_id")
);

-- Table: notification_delivery_logs (Row count: 28)
CREATE TABLE IF NOT EXISTS "notification_delivery_logs" (
    "log_id" VARCHAR,
    "notification_id" VARCHAR NOT NULL,
    "channel" VARCHAR NOT NULL,
    "recipient_destination" VARCHAR,
    "status" VARCHAR NOT NULL,
    "error_message" TEXT,
    "retry_count" BIGINT DEFAULT 0,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_notification_delivery_logs PRIMARY KEY ("log_id")
);

-- Table: notification_preferences (Row count: 1)
CREATE TABLE IF NOT EXISTS "notification_preferences" (
    "preference_id" VARCHAR,
    "user_id" VARCHAR NOT NULL,
    "academic_updates" BIGINT DEFAULT 1,
    "attendance_alerts" BIGINT DEFAULT 1,
    "examination_alerts" BIGINT DEFAULT 1,
    "admission_updates" BIGINT DEFAULT 1,
    "institution_announcements" BIGINT DEFAULT 1,
    "administrative_alerts" BIGINT DEFAULT 1,
    "email_enabled" BIGINT DEFAULT 1,
    "sms_enabled" BIGINT DEFAULT 1,
    "whatsapp_enabled" BIGINT DEFAULT 0,
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_notification_preferences PRIMARY KEY ("preference_id")
);

-- Table: password_reset_tokens (Row count: 6)
CREATE TABLE IF NOT EXISTS "password_reset_tokens" (
    "reset_id" TEXT,
    "token_hash" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "expires_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "is_used" BIGINT DEFAULT 0,
    "used_at" TIMESTAMP WITH TIME ZONE,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_password_reset_tokens PRIMARY KEY ("reset_id")
);

-- Table: portal_notifications (Row count: 149)
CREATE TABLE IF NOT EXISTS "portal_notifications" (
    "notification_id" VARCHAR,
    "recipient_user_id" VARCHAR DEFAULT NULL,
    "recipient_role" VARCHAR DEFAULT NULL,
    "institution_id" VARCHAR DEFAULT NULL,
    "application_id" VARCHAR DEFAULT NULL,
    "title" VARCHAR NOT NULL,
    "message" TEXT NOT NULL,
    "action_url" VARCHAR,
    "is_read" BIGINT DEFAULT 0,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "category" VARCHAR DEFAULT 'general',
    "priority" VARCHAR DEFAULT 'normal',
    "channel" VARCHAR DEFAULT 'in_app',
    "delivery_status" VARCHAR DEFAULT 'delivered',
    "related_record_type" VARCHAR,
    "related_record_id" VARCHAR,
    "read_at" TIMESTAMP WITH TIME ZONE,
    "idempotency_key" VARCHAR,
    CONSTRAINT pk_portal_notifications PRIMARY KEY ("notification_id")
);

-- Table: program_sections (Row count: 455)
CREATE TABLE IF NOT EXISTS "program_sections" (
    "section_id" TEXT,
    "institution_id" TEXT NOT NULL,
    "program_id" TEXT NOT NULL,
    "academic_year" TEXT NOT NULL,
    "term_or_year" BIGINT NOT NULL DEFAULT 1,
    "semester" BIGINT,
    "section_name" TEXT NOT NULL,
    "capacity" BIGINT NOT NULL DEFAULT 60,
    "current_strength" BIGINT NOT NULL DEFAULT 0,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_program_sections PRIMARY KEY ("section_id")
);

-- Table: scholarships (Row count: 0)
CREATE TABLE IF NOT EXISTS "scholarships" (
    "scholarship_id" TEXT,
    "permanent_student_id" TEXT NOT NULL,
    "scholarship_name" TEXT NOT NULL,
    "eligibility_status" TEXT NOT NULL DEFAULT 'not_assessed',
    "application_status" TEXT NOT NULL DEFAULT 'not_applied',
    "academic_year" TEXT NOT NULL,
    "notes" TEXT,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_scholarships PRIMARY KEY ("scholarship_id")
);

-- Table: school_achievements (Row count: 21)
CREATE TABLE IF NOT EXISTS "school_achievements" (
    "achievement_id" TEXT,
    "school_id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "achievement_date" TEXT,
    "public_document_url" TEXT,
    "is_published" BIGINT NOT NULL DEFAULT 0,
    "year" BIGINT,
    "award_level" TEXT DEFAULT 'State',
    "issuing_authority" TEXT,
    "verification_status" TEXT DEFAULT 'verified',
    CONSTRAINT pk_school_achievements PRIMARY KEY ("achievement_id")
);

-- Table: school_change_log (Row count: 1)
CREATE TABLE IF NOT EXISTS "school_change_log" (
    "log_id" TEXT,
    "school_id" TEXT NOT NULL,
    "permanent_student_id" TEXT NOT NULL,
    "field_name" TEXT NOT NULL,
    "old_value" TEXT,
    "new_value" TEXT,
    "changed_by_user_id" TEXT,
    "change_reason" TEXT,
    "changed_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_school_change_log PRIMARY KEY ("log_id")
);

-- Table: school_programs (Row count: 0)
CREATE TABLE IF NOT EXISTS "school_programs" (
    "program_id" TEXT,
    "school_id" TEXT NOT NULL,
    "standard" BIGINT NOT NULL,
    "section" TEXT,
    "first_language" TEXT,
    "stream" TEXT,
    "subject_combination" TEXT,
    "is_available" BIGINT NOT NULL DEFAULT 1,
    CONSTRAINT pk_school_programs PRIMARY KEY ("program_id")
);

-- Table: school_transfers (Row count: 0)
CREATE TABLE IF NOT EXISTS "school_transfers" (
    "transfer_id" TEXT,
    "permanent_student_id" TEXT NOT NULL,
    "previous_enrollment_id" TEXT,
    "new_enrollment_id" TEXT,
    "requested_by_guardian_id" TEXT,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "reason" TEXT,
    "requested_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "reviewed_by_user_id" TEXT,
    "reviewed_at" TEXT,
    CONSTRAINT pk_school_transfers PRIMARY KEY ("transfer_id")
);

-- Table: schools (Row count: 30)
CREATE TABLE IF NOT EXISTS "schools" (
    "school_id" TEXT,
    "school_name" TEXT NOT NULL,
    "district" TEXT NOT NULL,
    "state" TEXT NOT NULL,
    "school_type" TEXT NOT NULL,
    "address" TEXT,
    "established_year" BIGINT,
    "description" TEXT,
    "public_phone" TEXT,
    "website" TEXT,
    "facilities_json" TEXT NOT NULL DEFAULT '[]',
    "logo_url" TEXT,
    "cover_image_url" TEXT,
    "email" TEXT,
    "affiliation" TEXT,
    "recognition" TEXT,
    "campus_name" TEXT,
    "is_parent_group" BIGINT DEFAULT 0,
    "map_url" TEXT,
    "about_json" TEXT,
    "facilities_details_json" TEXT,
    "hostel_details_json" TEXT,
    "transport_details_json" TEXT,
    "admissions_details_json" TEXT,
    "category" TEXT,
    CONSTRAINT pk_schools PRIMARY KEY ("school_id")
);

-- Table: staff_applications (Row count: 13)
CREATE TABLE IF NOT EXISTS "staff_applications" (
    "application_id" TEXT,
    "candidate_token" TEXT NOT NULL,
    "institution_id" TEXT NOT NULL,
    "candidate_email" TEXT NOT NULL,
    "candidate_name" TEXT NOT NULL,
    "candidate_phone" TEXT,
    "role_id" TEXT NOT NULL DEFAULT 'school_staff',
    "status" TEXT NOT NULL DEFAULT 'invited',
    "qualifications_json" TEXT DEFAULT '[]',
    "employment_details_json" TEXT DEFAULT '{}',
    "documents_json" TEXT DEFAULT '[]',
    "correction_notes" TEXT,
    "review_notes" TEXT,
    "created_by_user_id" TEXT,
    "reviewed_by_user_id" TEXT,
    "reviewed_at" TIMESTAMP WITH TIME ZONE,
    "activation_token" TEXT,
    "activation_expires_at" TIMESTAMP WITH TIME ZONE,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_staff_applications PRIMARY KEY ("application_id")
);

-- Table: student_attendance (Row count: 23)
CREATE TABLE IF NOT EXISTS "student_attendance" (
    "attendance_id" TEXT,
    "institution_id" TEXT NOT NULL,
    "permanent_student_id" TEXT NOT NULL,
    "academic_year" TEXT NOT NULL DEFAULT '2026-2027',
    "attendance_date" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "subject_name" TEXT,
    "remarks" TEXT,
    "recorded_by_user_id" TEXT NOT NULL,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_student_attendance PRIMARY KEY ("attendance_id")
);

-- Table: student_documents (Row count: 0)
CREATE TABLE IF NOT EXISTS "student_documents" (
    "document_id" TEXT,
    "permanent_student_id" TEXT NOT NULL,
    "enrollment_id" TEXT,
    "document_type" TEXT NOT NULL,
    "file_name" TEXT NOT NULL,
    "private_storage_key" TEXT NOT NULL,
    "uploaded_by_user_id" TEXT,
    "verified_by_user_id" TEXT,
    "verification_status" TEXT NOT NULL DEFAULT 'pending',
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_student_documents PRIMARY KEY ("document_id")
);

-- Table: student_guardians (Row count: 6)
CREATE TABLE IF NOT EXISTS "student_guardians" (
    "student_guardian_id" TEXT,
    "permanent_student_id" TEXT NOT NULL,
    "guardian_id" TEXT NOT NULL,
    "can_view_records" BIGINT NOT NULL DEFAULT 1,
    "can_request_updates" BIGINT NOT NULL DEFAULT 1,
    "is_verified" BIGINT NOT NULL DEFAULT 0,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_student_guardians PRIMARY KEY ("student_guardian_id")
);

-- Table: students (Row count: 30001)
CREATE TABLE IF NOT EXISTS "students" (
    "student_id" TEXT,
    "student_name" TEXT NOT NULL,
    "school_id" TEXT NOT NULL,
    "standard" BIGINT NOT NULL,
    "section" TEXT NOT NULL,
    "age" BIGINT NOT NULL,
    "permanent_student_id" TEXT,
    "first_language" TEXT,
    "date_of_birth" TEXT,
    "gender" TEXT,
    "admission_date" TEXT,
    "enrollment_status" TEXT NOT NULL DEFAULT 'active',
    CONSTRAINT pk_students PRIMARY KEY ("student_id")
);

-- Table: update_requests (Row count: 2)
CREATE TABLE IF NOT EXISTS "update_requests" (
    "request_id" TEXT,
    "permanent_student_id" TEXT NOT NULL,
    "guardian_id" TEXT NOT NULL,
    "request_type" TEXT NOT NULL,
    "field_name" TEXT NOT NULL,
    "old_value" TEXT,
    "proposed_value" TEXT NOT NULL,
    "reason" TEXT,
    "supporting_document_id" TEXT,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "reviewed_by_user_id" TEXT,
    "review_comment" TEXT,
    "submitted_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "reviewed_at" TEXT,
    CONSTRAINT pk_update_requests PRIMARY KEY ("request_id")
);

-- Table: user_institution_roles (Row count: 36)
CREATE TABLE IF NOT EXISTS "user_institution_roles" (
    "id" TEXT,
    "user_id" TEXT NOT NULL,
    "institution_id" TEXT NOT NULL,
    "role_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'active',
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "created_by" TEXT,
    CONSTRAINT pk_user_institution_roles PRIMARY KEY ("id")
);

-- Table: users (Row count: 54)
CREATE TABLE IF NOT EXISTS "users" (
    "user_id" TEXT,
    "email" TEXT,
    "phone" TEXT,
    "password_hash" TEXT NOT NULL,
    "role" TEXT NOT NULL,
    "school_id" TEXT,
    "is_active" BIGINT NOT NULL DEFAULT 1,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "full_name" TEXT,
    "status" TEXT DEFAULT 'active',
    "last_login" TEXT,
    "permanent_student_id" TEXT,
    "student_id" TEXT,
    CONSTRAINT pk_users PRIMARY KEY ("user_id")
);

COMMIT;
