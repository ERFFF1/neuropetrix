from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json
from datetime import datetime

router = APIRouter(prefix="/pico", tags=["PICO Automation"])

@router.post("/generate")
async def generate_pico_question(payload: Dict[str, Any]):
    """PICO soru oluşturma endpoint'i"""
    try:
        patient_data = payload.get("patientData", {})
        clinical_context = payload.get("clinicalContext", "")
        
        # Google GenAI ile PICO soru oluşturma simülasyonu
        # Gerçek implementasyonda Google GenAI API'si kullanılacak
        
        pico_question = {
            "population": f"{patient_data.get('age', '')} yaşında {patient_data.get('gender', '')} hasta",
            "intervention": "FDG-PET/CT görüntüleme",
            "comparison": "Standart görüntüleme yöntemleri",
            "outcome": "Tanısal doğruluk ve tedavi planlaması",
            "clinicalContext": clinical_context
        }
        
        return {
            "success": True,
            "picoQuestion": pico_question,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PICO soru oluşturma hatası: {str(e)}")

@router.post("/validate")
async def validate_pico_question(payload: Dict[str, Any]):
    """PICO soru validasyonu"""
    try:
        pico_question = payload.get("picoQuestion", {})
        
        # PICO bileşenlerinin varlığını kontrol et
        required_fields = ["population", "intervention", "comparison", "outcome"]
        missing_fields = [field for field in required_fields if not pico_question.get(field)]
        
        if missing_fields:
            return {
                "valid": False,
                "missing_fields": missing_fields,
                "message": f"Eksik PICO bileşenleri: {', '.join(missing_fields)}"
            }
        
        return {
            "valid": True,
            "message": "PICO soru geçerli",
            "score": 0.95  # PICO kalite skoru
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PICO validasyon hatası: {str(e)}")


