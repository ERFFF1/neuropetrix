from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import shutil
from pathlib import Path
import tempfile

router = APIRouter(prefix="/imaging", tags=["Imaging Pipeline"])

class CaseMeta(BaseModel):
    patient_id: str
    study_uid: str
    icd10: str
    clinical_goal: str
    pico: Dict[str, str]
    hints: Dict[str, Any]
    acquisition: Dict[str, Any]

class ImagingResult(BaseModel):
    patient_id: str
    study_uid: str
    status: str
    imaging_metrics: Optional[Dict[str, Any]] = None
    qc_flags: List[str] = []
    processing_time: float = 0.0
    error_message: Optional[str] = None

@router.post("/run")
async def run_imaging_pipeline(
    case_meta: CaseMeta,
    dicom_files: List[UploadFile] = File(...)
):
    """
    DICOM dosyalarını alıp imaging pipeline'ı çalıştır
    """
    try:
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            # DICOM dosyalarını kaydet
            dicom_dir = os.path.join(temp_dir, "dicom")
            os.makedirs(dicom_dir, exist_ok=True)
            
            for file in dicom_files:
                if file.filename.endswith('.dcm'):
                    file_path = os.path.join(dicom_dir, file.filename)
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
            
            # Case dizini oluştur
            case_dir = f"data/cases/{case_meta.patient_id}"
            os.makedirs(case_dir, exist_ok=True)
            
            # Case meta'yı kaydet
            meta_file = f"{case_dir}/case_meta.json"
            with open(meta_file, "w") as f:
                json.dump(case_meta.dict(), f, indent=2)
            
            # Imaging pipeline'ı çalıştır (simulated)
            imaging_result = await _run_pipeline(case_meta, dicom_dir)
            
            # Sonucu kaydet
            result_file = f"{case_dir}/imaging_result.json"
            with open(result_file, "w") as f:
                json.dump(imaging_result.dict(), f, indent=2)
            
            # Case meta'yı güncelle
            case_meta_data = {
                "patient_id": case_meta.patient_id,
                "icd10": case_meta.icd10,
                "clinical_goal": case_meta.clinical_goal,
                "imaging_available": True,
                "study_uid": case_meta.study_uid,
                "imaging_completed": True
            }
            
            with open(meta_file, "w") as f:
                json.dump(case_meta_data, f, indent=2)
            
            return imaging_result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Imaging pipeline failed: {str(e)}")

async def _run_pipeline(case_meta: CaseMeta, dicom_dir: str) -> ImagingResult:
    """
    Imaging pipeline'ı çalıştır (simulated)
    """
    import time
    start_time = time.time()
    
    try:
        # Simulated pipeline steps
        # 1. DICOM validation
        await _validate_dicom(dicom_dir)
        
        # 2. MPR/MIP generation
        mpr_mip = await _generate_mpr_mip(dicom_dir)
        
        # 3. MONAI segmentation
        segmentation = await _run_monai_segmentation(dicom_dir)
        
        # 4. PyRadiomics extraction
        radiomics = await _extract_radiomics(segmentation)
        
        # 5. PERCIST/Deauville calculation
        clinical_metrics = await _calculate_clinical_metrics(
            radiomics, case_meta.clinical_goal
        )
        
        # 6. QC checks
        qc_flags = await _run_qc_checks(case_meta, radiomics)
        
        processing_time = time.time() - start_time
        
        return ImagingResult(
            patient_id=case_meta.patient_id,
            study_uid=case_meta.study_uid,
            status="completed",
            imaging_metrics={
                "radiomics": radiomics,
                "clinical_metrics": clinical_metrics,
                "mpr_mip": mpr_mip
            },
            qc_flags=qc_flags,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return ImagingResult(
            patient_id=case_meta.patient_id,
            study_uid=case_meta.study_uid,
            status="failed",
            error_message=str(e),
            processing_time=processing_time
        )

async def _validate_dicom(dicom_dir: str):
    """DICOM validation (simulated)"""
    # TODO: Implement actual DICOM validation
    pass

async def _generate_mpr_mip(dicom_dir: str):
    """MPR/MIP generation (simulated)"""
    # TODO: Implement SimpleITK/GDCM MPR/MIP
    return {"mpr": "generated", "mip": "generated"}

async def _run_monai_segmentation(dicom_dir: str):
    """MONAI segmentation (simulated)"""
    # TODO: Implement actual MONAI model inference
    return {"mask_path": "segmentation.nii.gz", "confidence": 0.95}

async def _extract_radiomics(segmentation: Dict[str, Any]):
    """PyRadiomics extraction (simulated)"""
    # TODO: Implement actual PyRadiomics extraction
    return {
        "SUVmax": 12.5,
        "SUVmean": 8.2,
        "MTV": 45.6,
        "TLG": 374.2,
        "texture_features": {
            "GLCM_energy": 0.023,
            "GLCM_contrast": 45.2,
            "GLCM_correlation": 0.78
        }
    }

async def _calculate_clinical_metrics(radiomics: Dict[str, Any], clinical_goal: str):
    """PERCIST/Deauville calculation"""
    if clinical_goal == "response":
        # PERCIST calculation
        suvmax = radiomics.get("SUVmax", 0)
        if suvmax > 10:
            return {"PERCIST": "PMD", "category": "Progressive Metabolic Disease"}
        elif suvmax > 5:
            return {"PERCIST": "SMD", "category": "Stable Metabolic Disease"}
        else:
            return {"PERCIST": "PMR", "category": "Partial Metabolic Response"}
    
    elif clinical_goal == "lymphoma_followup":
        # Deauville calculation
        suvmax = radiomics.get("SUVmax", 0)
        if suvmax < 2:
            return {"Deauville": 1, "category": "No uptake"}
        elif suvmax < 3:
            return {"Deauville": 2, "category": "Uptake ≤ mediastinum"}
        elif suvmax < 4:
            return {"Deauville": 3, "category": "Uptake > mediastinum but ≤ liver"}
        elif suvmax < 5:
            return {"Deauville": 4, "category": "Uptake moderately higher than liver"}
        else:
            return {"Deauville": 5, "category": "Uptake markedly higher than liver"}
    
    return {"clinical_metrics": "not_applicable"}

async def _run_qc_checks(case_meta: CaseMeta, radiomics: Dict[str, Any]):
    """QC checks"""
    qc_flags = []
    
    # Blood glucose check
    blood_glucose = case_meta.acquisition.get("blood_glucose_mgdl", 0)
    if blood_glucose > 200:
        qc_flags.append("High blood glucose - may affect FDG uptake")
    
    # Uptake time check
    uptake_time = case_meta.acquisition.get("uptake_time_min", 0)
    if uptake_time < 45 or uptake_time > 90:
        qc_flags.append("Non-standard uptake time")
    
    # SUVmax check
    suvmax = radiomics.get("SUVmax", 0)
    if suvmax > 20:
        qc_flags.append("Very high SUVmax - consider artifact")
    
    return qc_flags

@router.get("/status/{patient_id}")
async def get_imaging_status(patient_id: str):
    """Imaging durumunu kontrol et"""
    try:
        case_dir = f"data/cases/{patient_id}"
        result_file = f"{case_dir}/imaging_result.json"
        
        if not os.path.exists(result_file):
            return {"status": "not_started"}
        
        with open(result_file, "r") as f:
            result = json.load(f)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get imaging status: {str(e)}")
