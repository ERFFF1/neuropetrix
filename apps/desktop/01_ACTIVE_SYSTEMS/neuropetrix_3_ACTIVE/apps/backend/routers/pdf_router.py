"""
PDF Report Router
NeuroPETRIX - PDF rapor oluşturma ve paylaşım API'leri
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path

try:
    from services.pdf_service import pdf_service
except ImportError:
    from backend.services.pdf_service import pdf_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf", tags=["PDF Reports"])

# Pydantic Models
class CaseReportRequest(BaseModel):
    case_id: str
    case_data: Dict[str, Any]

class ShareLinkRequest(BaseModel):
    report_id: str
    expires_hours: int = 24
    max_views: int = 10

class ShareLinkResponse(BaseModel):
    share_id: str
    share_url: str
    expires_at: str
    max_views: int

@router.post("/generate", response_model=Dict[str, str])
async def generate_case_report(request: CaseReportRequest):
    """Vaka raporu oluştur"""
    try:
        logger.info(f"PDF raporu oluşturuluyor: {request.case_id}")
        
        # Rapor oluştur
        report_path = pdf_service.generate_case_report(request.case_data)
        
        return {
            "status": "success",
            "message": "PDF raporu başarıyla oluşturuldu",
            "report_path": report_path,
            "report_id": Path(report_path).stem
        }
        
    except Exception as e:
        logger.error(f"PDF raporu oluşturulamadı: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF raporu oluşturulamadı: {str(e)}"
        )

@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """Rapor indir"""
    try:
        # Rapor dosyasını bul
        reports_dir = Path("backend/reports")
        report_file = reports_dir / f"{report_id}.html"
        
        if not report_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rapor bulunamadı"
            )
        
        return FileResponse(
            path=str(report_file),
            filename=f"neuropetrix_report_{report_id}.html",
            media_type="text/html"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rapor indirilemedi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rapor indirilemedi: {str(e)}"
        )

@router.post("/share", response_model=ShareLinkResponse)
async def create_shareable_link(request: ShareLinkRequest):
    """Paylaşılabilir link oluştur"""
    try:
        logger.info(f"Paylaşılabilir link oluşturuluyor: {request.report_id}")
        
        # Paylaşılabilir link oluştur
        share_data = pdf_service.create_shareable_link(
            request.report_id,
            request.expires_hours
        )
        
        return ShareLinkResponse(**share_data)
        
    except Exception as e:
        logger.error(f"Paylaşılabilir link oluşturulamadı: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Paylaşılabilir link oluşturulamadı: {str(e)}"
        )

@router.get("/share/{share_id}")
async def view_shared_report(share_id: str):
    """Paylaşılan raporu görüntüle"""
    try:
        # Share data'yı yükle
        reports_dir = Path("backend/reports")
        share_file = reports_dir / f"{share_id}.json"
        
        if not share_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paylaşım bulunamadı"
            )
        
        with open(share_file, 'r', encoding='utf-8') as f:
            share_data = json.load(f)
        
        # Süre kontrolü
        if datetime.now().timestamp() > share_data['expires_at']:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Paylaşım süresi dolmuş"
            )
        
        # Görüntüleme sayısı kontrolü
        if share_data['current_views'] >= share_data['max_views']:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Maksimum görüntüleme sayısına ulaşıldı"
            )
        
        # Görüntüleme sayısını artır
        share_data['current_views'] += 1
        with open(share_file, 'w', encoding='utf-8') as f:
            json.dump(share_data, f, indent=2, ensure_ascii=False)
        
        # Rapor dosyasını bul
        report_file = reports_dir / f"{share_data['report_id']}.html"
        
        if not report_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rapor dosyası bulunamadı"
            )
        
        # HTML içeriğini oku ve döndür
        with open(report_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Paylaşılan rapor görüntülenemedi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Paylaşılan rapor görüntülenemedi: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """PDF servis sağlık kontrolü"""
    return {
        "status": "healthy",
        "service": "pdf_reports",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
