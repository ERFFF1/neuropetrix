from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/dicom", tags=["DICOM"])

@router.get("/series")
async def get_series_meta():
    """DICOM seri meta verilerini getir"""
    return {
        "series_length": 120,
        "image_quality": "Yüksek",
        "slice_thickness": "3.0 mm",
        "pixel_spacing": "2.73 x 2.73 mm",
        "modality": "PT",
        "manufacturer": "Siemens",
        "model": "Biograph mCT"
    }

@router.post("/upload")
async def upload_dicom(payload: Dict[str, Any]):
    """DICOM dosyası yükleme"""
    try:
        # Mock DICOM işleme
        return {
            "success": True,
            "message": "DICOM dosyası başarıyla yüklendi",
            "file_id": "dicom_001",
            "series_count": 1,
            "image_count": 120
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DICOM yükleme hatası: {str(e)}")

@router.post("/analyze")
async def analyze_dicom(payload: Dict[str, Any]):
    """DICOM analizi"""
    try:
        # Mock DICOM analizi
        return {
            "success": True,
            "analysis": {
                "suv_max": 12.5,
                "suv_mean": 8.2,
                "volume": 45.6,
                "lesion_count": 1,
                "quality_score": 0.95
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DICOM analiz hatası: {str(e)}")




