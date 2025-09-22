from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from typing import List, Dict, Any, Optional
from jinja2 import Environment, BaseLoader, select_autoescape
import uvicorn
import os
import json
from pathlib import Path
from datetime import datetime
from database import init_database
import sqlite3
from reporting import sentence_diff, build_docx, ebm_composite_score, format_diff_html

# Jinja2 template engine
_env = Environment(loader=BaseLoader(), autoescape=select_autoescape())

def _db(): 
    return sqlite3.connect("neuropetrix.db")

def _load_inst():
    """Kurum konfigürasyonunu yükle"""
    try:
        with open(os.path.join("backend", "config", "institution.json"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Varsayılan konfigürasyon
        return {
            "tsnm_defaults": {
                "device_model": "Siemens Biograph mCT",
                "fdg_dose_mbq": 300,
                "glycemia_mgdl": 110,
                "fasting_hours": 6
            },
            "report_priority_order": [
                "primer_lez", "lenf_nodu", "uzak_met", "ilk_defa", 
                "malignite_suphe", "klinik_onem", "onerilen_mudahale"
            ]
        }

def _sentence_texts(keys: List[str]) -> List[str]:
    """Cümle bankasından metinleri getir"""
    if not keys: 
        return []
    q = ",".join("?" * len(keys))
    con = _db()
    cur = con.cursor()
    cur.execute(f"SELECT text FROM sentence_bank WHERE key IN ({q})", keys)
    out = [r[0] for r in cur.fetchall()]
    cur.close()
    con.close()
    return out

def _default_template(modality: str) -> str:
    """Belirtilen modalite için varsayılan template getir"""
    con = _db()
    cur = con.cursor()
    cur.execute("""
        SELECT jinja FROM report_templates 
        WHERE modality=? AND is_default=1 
        ORDER BY id DESC LIMIT 1
    """, (modality,))
    row = cur.fetchone()
    cur.close()
    con.close()
    return row[0] if row else "# Şablon yok"

# Veritabanını başlat
init_database()

app = FastAPI(
    title="NeuroPETrix API", 
    version="1.0.0",
    description="AI destekli PET/CT analizi ve rapor üretimi platformu"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basit health endpoint
@app.get("/health")
async def health():
    """Sistem sağlık kontrolü"""
    return {
        "status": "healthy",
        "message": "NeuroPETrix API çalışıyor",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Basit reports endpoint
@app.post("/reports/generate")
async def generate_report(payload: dict):
    """Basit rapor üretimi"""
    try:
        patient = payload.get("patient", {})
        report_type = payload.get("report_type", "standard")
        
        # Basit markdown oluştur
        markdown = f"""# {report_type.title()} Raporu

**Hasta:** {patient.get('ad_soyad', 'N/A')} - {patient.get('hasta_no', 'N/A')}  
**Tarih:** {datetime.now().strftime('%Y-%m-%d')}  
**Tür:** {report_type}

## Klinik Hikaye
{payload.get('clinical_history', 'Belirtilmemiş')}

## Bulgular
{payload.get('findings', 'Belirtilmemiş')}

## İzlenim
{payload.get('impression', 'Belirtilmemiş')}

---
*Bu rapor NeuroPETrix AI sistemi ile oluşturulmuştur.*
"""
        
        return {
            "markdown": markdown,
            "meta": {"report_type": report_type, "generated_at": datetime.now().isoformat()},
            "report_type": f"{report_type.title()} Raporu",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rapor üretimi hatası: {str(e)}")

# Basit whisper endpoint
@app.post("/whisper/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Ses dosyasını transkribe et"""
    try:
        # Dosya uzantısını kontrol et
        if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
            raise HTTPException(status_code=400, detail="Sadece ses dosyaları kabul edilir")
        
        # Mock transkript
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

# Basit DICOM endpoint
@app.get("/dicom/series")
async def get_series_meta():
    """DICOM seri meta verilerini getir"""
    return {
        "series_length": 120,
        "image_quality": "Yüksek",
        "slice_thickness": "3.0 mm",
        "pixel_spacing": "2.73 x 2.73 mm"
    }

# Root endpoint
@app.get("/")
async def root():
    """API ana sayfası"""
    return {
        "message": "NeuroPETrix API'ye Hoş Geldiniz",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "health": "/health",
            "reports": "/reports/generate",
            "whisper": "/whisper/transcribe",
            "dicom": "/dicom/series"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)