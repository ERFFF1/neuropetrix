"""
TSNM Kılavuzu Rapor Şablonları
NeuroPETrix - TSNM Entegrasyonu
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

class TSNMTemplateManager:
    """
    TSNM Kılavuzu Rapor Şablonları Yöneticisi
    """
    
    def __init__(self):
        self.templates = self._load_templates()
        self.variations = self._load_variations()
    
    def _load_templates(self) -> Dict:
        """TSNM rapor şablonlarını yükle"""
        return {
            "fdg_pet_ct": {
                "name": "FDG PET/BT - Onkoloji",
                "file_id": "2020-0032",
                "sections": [
                    "hasta_kimligi",
                    "on_tani_endikasyon", 
                    "yontem",
                    "bulgular",
                    "suvmax_tablosu",
                    "karsilastirma",
                    "sonuc",
                    "ek_oneriler"
                ],
                "anatomical_regions": [
                    "bas_boyun",
                    "toraks", 
                    "abdomen",
                    "pelvis",
                    "kemik_sistemi"
                ]
            },
            "psma_pet_ct": {
                "name": "PSMA PET/BT - Prostat Kanseri",
                "file_id": "2020-0030",
                "sections": [
                    "hasta_kimligi",
                    "on_tani_endikasyon",
                    "yontem",
                    "bulgular",
                    "prostat_lokasyonu",
                    "lenf_nodu",
                    "kemik_metastaz",
                    "ekstranodal",
                    "suvmax_listesi",
                    "karsilastirma",
                    "sonuc_yorum"
                ],
                "specific_features": [
                    "lezyon_bazli_tablo",
                    "ekstranodal_metastaz",
                    "tedavi_yanit"
                ]
            },
            "dotatate_pet_ct": {
                "name": "DOTATATE PET/BT - Nöroendokrin Tümör",
                "file_id": "2020-0028",
                "sections": [
                    "hasta_kimligi",
                    "on_tani_endikasyon",
                    "yontem",
                    "bulgular",
                    "primer_tumor",
                    "hepatik_metastaz",
                    "lenf_nodu_metastaz",
                    "kemik_metastaz",
                    "ek_organ_tutulum",
                    "suvmax_dagilimi",
                    "karsilastirma",
                    "sonuc"
                ],
                "special_features": [
                    "immunohistokimyasal_korelasyon",
                    "tedavi_uygunluk_prrt",
                    "somatostatin_reseptor_ekspresyon"
                ]
            }
        }
    
    def _load_variations(self) -> Dict:
        """Otomatik varyasyon seçeneklerini yükle"""
        return {
            "bulgular_varyasyonlari": {
                "normal": [
                    "Dansit alanlarda FDG tutulumu izlenmemiştir",
                    "Patolojik FDG tutulumu saptanmamıştır",
                    "Normal metabolik aktivite dağılımı mevcuttur"
                ],
                "fokal_artis": [
                    "Fokal artmış FDG tutulumu izlenmiştir",
                    "Metabolik olarak aktif lezyon tespit edilmiştir",
                    "SUVmax değeri yüksek odak görülmüştür"
                ],
                "yaygin_artis": [
                    "Yaygın artmış metabolik aktivite izlenmiştir",
                    "Diffüz FDG tutulum artışı mevcuttur",
                    "Multifokal metabolik aktivite artışı görülmüştür"
                ]
            },
            "sonuc_varyasyonlari": {
                "tedavi_yanit": [
                    "Tedaviye yanıt alınmıştır",
                    "Kısmi yanıt izlenmiştir",
                    "Tedaviye yanıt alınamamıştır"
                ],
                "progresyon": [
                    "Hastalık progresyonu tespit edilmiştir",
                    "Yeni lezyonlar gelişmiştir",
                    "Mevcut lezyonlarda büyüme izlenmiştir"
                ],
                "stabil": [
                    "Hastalık stabil seyretmektedir",
                    "Önceki inceleme ile karşılaştırıldığında değişiklik yoktur",
                    "Stabil hastalık bulguları mevcuttur"
                ]
            }
        }
    
    def generate_report(self, template_type: str, patient_data: Dict, 
                       ai_analysis: Dict, user_preferences: Dict) -> Dict:
        """
        TSNM formatında rapor oluştur
        
        Args:
            template_type: Şablon türü (fdg_pet_ct, psma_pet_ct, dotatate_pet_ct)
            patient_data: Hasta bilgileri
            ai_analysis: AI analiz sonuçları
            user_preferences: Kullanıcı tercihleri
            
        Returns:
            TSNM formatında rapor
        """
        if template_type not in self.templates:
            raise ValueError(f"Bilinmeyen şablon türü: {template_type}")
        
        template = self.templates[template_type]
        report = {
            "template_type": template_type,
            "template_name": template["name"],
            "file_id": template["file_id"],
            "generation_date": datetime.now().isoformat(),
            "sections": {}
        }
        
        # Her bölümü doldur
        for section in template["sections"]:
            report["sections"][section] = self._fill_section(
                section, template_type, patient_data, ai_analysis, user_preferences
            )
        
        return report
    
    def _fill_section(self, section: str, template_type: str, 
                      patient_data: Dict, ai_analysis: Dict, 
                      user_preferences: Dict) -> Dict:
        """Bölümü doldur"""
        
        if section == "hasta_kimligi":
            return self._fill_patient_identity(patient_data)
        
        elif section == "on_tani_endikasyon":
            return self._fill_diagnosis_indication(patient_data, template_type)
        
        elif section == "yontem":
            return self._fill_methodology(template_type, patient_data)
        
        elif section == "bulgular":
            return self._fill_findings(template_type, ai_analysis, user_preferences)
        
        elif section == "suvmax_tablosu":
            return self._fill_suvmax_table(ai_analysis)
        
        elif section == "sonuc":
            return self._fill_conclusion(ai_analysis, user_preferences)
        
        elif section == "ek_oneriler":
            return self._fill_additional_recommendations(ai_analysis)
        
        else:
            return {"content": f"{section} bölümü - AI analizi bekleniyor"}
    
    def _fill_patient_identity(self, patient_data: Dict) -> Dict:
        """Hasta kimliği bölümünü doldur"""
        return {
            "hasta_no": patient_data.get("hasta_no", "Anonim"),
            "yas": patient_data.get("yas", "Bilinmiyor"),
            "cinsiyet": patient_data.get("cinsiyet", "Bilinmiyor"),
            "anonim_hash": patient_data.get("patient_hash", "Hash üretilemedi"),
            "calisma_tarihi": patient_data.get("study_date", "Tarih belirtilmedi")
        }
    
    def _fill_diagnosis_indication(self, patient_data: Dict, template_type: str) -> Dict:
        """Ön tanı/endikasyon bölümünü doldur"""
        icd_kodu = patient_data.get("icd_kodu", "")
        klinik_tani = patient_data.get("klinik_tani", "")
        
        if template_type == "fdg_pet_ct":
            indication = f"ICD: {icd_kodu} - {klinik_tani}. FDG PET/BT ile evreleme ve tedavi yanıtı değerlendirmesi."
        elif template_type == "psma_pet_ct":
            indication = f"ICD: {icd_kodu} - {klinik_tani}. PSMA PET/BT ile biyokimyasal rekürrens değerlendirmesi."
        elif template_type == "dotatate_pet_ct":
            indication = f"ICD: {icd_kodu} - {klinik_tani}. DOTATATE PET/BT ile NET evreleme ve takip."
        else:
            indication = f"ICD: {icd_kodu} - {klinik_tani}"
        
        return {
            "icd_kodu": icd_kodu,
            "klinik_tani": klinik_tani,
            "endikasyon": indication,
            "oncelik": patient_data.get("oncelik", "Rutin")
        }
    
    def _fill_methodology(self, template_type: str, patient_data: Dict) -> Dict:
        """Yöntem bölümünü doldur"""
        if template_type == "fdg_pet_ct":
            method = "FDG PET/BT incelemesi - Standart protokol uygulanmıştır"
            tracer = "F-18 FDG"
        elif template_type == "psma_pet_ct":
            method = "PSMA PET/BT incelemesi - Prostat spesifik membran antijeni görüntülemesi"
            tracer = "Ga-68 PSMA"
        elif template_type == "dotatate_pet_ct":
            method = "DOTATATE PET/BT incelemesi - Somatostatin reseptör görüntülemesi"
            tracer = "Ga-68 DOTATATE"
        else:
            method = "PET/BT incelemesi"
            tracer = "Bilinmiyor"
        
        return {
            "yontem": method,
            "tracer": tracer,
            "injection_dose": patient_data.get("petct", {}).get("injected_dose_MBq", "Bilinmiyor"),
            "uptake_time": patient_data.get("petct", {}).get("uptake_time_min", "Bilinmiyor"),
            "suv_scale": patient_data.get("petct", {}).get("suv_scale", "BW")
        }
    
    def _fill_findings(self, template_type: str, ai_analysis: Dict, 
                       user_preferences: Dict) -> Dict:
        """Bulgular bölümünü doldur"""
        findings = {}
        
        # AI analiz sonuçlarını kullan
        if "radiomics" in ai_analysis:
            radiomics = ai_analysis["radiomics"]
            
            # SUV değerleri
            suv_max = radiomics.get("suv_max", 0)
            suv_mean = radiomics.get("suv_mean", 0)
            
            # Risk değerlendirmesi
            if suv_max > 8.0:
                risk_level = "Çok Yüksek"
                finding_text = "Çok yüksek SUVmax değeri ile malignite şüphesi"
            elif suv_max > 5.0:
                risk_level = "Yüksek"
                finding_text = "Yüksek SUVmax değeri ile malignite şüphesi"
            elif suv_max > 2.5:
                risk_level = "Orta"
                finding_text = "Orta düzeyde metabolik aktivite artışı"
            else:
                risk_level = "Düşük"
                finding_text = "Normal metabolik aktivite"
            
            findings["risk_degerlendirmesi"] = {
                "risk_level": risk_level,
                "suv_max": suv_max,
                "suv_mean": suv_mean,
                "yorum": finding_text
            }
        
        # Anatomik bölge bulguları
        if template_type == "fdg_pet_ct":
            findings["anatomik_bulgular"] = self._get_anatomical_findings_fdg(ai_analysis)
        elif template_type == "psma_pet_ct":
            findings["anatomik_bulgular"] = self._get_anatomical_findings_psma(ai_analysis)
        elif template_type == "dotatate_pet_ct":
            findings["anatomik_bulgular"] = self._get_anatomical_findings_dotatate(ai_analysis)
        
        # Kullanıcı tercihlerine göre varyasyon seç
        if user_preferences.get("auto_variations", True):
            findings["otomatik_varyasyon"] = self._select_automatic_variation(ai_analysis)
        
        return findings
    
    def _get_anatomical_findings_fdg(self, ai_analysis: Dict) -> Dict:
        """FDG PET/BT anatomik bulguları"""
        findings = {}
        
        # Segmentasyon sonuçları
        if "segmentation" in ai_analysis:
            seg = ai_analysis["segmentation"]
            volume_ml = seg.get("volume_ml", 0)
            
            if volume_ml > 50:
                findings["toraks"] = "Büyük lezyon - toraks bölgesinde dominant tutulum"
            elif volume_ml > 20:
                findings["abdomen"] = "Orta boyut lezyon - abdominal bölgede tutulum"
            else:
                findings["pelvis"] = "Küçük lezyon - pelvik bölgede minimal tutulum"
        
        return findings
    
    def _get_anatomical_findings_psma(self, ai_analysis: Dict) -> Dict:
        """PSMA PET/BT anatomik bulguları"""
        findings = {
            "prostat": "Prostat lojunda PSMA tutulumu değerlendirildi",
            "lenf_nodu": "Pelvik ve retroperitoneal lenf nodları incelendi",
            "kemik": "Kemik metastazları değerlendirildi"
        }
        return findings
    
    def _get_anatomical_findings_dotatate(self, ai_analysis: Dict) -> Dict:
        """DOTATATE PET/BT anatomik bulguları"""
        findings = {
            "primer": "Primer tümör lokalizasyonu değerlendirildi",
            "hepatik": "Hepatik metastazlar incelendi",
            "lenf_nodu": "Lenf nodu metastazları değerlendirildi"
        }
        return findings
    
    def _select_automatic_variation(self, ai_analysis: Dict) -> str:
        """Otomatik varyasyon seç"""
        if "radiomics" in ai_analysis:
            suv_max = ai_analysis["radiomics"].get("suv_max", 0)
            
            if suv_max > 5.0:
                return self.variations["bulgular_varyasyonlari"]["fokal_artis"][0]
            elif suv_max > 2.5:
                return self.variations["bulgular_varyasyonlari"]["yaygin_artis"][0]
            else:
                return self.variations["bulgular_varyasyonlari"]["normal"][0]
        
        return self.variations["bulgular_varyasyonlari"]["normal"][0]
    
    def _fill_suvmax_table(self, ai_analysis: Dict) -> Dict:
        """SUVmax tablosu bölümünü doldur"""
        if "radiomics" not in ai_analysis:
            return {"error": "AI analiz sonuçları bulunamadı"}
        
        radiomics = ai_analysis["radiomics"]
        
        return {
            "suv_values": {
                "suv_max": radiomics.get("suv_max", 0),
                "suv_mean": radiomics.get("suv_mean", 0),
                "suv_min": radiomics.get("min", 0),
                "suv_std": radiomics.get("std", 0)
            },
            "texture_features": {
                "entropy": radiomics.get("texture_features", {}).get("entropy", 0),
                "energy": radiomics.get("texture_features", {}).get("energy", 0),
                "contrast": radiomics.get("texture_features", {}).get("contrast", 0)
            },
            "volume_info": {
                "volume_ml": ai_analysis.get("segmentation", {}).get("volume_ml", 0),
                "dice_score": ai_analysis.get("segmentation", {}).get("dice_score", 0)
            }
        }
    
    def _fill_conclusion(self, ai_analysis: Dict, user_preferences: Dict) -> Dict:
        """Sonuç bölümünü doldur"""
        if "clinical_analysis" not in ai_analysis:
            return {"error": "Klinik analiz sonuçları bulunamadı"}
        
        clinical = ai_analysis["clinical_analysis"]
        
        conclusion = {
            "risk_level": clinical.get("risk_level", "Bilinmiyor"),
            "prognosis": clinical.get("prognosis", "Bilinmiyor"),
            "recommendations": clinical.get("recommendations", []),
            "confidence_score": ai_analysis.get("confidence_score", 0)
        }
        
        # Kullanıcı tercihlerine göre varyasyon seç
        if user_preferences.get("auto_conclusion_variations", True):
            conclusion["otomatik_yorum"] = self._select_conclusion_variation(ai_analysis)
        
        return conclusion
    
    def _select_conclusion_variation(self, ai_analysis: Dict) -> str:
        """Sonuç varyasyonu seç"""
        if "clinical_analysis" in ai_analysis:
            risk_level = ai_analysis["clinical_analysis"].get("risk_level", "Low")
            
            if risk_level == "Very High":
                return self.variations["sonuc_varyasyonlari"]["progresyon"][0]
            elif risk_level == "High":
                return self.variations["sonuc_varyasyonlari"]["tedavi_yanit"][1]
            else:
                return self.variations["sonuc_varyasyonlari"]["stabil"][0]
        
        return self.variations["sonuc_varyasyonlari"]["stabil"][0]
    
    def _fill_additional_recommendations(self, ai_analysis: Dict) -> Dict:
        """Ek öneriler bölümünü doldur"""
        if "clinical_analysis" not in ai_analysis:
            return {"recommendations": ["AI analiz sonuçları bekleniyor"]}
        
        clinical = ai_analysis["clinical_analysis"]
        recommendations = clinical.get("recommendations", [])
        
        # Literatür referansları
        literature_refs = clinical.get("literature_references", [])
        
        return {
            "ai_recommendations": recommendations,
            "literature_support": literature_refs,
            "additional_notes": "Bu öneriler AI analizi ve literatür taraması sonucunda üretilmiştir"
        }
    
    def get_template_info(self, template_type: str) -> Dict:
        """Şablon bilgilerini getir"""
        if template_type not in self.templates:
            return {"error": "Şablon bulunamadı"}
        
        return self.templates[template_type]
    
    def list_available_templates(self) -> List[str]:
        """Mevcut şablonları listele"""
        return list(self.templates.keys())
    
    def export_report_json(self, report: Dict, filename: str = None) -> str:
        """Raporu JSON formatında export et"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tsnm_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filename

# Test fonksiyonu
def test_tsnm_templates():
    """TSNM şablonlarını test et"""
    manager = TSNMTemplateManager()
    
    print("🧪 TSNM Şablon Testi Başlıyor...")
    
    # Mevcut şablonları listele
    templates = manager.list_available_templates()
    print(f"✅ Mevcut şablonlar: {templates}")
    
    # Test hasta verisi
    test_patient = {
        "hasta_no": "TEST001",
        "yas": 65,
        "cinsiyet": "Erkek",
        "icd_kodu": "C61.9",
        "klinik_tani": "Prostat kanseri",
        "oncelik": "Yüksek",
        "study_date": "2024-01-15",
        "patient_hash": "abc123def456",
        "petct": {
            "injected_dose_MBq": 185,
            "uptake_time_min": 60,
            "suv_scale": "BW"
        }
    }
    
    # Test AI analiz verisi
    test_ai_analysis = {
        "radiomics": {
            "suv_max": 7.8,
            "suv_mean": 4.2,
            "min": 0.1,
            "std": 2.1,
            "texture_features": {
                "entropy": 3.45,
                "energy": 0.12,
                "contrast": 2.1
            }
        },
        "segmentation": {
            "volume_ml": 45.2,
            "dice_score": 0.87
        },
        "clinical_analysis": {
            "risk_level": "High",
            "prognosis": "Intermediate",
            "recommendations": [
                "Biopsy recommended",
                "Follow-up in 1 month"
            ],
            "literature_references": [
                "NCCN Guidelines v2.2024",
                "ESMO Clinical Practice Guidelines"
            ]
        },
        "confidence_score": 0.89
    }
    
    # Test kullanıcı tercihleri
    test_user_preferences = {
        "auto_variations": True,
        "auto_conclusion_variations": True
    }
    
    # PSMA PET/CT raporu oluştur
    print("\n📊 PSMA PET/CT Raporu Oluşturuluyor...")
    psma_report = manager.generate_report(
        "psma_pet_ct", test_patient, test_ai_analysis, test_user_preferences
    )
    
    print(f"✅ Rapor oluşturuldu: {len(psma_report['sections'])} bölüm")
    
    # JSON export
    filename = manager.export_report_json(psma_report)
    print(f"💾 Rapor export edildi: {filename}")
    
    print("\n🎉 TSNM Şablon Testi Tamamlandı!")

if __name__ == "__main__":
    test_tsnm_templates()


