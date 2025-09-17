from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="NeuroPETRIX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    case_id: str
    tasks: list[str] = ["radiomics"]
    options: dict = {}

@app.get("/healthz")
def healthz():
    return {"ok": True, "service": "api", "version": "0.1.0"}

@app.post("/api/v1/analysis/run")
async def analysis_run(req: AnalysisRequest):
    return {"job_id": f"job-{req.case_id}", "accepted": True}

@app.get("/api/v1/analysis/status")
def analysis_status(job_id: str):
    return {"job_id": job_id, "state": "done", "progress": 100}

@app.post("/api/v1/dicom/upload")
async def dicom_upload(file: UploadFile = File(...)):
    return {"filename": file.filename, "stored": True}
