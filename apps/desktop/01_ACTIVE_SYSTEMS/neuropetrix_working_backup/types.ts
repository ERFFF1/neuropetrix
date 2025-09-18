import { clinicalRules } from "./clinical-rules";

export type QualityControl = 'PASSED' | 'BORDERLINE' | 'FAILED';
export type EvidenceLevel = '1A' | '1B' | '2A' | '2B' | '3' | 'Expert' | 'Good Practice' | string;
export type ClinicalGoal = keyof typeof clinicalRules.goals;

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

export interface PatientCase {
  id: string;
  patientInfo: {
    name: string;
    age: number;
    gender: 'Male' | 'Female' | 'Other';
    admissionDate: string;
  };
  diagnosis?: string;
  clinicalNotes?: string;
  
  // New fields for expert system
  previousMeasurements: PreviousMeasurement[];
  currentSUVmax?: number;
  qualityControl: QualityControl;
  clinicalTemplate: keyof typeof clinicalRules.templates;
  ent?: ENTComplaint; // KBB formu (opsiyonel)
  
  // TSNM Report fields
  tsnmReport?: {
    modality: 'FDG' | 'TSNM' | 'Other';
    deviceModel: string;
    fdgDoseMBq: number;
    glycemiaMgdl: number;
    fastingHours: number;
    structuredFindings: {
      primerLez?: string;
      lenfNodu?: string;
      uzakMet?: string;
      suvMax?: number;
    };
    selectedSentences: string[];
    reportBody?: string;
    reportId?: number;
    version?: number;
    previousReportId?: number;
  };
  
  // Status and results
  status: 'Pending Analysis' | 'Analysis Complete' | 'Awaiting Review';
  analysisResult?: AnalysisResult;
  manualCorrectionApplied?: boolean;
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