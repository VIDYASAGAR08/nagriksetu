import {
  User,
  CitizenProfile,
  Household,
  AdminDashboardMetrics,
  AuditLog,
  AdministrativeUnit,
  AdministrativeUnitListResponse,
  HouseholdMembership,
  OutboxEventListResponse,
  OTPGenerateResponse,
  OTPVerifyResponse,
  MedicalRecord,
  EducationRecord,
  LandRecord,
  HouseholdDossier,
  HouseholdLinkRequest,
} from '../types';

export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// In-memory token storage with sessionStorage fallback (lifecycle bounded to browser session)
let authToken: string | null = sessionStorage.getItem('civic_auth_token');

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    sessionStorage.setItem('civic_auth_token', token);
  } else {
    sessionStorage.removeItem('civic_auth_token');
  }
};

export const getAuthToken = () => authToken;

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set('Content-Type', 'application/json');

  if (authToken) {
    headers.set('Authorization', `Bearer ${authToken}`);
  }

  const config: RequestInit = {
    ...options,
    headers,
    credentials: 'include', // Support HttpOnly cookie sessions
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (response.status === 204) {
    return {} as T;
  }

  let data;
  try {
    data = await response.json();
  } catch (err) {
    data = null;
  }

  if (!response.ok) {
    const errorMsg = data?.detail || `HTTP Error ${response.status}: ${response.statusText}`;
    throw new Error(errorMsg);
  }

  return data as T;
}

export const api = {
  // Authentication
  auth: {
    register: (payload: any) =>
      request<{ access_token: string; user: User }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    login: (payload: any) =>
      request<{ access_token: string; user: User }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    logout: () =>
      request<{ message: string }>('/auth/logout', {
        method: 'POST',
      }),
    me: () =>
      request<{ user: User; citizen_profile?: CitizenProfile }>('/auth/me'),
    generateOTP: (payload?: { purpose?: string; recipient?: string }) =>
      request<OTPGenerateResponse>('/auth/otp/generate', {
        method: 'POST',
        body: JSON.stringify(payload || { purpose: 'CITIZEN_PROFILE_UPDATE' }),
      }),
    verifyOTP: (payload: { reference_id: string; otp_code: string; purpose?: string }) =>
      request<OTPVerifyResponse>('/auth/otp/verify', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    requestLoginOTP: (identifier: string) =>
      request<OTPGenerateResponse>('/auth/login-otp/request', {
        method: 'POST',
        body: JSON.stringify({ identifier }),
      }),
    verifyLoginOTP: (payload: { identifier: string; reference_id: string; otp_code: string }) =>
      request<{ access_token: string; user: User; match_score?: number; message?: string }>('/auth/login-otp/verify', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    getBiometricChallenge: () =>
      request<{ challenge: string; rp_name: string; rp_id: string }>('/auth/biometrics/challenge'),
    registerBiometrics: (payload: { credential_id: string; public_key?: string; biometric_type?: string }) =>
      request<{ success: boolean; message: string; biometric_enabled: boolean }>('/auth/biometrics/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    biometricLogin: (payload: {
      email?: string;
      phone?: string;
      phone_number?: string;
      credential_id?: string;
      face_data?: string;
      biometric_type?: string;
      client_data_hash?: string;
      require_otp?: boolean;
    }) =>
      request<{
        access_token: string;
        user?: User;
        match_score?: number;
        message?: string;
        requires_otp?: boolean;
        reference_id?: string;
        recipient?: string;
        demo_hint?: string;
        identifier?: string;
      }>('/auth/biometrics/login', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  },

  // Citizen Self-Service & Confidential Records
  citizen: {
    getMyProfile: () => request<CitizenProfile>('/citizens/me'),
    updateMyProfile: (data: Partial<CitizenProfile> & { otp_reference_id?: string }) =>
      request<CitizenProfile>('/citizens/me', {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    updateFamilyMemberProfile: (
      citizenId: number,
      data: { phone_number?: string; preferred_language?: string; otp_reference_id?: string }
    ) =>
      request<CitizenProfile>(`/citizens/${citizenId}/family-update`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    getMedicalRecord: (citizenId: number) =>
      request<MedicalRecord>(`/citizens/${citizenId}/medical`),
    updateMedicalRecord: (
      citizenId: number,
      data: Partial<MedicalRecord> & { otp_reference_id?: string }
    ) =>
      request<MedicalRecord>(`/citizens/${citizenId}/medical`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    getEducationRecord: (citizenId: number) =>
      request<EducationRecord>(`/citizens/${citizenId}/education`),
    updateEducationRecord: (
      citizenId: number,
      data: Partial<EducationRecord> & { otp_reference_id?: string }
    ) =>
      request<EducationRecord>(`/citizens/${citizenId}/education`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    getMyHousehold: async () => {
      try {
        return await request<Household>('/households/me');
      } catch (err: any) {
        if (err.message && (err.message.includes('404') || err.message.includes('not currently linked'))) {
          return null;
        }
        throw err;
      }
    },
  },

  // Household Dwelling & Asset Dossier
  household: {
    getMyDossier: () => request<HouseholdDossier>('/households/me/dossier'),
    addLandRecord: (data: Partial<LandRecord>) =>
      request<LandRecord>('/households/me/land', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    submitMemberLinkRequest: (payload: {
      target_citizen_code: string;
      relationship: string;
      household_role?: string;
      assigned_tasks?: string[];
    }) =>
      request<HouseholdLinkRequest>('/households/me/link-requests', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    getMyHouseholdLinkRequests: () =>
      request<HouseholdLinkRequest[]>('/households/me/link-requests'),
  },

  // Citizen Chat Assistant
  chat: {
    sendMessage: (message: string) =>
      request<{
        reply: string;
        sender: string;
        timestamp: string;
        suggested_prompts: string[];
        context_data?: Record<string, any>;
      }>('/chat/message', {
        method: 'POST',
        body: JSON.stringify({ message }),
      }),
  },

  // Administrative Hierarchy (FR-ADM-001 to FR-ADM-005)
  hierarchy: {
    list: (params?: {
      search?: string;
      unit_type?: string;
      parent_id?: number;
      status?: string;
      page?: number;
      page_size?: number;
    }) => {
      const q = new URLSearchParams();
      if (params?.search) q.append('search', params.search);
      if (params?.unit_type) q.append('unit_type', params.unit_type);
      if (params?.parent_id !== undefined && params?.parent_id !== null) q.append('parent_id', String(params.parent_id));
      if (params?.status) q.append('status', params.status);
      if (params?.page) q.append('page', String(params.page));
      if (params?.page_size) q.append('page_size', String(params.page_size));
      const queryString = q.toString();
      return request<AdministrativeUnitListResponse>(`/hierarchy${queryString ? `?${queryString}` : ''}`);
    },
    get: (id: number) => request<AdministrativeUnit>(`/hierarchy/${id}`),
    create: (payload: {
      identifier: string;
      name: string;
      unit_type: string;
      parent_id?: number | null;
      status?: string;
    }) =>
      request<AdministrativeUnit>('/hierarchy', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    update: (
      id: number,
      payload: {
        name?: string;
        parent_id?: number | null;
        status?: string;
      }
    ) =>
      request<AdministrativeUnit>(`/hierarchy/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
  },

  // Administrator Portal Operations (FR-ADM-006 to FR-ADM-024)
  admin: {
    getDashboard: () => request<AdminDashboardMetrics>('/admin/dashboard'),
    getAuditLogs: (skip = 0, limit = 50) =>
      request<AuditLog[]>(`/admin/audit-logs?skip=${skip}&limit=${limit}`),
    listAdmins: () => request<User[]>('/admin/admins'),
    assignScope: (userId: number, administrativeUnitId?: number | null) =>
      request<{ message: string; user_id: number; administrative_unit_id: number | null; administrative_unit_name?: string }>(
        '/admin/scope/assign',
        {
          method: 'POST',
          body: JSON.stringify({ user_id: userId, administrative_unit_id: administrativeUnitId }),
        }
      ),

    // Citizen management
    listCitizens: (search?: string, status?: string) => {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (status) params.append('status', status);
      return request<CitizenProfile[]>(`/citizens?${params.toString()}`);
    },
    getCitizen: (id: number) => request<CitizenProfile>(`/citizens/${id}`),
    createCitizen: (payload: any) =>
      request<CitizenProfile>('/citizens', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    updateCitizen: (id: number, payload: any) =>
      request<CitizenProfile>(`/citizens/${id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      }),
    updateCitizenStatus: (id: number, status: string) =>
      request<CitizenProfile>(`/citizens/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ profile_status: status }),
      }),
    deleteCitizen: (id: number) =>
      request<{ message: string }>(`/citizens/${id}`, {
        method: 'DELETE',
      }),

    // Household management
    listHouseholds: (search?: string) => {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      return request<Household[]>(`/households?${params.toString()}`);
    },
    getHousehold: (id: number) => request<Household>(`/households/${id}`),
    createHousehold: (payload: any) =>
      request<Household>('/households', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    updateHousehold: (id: number, payload: any) =>
      request<Household>(`/households/${id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      }),
    deleteHousehold: (id: number) =>
      request<{ message: string }>(`/households/${id}`, {
        method: 'DELETE',
      }),
    assignMember: (householdId: number, citizenId: number, relationship: string) =>
      request<Household>(`/households/${householdId}/assign`, {
        method: 'POST',
        body: JSON.stringify({ citizen_id: citizenId, household_relationship: relationship }),
      }),
    unassignMember: (householdId: number, citizenId: number) =>
      request<Household>(`/households/${householdId}/unassign/${citizenId}`, {
        method: 'POST',
      }),
    getHouseholdMemberships: (householdId: number) =>
      request<HouseholdMembership[]>(`/households/${householdId}/memberships`),
    endMembership: (householdId: number, citizenId: number, notes?: string) =>
      request<Household>(`/households/${householdId}/end-membership/${citizenId}`, {
        method: 'POST',
        body: JSON.stringify({ notes }),
      }),
    listHouseholdLinkRequests: (statusFilter?: string) => {
      const q = statusFilter ? `?status_filter=${statusFilter}` : '';
      return request<HouseholdLinkRequest[]>(`/households/link-requests${q}`);
    },
    reviewHouseholdLinkRequest: (requestId: number, action: 'approve' | 'reject', adminNotes?: string) =>
      request<HouseholdLinkRequest>(`/households/link-requests/${requestId}/action`, {
        method: 'POST',
        body: JSON.stringify({ action, admin_notes: adminNotes }),
      }),
  },

  // Service Integration & Domain Events (FR-ADM-025)
  events: {
    list: (params?: { event_type?: string; aggregate_type?: string; page?: number; page_size?: number }) => {
      const q = new URLSearchParams();
      if (params?.event_type) q.append('event_type', params.event_type);
      if (params?.aggregate_type) q.append('aggregate_type', params.aggregate_type);
      if (params?.page) q.append('page', String(params.page));
      if (params?.page_size) q.append('page_size', String(params.page_size));
      const queryString = q.toString();
      return request<OutboxEventListResponse>(`/events${queryString ? `?${queryString}` : ''}`);
    },
  },

  // WhatsApp Municipal Bot Services
  whatsapp: {
    getInfo: () =>
      request<{
        bot_name: string;
        phone_number: string;
        clean_number: string;
        prefill_text: string;
        wa_me_url: string;
        qr_code_svg: string;
        capabilities: string[];
      }>('/whatsapp/info'),
    simulate: (phoneNumber: string, message: string) =>
      request<{
        reply: string;
        state: string;
        is_registered: boolean;
        citizen_code?: string;
        options: string[];
      }>('/whatsapp/simulate', {
        method: 'POST',
        body: JSON.stringify({ phone_number: phoneNumber, message }),
      }),
  },
};
