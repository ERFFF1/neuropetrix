from fastapi import FastAPI
from datetime import datetime
app = FastAPI(title="HBYS Mock")

STUDIES = [
    {"study_uid":"1.2.3","patient_hash":"abc123","date":"2025-07-10"},
    {"study_uid":"9.8.7","patient_hash":"def456","date":"2025-07-22"},
]

REPORTS = {
    "1.2.3":"Right lung hypermetabolic nodule - metastasis suspected.",
    "9.8.7":"No significant uptake changes. Stable disease likely."
}

@app.get("/studies")
def studies(frm: str = "", to: str = ""):
    def ok(d): 
        if not frm and not to: return True
        dt = datetime.fromisoformat(d)
        return (not frm or dt >= datetime.fromisoformat(frm)) and (not to or dt <= datetime.fromisoformat(to))
    return [s for s in STUDIES if ok(s["date"])]

@app.get("/reports/{study_uid}")
def report(study_uid: str):
    return {"study_uid": study_uid, "report": REPORTS.get(study_uid, "")}
