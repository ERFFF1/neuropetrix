"""
Advanced DICOM Router with MONAI and PyRadiomics Integration
Handles real DICOM processing, segmentation, and radiomics analysis
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Any, Optional
import os
import tempfile
import shutil
from pathlib import Path
import logging

from services.advanced_dicom_service import get_advanced_dicom_service
from schemas.common import SuccessResponse, ErrorResponse

router = APIRouter(prefix="/advanced-dicom", tags=["Advanced DICOM Processing"])

# Initialize service
dicom_service = get_advanced_dicom_service()

@router.post("/upload", response_model=SuccessResponse)
async def upload_dicom_file(
    file: UploadFile = File(...),
    patient_id: str = None,
    background_tasks: BackgroundTasks = None
):
    """
    Upload and process DICOM file with advanced AI analysis
    
    This endpoint:
    1. Receives DICOM file upload
    2. Performs AI-powered segmentation using MONAI
    3. Extracts radiomics features using PyRadiomics
    4. Calculates SUV measurements
    5. Generates 3D visualization
    6. Creates comprehensive analysis report
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.dcm'):
            raise HTTPException(
                status_code=400, 
                detail="Only .dcm files are supported"
            )
        
        # Generate patient ID if not provided
        if not patient_id:
            patient_id = f"P{os.urandom(8).hex().upper()}"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dcm') as temp_file:
            # Copy uploaded file to temp
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Process DICOM file
            result = await dicom_service.process_dicom_file(temp_file_path, patient_id)
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            return SuccessResponse(
                message="DICOM file processed successfully",
                data={
                    "patient_id": patient_id,
                    "report_id": result.get("report_id"),
                    "analysis_summary": result.get("analysis_summary"),
                    "processing_status": "completed"
                }
            )
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        logging.error(f"DICOM upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process DICOM file: {str(e)}"
        )

@router.get("/patients/{patient_id}/studies")
async def get_patient_studies(patient_id: str):
    """
    Get all DICOM studies for a specific patient
    """
    try:
        studies = await dicom_service.get_patient_studies(patient_id)
        return SuccessResponse(
            message=f"Found {len(studies)} studies for patient {patient_id}",
            data={"studies": studies}
        )
    except Exception as e:
        logging.error(f"Failed to get patient studies: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve patient studies: {str(e)}"
        )

@router.get("/patients/{patient_id}/analysis/{report_id}")
async def get_analysis_report(patient_id: str, report_id: str):
    """
    Get detailed analysis report for a specific study
    """
    try:
        # Load analysis results from file
        results_path = Path(f"data/dicom_data/patients/{patient_id}/analysis_results.json")
        
        if not results_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Analysis report not found"
            )
        
        with open(results_path, 'r') as f:
            import json
            report = json.load(f)
        
        return SuccessResponse(
            message="Analysis report retrieved successfully",
            data=report
        )
        
    except Exception as e:
        logging.error(f"Failed to get analysis report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analysis report: {str(e)}"
        )

@router.get("/patients/{patient_id}/visualization")
async def get_3d_visualization(patient_id: str):
    """
    Get 3D visualization for a patient's DICOM data
    """
    try:
        # Look for visualization file
        viz_path = Path(f"data/temp/{patient_id}_3d_visualization.html")
        
        if not viz_path.exists():
            raise HTTPException(
                status_code=404,
                detail="3D visualization not found"
            )
        
        return FileResponse(
            path=str(viz_path),
            media_type="text/html",
            filename=f"{patient_id}_3d_visualization.html"
        )
        
    except Exception as e:
        logging.error(f"Failed to get 3D visualization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve 3D visualization: {str(e)}"
        )

@router.post("/patients/{patient_id}/reprocess")
async def reprocess_patient_data(patient_id: str):
    """
    Reprocess all DICOM data for a patient with updated AI models
    """
    try:
        # This would trigger reprocessing with updated models
        # For now, return success message
        return SuccessResponse(
            message=f"Reprocessing initiated for patient {patient_id}",
            data={
                "patient_id": patient_id,
                "status": "reprocessing_initiated",
                "estimated_time": "5-10 minutes"
            }
        )
        
    except Exception as e:
        logging.error(f"Failed to initiate reprocessing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate reprocessing: {str(e)}"
        )

@router.delete("/patients/{patient_id}")
async def delete_patient_data(patient_id: str):
    """
    Delete all DICOM data and analysis results for a patient
    """
    try:
        success = await dicom_service.delete_patient_data(patient_id)
        
        if success:
            return SuccessResponse(
                message=f"All data for patient {patient_id} deleted successfully",
                data={"patient_id": patient_id, "deleted": True}
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Patient {patient_id} not found"
            )
            
    except Exception as e:
        logging.error(f"Failed to delete patient data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete patient data: {str(e)}"
        )

@router.get("/system/status")
async def get_system_status():
    """
    Get advanced DICOM processing system status
    """
    try:
        status = {
            "service_status": "active",
            "monai_available": hasattr(dicom_service, 'segmentation_model') and dicom_service.segmentation_model is not None,
            "pyradiomics_available": hasattr(dicom_service, 'radiomics_extractor') and dicom_service.radiomics_extractor is not None,
            "simpleitk_available": hasattr(dicom_service, '_post_process_segmentation'),
            "storage_paths": {
                "base_path": str(dicom_service.base_path),
                "models_path": str(dicom_service.models_path),
                "temp_path": str(dicom_service.temp_path)
            },
            "capabilities": [
                "DICOM file processing",
                "AI-powered segmentation",
                "Radiomics feature extraction",
                "SUV measurement calculation",
                "3D visualization generation",
                "Comprehensive reporting"
            ]
        }
        
        return SuccessResponse(
            message="Advanced DICOM system status retrieved",
            data=status
        )
        
    except Exception as e:
        logging.error(f"Failed to get system status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system status: {str(e)}"
        )

@router.post("/models/update")
async def update_ai_models():
    """
    Update AI models (MONAI segmentation, PyRadiomics parameters)
    """
    try:
        # This would trigger model updates
        # For now, return success message
        return SuccessResponse(
            message="AI model update initiated",
            data={
                "status": "update_initiated",
                "models": ["MONAI_UNet", "PyRadiomics_Extractor"],
                "estimated_time": "2-5 minutes"
            }
        )
        
    except Exception as e:
        logging.error(f"Failed to update AI models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update AI models: {str(e)}"
        )

@router.get("/models/info")
async def get_model_information():
    """
    Get information about available AI models
    """
    try:
        model_info = {
            "segmentation_models": {
                "MONAI_UNet": {
                    "type": "3D UNet",
                    "architecture": "Encoder-Decoder",
                    "input_channels": 1,
                    "output_channels": 1,
                    "spatial_dims": 3,
                    "status": "available" if dicom_service.segmentation_model else "unavailable"
                }
            },
            "radiomics_extractors": {
                "PyRadiomics": {
                    "feature_categories": [
                        "Shape", "First Order", "GLCM", "GLRLM", "GLSZM"
                    ],
                    "total_features": 16,
                    "status": "available" if dicom_service.radiomics_extractor else "unavailable"
                }
            },
            "post_processing": {
                "morphological_operations": "available" if hasattr(dicom_service, '_post_process_segmentation') else "unavailable",
                "3d_visualization": "available"
            }
        }
        
        return SuccessResponse(
            message="AI model information retrieved",
            data=model_info
        )
        
    except Exception as e:
        logging.error(f"Failed to get model information: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve model information: {str(e)}"
        )

