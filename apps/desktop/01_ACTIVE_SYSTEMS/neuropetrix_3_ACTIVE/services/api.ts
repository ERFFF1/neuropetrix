const BASE = "http://127.0.0.1:8000";

// Health & System
export async function health() {
  const r = await fetch(`${BASE}/health`);
  if (!r.ok) throw new Error("Health check failed");
  return r.json();
}

export async function version() {
  const r = await fetch(`${BASE}/version`);
  if (!r.ok) throw new Error("Version check failed");
  return r.json();
}

// DICOM & Imaging
export async function listDicomSeries() {
  const r = await fetch(`${BASE}/dicom/series`);
  if (!r.ok) throw new Error("DICOM series fetch failed");
  return r.json();
}

// Reports
export async function generateReport(payload: any) {
  const r = await fetch(`${BASE}/reports/generate`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error("Report generation failed");
  return r.json();
}

// Whisper ASR
export async function transcribe(formData: FormData) {
  const r = await fetch(`${BASE}/whisper/transcribe`, { 
    method: "POST", 
    body: formData 
  });
  if (!r.ok) throw new Error("Transcription failed");
  return r.json();
}

// Error handling wrapper
export async function apiCall<T>(
  endpoint: string, 
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(`${BASE}${endpoint}`, options);
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
}















