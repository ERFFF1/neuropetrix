from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import sys
import json

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

try:
    from backend.core.settings import settings
except ImportError:
    from core.settings import settings

app = FastAPI(
    title=settings.API_TITLE,
    description="Eski sistem + HBYS + AI + MONAI + Evidence + Integration",
    version=settings.API_VERSION
)

# Request-ID middleware ekle
try:
    from backend.middleware.request_id import RequestIDMiddleware
    app.add_middleware(RequestIDMiddleware)
except ImportError:
    from middleware.request_id import RequestIDMiddleware
    app.add_middleware(RequestIDMiddleware)

# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global exception handler (JSON + request_id)
@app.exception_handler(Exception)
async def unhandled_exc(request: Request, exc: Exception):
    rid = getattr(request.state, "request_id", "-")
    logging.exception("uncaught_exception | rid=%s", rid)
    return JSONResponse(
        status_code=500, 
        content={"ok": False, "error": "internal_error", "request_id": rid}
    )

# ===== ESKİ SİSTEM ROUTER'LARI =====
print("🔧 Eski sistem router'ları yükleniyor...")

# Güvenli router yükleme fonksiyonu
def _safe_include_router(modpath, name):
    try:
        module = __import__(modpath, fromlist=[name])
        app.include_router(getattr(module, name))
        print(f"✓ {modpath} yüklendi")
        return True
    except Exception as e:
        print(f"⚠️ {modpath} yüklenemedi: {e}")
        return False

try:
    from routers import health
    app.include_router(health.router)
    print("✓ Health router eklendi")
except Exception as e:
    print(f"❌ Health router eklenemedi: {e}")

try:
    from routers import pico
    app.include_router(pico.router)
    print("✓ PICO router eklendi")
except Exception as e:
    print(f"❌ PICO router eklenemedi: {e}")

try:
    from routers import patients
    app.include_router(patients.router)
    print("✓ Patients router eklendi")
except Exception as e:
    print(f"❌ Patients router eklenemedi: {e}")

try:
    from routers import suv
    app.include_router(suv.router)
    print("✓ SUV router eklendi")
except Exception as e:
    print(f"❌ SUV router eklenemedi: {e}")

try:
    from routers import dicom
    app.include_router(dicom.router)
    print("✓ DICOM router eklendi")
except Exception as e:
    print(f"❌ DICOM router eklenemedi: {e}")

# Reports router - report.py kullanılıyor (duplikasyon kaldırıldı)

try:
    from routers import whisper
    app.include_router(whisper.router)
    print("✓ Whisper router eklendi")
except Exception as e:
    print(f"❌ Whisper router eklenemedi: {e}")

try:
    from routers import clinical_workflow
    app.include_router(clinical_workflow.router)
    print("✓ Clinical Workflow router eklendi")
except Exception as e:
    print(f"❌ Clinical Workflow router eklenemedi: {e}")

try:
    from routers.ai_manager_router import router as ai_manager_router
    app.include_router(ai_manager_router)
    print("✓ AI Manager router eklendi")
except Exception as e:
    print(f"❌ AI Manager router eklenemedi: {e}")

try:
    from routers import io_flows
    app.include_router(io_flows.router)
    print("✓ IO Flows router eklendi")
except Exception as e:
    print(f"❌ IO Flows router eklenemedi: {e}")

# ===== YENİ v2.0 ROUTER'LARI =====
print("\n🚀 Yeni v2.0 router'ları yükleniyor...")

try:
    from routers import intake
    app.include_router(intake.router)
    print("✓ Intake router eklendi")
except Exception as e:
    print(f"❌ Intake router eklenemedi: {e}")

try:
    from routers import imaging
    app.include_router(imaging.router)
    print("✓ Imaging router eklendi")
except Exception as e:
    print(f"❌ Imaging router eklenemedi: {e}")

try:
    from routers import evidence
    app.include_router(evidence.router)
    print("✓ Evidence router eklendi")
except Exception as e:
    print(f"❌ Evidence router eklenemedi: {e}")

try:
    from routers import report
    app.include_router(report.router)
    print("✓ Report router eklendi")
except Exception as e:
    print(f"❌ Report router eklenemedi: {e}")

# ===== GELİŞMİŞ ROUTER'LAR =====
print("\n⚡ Gelişmiş router'lar yükleniyor...")

try:
    from routers import hbys_integration
    app.include_router(hbys_integration.router)
    print("✓ HBYS Integration router eklendi")
except Exception as e:
    print(f"❌ HBYS Integration router eklenemedi: {e}")

try:
    from routers import monai_radiomics
    app.include_router(monai_radiomics.router)
    print("✓ MONAI Radiomics router eklendi")
except Exception as e:
    print(f"❌ MONAI Radiomics router eklenemedi: {e}")

try:
    from routers import desktop_runner
    app.include_router(desktop_runner.router)
    print("✓ Desktop Runner router eklendi")
except Exception as e:
    print(f"❌ Desktop Runner router eklenemedi: {e}")

try:
    from routers import advanced_dicom
    app.include_router(advanced_dicom.router)
    print("✓ Advanced DICOM router eklendi")
except Exception as e:
    print(f"❌ Advanced DICOM router eklenemedi: {e}")

try:
    from routers import branch_specialization
    app.include_router(branch_specialization.router)
    print("✓ Branch Specialization router eklendi")
except Exception as e:
    print(f"❌ Branch Specialization router eklenemedi: {e}")

try:
    from routers import integration_workflow
    app.include_router(integration_workflow.router)
    print("✓ Integration Workflow router eklendi")
except Exception as e:
    print(f"❌ Integration Workflow router eklenemedi: {e}")

# ===== GEMINI AI STUDIO ROUTER'LARI =====
print("\n🤖 Gemini AI Studio router'ları yükleniyor...")

try:
    from routers import gemini
    app.include_router(gemini.router)
    print("✓ Gemini AI Studio router eklendi")
except Exception as e:
    print(f"❌ Gemini AI Studio router eklenemedi: {e}")

# ===== METRICS ROUTER =====
print("\n📊 Metrics router yükleniyor...")

# Metrics router - metrics_router.py kullanılıyor (duplikasyon kaldırıldı)

# ===== FHIR PUSH ROUTER =====
print("\n🏥 FHIR Push router yükleniyor...")

try:
    from routers import fhir_push
    app.include_router(fhir_push.router)
    print("✓ FHIR Push router eklendi")
except Exception as e:
    print(f"❌ FHIR Push router eklenemedi: {e}")

# ===== ANALYTICS ROUTER =====
print("\n📈 Analytics router yükleniyor...")

try:
    from routers import analytics_router
    app.include_router(analytics_router.router)
    print("✓ Analytics router eklendi")
except Exception as e:
    print(f"❌ Analytics router eklenemedi: {e}")

# ===== NOTIFICATION ROUTER =====
print("\n🔔 Notification router yükleniyor...")

try:
    from routers import notification_router
    app.include_router(notification_router.router)
    print("✓ Notification router eklendi")
except Exception as e:
    print(f"❌ Notification router eklenemedi: {e}")

# ===== WEBSOCKET ROUTER =====
print("\n🔌 WebSocket router yükleniyor...")

try:
    from routers import websocket_router
    app.include_router(websocket_router.router)
    print("✓ WebSocket router eklendi")
except Exception as e:
    print(f"❌ WebSocket router eklenemedi: {e}")

# ===== ADVANCED AI ROUTER =====
print("\n🤖 Advanced AI router yükleniyor...")

try:
    from routers import advanced_ai_router
    app.include_router(advanced_ai_router.router)
    print("✓ Advanced AI router eklendi")
except Exception as e:
    print(f"❌ Advanced AI router eklenemedi: {e}")

# ===== MOBILE API ROUTER =====
print("\n📱 Mobile API router yükleniyor...")

try:
    from routers import mobile_api_router
    app.include_router(mobile_api_router.router)
    print("✓ Mobile API router eklendi")
except Exception as e:
    print(f"❌ Mobile API router eklenemedi: {e}")

# ===== SECURITY ROUTER =====
print("\n🔐 Security router yükleniyor...")

try:
    from routers import security_router
    app.include_router(security_router.router)
    print("✓ Security router eklendi")
except Exception as e:
    print(f"❌ Security router eklenemedi: {e}")

# ===== REAL AI ROUTER =====
print("\n🤖 Real AI router yükleniyor...")

try:
    from routers import real_ai_router
    app.include_router(real_ai_router.router)
    print("✓ Real AI router eklendi")
except Exception as e:
    print(f"❌ Real AI router eklenemedi: {e}")

# ===== FRONTEND ROUTER =====
print("\n🌐 Frontend router yükleniyor...")

try:
    from routers import frontend_router
    app.include_router(frontend_router.router)
    print("✓ Frontend router eklendi")
except Exception as e:
    print(f"❌ Frontend router eklenemedi: {e}")

# ===== PDF ROUTER =====
print("\n📄 PDF router yükleniyor...")

try:
    from routers import pdf_router
    app.include_router(pdf_router.router)
    print("✓ PDF router eklendi")
except Exception as e:
    print(f"❌ PDF router eklenemedi: {e}")

# ===== NOTIFICATION ROUTER =====
print("\n🔔 Notification router yükleniyor...")

try:
    from routers import notification_router
    app.include_router(notification_router.router)
    print("✓ Notification router eklendi")
except Exception as e:
    print(f"❌ Notification router eklenemedi: {e}")

# ===== METRICS ROUTER =====
print("\n📊 Metrics router yükleniyor...")

try:
    from routers import metrics_router
    app.include_router(metrics_router.router)
    print("✓ Metrics router eklendi")
except Exception as e:
    print(f"❌ Metrics router eklenemedi: {e}")

# ===== ANA ENDPOINT'LER =====
@app.get("/")
async def root():
    return {
        "message": "NeuroPETRIX - Complete AI System",
        "version": "1.5.0",
        "status": "Tüm sistemler entegre edildi",
                            "systems": {
                        "legacy": ["Health", "PICO", "Patients", "SUV", "DICOM", "Reports", "Whisper"],
                        "v2_0": ["Intake", "Imaging", "Evidence", "Report"],
                        "advanced": ["HBYS", "MONAI", "Desktop Runner", "Advanced DICOM", "Branch Specialization", "Integration Workflow"],
                        "gemini": ["AI Studio", "Decision Composer", "Evidence Search", "FHIR Integration"],
                        "analytics": ["Dashboard", "Metrics", "Trends", "Alerts"],
                        "notifications": ["Real-time", "Email", "SMS", "Push"],
                        "websocket": ["Real-time Updates", "Case Monitoring", "Dashboard Live"],
                        "advanced_ai": ["Comprehensive Analysis", "Model Training", "Performance Metrics"],
                        "mobile": ["Authentication", "Case Management", "Push Notifications", "Sync"],
                        "security": ["JWT Authentication", "User Management", "Session Control", "Permissions"],
                        "real_ai": ["Lung Segmentation", "Lymph Detection", "Radiomics", "Prognosis"]
                    }
    }

@app.get("/health")
async def health():
    return {
        "status": "OK", 
        "message": "Complete AI System çalışıyor!",
        "version": "1.5.0",
        "integrations": ["Legacy", "v2.0", "Advanced"]
    }

@app.get("/test")
async def test():
    return {"message": "Test endpoint çalışıyor!"}

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "1.5.0",
        "status": "operational",
        "systems": {
            "legacy": "active",
            "v2_0": "active", 
            "advanced": "active"
        }
    }

if __name__ == "__main__":
    print("\n🚀 NeuroPETRIX v1.5.0 başlatılıyor...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
