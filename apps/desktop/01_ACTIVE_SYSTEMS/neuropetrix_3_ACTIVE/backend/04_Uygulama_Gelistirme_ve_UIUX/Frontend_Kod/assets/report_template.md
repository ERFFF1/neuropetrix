# PET/CT Raporu

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
*NeuroPETrix AI Sistemi ile desteklenmiştir.*


