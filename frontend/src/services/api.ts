import {
  User,
  CitizenProfile,
  Household,
  AdminDashboardMetrics,
  AuditLog,
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
  },

  // Citizen Self-Service
  citizen: {
    getMyProfile: () => request<CitizenProfile>('/citizens/me'),
    updateMyProfile: (data: Partial<CitizenProfile>) =>
      request<CitizenProfile>('/citizens/me', {
        method: 'PATCH',
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

  // Administrator Portal Operations
  admin: {
    getDashboard: () => request<AdminDashboardMetrics>('/admin/dashboard'),
    getAuditLogs: (skip = 0, limit = 50) =>
      request<AuditLog[]>(`/admin/audit-logs?skip=${skip}&limit=${limit}`),

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
