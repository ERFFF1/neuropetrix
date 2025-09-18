const API = process.env.NEXT_PUBLIC_API_URL!;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    // istersen cache: "no-store" ekleyebilirsin
  });
  if (!r.ok) throw new Error(`API ${r.status} ${path}`);
  // bazı health endpoint'leri text dönebilir; ona göre ayır:
  const ct = r.headers.get("content-type") || "";
  return (ct.includes("application/json") ? r.json() : (r.text() as any)) as T;
}

export const api = { request };
export const health = () => request<{ status: string }>("/health");

// Örnek endpoint'ler
export const multimodal = (body: { report_text: string; suvmax: number; suv_thresh: number }) =>
  api.request('/inference/multimodal', { method: 'POST', body: JSON.stringify(body) });

export const feedback = (body: any) => 
  api.request('/feedback', { method: 'POST', body: JSON.stringify(body) });

// DICOM ve rapor endpoint'leri
export const listDicomSeries = () => 
  api.request('/dicom/series');

export const generateReport = (payload: any) => 
  api.request('/reports/generate', { method: 'POST', body: JSON.stringify(payload) });

export const transcribe = (formData: FormData) => 
  fetch(`${API}/whisper/transcribe`, { method: 'POST', body: formData });















