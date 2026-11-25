-- NagrikSetu Skill Development Service - Database Migration
-- Phase 1 & 2: Safe Incremental Schema Enhancements (RBAC & Centre-Level Isolation)
-- Target Database: MySQL 8.4 (skill_db)

-- 1. Training Centres: Add Accreditation and Capacity Columns
ALTER TABLE training_centres
  ADD COLUMN IF NOT EXISTS approval_status VARCHAR(32) NOT NULL DEFAULT 'APPROVED',
  ADD COLUMN IF NOT EXISTS rejection_reason TEXT NULL,
  ADD COLUMN IF NOT EXISTS decision_by_admin_id INT NULL,
  ADD COLUMN IF NOT EXISTS decision_timestamp DATETIME NULL,
  ADD COLUMN IF NOT EXISTS classroom_count INT NOT NULL DEFAULT 5,
  ADD COLUMN IF NOT EXISTS lab_details TEXT NULL,
  ADD COLUMN IF NOT EXISTS equipment_details TEXT NULL;

-- 2. Accounts: Support Centre Admin Foreign Key and Role Constraints
ALTER TABLE accounts
  ADD COLUMN IF NOT EXISTS centre_id INT NULL;

-- Create index for quick lookup of centre-assigned accounts
CREATE INDEX IF NOT EXISTS idx_accounts_centre_id ON accounts(centre_id);

-- Ensure all existing 18 centres are marked as APPROVED
UPDATE training_centres SET approval_status = 'APPROVED' WHERE approval_status IS NULL OR approval_status = '';

-- 3. Enrollments: Verify Centre ID Scoping
ALTER TABLE enrollments
  ADD COLUMN IF NOT EXISTS centre_id INT NULL;

-- Backfill centre_id from training_programs where null
UPDATE enrollments e
JOIN training_programs p ON e.program_id = p.id
SET e.centre_id = p.centre_id
WHERE e.centre_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_enrollments_centre_id ON enrollments(centre_id);
