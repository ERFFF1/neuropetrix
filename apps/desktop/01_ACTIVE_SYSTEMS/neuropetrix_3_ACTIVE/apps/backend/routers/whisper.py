from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/whisper", tags=["Whisper ASR"])

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Ses dosyasını transkribe et"""
    try:
        # Dosya uzantısını kontrol et
        if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
            raise HTTPException(status_code=400, detail="Sadece ses dosyaları kabul edilir")
        
        # Mock transkript (gerçek implementasyonda Whisper API kullanılacak)
        mock_transcript = f"Mock transkript: {file.filename} dosyası işlendi. Sağ akciğer üst lobda 2.5 santimetre boyutunda hipermetabolik nodül tespit edildi."
        
        return {
            "filename": file.filename,
            "transcript": mock_transcript,
            "confidence": 0.95,
            "language": "tr",
            "model": "medium"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transkripsiyon hatası: {str(e)}")

@router.get("/models")
async def get_available_models():
    """Kullanılabilir Whisper modellerini getir"""
    return {
        "models": [
            {"id": "tiny", "name": "Tiny", "size": "39 MB", "accuracy": "Low"},
            {"id": "base", "name": "Base", "size": "74 MB", "accuracy": "Medium"},
            {"id": "small", "name": "Small", "size": "244 MB", "accuracy": "Medium"},
            {"id": "medium", "name": "Medium", "size": "769 MB", "accuracy": "High"},
            {"id": "large", "name": "Large", "size": "1550 MB", "accuracy": "Very High"}
        ],
        "default": "medium",
        "supported_languages": ["tr", "en", "de", "fr", "es", "it", "pt", "ru", "ja", "ko", "zh"]
    }




