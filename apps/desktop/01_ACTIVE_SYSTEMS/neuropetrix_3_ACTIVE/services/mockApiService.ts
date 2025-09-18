import { PatientCase, AnalysisResult, AnalysisProgress, ClinicalGoal } from '../types';

// The base URL for our new FastAPI backend
const API_BASE_URL = 'http://127.0.0.1:8000';

export const getPatientCases = async (): Promise<PatientCase[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/cases`);
    if (!response.ok) {
      throw new Error(`Failed to fetch cases: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching patient cases from backend:", error);
    // Return empty array or handle error as appropriate for the UI
    return []; 
  }
};

export const createPatientCase = async (newCaseData: Omit<PatientCase, 'id' | 'status'>): Promise<PatientCase> => {
    const response = await fetch(`${API_BASE_URL}/cases`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCaseData),
    });
    if (!response.ok) {
        throw new Error(`Failed to create case: ${response.statusText}`);
    }
    return await response.json();
};

export const getCaseDetails = async (id: string): Promise<PatientCase | undefined> => {
  try {
    const response = await fetch(`${API_BASE_URL}/cases/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch case details: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching details for case ${id}:`, error);
    return undefined;
  }
};

export const runAnalysis = async (caseData: PatientCase, goal: ClinicalGoal, onProgress: (progress: AnalysisProgress) => void): Promise<AnalysisResult | null> => {
    onProgress({ step: 'gathering', message: 'Connecting to NeuroPETrix AI Server...' });
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ case: caseData, goal: goal }),
        });

        if (!response.ok) {
            const errorBody = await response.text();
            throw new Error(`Backend analysis failed: ${response.statusText} - ${errorBody}`);
        }
        
        const result: AnalysisResult = await response.json();
        onProgress({ step: 'done', message: 'Analysis complete.' });
        
        return result;

    } catch (error) {
        console.error("Backend API call failed:", error);
        onProgress({
            step: 'error',
            message: 'Failed to retrieve analysis from server. Is the backend running?',
        });
        return null;
    }
};
