from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import sys
import json
import os

# PyRadiomics gürültüsünü sustur
logging.getLogger("radiomics").setLevel(logging.CRITICAL)

# JSON log formatı
class JsonFormatter(logging.Formatter):
    def format(self, record):
        msg = {"level": record.levelname, "msg": record.getMessage()}
        if hasattr(record, "request_id"):
            msg["request_id"] = record.request_id
        return json.dumps(msg)

h = logging.StreamHandler(sys.stdout)
h.setFormatter(JsonFormatter())
logging.getLogger().handlers = [h]
logging.getLogger().setLevel(logging.INFO)

# Path'i düzelt - Uvicorn için
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)

# Farklı çalışma dizinleri için path'leri ekle
sys.path.insert(0, current_dir)  # backend/
sys.path.insert(0, parent_dir)   # neuropetrix_3_ACTIVE/
sys.path.insert(0, project_root) # 01_ACTIVE_SYSTEMS/

# Uvicorn için ek path'ler
sys.path.insert(0, os.path.join(parent_dir, 'backend'))
sys.path.insert(0, os.path.join(project_root, 'neuropetrix_3_ACTIVE', 'backend'))

# Çalışma dizinini kontrol et ve path'leri buna göre ayarla
cwd = os.getcwd()
if 'neuropetrix_3_ACTIVE' in cwd:
    # Eğer neuropetrix_3_ACTIVE dizinindeysek
    sys.path.insert(0, os.path.join(cwd, 'backend'))
    sys.path.insert(0, cwd)
elif 'backend' in cwd:
    # Eğer backend dizinindeysek
    sys.path.insert(0, cwd)
    sys.path.insert(0, os.path.dirname(cwd))

try:
    from backend.core.settings import settings
except ImportError:
    from core.settings import settings

app = FastAPI(
    title=settings.API_TITLE,
    description="NeuroPETRIX - Complete AI System",
    version=settings.API_VERSION
)

# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Ana endpoint'ler
@app.get("/")
async def root():
    return {"message": "NeuroPETRIX API", "version": settings.API_VERSION}

@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "message": "Complete AI System çalışıyor!",
        "version": settings.API_VERSION,
        "integrations": ["Legacy", "v2.0", "Advanced"]
    }

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint çalışıyor"}

# Router'ları doğrudan import et
print("🔧 Router'lar yükleniyor...")

# Health router
try:
    from routers.health import router as health_router
    app.include_router(health_router)
    print("✓ Health router eklendi")
except Exception as e:
    print(f"❌ Health router eklenemedi: {e}")

# PICO router
try:
    from routers.pico import router as pico_router
    app.include_router(pico_router)
    print("✓ PICO router eklendi")
except Exception as e:
    print(f"❌ PICO router eklenemedi: {e}")

# Patients router
try:
    from routers.patients import router as patients_router
    app.include_router(patients_router)
    print("✓ Patients router eklendi")
except Exception as e:
    print(f"❌ Patients router eklenemedi: {e}")

# SUV router
try:
    from routers.suv import router as suv_router
    app.include_router(suv_router)
    print("✓ SUV router eklendi")
except Exception as e:
    print(f"❌ SUV router eklenemedi: {e}")

# DICOM router
try:
    from routers.dicom import router as dicom_router
    app.include_router(dicom_router)
    print("✓ DICOM router eklendi")
except Exception as e:
    print(f"❌ DICOM router eklenemedi: {e}")

# Whisper router
try:
    from routers.whisper import router as whisper_router
    app.include_router(whisper_router)
    print("✓ Whisper router eklendi")
except Exception as e:
    print(f"❌ Whisper router eklenemedi: {e}")

# Clinical Workflow router
try:
    from routers.clinical_workflow import router as clinical_workflow_router
    app.include_router(clinical_workflow_router)
    print("✓ Clinical Workflow router eklendi")
except Exception as e:
    print(f"❌ Clinical Workflow router eklenemedi: {e}")

# AI Manager router
try:
    from routers.ai_manager_router import router as ai_manager_router
    app.include_router(ai_manager_router)
    print("✓ AI Manager router eklendi")
except Exception as e:
    print(f"❌ AI Manager router eklenemedi: {e}")

# IO Flows router
try:
    from routers.io_flows import router as io_flows_router
    app.include_router(io_flows_router)
    print("✓ IO Flows router eklendi")
except Exception as e:
    print(f"❌ IO Flows router eklenemedi: {e}")

# Report router
try:
    from routers.report import router as report_router
    app.include_router(report_router)
    print("✓ Report router eklendi")
except Exception as e:
    print(f"❌ Report router eklenemedi: {e}")

# Monitoring router
try:
    from routers.monitoring import router as monitoring_router
    app.include_router(monitoring_router)
    print("✓ Monitoring router eklendi")
except Exception as e:
    print(f"❌ Monitoring router eklenemedi: {e}")

# Authentication router
try:
    from routers.auth import router as auth_router
    app.include_router(auth_router)
    print("✓ Authentication router eklendi")
except Exception as e:
    print(f"❌ Authentication router eklenemedi: {e}")

# Metrics router
try:
    from routers.metrics import router as metrics_router
    app.include_router(metrics_router)
    print("✓ Metrics router eklendi")
except Exception as e:
    print(f"❌ Metrics router eklenemedi: {e}")

# Performance router
try:
    from routers.performance import router as performance_router
    app.include_router(performance_router)
    print("✓ Performance router eklendi")
except Exception as e:
    print(f"❌ Performance router eklenemedi: {e}")

# Database router
try:
    from routers.database import router as database_router
    app.include_router(database_router)
    print("✓ Database router eklendi")
except Exception as e:
    print(f"❌ Database router eklenemedi: {e}")

# TSNM Reporting router
try:
    from routers.tsnm_router import router as tsnm_router
    app.include_router(tsnm_router)
    print("✓ TSNM Reporting router eklendi")
except Exception as e:
    print(f"❌ TSNM Reporting router eklenemedi: {e}")

# Workflow Management router
try:
    from routers.workflow_router import router as workflow_router
    app.include_router(workflow_router)
    print("✓ Workflow Management router eklendi")
except Exception as e:
    print(f"❌ Workflow Management router eklenemedi: {e}")

# Data Management router
try:
    from routers.data_management_router import router as data_management_router
    app.include_router(data_management_router)
    print("✓ Data Management router eklendi")
except Exception as e:
    print(f"❌ Data Management router eklenemedi: {e}")

# AI Integration router
try:
    from routers.ai_integration_router import router as ai_integration_router
    app.include_router(ai_integration_router)
    print("✓ AI Integration router eklendi")
except Exception as e:
    print(f"❌ AI Integration router eklenemedi: {e}")

# Compliance & IP router
try:
    from routers.compliance_router import router as compliance_router
    app.include_router(compliance_router)
    print("✓ Compliance & IP router eklendi")
except Exception as e:
    print(f"❌ Compliance & IP router eklenemedi: {e}")

print("🚀 Tüm router'lar yüklendi!")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
