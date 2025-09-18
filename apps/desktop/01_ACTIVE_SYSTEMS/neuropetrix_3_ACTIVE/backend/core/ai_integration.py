"""
AI Integration Engine - JSON Varyasyon + GPT4All + Gemini
Klinik yorum ve öneri sistemi entegrasyonu
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

@dataclass
class ClinicalContext:
    """Klinik Bağlam"""
    body_region: str
    organ: str
    variation_type: str  # "physiological" or "pathological"
    suv_max: float
    tracer_type: str
    patient_age_group: str
    clinical_goal: str
    icd_codes: List[str] = field(default_factory=list)

@dataclass
class AIResponse:
    """AI Yanıtı"""
    response_id: str
    source: str  # "gpt4all", "gemini", "json_variation"
    content: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ClinicalInterpretation:
    """Klinik Yorum"""
    interpretation_id: str
    clinical_context: ClinicalContext
    json_variation: str
    gpt4all_comment: str
    gemini_suggestion: str
    final_interpretation: str
    confidence_score: float
    recommendations: List[str] = field(default_factory=list)

class AIIntegrationEngine:
    """AI Entegrasyon Motoru"""
    
    def __init__(self):
        self.clinical_variations_path = Path(__file__).parent / "clinical_variations.json"
        self.gemini_api_key = os.getenv("VITE_GEMINI_API_KEY", "")
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        
        # GPT4All mock (gerçek implementasyon için GPT4All kütüphanesi gerekli)
        self.gpt4all_available = False
        
        # Clinical variations yükle
        self.clinical_variations = self._load_clinical_variations()
        
        logger.info("AI Integration Engine başlatıldı")

    def _load_clinical_variations(self) -> Dict[str, Any]:
        """Clinical variations JSON'ını yükle"""
        try:
            if self.clinical_variations_path.exists():
                with open(self.clinical_variations_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Clinical variations dosyası bulunamadı")
                return {}
        except Exception as e:
            logger.error(f"Clinical variations yükleme hatası: {e}")
            return {}

    def generate_clinical_interpretation(self, context: ClinicalContext) -> ClinicalInterpretation:
        """Klinik yorum oluştur"""
        logger.info(f"Klinik yorum oluşturuluyor - Bölge: {context.body_region}, Organ: {context.organ}")
        
        interpretation_id = f"int_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 1. JSON varyasyonu al
        json_variation = self._get_json_variation(context)
        
        # 2. GPT4All ile klinik yorum
        gpt4all_comment = self._get_gpt4all_comment(context, json_variation)
        
        # 3. Gemini ile öneri
        gemini_suggestion = self._get_gemini_suggestion(context, json_variation)
        
        # 4. Final yorumu oluştur
        final_interpretation = self._create_final_interpretation(
            json_variation, gpt4all_comment, gemini_suggestion, context
        )
        
        # 5. Güven skoru hesapla
        confidence_score = self._calculate_confidence_score(
            json_variation, gpt4all_comment, gemini_suggestion
        )
        
        # 6. Öneriler oluştur
        recommendations = self._generate_recommendations(context, final_interpretation)
        
        return ClinicalInterpretation(
            interpretation_id=interpretation_id,
            clinical_context=context,
            json_variation=json_variation,
            gpt4all_comment=gpt4all_comment,
            gemini_suggestion=gemini_suggestion,
            final_interpretation=final_interpretation,
            confidence_score=confidence_score,
            recommendations=recommendations
        )

    def _get_json_variation(self, context: ClinicalContext) -> str:
        """JSON'dan uygun varyasyonu al"""
        try:
            variations = self.clinical_variations.get("clinical_variations", {})
            region_variations = variations.get(context.body_region.lower(), {})
            type_variations = region_variations.get(context.variation_type, {})
            organ_variations = type_variations.get(context.organ, [])
            
            if not organ_variations:
                return f"SUVmax {context.suv_max:.1f} olan {context.organ} lezyonu tespit edilmiştir."
            
            # İlk varyasyonu al ve SUVmax ile formatla
            variation_template = organ_variations[0]
            return variation_template.format(suv_max=context.suv_max)
            
        except Exception as e:
            logger.error(f"JSON varyasyon alma hatası: {e}")
            return f"SUVmax {context.suv_max:.1f} olan {context.organ} lezyonu tespit edilmiştir."

    def _get_gpt4all_comment(self, context: ClinicalContext, json_variation: str) -> str:
        """GPT4All ile klinik yorum al"""
        try:
            if not self.gpt4all_available:
                # Mock GPT4All response
                return self._mock_gpt4all_response(context, json_variation)
            
            # Gerçek GPT4All implementasyonu burada olacak
            # Şimdilik mock response döndürüyoruz
            return self._mock_gpt4all_response(context, json_variation)
            
        except Exception as e:
            logger.error(f"GPT4All yorum alma hatası: {e}")
            return "GPT4All yorumu alınamadı."

    def _mock_gpt4all_response(self, context: ClinicalContext, json_variation: str) -> str:
        """Mock GPT4All yanıtı"""
        tracer_name = context.tracer_type
        age_group = context.patient_age_group
        
        if context.variation_type == "pathological":
            if context.suv_max > 4.0:
                return f"{tracer_name}-PET/CT incelemesinde yüksek metabolik aktivite gösteren lezyon tespit edilmiştir. {age_group} yaş grubunda malignite olasılığı yüksektir."
            elif context.suv_max > 2.5:
                return f"{tracer_name}-PET/CT incelemesinde orta düzeyde metabolik aktivite gösteren lezyon tespit edilmiştir. {age_group} yaş grubunda dikkatli değerlendirme önerilir."
            else:
                return f"{tracer_name}-PET/CT incelemesinde düşük metabolik aktivite gösteren lezyon tespit edilmiştir. {age_group} yaş grubunda benign lezyon olasılığı yüksektir."
        else:
            return f"{tracer_name}-PET/CT incelemesinde fizyolojik uptake izlenmektedir. {age_group} yaş grubunda normal varyasyon olarak değerlendirilmiştir."

    def _get_gemini_suggestion(self, context: ClinicalContext, json_variation: str) -> str:
        """Gemini ile öneri al"""
        try:
            if not self.gemini_api_key:
                return self._mock_gemini_response(context, json_variation)
            
            # Gemini API çağrısı
            prompt = self._create_gemini_prompt(context, json_variation)
            response = self._call_gemini_api(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Gemini öneri alma hatası: {e}")
            return self._mock_gemini_response(context, json_variation)

    def _create_gemini_prompt(self, context: ClinicalContext, json_variation: str) -> str:
        """Gemini için prompt oluştur"""
        prompt = f"""
        Sen bir radyoloji uzmanısın. Aşağıdaki PET/CT bulgusu için klinik öneri ver:

        Bulgu: {json_variation}
        Vücut Bölgesi: {context.body_region}
        Organ: {context.organ}
        SUVmax: {context.suv_max}
        Tracer: {context.tracer_type}
        Yaş Grubu: {context.patient_age_group}
        Klinik Hedef: {context.clinical_goal}
        ICD Kodları: {', '.join(context.icd_codes)}

        Lütfen:
        1. Klinik önemini değerlendir
        2. Takip önerilerini belirt
        3. Ek görüntüleme gereksinimlerini açıkla
        4. Kısa ve öz bir şekilde yanıtla (maksimum 100 kelime)
        """
        return prompt

    def _call_gemini_api(self, prompt: str) -> str:
        """Gemini API'sini çağır"""
        try:
            headers = {
                "Content-Type": "application/json",
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 200,
                }
            }
            
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    return "Gemini yanıtı alınamadı."
            else:
                logger.error(f"Gemini API hatası: {response.status_code}")
                return "Gemini API hatası."
                
        except Exception as e:
            logger.error(f"Gemini API çağrı hatası: {e}")
            return "Gemini API çağrısı başarısız."

    def _mock_gemini_response(self, context: ClinicalContext, json_variation: str) -> str:
        """Mock Gemini yanıtı"""
        if context.variation_type == "pathological":
            if context.suv_max > 4.0:
                return f"Yüksek SUVmax değeri malignite lehine. Histopatolojik doğrulama önerilir. 3 ay sonra kontrol PET/CT yapılabilir."
            elif context.suv_max > 2.5:
                return f"Orta düzeyde SUVmax değeri. Klinik korelasyon ve takip önerilir. 6 ay sonra kontrol görüntüleme yapılabilir."
            else:
                return f"Düşük SUVmax değeri. Benign lezyon olasılığı yüksek. Rutin takip yeterli olabilir."
        else:
            return f"Fizyolojik uptake. Normal varyasyon olarak değerlendirilir. Ek görüntüleme gereksiz."

    def _create_final_interpretation(self, json_variation: str, gpt4all_comment: str, 
                                   gemini_suggestion: str, context: ClinicalContext) -> str:
        """Final yorumu oluştur"""
        final_parts = []
        
        # JSON varyasyonu
        final_parts.append(json_variation)
        
        # GPT4All yorumu
        if gpt4all_comment and gpt4all_comment != "GPT4All yorumu alınamadı.":
            final_parts.append(f"Klinik değerlendirme: {gpt4all_comment}")
        
        # Gemini önerisi
        if gemini_suggestion and gemini_suggestion != "Gemini API hatası.":
            final_parts.append(f"Öneriler: {gemini_suggestion}")
        
        return " ".join(final_parts)

    def _calculate_confidence_score(self, json_variation: str, gpt4all_comment: str, 
                                  gemini_suggestion: str) -> float:
        """Güven skoru hesapla"""
        score = 0.0
        
        # JSON varyasyonu varsa +0.3
        if json_variation and len(json_variation) > 10:
            score += 0.3
        
        # GPT4All yorumu varsa +0.4
        if gpt4all_comment and gpt4all_comment not in ["GPT4All yorumu alınamadı.", ""]:
            score += 0.4
        
        # Gemini önerisi varsa +0.3
        if gemini_suggestion and gemini_suggestion not in ["Gemini API hatası.", ""]:
            score += 0.3
        
        return min(1.0, score)

    def _generate_recommendations(self, context: ClinicalContext, final_interpretation: str) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        # SUVmax'a göre öneriler
        if context.suv_max > 4.0:
            recommendations.append("Yüksek SUVmax değeri - histopatolojik doğrulama önerilir")
            recommendations.append("3 ay sonra kontrol PET/CT yapılabilir")
        elif context.suv_max > 2.5:
            recommendations.append("Orta düzeyde SUVmax değeri - klinik korelasyon önerilir")
            recommendations.append("6 ay sonra kontrol görüntüleme yapılabilir")
        else:
            recommendations.append("Düşük SUVmax değeri - rutin takip yeterli olabilir")
        
        # Tracer'a göre öneriler
        if context.tracer_type == "PSMA":
            recommendations.append("PSMA-PET/CT - prostat kanseri takibi önerilir")
        elif context.tracer_type == "DOTATATE":
            recommendations.append("DOTATATE-PET/CT - nöroendokrin tümör takibi önerilir")
        
        # Yaş grubuna göre öneriler
        if context.patient_age_group == "65+":
            recommendations.append("Yaşlı hasta - komorbiditeler değerlendirilmelidir")
        elif context.patient_age_group == "0-18":
            recommendations.append("Pediatrik hasta - özel protokol uygulanmalıdır")
        
        return recommendations

    def get_ai_status(self) -> Dict[str, Any]:
        """AI servislerinin durumunu getir"""
        return {
            "gpt4all_available": self.gpt4all_available,
            "gemini_available": bool(self.gemini_api_key),
            "clinical_variations_loaded": bool(self.clinical_variations),
            "variations_count": len(self.clinical_variations.get("clinical_variations", {})),
            "timestamp": datetime.now().isoformat()
        }

    def test_ai_integration(self) -> Dict[str, Any]:
        """AI entegrasyonunu test et"""
        try:
            # Test context oluştur
            test_context = ClinicalContext(
                body_region="head_neck",
                organ="tumor",
                variation_type="pathological",
                suv_max=4.5,
                tracer_type="FDG",
                patient_age_group="19-65",
                clinical_goal="staging",
                icd_codes=["C78.00"]
            )
            
            # Klinik yorum oluştur
            interpretation = self.generate_clinical_interpretation(test_context)
            
            return {
                "success": True,
                "test_interpretation": {
                    "interpretation_id": interpretation.interpretation_id,
                    "json_variation": interpretation.json_variation,
                    "gpt4all_comment": interpretation.gpt4all_comment,
                    "gemini_suggestion": interpretation.gemini_suggestion,
                    "final_interpretation": interpretation.final_interpretation,
                    "confidence_score": interpretation.confidence_score,
                    "recommendations": interpretation.recommendations
                },
                "ai_status": self.get_ai_status()
            }
            
        except Exception as e:
            logger.error(f"AI entegrasyon test hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_status": self.get_ai_status()
            }

# Global AI integration engine instance
ai_integration_engine = AIIntegrationEngine()

# Kullanım örneği
if __name__ == "__main__":
    # Test context
    context = ClinicalContext(
        body_region="thorax",
        organ="tumor",
        variation_type="pathological",
        suv_max=3.8,
        tracer_type="FDG",
        patient_age_group="19-65",
        clinical_goal="staging",
        icd_codes=["C78.00"]
    )
    
    # AI entegrasyonu test et
    result = ai_integration_engine.test_ai_integration()
    print(f"AI Test Sonucu: {result['success']}")
    
    if result['success']:
        interpretation = result['test_interpretation']
        print(f"Final Yorum: {interpretation['final_interpretation']}")
        print(f"Güven Skoru: {interpretation['confidence_score']}")
        print(f"Öneriler: {interpretation['recommendations']}")
