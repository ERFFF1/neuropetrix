from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import legacy, v1

app = FastAPI(title="NeuroPETRIX API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "NeuroPETRIX API", "version": "3.0.0"}

@app.get("/")
def root():
    return {
        "message": "NeuroPETRIX v3.0 API",
        "docs": "/docs",
        "health": "/healthz",
        "legacy": "/legacy",
        "v1": "/v1"
    }

# Legacy ve V1 router'ları ekle
app.include_router(legacy.router, prefix="/legacy", tags=["legacy"])
app.include_router(v1.router, prefix="/v1", tags=["v1"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
