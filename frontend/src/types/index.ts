export interface User {
  id: number;
  email: string;
  phone_number?: string | null;
  role: 'citizen' | 'admin';
  account_status: 'active' | 'suspended' | 'pending';
  administrative_unit_id?: number | null;
  administrative_unit_name?: string | null;
  biometric_enabled?: boolean;
  has_face_enrolled?: boolean;
  created_at: string;
}

export interface MedicalRecord {
  id?: number;
  citizen_id?: number;
  blood_group?: string;
  chronic_conditions?: string;
  allergies?: string;
  vaccination_status?: string;
  disability_status?: string;
  abha_id?: string | null;
  emergency_hospital?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
}

export interface EducationRecord {
  id?: number;
  citizen_id?: number;
  highest_qualification?: string;
  institution_name?: string | null;
  specialization?: string | null;
  year_of_completion?: number | null;
  literacy_status?: string;
  certificate_number?: string | null;
}

export interface LandRecord {
  id: number;
  household_id: number;
  survey_number: string;
  land_type: string;
  area_measurement: string;
  patta_passbook_number?: string | null;
  district_sub_registrar?: string | null;
  property_tax_status?: string | null;
  market_valuation_inr?: number | null;
  created_at?: string;
}

export interface FamilyMemberDossier {
  id: number;
  citizen_code: string;
  full_name: string;
  phone_number?: string | null;
  date_of_birth?: string | null;
  preferred_language: string;
  profile_status: string;
  household_relationship: string;
  household_role?: string;
  assigned_tasks?: string[];
  is_self: boolean;
  medical_record: MedicalRecord;
  education_record: EducationRecord;
}

export interface HouseholdDossier {
  household_id: number;
  household_code: string;
  address_line: string;
  locality: string;
  city: string;
  state: string;
  postal_code: string;
  members_count: number;
  land_records: LandRecord[];
  family_members: FamilyMemberDossier[];
}

export interface OTPGenerateResponse {
  reference_id: string;
  recipient: string;
  purpose: string;
  expires_in_seconds: number;
  demo_hint?: string;
  message: string;
}

export interface OTPVerifyResponse {
  success: boolean;
  reference_id: string;
  verified: boolean;
  message: string;
}

export interface AdministrativeUnit {
  id: number;
  identifier: string;
  name: string;
  unit_type: 'country' | 'state' | 'district' | 'sub_district' | 'ward' | 'village' | string;
  parent_id?: number | null;
  parent_name?: string | null;
  parent_identifier?: string | null;
  status: 'active' | 'inactive';
  created_at: string;
  updated_at: string;
  children_count: number;
  citizens_count: number;
  households_count: number;
}

export interface AdministrativeUnitListResponse {
  total: number;
  page: number;
  page_size: number;
  items: AdministrativeUnit[];
}

export interface CitizenProfile {
  id: number;
  citizen_code: string;
  full_name: string;
  date_of_birth?: string | null;
  phone_number?: string | null;
  preferred_language: string;
  profile_status: 'pending_review' | 'active' | 'archived';
  face_photo?: string | null;
  household_id?: number | null;
  household_relationship?: string | null;
  administrative_unit_id?: number | null;
  administrative_unit_name?: string | null;
  completeness_score?: number;
  missing_fields?: string[];
  created_at: string;
  updated_at: string;
}

export interface HouseholdMember {
  id: number;
  citizen_code: string;
  full_name: string;
  household_relationship?: string | null;
  household_role?: string;
  assigned_tasks?: string[];
}

export interface HouseholdLinkRequest {
  id: number;
  household_id: number;
  household_code: string;
  requester_citizen_id: number;
  requester_name: string;
  target_citizen_id: number;
  target_citizen_code: string;
  target_citizen_name: string;
  relationship: string;
  household_role: string;
  assigned_tasks: string[];
  status: 'pending_admin_approval' | 'approved' | 'rejected';
  admin_notes?: string | null;
  created_at: string;
  reviewed_at?: string | null;
}

export interface HouseholdMembership {
  id: number;
  household_id: number;
  citizen_id: number;
  citizen_code: string;
  citizen_name: string;
  relationship_type: string;
  start_date: string;
  end_date?: string | null;
  status: string;
  notes?: string | null;
  created_at: string;
}

export interface Household {
  id: number;
  household_code: string;
  address_line: string;
  locality: string;
  city: string;
  state: string;
  postal_code: string;
  administrative_unit_id?: number | null;
  administrative_unit_name?: string | null;
  administrative_notes?: string | null;
  members: HouseholdMember[];
  consistency_flags?: string[];
  duplicate_warning?: boolean;
  matching_households?: string[];
  created_at: string;
  updated_at: string;
}

export interface AdminDashboardMetrics {
  total_citizens: number;
  active_citizens: number;
  pending_citizens: number;
  total_households: number;
  total_administrative_units: number;
  active_units: number;
  admin_scope: string;
  admin_scope_unit_id?: number | null;
  recent_registrations: CitizenProfile[];
}

export interface AuditLog {
  id: number;
  actor_id?: number | null;
  actor_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details?: string | null;
  created_at: string;
}

export interface OutboxEvent {
  id: number;
  event_id: string;
  event_type: string;
  aggregate_type: string;
  aggregate_id: string;
  payload: Record<string, any>;
  created_at?: string;
}

export interface OutboxEventListResponse {
  total: number;
  page: number;
  page_size: number;
  items: OutboxEvent[];
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  suggested_prompts?: string[];
  context_data?: Record<string, any>;
}
