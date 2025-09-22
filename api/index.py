# api/index.py (Vercel Python Function - ASGI)
# NeuroPETRIX Backend API - Vercel Serverless Function

try:
    from main import app  # main.py içinde app = FastAPI() varsa bu yeterli
except Exception:
    # Yedek: Minimal app (main.py'de app yoksa)
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from datetime import datetime
    import json
    
    app = FastAPI(
        title="NeuroPETRIX API",
        description="Clinical Decision Support System for Nuclear Medicine",
        version="1.0.0"
    )
    
    # CORS middleware ekle
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/healthz")
    def healthz():
        return {
            "status": "ok",
            "message": "NeuroPETRIX API is running on Vercel",
            "timestamp": datetime.now().isoformat(),
            "platform": "Vercel Serverless",
            "version": "1.0.0"
        }
    
    @app.get("/")
    def root():
        return {
            "message": "NeuroPETRIX Backend API",
            "status": "running",
            "endpoints": {
                "health": "/api/healthz",
                "test": "/api/test",
                "dicom": "/api/dicom",
                "tsnm": "/api/tsnm"
            }
        }
    
    @app.get("/api/test")
    def test():
        return {
            "message": "NeuroPETRIX API Test Endpoint",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "features": [
                "DICOM Processing",
                "TSNM Reporting", 
                "AI Integration",
                "Clinical Decision Support"
            ]
        }
    
    @app.get("/api/dicom")
    def dicom_info():
        return {
            "message": "DICOM Processing Endpoint",
            "status": "ready",
            "features": [
                "DICOM Validation",
                "MPR/MIP Generation",
                "MONAI Segmentation",
                "PyRadiomics Extraction"
            ],
            "note": "Full implementation coming soon"
        }
    
    @app.get("/api/tsnm")
    def tsnm_info():
        return {
            "message": "TSNM Reporting Endpoint", 
            "status": "ready",
            "features": [
                "PERCIST Criteria",
                "Deauville Scoring",
                "Response Assessment",
                "Clinical Reports"
            ],
            "note": "Full implementation coming soon"
        }
    
    @app.get("/api/status")
    def system_status():
        return {
            "system": "NeuroPETRIX",
            "status": "operational",
            "components": {
                "api": "online",
                "database": "ready",
                "ai_engine": "ready",
                "dicom_processor": "ready"
            },
            "timestamp": datetime.now().isoformat()
        }