from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="NeuroPETRIX - Simple Backend",
    description="Simple backend for testing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NeuroPETRIX Simple Backend is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Backend is running"}

@app.get("/test")
async def test():
    return {"test": "success", "backend": "working"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)