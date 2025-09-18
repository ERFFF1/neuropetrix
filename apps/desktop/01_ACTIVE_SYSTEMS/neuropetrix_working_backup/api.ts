const BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const gen = (p: any) =>
  fetch(`${BASE}/report/generate`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(p)
  }).then(r => r.json());

export const compare = (curr: number, prev: number) =>
  fetch(`${BASE}/report/compare?current_id=${curr}&previous_id=${prev}`, {
    method: "POST"
  }).then(r => r.json());

export const transcribe = (file: File) => {
  const fd = new FormData();
  fd.append('file', file);
  return fetch(`${BASE}/asr/transcribe`, {
    method: 'POST',
    body: fd
  }).then(r => r.json());
};

export const getTemplate = (modality: string) =>
  fetch(`${BASE}/templates/${modality}`).then(r => r.json());

export const getSentences = (category?: string) =>
  fetch(`${BASE}/sentences${category ? `?category=${category}` : ''}`).then(r => r.json());

