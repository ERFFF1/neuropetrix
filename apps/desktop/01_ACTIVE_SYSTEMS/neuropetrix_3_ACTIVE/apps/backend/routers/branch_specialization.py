from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime

router = APIRouter(prefix="/branch", tags=["Branch Specialization"])

class BranchRequest(BaseModel):
    branch: str
    clinical_target: str
    icd_code: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    performance_score: Optional[str] = None

class BranchResponse(BaseModel):
    branch: str
    clinical_target: str
    specialized_workflow: List[str]
    required_metrics: Dict[str, Any]
    clinical_guidelines: List[str]
    risk_factors: List[str]
    recommendations: List[str]
    generated_at: str

# Branch-specific configurations
BRANCH_CONFIGS = {
    "Onkoloji": {
        "priorities": ["TSNM evreleme", "Kemoterapi protokolleri", "PFS/OS", "Yanıt değerlendirmesi"],
        "metrics": {
            "laboratory": ["Hb", "WBC", "Plt", "LDH", "CEA", "CA19-9", "PSA"],
            "clinical": ["ECOG skoru", "Kilo kaybı", "Komorbiditeler", "Aile öyküsü"],
            "imaging": ["SUVmax", "SUVmean", "MTV", "TLG", "Lezyon boyutu", "Metastaz"],
            "medication": ["Mevcut tedaviler", "Alerjiler", "İlaç etkileşimleri", "Yan etkiler"]
        },
        "guidelines": ["NCCN Guidelines", "ESMO Guidelines", "ASCO Guidelines"],
        "risk_factors": ["Yaş", "Performans skoru", "Komorbiditeler", "Metastaz varlığı"]
    },
    "Radyoloji": {
        "priorities": ["Lezyon karakterizasyonu", "SUV analizi", "3D görüntüleme", "Karşılaştırmalı analiz"],
        "metrics": {
            "laboratory": ["Tümör belirteçleri", "İnflamasyon parametreleri"],
            "clinical": ["Semptomlar", "Fizik muayene", "Önceki görüntüleme"],
            "imaging": ["SUV değerleri", "Lezyon morfolojisi", "Perfüzyon", "Dinamik kontrast"],
            "medication": ["Kontrast madde alerjileri", "Önceki tedaviler"]
        },
        "guidelines": ["ACR Guidelines", "ESR Guidelines", "RANZCR Guidelines"],
        "risk_factors": ["Kontrast madde alerjisi", "Böbrek fonksiyonu", "Gebelik"]
    },
    "KBB": {
        "priorities": ["Akut farenjit", "Kronik rinosinüzit", "Baş-boyun tümörleri", "İşitme kaybı"],
        "metrics": {
            "laboratory": ["CRP", "ESR", "Kültür sonuçları"],
            "clinical": ["Semptom süresi", "Ateş", "Ağrı skoru"],
            "imaging": ["CT/MR bulguları", "Endoskopik bulgular"],
            "medication": ["Antibiyotik kullanımı", "Alerjiler"]
        },
        "guidelines": ["AAO-HNS Guidelines", "IDSA Guidelines"],
        "risk_factors": ["Yaş", "Komorbiditeler", "Bağışıklık durumu"]
    },
    "Nöroloji": {
        "priorities": ["Beyin tümörleri", "Alzheimer", "Epilepsi", "İnme"],
        "metrics": {
            "laboratory": ["B12", "Folat", "TSH", "Glukoz"],
            "clinical": ["MMSE skoru", "Glasgow skoru", "Nörolojik muayene"],
            "imaging": ["Beyin MR", "PET bulguları", "Lezyon lokalizasyonu"],
            "medication": ["Antiepileptikler", "Antikoagülanlar", "Psikotropikler"]
        },
        "guidelines": ["AAN Guidelines", "EFNS Guidelines", "ESO Guidelines"],
        "risk_factors": ["Yaş", "Vasküler risk faktörleri", "Aile öyküsü"]
    },
    "Kardiyoloji": {
        "priorities": ["Koroner arter hastalığı", "Miyokard infarktüsü", "Kardiyomiyopati", "Kalp yetmezliği"],
        "metrics": {
            "laboratory": ["Troponin", "BNP", "CRP", "Lipid profili"],
            "clinical": ["NYHA sınıfı", "Ağrı skoru", "Risk skorları"],
            "imaging": ["Koroner CT", "Ekokardiyografi", "Perfüzyon sintigrafisi"],
            "medication": ["Beta blokerler", "ACE inhibitörleri", "Antikoagülanlar"]
        },
        "guidelines": ["ESC Guidelines", "ACC/AHA Guidelines", "CCS Guidelines"],
        "risk_factors": ["Yaş", "Cinsiyet", "Diyabet", "Hipertansiyon", "Dyslipidemi"]
    },
    "Ortopedi": {
        "priorities": ["Kemik tümörleri", "Artrit", "Osteomiyelit", "Travma"],
        "metrics": {
            "laboratory": ["CRP", "ESR", "Kalsiyum", "Fosfor", "ALP"],
            "clinical": ["Ağrı skoru", "Fonksiyonel skor", "ROM"],
            "imaging": ["Kemik sintigrafisi", "CT/MR", "Radyografi"],
            "medication": ["NSAID", "Opioidler", "Kortikosteroidler"]
        },
        "guidelines": ["AAOS Guidelines", "ESMO Guidelines"],
        "risk_factors": ["Yaş", "Cinsiyet", "Osteoporoz", "Travma öyküsü"]
    },
    "Nükleer Tıp": {
        "priorities": ["Tiroid hastalıkları", "Paratiroid", "Adrenal", "Kemik sintigrafisi"],
        "metrics": {
            "laboratory": ["TSH", "T3", "T4", "PTH", "Kalsiyum"],
            "clinical": ["Semptomlar", "Fizik muayene", "Önceki tedaviler"],
            "imaging": ["Sintigrafi bulguları", "SUV değerleri", "Fonksiyonel görüntüleme"],
            "medication": ["Radyoaktif iyot", "Tiroid hormonları", "Kalsiyum"]
        },
        "guidelines": ["SNMMI Guidelines", "ATA Guidelines", "EANM Guidelines"],
        "risk_factors": ["Yaş", "Cinsiyet", "Gebelik", "Emzirme", "Radyasyon öyküsü"]
    }
}

@router.post("/specialize", response_model=BranchResponse)
async def get_branch_specialization(request: BranchRequest):
    """Branşa özel iş akışı ve önerileri getir"""
    
    try:
        branch = request.branch
        clinical_target = request.clinical_target
        
        if branch not in BRANCH_CONFIGS:
            raise HTTPException(status_code=400, detail=f"Bilinmeyen branş: {branch}")
        
        config = BRANCH_CONFIGS[branch]
        
        # Generate specialized workflow based on clinical target
        workflow = generate_workflow(branch, clinical_target, config)
        
        # Generate required metrics
        metrics = generate_metrics(branch, clinical_target, config)
        
        # Generate clinical guidelines
        guidelines = config["guidelines"]
        
        # Generate risk factors
        risk_factors = generate_risk_factors(branch, clinical_target, config, request)
        
        # Generate recommendations
        recommendations = generate_recommendations(branch, clinical_target, config, request)
        
        return BranchResponse(
            branch=branch,
            clinical_target=clinical_target,
            specialized_workflow=workflow,
            required_metrics=metrics,
            clinical_guidelines=guidelines,
            risk_factors=risk_factors,
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logging.error(f"Branch specialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Branch specialization error: {str(e)}")

def generate_workflow(branch: str, clinical_target: str, config: Dict[str, Any]) -> List[str]:
    """Branşa ve klinik hedefe özel iş akışı oluştur"""
    
    base_workflow = [
        "📋 ICD Kodu + Branş + Klinik Hedef Seçimi",
        "🤖 Akıllı Metrik Tanımlama",
        "📊 Veri Toplama (HBYS/Manuel/DICOM)",
        "🧠 MONAI + PyRadiomics Analizi",
        "📈 SUV Trend Analizi",
        "🎯 Klinik Karar Hedefi Güncelleme",
        "🧠 PICO + Literatür + GRADE",
        "🧠 Kanıt Değerlendirme",
        "📄 Final Öneri",
        "📄 Detaylı Rapor Üretimi"
    ]
    
    # Add branch-specific steps
    if branch == "Onkoloji":
        base_workflow.insert(4, "🏥 TSNM Evreleme")
        base_workflow.insert(6, "💊 Tedavi Protokolü Seçimi")
    elif branch == "Radyoloji":
        base_workflow.insert(4, "🖼️ 3D Görüntüleme")
        base_workflow.insert(6, "📊 Karşılaştırmalı Analiz")
    elif branch == "Kardiyoloji":
        base_workflow.insert(4, "🫀 Perfüzyon Analizi")
        base_workflow.insert(6, "📊 Risk Stratifikasyonu")
    
    return base_workflow

def generate_metrics(branch: str, clinical_target: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Branşa ve klinik hedefe özel metrikleri oluştur"""
    
    metrics = config["metrics"].copy()
    
    # Add clinical target specific metrics
    if clinical_target == "Tanı Kararı":
        metrics["priority"] = "Yüksek"
        metrics["focus"] = "Hızlı tanı"
    elif clinical_target == "Tedavi Kararı":
        metrics["priority"] = "Kritik"
        metrics["focus"] = "Tedavi optimizasyonu"
    elif clinical_target == "Prognoz Kararı":
        metrics["priority"] = "Orta"
        metrics["focus"] = "Risk değerlendirmesi"
    elif clinical_target == "Takip Kararı":
        metrics["priority"] = "Düşük"
        metrics["focus"] = "İzlem planı"
    
    return metrics

def generate_risk_factors(branch: str, clinical_target: str, config: Dict[str, Any], request: BranchRequest) -> List[str]:
    """Branşa özel risk faktörlerini oluştur"""
    
    risk_factors = config["risk_factors"].copy()
    
    # Add patient-specific risk factors
    if request.patient_age and request.patient_age > 65:
        risk_factors.append("İleri yaş")
    
    if request.performance_score and int(request.performance_score) > 2:
        risk_factors.append("Kötü performans skoru")
    
    if request.patient_gender == "Kadın" and branch in ["Kardiyoloji", "Ortopedi"]:
        risk_factors.append("Cinsiyet-spesifik risk")
    
    return risk_factors

def generate_recommendations(branch: str, clinical_target: str, config: Dict[str, Any], request: BranchRequest) -> List[str]:
    """Branşa özel önerileri oluştur"""
    
    recommendations = []
    
    # Branch-specific recommendations
    if branch == "Onkoloji":
        recommendations.extend([
            "TSNM evreleme yapılmalı",
            "Kemoterapi protokolü seçilmeli",
            "Yanıt değerlendirmesi planlanmalı"
        ])
    elif branch == "Radyoloji":
        recommendations.extend([
            "3D görüntüleme yapılmalı",
            "Karşılaştırmalı analiz yapılmalı",
            "SUV değerleri hesaplanmalı"
        ])
    elif branch == "Kardiyoloji":
        recommendations.extend([
            "Risk stratifikasyonu yapılmalı",
            "Perfüzyon analizi planlanmalı",
            "Kardiyak fonksiyon değerlendirilmeli"
        ])
    
    # Clinical target specific recommendations
    if clinical_target == "Tanı Kararı":
        recommendations.append("Hızlı tanı için gerekli tetkikler planlanmalı")
    elif clinical_target == "Tedavi Kararı":
        recommendations.append("Tedavi protokolü optimize edilmeli")
    elif clinical_target == "Prognoz Kararı":
        recommendations.append("Risk faktörleri değerlendirilmeli")
    elif clinical_target == "Takip Kararı":
        recommendations.append("İzlem planı oluşturulmalı")
    
    return recommendations

@router.get("/branches")
async def get_available_branches():
    """Kullanılabilir branşları listele"""
    return {"branches": list(BRANCH_CONFIGS.keys())}

@router.get("/config/{branch}")
async def get_branch_config(branch: str):
    """Belirli bir branşın konfigürasyonunu getir"""
    if branch not in BRANCH_CONFIGS:
        raise HTTPException(status_code=404, detail=f"Branş bulunamadı: {branch}")
    
    return {"branch": branch, "config": BRANCH_CONFIGS[branch]}
