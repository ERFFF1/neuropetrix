import os, requests
API_BASE = os.getenv("NPX_API_BASE", "http://localhost:8080")
def start_analysis(case_id: str, tasks=None, options=None):
    payload = {"case_id": case_id, "tasks": tasks or ["radiomics"], "options": options or {}}
    r = requests.post(f"{API_BASE}/api/v1/analysis/run", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()
def get_status(job_id: str):
    r = requests.get(f"{API_BASE}/api/v1/analysis/status", params={"job_id": job_id}, timeout=30)
    r.raise_for_status()
    return r.json()
