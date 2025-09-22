import axios from 'axios';

// API Base URL
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface Case {
  id: number;
  patient_id?: string;
  title: string;
  icd_code?: string;
  case_meta?: any;
  system_status: 'DRAFT' | 'AI_RUNNING' | 'AI_DONE' | 'AI_ERROR';
  clinical_status: 'NEW' | 'NEEDS_REVIEW' | 'IN_REVIEW' | 'AWAITING_SIGNATURE' | 'FINALIZED' | 'REOPENED' | 'ARCHIVED';
  created_at: string;
}

export interface CaseCreate {
  patient_id?: string;
  title: string;
  icd_code?: string;
  case_meta?: any;
}

export interface AnalysisResult {
  job_id: string;
  status: string;
  outputs_ref?: any;
}

export interface PDFResult {
  pdf_url: string;
}

export interface ShareResult {
  share_url: string;
}

// API Functions
export const apiService = {
  // Authentication
  async login(username: string, password: string) {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },

  // Cases
  async getCases(): Promise<Case[]> {
    const response = await api.get('/cases');
    return response.data;
  },

  async createCase(caseData: CaseCreate): Promise<Case> {
    const response = await api.post('/cases', caseData);
    return response.data;
  },

  async updateCase(caseId: number, updates: Partial<Case>): Promise<Case> {
    const response = await api.patch(`/cases/${caseId}`, updates);
    return response.data;
  },

  // Studies
  async createStudyUpload(caseId: number) {
    const response = await api.post(`/cases/${caseId}/studies`);
    return response.data;
  },

  // Analysis
  async enqueueAnalysis(caseId: number): Promise<AnalysisResult> {
    const response = await api.post(`/cases/${caseId}/analyses`);
    return response.data;
  },

  async getAnalysis(caseId: number): Promise<AnalysisResult> {
    const response = await api.get(`/cases/${caseId}/analyses`);
    return response.data;
  },

  // Conversation
  async addConversation(caseId: number, message: string) {
    const response = await api.post(`/cases/${caseId}/conversation`, { message });
    return response.data;
  },

  // PDF Report
  async generatePDF(caseId: number): Promise<PDFResult> {
    const response = await api.post(`/cases/${caseId}/report/pdf`);
    return response.data;
  },

  // Share
  async createShare(caseId: number, expiresAt: string, maxViews: number = 3): Promise<ShareResult> {
    const response = await api.post('/shares', { case_id: caseId, expires_at: expiresAt, max_views: maxViews });
    return response.data;
  },

  // Health check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }
};

export default api;