from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from prometheus_fastapi_instrumentator import Instrumentator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Neuropetrix API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# --------- MODELLER (örnek, gerçek DB'ye bağlayacağız) ----------
class CaseIn(BaseModel):
    patient_id: Optional[str] = None
    title: str
    icd_code: Optional[str] = None
    case_meta: Optional[dict] = None

class CaseOut(CaseIn):
    id: int
    system_status: str = "DRAFT"   # DRAFT → AI_RUNNING → AI_DONE|AI_ERROR
    clinical_status: str = "NEW"   # NEW → NEEDS_REVIEW → ... → FINALIZED
    created_at: str = "2025-09-05T17:00:00Z"

FAKE_DB: List[CaseOut] = []

# --------- UÇLAR (D1 listesi) ----------
@app.post("/auth/login")
def login(username: str, password: str):
    # TODO: JWT üret
    return {"access_token": "fake-token", "token_type": "bearer"}

@app.get("/cases", response_model=List[CaseOut])
def list_cases(): 
    return FAKE_DB

@app.post("/cases", response_model=CaseOut)
def create_case(ci: CaseIn):
    new = CaseOut(id=len(FAKE_DB)+1, **ci.dict())
    FAKE_DB.append(new)
    logger.info(f"Case created: {new.id}")
    return new

@app.patch("/cases/{case_id}", response_model=CaseOut)
def patch_case(case_id: int, system_status: Optional[str]=None, clinical_status: Optional[str]=None):
    for c in FAKE_DB:
        if c.id == case_id:
            if system_status: c.system_status = system_status
            if clinical_status: c.clinical_status = clinical_status
            logger.info(f"Case {case_id} updated: system={system_status}, clinical={clinical_status}")
            return c
    raise HTTPException(404, "case not found")

@app.post("/cases/{case_id}/studies")
def create_study_upload(case_id: int):
    # TODO: presigned URL (MinIO/S3)
    return {"upload_url": "https://example", "case_id": case_id}

@app.post("/cases/{case_id}/analyses")
def enqueue_analysis(case_id: int):
    # TODO: RQ job enqueue → worker
    return {"job_id": f"job-{case_id}"}

@app.get("/cases/{case_id}/analyses")
def get_analysis(case_id: int):
    # TODO: job progress/result
    return {"status": "queued"}

@app.post("/cases/{case_id}/conversation")
def add_conversation(case_id: int, message: str):
    return {"ok": True}

@app.post("/cases/{case_id}/report/pdf")
def generate_pdf(case_id: int):
    # TODO: HTML->PDF üret, dosya deposuna yaz
    return {"pdf_url": f"/static/reports/{case_id}.pdf"}

@app.post("/shares")
def create_share(case_id: int, expires_at: str, max_views: int=3):
    return {"share_url": f"https://share/{case_id}"}

# Health check
@app.get("/health")
def health():
    return {"status": "ok", "systems": {"backend": "running", "database": "connected"}}

# Prometheus
@app.on_event("startup")
async def _startup():
    Instrumentator().instrument(app).expose(app)
    logger.info("Neuropetrix API started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)