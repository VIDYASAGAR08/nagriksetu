export interface User {
  id: number;
  email: string;
  role: 'citizen' | 'admin';
  account_status: 'active' | 'suspended' | 'pending';
  administrative_unit_id?: number | null;
  administrative_unit_name?: string | null;
  created_at: string;
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
