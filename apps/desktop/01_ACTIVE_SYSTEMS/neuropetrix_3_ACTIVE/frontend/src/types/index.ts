// User types
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'doctor' | 'admin' | 'radiologist' | 'nurse';
  department?: string;
  permissions?: string[];
}

// Patient data types
export interface Vitals {
  bloodPressure: string;
  heartRate: number;
  temperature: number;
  respiratoryRate: number;
  oxygenSaturation: number;
}

export interface PatientData {
  age: number;
  gender: 'male' | 'female' | 'other';
  chiefComplaint: string;
  medicalHistory: string;
  currentMedications: string;
  vitals: Vitals;
  additionalNotes?: string;
}

// AI Analysis types
export interface AnalysisResult {
  summary: string;
  differentialDiagnosis: string[];
  suggestions: string[];
  confidence: number;
  processingTime: number;
  modelVersion: string;
}

// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

// Case types
export interface Case {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  patientData: PatientData;
  analysis?: AnalysisResult;
  chatHistory: ChatMessage[];
  systemStatus: 'draft' | 'ai_running' | 'ai_done' | 'ai_error' | 'needs_review' | 'in_review' | 'awaiting_signature' | 'finalized' | 'reopened' | 'archived';
  clinicalStatus: 'new' | 'needs_review' | 'in_review' | 'awaiting_signature' | 'finalized' | 'reopened' | 'archived';
  error?: string;
  assignedTo?: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  tags?: string[];
  attachments?: Attachment[];
}

// Attachment types
export interface Attachment {
  id: string;
  name: string;
  type: 'dicom' | 'image' | 'document' | 'other';
  url: string;
  size: number;
  uploadedAt: Date;
  metadata?: Record<string, any>;
}

// DICOM types
export interface DicomMetadata {
  patientName?: string;
  patientId?: string;
  studyDate?: string;
  modality?: string;
  seriesDescription?: string;
  imageCount?: number;
  sliceThickness?: number;
  pixelSpacing?: [number, number];
}

// API Response types
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
  error?: string;
}

// WebSocket types
export interface WebSocketMessage {
  type: 'case_update' | 'analysis_progress' | 'notification' | 'system_status';
  data: any;
  timestamp: Date;
}

// Filter and search types
export interface CaseFilter {
  status?: string[];
  priority?: string[];
  assignedTo?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
  tags?: string[];
}

export interface SearchParams {
  query?: string;
  filters?: CaseFilter;
  sortBy?: 'createdAt' | 'updatedAt' | 'priority' | 'status';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}
