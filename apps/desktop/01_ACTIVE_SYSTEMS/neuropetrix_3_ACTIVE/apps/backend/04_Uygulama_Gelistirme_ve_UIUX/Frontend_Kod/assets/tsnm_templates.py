# TSNM Templates for NeuroPETrix

TSNM_TEMPLATES = {
    "fdg": {
        "name": "FDG-PET/CT Raporu",
        "template": """
# FDG-PET/CT Raporu

## Hasta Bilgileri
- **Ad Soyad:** {{ patient.name }}
- **Yaş:** {{ patient.age }}
- **Cinsiyet:** {{ patient.gender }}
- **Hasta No:** {{ patient.id }}

## İndikasyon
{{ indication }}

## Teknik Bilgiler
- **Cihaz:** {{ device_model }}
- **FDG Dozu:** {{ fdg_dose_mbq }} MBq
- **Glikoz:** {{ glycemia_mgdl }} mg/dL
- **Açlık Süresi:** {{ fasting_hours }} saat
- **Uptake Süresi:** {{ uptake_time }}

## Bulgular

### Baş-Boyun
{{ head_neck_findings }}

### Toraks
{{ chest_findings }}

### Abdomen
{{ abdomen_findings }}

### Pelvis
{{ pelvis_findings }}

### Kemik Sistemi
{{ bone_findings }}

## SUV Değerleri
- **Lezyon SUVmax:** {{ lesion_suv_max }}
- **Lezyon SUVmean:** {{ lesion_suv_mean }}
- **Karaciğer SUVmean:** {{ liver_suv_mean }} (Referans)
- **Mediastinum SUVmean:** {{ mediastinum_suv_mean }} (Referans)

## Sonuç
{{ conclusion }}

## Öneriler
{{ recommendations }}

## Takip Planı
{{ follow_up_plan }}

---
*Rapor {{ timestamp }} tarihinde oluşturuldu.*
*TSNM Kılavuzlarına Uygun - NeuroPETrix AI Sistemi*
        """
    },
    
    "psma": {
        "name": "PSMA-PET/CT Raporu",
        "template": """
# PSMA-PET/CT Raporu

## Hasta Bilgileri
- **Ad Soyad:** {{ patient.name }}
- **Yaş:** {{ patient.age }}
- **Cinsiyet:** {{ patient.gender }}
- **Hasta No:** {{ patient.id }}

## İndikasyon
{{ indication }}

## Teknik Bilgiler
- **Cihaz:** {{ device_model }}
- **PSMA Dozu:** {{ psma_dose_mbq }} MBq
- **Glikoz:** {{ glycemia_mgdl }} mg/dL
- **Açlık Süresi:** {{ fasting_hours }} saat
- **Uptake Süresi:** {{ uptake_time }}

## Bulgular

### Prostat Bölgesi
{{ prostate_findings }}

### Lenf Nodları
{{ lymph_node_findings }}

### Kemik Metastazları
{{ bone_metastasis_findings }}

### Diğer Organlar
{{ other_organ_findings }}

## SUV Değerleri
- **Prostat SUVmax:** {{ prostate_suv_max }}
- **Lenf Nodu SUVmax:** {{ lymph_node_suv_max }}
- **Kemik SUVmax:** {{ bone_suv_max }}

## Sonuç
{{ conclusion }}

## Öneriler
{{ recommendations }}

## Takip Planı
{{ follow_up_plan }}

---
*Rapor {{ timestamp }} tarihinde oluşturuldu.*
*TSNM Kılavuzlarına Uygun - NeuroPETrix AI Sistemi*
        """
    },
    
    "dotatate": {
        "name": "DOTATATE-PET/CT Raporu",
        "template": """
# DOTATATE-PET/CT Raporu

## Hasta Bilgileri
- **Ad Soyad:** {{ patient.name }}
- **Yaş:** {{ patient.age }}
- **Cinsiyet:** {{ patient.gender }}
- **Hasta No:** {{ patient.id }}

## İndikasyon
{{ indication }}

## Teknik Bilgiler
- **Cihaz:** {{ device_model }}
- **DOTATATE Dozu:** {{ dotatate_dose_mbq }} MBq
- **Glikoz:** {{ glycemia_mgdl }} mg/dL
- **Açlık Süresi:** {{ fasting_hours }} saat
- **Uptake Süresi:** {{ uptake_time }}

## Bulgular

### Primer Tümör
{{ primary_tumor_findings }}

### Lenf Nodları
{{ lymph_node_findings }}

### Karaciğer Metastazları
{{ liver_metastasis_findings }}

### Kemik Metastazları
{{ bone_metastasis_findings }}

## SUV Değerleri
- **Primer Tümör SUVmax:** {{ primary_suv_max }}
- **Lenf Nodu SUVmax:** {{ lymph_node_suv_max }}
- **Karaciğer SUVmax:** {{ liver_suv_max }}

## Sonuç
{{ conclusion }}

## Öneriler
{{ recommendations }}

## Takip Planı
{{ follow_up_plan }}

---
*Rapor {{ timestamp }} tarihinde oluşturuldu.*
*TSNM Kılavuzlarına Uygun - NeuroPETrix AI Sistemi*
        """
    }
}

def get_tsnm_template(template_type: str) -> dict:
    """TSNM şablonunu getir"""
    return TSNM_TEMPLATES.get(template_type, TSNM_TEMPLATES["fdg"])

def render_tsnm_report(template_type: str, data: dict) -> str:
    """TSNM raporunu render et"""
    template = get_tsnm_template(template_type)
    
    # Basit template rendering (gerçek implementasyonda Jinja2 kullanılacak)
    report = template["template"]
    
    for key, value in data.items():
        placeholder = f"{{{{ {key} }}}}"
        report = report.replace(placeholder, str(value))
    
    return report


