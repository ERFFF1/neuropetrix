# api/index.py (Vercel Python Function - ASGI)
# Vercel otomatik olarak bu dosyayı serverless function olarak deploy eder

try:
    from main import app  # main.py içinde app = FastAPI() varsa bu yeterli
except Exception:
    # Yedek: Minimal app (main.py'de app yoksa)
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/healthz")
    def healthz():
        return {"neuropetrix": "online"}
    
    @app.get("/")
    def root():
        return {"message": "NeuroPETRIX Backend API", "status": "running"}
