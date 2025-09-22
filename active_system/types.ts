import { clinicalRules } from "./clinical-rules";

export type QualityControl = 'PASSED' | 'BORDERLINE' | 'FAILED';
export type EvidenceLevel = '1A' | '1B' | '2A' | '2B' | '3' | 'Expert' | 'Good Practice' | string;
export type ClinicalGoal = keyof typeof clinicalRules.goals;

// PICO Otomatikleştirme Algoritması için yeni tipler
export interface PICOQuestion {
  population: string;      // Hasta popülasyonu
  intervention: string;    // Müdahale/tedavi
  comparison: string;      // Karşılaştırma
  outcome: string;         // Sonuç
  clinicalContext: string; // Klinik bağlam
}

export interface EvidenceSearch {
  picoQuestion: PICOQuestion;
  searchStrategy: string;
  databases: string[];     // PubMed, Cochrane, vb.
  inclusionCriteria: string[];
  exclusionCriteria: string[];
  dateRange: {
    start: string;
    end: string;
  };
}

export interface CriticalAppraisal {
  studyDesign: string;
  sampleSize: number;
  biasRisk: 'low' | 'some' | 'high';
  methodologyQuality: number; // 1-10
  statisticalPower: number;   // 1-10
  limitations: string[];
  strengths: string[];
}

export interface ApplicabilityAnalysis {
  patientComorbidities: string[];
  drugInteractions: string[];
  toxicityRisks: string[];
  contraindications: string[];
  applicabilityScore: number; // 1-10
  recommendation: 'strong' | 'moderate' | 'weak' | 'against';
  reasoning: string;
}

// Multimodal Füzyon Mimarisi için yeni tipler
export interface MultimodalData {
  imaging: {
    dicomFiles: string[];
    radiomicsFeatures: RadiomicsFeatures;
    segmentationMasks: string[];
    suvMeasurements: SUVMeasurement[];
  };
  clinical: {
    demographics: PatientDemographics;
    laboratory: LaboratoryData;
    biomarkers: BiomarkerData;
    medications: MedicationData;
  };
  textual: {
    clinicalNotes: string;
    radiologyReports: string[];
    pathologyReports: string[];
    transcribedAudio: string;
  };
}

export interface RadiomicsFeatures {
  firstOrder: {
    suvMax: number;
    suvMean: number;
    volume: number;
    density: number;
  };
  shape: {
    compactness: number;
    sphericity: number;
    surfaceArea: number;
  };
  texture: {
    glcm: Record<string, number>;
    glrlm: Record<string, number>;
    glszm: Record<string, number>;
  };
}

export interface SUVMeasurement {
  location: string;
  suvMax: number;
  suvMean: number;
  volume: number;
  date: string;
}

export interface PatientDemographics {
  age: number;
  gender: 'Male' | 'Female' | 'Other';
  weight: number;
  height: number;
  bmi: number;
  smokingHistory: boolean;
  alcoholHistory: boolean;
  familyHistory: string[];
}

export interface LaboratoryData {
  glucose: number;
  creatinine: number;
  egfr: number;
  liverFunction: {
    alt: number;
    ast: number;
    bilirubin: number;
  };
  completeBloodCount: {
    wbc: number;
    rbc: number;
    hemoglobin: number;
    platelets: number;
  };
}

export interface BiomarkerData {
  psa?: number;
  cea?: number;
  ca125?: number;
  ca199?: number;
  afp?: number;
  hcg?: number;
  ldh?: number;
}

export interface MedicationData {
  currentMedications: {
    name: string;
    dose: string;
    frequency: string;
    startDate: string;
  }[];
  allergies: string[];
  drugInteractions: string[];
}

// Klinik Karar Döngüsü için yeni tipler
export interface ClinicalFeedback {
  caseId: string;
  physicianId: string;
  feedbackType: 'hard_negative' | 'supportive_positive' | 'neutral';
  feedbackDetails: string;
  timestamp: string;
  confidenceLevel: number; // 1-10
  alternativeRecommendation?: string;
}

export interface LearningLoop {
  feedback: ClinicalFeedback;
  modelUpdate: {
    version: string;
    changes: string[];
    performanceMetrics: {
      accuracy: number;
      sensitivity: number;
      specificity: number;
    };
  };
  validationStatus: 'pending' | 'approved' | 'rejected';
  approvedBy?: string;
  approvalDate?: string;
}

// Yasal Uyum ve Regülasyonlar için yeni tipler
export interface ComplianceData {
  dataPrivacy: {
    anonymizationLevel: 'full' | 'partial' | 'none';
    maskingApplied: boolean;
    encryptionLevel: 'standard' | 'high' | 'military';
    retentionPolicy: string;
  };
  regulatoryCompliance: {
    kvkk: boolean;
    hipaa: boolean;
    gdpr: boolean;
    ceMdr: boolean;
    fda510k: boolean;
  };
  auditTrail: {
    dataAccess: DataAccessLog[];
    modifications: ModificationLog[];
    exports: ExportLog[];
  };
}

export interface DataAccessLog {
  userId: string;
  timestamp: string;
  action: string;
  dataType: string;
  justification: string;
}

export interface ModificationLog {
  userId: string;
  timestamp: string;
  field: string;
  oldValue: string;
  newValue: string;
  reason: string;
}

export interface ExportLog {
  userId: string;
  timestamp: string;
  dataType: string;
  format: string;
  destination: string;
  purpose: string;
}

export interface PreviousMeasurement {
  dateISO: string;
  suvMax?: number;
}

// KBB’ye özgü alanlar
export type ENTComplaint = {
  durationDays?: number;              // şikâyet süresi
  rhinorrhea?: "none"|"serous"|"mucous"|"purulent";
  facialPainPressure?: boolean;
  fever?: "none"|"low"|"high";
  smellLoss?: boolean;
  dentalPain?: boolean;
  doubleWorsening?: boolean;          // iyileşme sonrası yeniden kötüleşme
  redFlags?: {                        // acil/komplike riskleri
    orbitalSwelling?: boolean;
    visionChange?: boolean;
    severeHeadache?: boolean;
    neuroDeficit?: boolean;
  };
  priorAntibiotic?: { used:boolean; name?:string; days?:number };
  allergyPenicillin?: boolean;
  immunocompromised?: boolean;
  pregnancy?: boolean;
};

export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: 'Erkek' | 'Kadın' | 'Other';
  diagnosis: string;
  lastVisit: string;
  status: 'active' | 'followup' | 'completed';
  icd_codes?: string[];
  medications?: string[];
  comorbidities?: string[];
  clinical_goals?: string[];
}

export interface PatientCase {
  id: string;
  name?: string;
  age?: number;
  gender?: string;
  diagnosis?: string;
  comorbidities?: string[];
  medications?: string[];
  icdCodes?: string[];
  clinicalGoals?: string[];
  patient?: Patient;
  status?: string;
  created_at?: string;
  updated_at?: string;
  clinical_notes?: string;
  suv_measurements?: SUVMeasurement[];
  currentRecommendation?: any;
}

export interface RecommendationCard {
  title: string;
  rationale: string;
  evidenceLevel: EvidenceLevel;
}

export interface StructuredReport {
  indication: string;
  findings: string;
  conclusion: string;
}

export interface DiagnosticStep {
    name: string;
    rationale: string;
    accuracy?: {
        sensitivity?: number;
        specificity?: number;
        auc?: number;
    };
}

export interface TreatmentOption {
    label: string;
    line: "first" | "second" | "adjunct";
    regimen: string;
    durationDays?: number;
    benefitSummary: string;
    riskSummary: string;
}

export interface ApplicabilityCheck {
    name: string;
    status: "present" | "absent" | "unknown";
    impact: "contra" | "relative" | "none";
}

export interface Evidence {
    title: string;
    year: number;
    source: string;
    evidence_level: string;
    bias_risk: "low" | "some" | "high";
    key_findings: string;
}

// A generic result type that can hold different goal-specific data
export interface AnalysisResult {
  // TX_RESPONSE specific
  trend?: {
    deltaSUVpct?: number;
    label?: 'Progresyon adayı' | 'Anlamlı yanıt adayı' | 'Stabil/Belirsiz';
  };
  
  // DIAGNOSIS specific
  diagnosticSteps?: DiagnosticStep[];

  // TREATMENT specific
  treatmentOptions?: TreatmentOption[];
  applicability?: {
    checks: ApplicabilityCheck[];
    score: number;
  };
  
  // Common fields
  structuredReport: StructuredReport;
  recommendationCards: RecommendationCard[];
  evidence?: Evidence[];

  // Metadata
  rulesVersion?: string;
  guidelineVersion?: string;
  qcFlag?: 'LOW_CONFIDENCE' | 'NORMAL';
}


// Keep progress types for UI feedback during generation
export type AnalysisStep = 'gathering' | 'done' | 'error';
export interface AnalysisProgress {
    step: AnalysisStep;
    message: string;
}