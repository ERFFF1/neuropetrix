from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sqlite3
from pydantic import BaseModel
import numpy as np
from scipy import stats

router = APIRouter(prefix="/suv", tags=["suv"])

class SUVMeasurement(BaseModel):
    patient_id: str
    case_id: str
    region: str
    suv_value: float
    measurement_date: datetime
    region_volume: Optional[float] = None
    notes: Optional[str] = None

class SUVTrendAnalysis(BaseModel):
    patient_id: str
    region: str
    time_range: str  # '3months', '6months', '1year', 'all'
    analysis_type: str  # 'linear', 'exponential', 'polynomial'

def get_db():
    return sqlite3.connect("neuropetrix.db")

@router.post("/measurements")
async def add_suv_measurement(measurement: SUVMeasurement):
    """Yeni SUV ölçümü ekle"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        measurement_id = f"SUV{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
            INSERT INTO suv_measurements (id, patient_id, case_id, region, suv_value,
                                        measurement_date, region_volume, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            measurement_id, measurement.patient_id, measurement.case_id,
            measurement.region, measurement.suv_value, measurement.measurement_date,
            measurement.region_volume, measurement.notes, datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        return {"measurement_id": measurement_id, "message": "SUV ölçümü başarıyla eklendi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SUV ölçümü ekleme hatası: {str(e)}")

@router.get("/measurements")
async def get_all_suv_measurements():
    """Tüm SUV ölçümlerini getir"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM suv_measurements 
            ORDER BY measurement_date DESC
            LIMIT 100
        """)
        
        measurements = cursor.fetchall()
        conn.close()
        
        return [{
            "id": m[0], "patient_id": m[1], "case_id": m[2], "region": m[3],
            "suv_value": m[4], "measurement_date": m[5], "region_volume": m[6],
            "notes": m[7], "created_at": m[8]
        } for m in measurements]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SUV ölçümleri getirme hatası: {str(e)}")

@router.get("/measurements/{patient_id}")
async def get_suv_measurements(patient_id: str, region: Optional[str] = None):
    """Hastanın SUV ölçümlerini getir"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if region:
            cursor.execute("""
                SELECT * FROM suv_measurements 
                WHERE patient_id = ? AND region = ? 
                ORDER BY measurement_date ASC
            """, (patient_id, region))
        else:
            cursor.execute("""
                SELECT * FROM suv_measurements 
                WHERE patient_id = ? 
                ORDER BY measurement_date ASC
            """, (patient_id,))
        
        measurements = cursor.fetchall()
        conn.close()
        
        return [{
            "id": m[0], "patient_id": m[1], "case_id": m[2], "region": m[3],
            "suv_value": m[4], "measurement_date": m[5], "region_volume": m[6],
            "notes": m[7], "created_at": m[8]
        } for m in measurements]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SUV ölçümleri getirme hatası: {str(e)}")

@router.post("/trend-analysis")
async def analyze_suv_trend(analysis: SUVTrendAnalysis):
    """SUV trend analizi yap"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Zaman aralığını hesapla
        end_date = datetime.now()
        if analysis.time_range == '3months':
            start_date = end_date - timedelta(days=90)
        elif analysis.time_range == '6months':
            start_date = end_date - timedelta(days=180)
        elif analysis.time_range == '1year':
            start_date = end_date - timedelta(days=365)
        else:  # 'all'
            start_date = datetime(2020, 1, 1)
        
        # Ölçümleri getir
        cursor.execute("""
            SELECT suv_value, measurement_date FROM suv_measurements 
            WHERE patient_id = ? AND region = ? AND measurement_date BETWEEN ? AND ?
            ORDER BY measurement_date ASC
        """, (analysis.patient_id, analysis.region, start_date, end_date))
        
        measurements = cursor.fetchall()
        conn.close()
        
        if len(measurements) < 2:
            raise HTTPException(status_code=400, detail="Trend analizi için en az 2 ölçüm gerekli")
        
        # Veriyi hazırla
        suv_values = [m[0] for m in measurements]
        dates = [datetime.fromisoformat(m[1]) for m in measurements]
        days_since_first = [(d - dates[0]).days for d in dates]
        
        # Trend analizi
        if analysis.analysis_type == 'linear':
            slope, intercept, r_value, p_value, std_err = stats.linregress(days_since_first, suv_values)
            trend_direction = "artış" if slope > 0 else "azalış" if slope < 0 else "değişim yok"
            trend_strength = abs(r_value)
            
        elif analysis.analysis_type == 'exponential':
            # Logaritmik dönüşüm ile lineer analiz
            log_suv = np.log(suv_values)
            slope, intercept, r_value, p_value, std_err = stats.linregress(days_since_first, log_suv)
            trend_direction = "artış" if slope > 0 else "azalış" if slope < 0 else "değişim yok"
            trend_strength = abs(r_value)
            
        else:  # polynomial
            # 2. derece polinom
            coeffs = np.polyfit(days_since_first, suv_values, 2)
            trend_direction = "polinomik"
            trend_strength = 0.8  # Placeholder
        
        # İstatistiksel anlamlılık
        is_significant = p_value < 0.05 if 'p_value' in locals() else False
        
        # Sonuçları hesapla
        current_suv = suv_values[-1]
        first_suv = suv_values[0]
        total_change = ((current_suv - first_suv) / first_suv) * 100
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": round(trend_strength, 3),
            "p_value": round(p_value, 4) if 'p_value' in locals() else None,
            "is_significant": is_significant,
            "total_change_percent": round(total_change, 2),
            "current_suv": round(current_suv, 2),
            "first_suv": round(first_suv, 2),
            "measurement_count": len(measurements),
            "time_span_days": days_since_first[-1],
            "analysis_type": analysis.analysis_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analizi hatası: {str(e)}")

@router.get("/regions/{patient_id}")
async def get_patient_regions(patient_id: str):
    """Hastanın ölçüm yapılan bölgelerini getir"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT region FROM suv_measurements 
            WHERE patient_id = ? 
            ORDER BY region
        """, (patient_id,))
        
        regions = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {"regions": regions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bölge listesi hatası: {str(e)}")

@router.get("/summary/{patient_id}")
async def get_suv_summary(patient_id: str):
    """Hastanın SUV özet bilgilerini getir"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Toplam ölçüm sayısı
        cursor.execute("SELECT COUNT(*) FROM suv_measurements WHERE patient_id = ?", (patient_id,))
        total_measurements = cursor.fetchone()[0]
        
        # Bölge sayısı
        cursor.execute("SELECT COUNT(DISTINCT region) FROM suv_measurements WHERE patient_id = ?", (patient_id,))
        region_count = cursor.fetchone()[0]
        
        # En son ölçüm tarihi
        cursor.execute("""
            SELECT MAX(measurement_date) FROM suv_measurements WHERE patient_id = ?
        """, (patient_id,))
        last_measurement = cursor.fetchone()[0]
        
        # Ortalama SUV değeri
        cursor.execute("SELECT AVG(suv_value) FROM suv_measurements WHERE patient_id = ?", (patient_id,))
        avg_suv = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_measurements": total_measurements,
            "region_count": region_count,
            "last_measurement": last_measurement,
            "average_suv": round(avg_suv, 2) if avg_suv else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Özet bilgi hatası: {str(e)}")


