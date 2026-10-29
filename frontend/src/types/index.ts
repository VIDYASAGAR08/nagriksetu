export interface User {
  id: number;
  email: string;
  role: 'citizen' | 'admin';
  account_status: 'active' | 'suspended' | 'pending';
  created_at: string;
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
  created_at: string;
  updated_at: string;
}

export interface HouseholdMember {
  id: number;
  citizen_code: string;
  full_name: string;
  household_relationship?: string | null;
}

export interface Household {
  id: number;
  household_code: string;
  address_line: string;
  locality: string;
  city: string;
  state: string;
  postal_code: string;
  administrative_notes?: string | null;
  members: HouseholdMember[];
  created_at: string;
  updated_at: string;
}

export interface AdminDashboardMetrics {
  total_citizens: number;
  active_citizens: number;
  pending_citizens: number;
  total_households: number;
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

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  suggested_prompts?: string[];
  context_data?: Record<string, any>;
}
