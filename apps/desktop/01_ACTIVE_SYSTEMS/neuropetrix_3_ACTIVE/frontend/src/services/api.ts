import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  Case, 
  PatientData, 
  AnalysisResult, 
  ChatMessage, 
  ApiResponse,
  CaseFilter,
  SearchParams 
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );

    // Load token from localStorage
    this.loadToken();
  }

  private loadToken() {
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  logout() {
    this.token = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<{ user: User; token: string }> {
    const response = await this.api.post('/security/login', {
      username,
      password
    });
    
    const { access_token, user_info } = response.data;
    this.setToken(access_token);
    
    return {
      user: user_info,
      token: access_token
    };
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get('/security/profile');
    return response.data;
  }

  // Case endpoints
  async getCases(params?: SearchParams): Promise<{ cases: Case[]; total: number }> {
    const response = await this.api.get('/cases', { params });
    return response.data;
  }

  async getCase(id: string): Promise<Case> {
    const response = await this.api.get(`/cases/${id}`);
    return response.data;
  }

  async createCase(patientData: PatientData): Promise<Case> {
    const response = await this.api.post('/cases', {
      patient_id: `P-${Date.now()}`,
      purpose: 'clinical_analysis',
      icd_code: 'Z00.0',
      case_meta: patientData
    });
    return response.data;
  }

  async updateCase(id: string, updates: Partial<Case>): Promise<Case> {
    const response = await this.api.patch(`/cases/${id}`, updates);
    return response.data;
  }

  async deleteCase(id: string): Promise<void> {
    await this.api.delete(`/cases/${id}`);
  }

  // Analysis endpoints
  async startAnalysis(caseId: string, analysisType: string = 'comprehensive'): Promise<{ analysisId: string }> {
    const response = await this.api.post('/advanced-ai/analyze', {
      case_id: caseId,
      patient_id: `P-${Date.now()}`,
      analysis_type: analysisType,
      priority: 'normal'
    });
    return response.data;
  }

  async getAnalysisStatus(analysisId: string): Promise<AnalysisResult> {
    const response = await this.api.get(`/advanced-ai/analysis/${analysisId}`);
    return response.data;
  }

  // Chat endpoints
  async sendMessage(caseId: string, message: string): Promise<ChatMessage> {
    const response = await this.api.post(`/cases/${caseId}/chat`, {
      message,
      role: 'user'
    });
    return response.data;
  }

  async getChatHistory(caseId: string): Promise<ChatMessage[]> {
    const response = await this.api.get(`/cases/${caseId}/chat`);
    return response.data;
  }

  // DICOM endpoints
  async uploadDicom(caseId: string, file: File): Promise<{ fileId: string; url: string }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await this.api.post(`/cases/${caseId}/dicom`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getDicomMetadata(fileId: string): Promise<any> {
    const response = await this.api.get(`/dicom/metadata/${fileId}`);
    return response.data;
  }

  // Report endpoints
  async generateReport(caseId: string): Promise<{ reportId: string; url: string }> {
    const response = await this.api.post(`/cases/${caseId}/report`);
    return response.data;
  }

  async downloadReport(reportId: string): Promise<Blob> {
    const response = await this.api.get(`/reports/${reportId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  }

  // Analytics endpoints
  async getDashboardData(): Promise<any> {
    const response = await this.api.get('/analytics/dashboard');
    return response.data;
  }

  async getMetrics(): Promise<any> {
    const response = await this.api.get('/metrics');
    return response.data;
  }

  // Notification endpoints
  async getNotifications(): Promise<any[]> {
    const response = await this.api.get('/notifications');
    return response.data;
  }

  async markNotificationAsRead(notificationId: string): Promise<void> {
    await this.api.patch(`/notifications/${notificationId}/read`);
  }

  // WebSocket connection
  connectWebSocket(): WebSocket {
    const wsUrl = `ws://localhost:8000/ws/connect/${this.token}`;
    return new WebSocket(wsUrl);
  }
}

export const apiService = new ApiService();
export default apiService;
