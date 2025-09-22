from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import subprocess
import json
import os
from pathlib import Path

router = APIRouter(prefix="/desktop-runner", tags=["Desktop Runner"])

class CaseConfig(BaseModel):
    case_id: str
    purpose: str
    ICD: str
    notes: Optional[str] = None
    patient_info: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    status: str
    message: str
    report_id: Optional[str] = None
    case_id: str

@router.post("/run-analysis", response_model=AnalysisResponse)
async def run_analysis(case_config: CaseConfig, background_tasks: BackgroundTasks):
    """Desktop Runner ile analiz başlat"""
    try:
        # Case config dosyasını oluştur
        neuropetrix_dir = Path.home() / "NeuroPETRIX" / "local"
        case_file = neuropetrix_dir / "input_dicom" / f"{case_config.case_id}.json"
        
        # Dizin oluştur
        case_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Case config'i kaydet
        with open(case_file, 'w', encoding='utf-8') as f:
            json.dump(case_config.dict(), f, indent=2)
        
        # Background task olarak analizi başlat
        background_tasks.add_task(run_desktop_analysis, case_config.case_id, str(case_file))
        
        return AnalysisResponse(
            status="started",
            message=f"Analysis started for case {case_config.case_id}",
            case_id=case_config.case_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@router.get("/status/{case_id}", response_model=AnalysisResponse)
async def get_analysis_status(case_id: str):
    """Analiz durumunu kontrol et"""
    try:
        neuropetrix_dir = Path.home() / "NeuroPETRIX" / "local"
        output_dir = neuropetrix_dir / "output" / case_id
        
        if not output_dir.exists():
            return AnalysisResponse(
                status="not_found",
                message=f"Case {case_id} not found",
                case_id=case_id
            )
        
        # Rapor dosyasını kontrol et
        report_file = output_dir / "reports" / f"{case_id}_report.json"
        if report_file.exists():
            with open(report_file, 'r') as f:
                report = json.load(f)
            
            return AnalysisResponse(
                status="completed",
                message="Analysis completed successfully",
                report_id=report.get("report_id"),
                case_id=case_id
            )
        else:
            return AnalysisResponse(
                status="running",
                message="Analysis in progress",
                case_id=case_id
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/results/{case_id}")
async def get_analysis_results(case_id: str):
    """Analiz sonuçlarını getir"""
    try:
        neuropetrix_dir = Path.home() / "NeuroPETRIX" / "local"
        output_dir = neuropetrix_dir / "output" / case_id
        
        if not output_dir.exists():
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        results = {}
        
        # Segmentation results
        seg_dir = output_dir / "seg"
        if seg_dir.exists():
            seg_files = list(seg_dir.glob("*.json"))
            if seg_files:
                with open(seg_files[0], 'r') as f:
                    results["segmentation"] = json.load(f)
        
        # Radiomics results
        radiomics_dir = output_dir / "radiomics"
        if radiomics_dir.exists():
            radiomics_files = list(radiomics_dir.glob("*.json"))
            if radiomics_files:
                with open(radiomics_files[0], 'r') as f:
                    results["radiomics"] = json.load(f)
        
        # Report
        reports_dir = output_dir / "reports"
        if reports_dir.exists():
            report_files = list(reports_dir.glob("*.json"))
            if report_files:
                with open(report_files[0], 'r') as f:
                    results["report"] = json.load(f)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

def run_desktop_analysis(case_id: str, case_file: str):
    """Background task: Desktop Runner analizi çalıştır"""
    try:
        neuropetrix_dir = Path.home() / "NeuroPETRIX" / "local"
        runner_script = neuropetrix_dir / "runner.py"
        
        if not runner_script.exists():
            print(f"❌ Runner script not found: {runner_script}")
            return
        
        # Python runner'ı çalıştır
        cmd = ["python", str(runner_script), "--case", case_file]
        
        result = subprocess.run(
            cmd,
            cwd=str(neuropetrix_dir),
            capture_output=True,
            text=True,
            timeout=300  # 5 dakika timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Analysis completed for case {case_id}")
            print(f"Output: {result.stdout}")
        else:
            print(f"❌ Analysis failed for case {case_id}")
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Analysis timeout for case {case_id}")
    except Exception as e:
        print(f"❌ Analysis error for case {case_id}: {e}")

@router.get("/health")
async def health_check():
    """Desktop Runner sağlık kontrolü - Optimized"""
    try:
        neuropetrix_dir = Path.home() / "NeuroPETRIX" / "local"
        
        # Hızlı health check - sadece dizin kontrolü
        if neuropetrix_dir.exists():
            return {
                "status": "healthy", 
                "message": "Desktop Runner is working",
                "local_dir": str(neuropetrix_dir),
                "response_time": "fast"
            }
        else:
            return {
                "status": "warning",
                "message": "Local directory not found",
                "local_dir": str(neuropetrix_dir),
                "response_time": "fast"
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Health check failed: {str(e)}",
            "response_time": "fast"
        }
