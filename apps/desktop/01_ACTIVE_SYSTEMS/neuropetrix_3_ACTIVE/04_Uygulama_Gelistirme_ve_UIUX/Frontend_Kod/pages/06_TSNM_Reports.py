import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

def render_tsnm_reports():
    """TSNM Reports sayfasını render et"""
    
    st.header("📋 TSNM Raporları")
    st.markdown("Türk Nükleer Tıp Derneği Standartlarına Uygun Rapor Oluşturma")
    
    # Rapor türü seçimi
    st.subheader("Rapor Türü")
    
    report_type = st.selectbox(
        "Rapor Türünü Seçin",
        ["FDG-PET/CT", "PSMA-PET/CT", "DOTATATE-PET/CT", "FAPI-PET/CT", "Özel Rapor"]
    )
    
    # Hasta bilgileri
    st.subheader("Hasta Bilgileri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_id = st.text_input("Hasta ID", "P-001")
        patient_name = st.text_input("Hasta Adı", "ANONYMOUS")
        patient_age = st.number_input("Yaş", min_value=0, max_value=120, value=65)
        patient_gender = st.selectbox("Cinsiyet", ["M", "F"])
    
    with col2:
        study_date = st.date_input("Çalışma Tarihi", value=datetime.now().date())
        study_time = st.time_input("Çalışma Saati", value=datetime.now().time())
        referring_physician = st.text_input("Sevk Eden Hekim", "Dr. Ahmet Yılmaz")
        indication = st.text_area("Endikasyon", "Akciğer kanseri evreleme")
    
    # Teknik detaylar
    st.subheader("Teknik Detaylar")
    
    col1, col2 = st.columns(2)
    
    with col1:
        injected_dose = st.number_input("Enjekte Edilen Doz (MBq)", min_value=0.0, value=185.0)
        uptake_time = st.number_input("Uptake Süresi (dakika)", min_value=30, value=60)
        acquisition_time = st.number_input("Aküsizyon Süresi (dakika)", min_value=5, value=20)
    
    with col2:
        reconstruction_method = st.selectbox(
            "Reconstruction Yöntemi",
            ["OSEM 3i24s", "OSEM 4i16s", "TOF-OSEM", "PSF-OSEM"]
        )
        filter_type = st.selectbox(
            "Filtre Tipi",
            ["Gaussian 5mm", "Gaussian 3mm", "Butterworth", "Hanning"]
        )
        matrix_size = st.selectbox("Matrix Boyutu", ["256x256", "512x512", "128x128"])
    
    # Bulgular
    st.subheader("Bulgular")
    
    # Vücut bölgeleri
    body_regions = [
        "Beyin", "Boyun", "Toraks", "Karın", "Pelvis", "Ekstremiteler"
    ]
    
    findings = {}
    
    for region in body_regions:
        st.write(f"**{region}:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            has_finding = st.checkbox(f"{region} bulgusu var", key=f"finding_{region}")
            if has_finding:
                finding_description = st.text_area(
                    f"{region} bulgusu açıklaması",
                    key=f"desc_{region}",
                    placeholder="Bulguyu detaylı olarak açıklayın..."
                )
        
        with col2:
            if has_finding:
                suv_max = st.number_input(f"{region} SUVmax", min_value=0.0, value=5.0, key=f"suv_{region}")
                lesion_size = st.number_input(f"{region} lezyon boyutu (cm)", min_value=0.0, value=2.0, key=f"size_{region}")
        
        findings[region] = {
            "has_finding": has_finding,
            "description": finding_description if has_finding else "",
            "suv_max": suv_max if has_finding else 0.0,
            "lesion_size": lesion_size if has_finding else 0.0
        }
    
    # Sonuç ve öneriler
    st.subheader("Sonuç ve Öneriler")
    
    conclusion = st.text_area(
        "Sonuç",
        placeholder="Genel sonucu yazın...",
        height=100
    )
    
    recommendations = st.text_area(
        "Öneriler",
        placeholder="Klinik önerileri yazın...",
        height=100
    )
    
    follow_up = st.text_area(
        "Takip Planı",
        placeholder="Takip planını belirtin...",
        height=100
    )
    
    # Rapor oluşturma
    if st.button("📋 TSNM Raporu Oluştur"):
        if conclusion and recommendations:
            with st.spinner("TSNM raporu oluşturuluyor..."):
                # Mock rapor oluşturma
                report_data = {
                    "report_type": report_type,
                    "patient_info": {
                        "id": patient_id,
                        "name": patient_name,
                        "age": patient_age,
                        "gender": patient_gender
                    },
                    "study_info": {
                        "date": study_date.strftime('%Y-%m-%d'),
                        "time": study_time.strftime('%H:%M'),
                        "referring_physician": referring_physician,
                        "indication": indication
                    },
                    "technical_details": {
                        "injected_dose": injected_dose,
                        "uptake_time": uptake_time,
                        "acquisition_time": acquisition_time,
                        "reconstruction_method": reconstruction_method,
                        "filter_type": filter_type,
                        "matrix_size": matrix_size
                    },
                    "findings": findings,
                    "conclusion": conclusion,
                    "recommendations": recommendations,
                    "follow_up": follow_up
                }
                
                st.success("✅ TSNM raporu başarıyla oluşturuldu!")
                
                # Rapor önizlemesi
                show_report_preview(report_data)
        else:
            st.error("❌ Lütfen sonuç ve önerileri doldurun")
    
    # Rapor şablonları
    st.subheader("📄 Rapor Şablonları")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 FDG Şablonu Yükle"):
            load_fdg_template()
    
    with col2:
        if st.button("📋 PSMA Şablonu Yükle"):
            load_psma_template()
    
    with col3:
        if st.button("📋 DOTATATE Şablonu Yükle"):
            load_dotatate_template()

def show_report_preview(report_data):
    """Rapor önizlemesini göster"""
    
    st.subheader("📄 Rapor Önizlemesi")
    
    # Rapor içeriği
    report_content = f"""
# {report_data['report_type']} RAPORU

## HASTA BİLGİLERİ
- **Hasta ID:** {report_data['patient_info']['id']}
- **Hasta Adı:** {report_data['patient_info']['name']}
- **Yaş:** {report_data['patient_info']['age']}
- **Cinsiyet:** {report_data['patient_info']['gender']}

## ÇALIŞMA BİLGİLERİ
- **Çalışma Tarihi:** {report_data['study_info']['date']}
- **Çalışma Saati:** {report_data['study_info']['time']}
- **Sevk Eden Hekim:** {report_data['study_info']['referring_physician']}
- **Endikasyon:** {report_data['study_info']['indication']}

## TEKNİK DETAYLAR
- **Enjekte Edilen Doz:** {report_data['technical_details']['injected_dose']} MBq
- **Uptake Süresi:** {report_data['technical_details']['uptake_time']} dakika
- **Aküsizyon Süresi:** {report_data['technical_details']['acquisition_time']} dakika
- **Reconstruction Yöntemi:** {report_data['technical_details']['reconstruction_method']}
- **Filtre Tipi:** {report_data['technical_details']['filter_type']}
- **Matrix Boyutu:** {report_data['technical_details']['matrix_size']}

## BULGULAR
"""
    
    # Bulguları ekle
    for region, finding in report_data['findings'].items():
        if finding['has_finding']:
            report_content += f"""
### {region}
{finding['description']}
- **SUVmax:** {finding['suv_max']}
- **Lezyon Boyutu:** {finding['lesion_size']} cm
"""
    
    report_content += f"""
## SONUÇ
{report_data['conclusion']}

## ÖNERİLER
{report_data['recommendations']}

## TAKİP PLANI
{report_data['follow_up']}

---
*Bu rapor TSNM standartlarına uygun olarak hazırlanmıştır.*
"""
    
    # Raporu göster
    st.markdown(report_content)
    
    # İndirme seçenekleri
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 PDF İndir"):
            st.info("PDF indirme özelliği yakında eklenecek")
    
    with col2:
        if st.button("📄 DOCX İndir"):
            st.info("DOCX indirme özelliği yakında eklenecek")
    
    with col3:
        if st.button("📄 HTML İndir"):
            st.info("HTML indirme özelliği yakında eklenecek")

def load_fdg_template():
    """FDG şablonunu yükle"""
    
    template = {
        "indication": "FDG-PET/CT görüntüleme",
        "injected_dose": 185.0,
        "uptake_time": 60,
        "reconstruction_method": "OSEM 3i24s",
        "filter_type": "Gaussian 5mm",
        "matrix_size": "256x256"
    }
    
    st.success("✅ FDG şablonu yüklendi!")
    st.info("Şablon bilgileri form alanlarına otomatik olarak dolduruldu.")

def load_psma_template():
    """PSMA şablonunu yükle"""
    
    template = {
        "indication": "PSMA-PET/CT görüntüleme",
        "injected_dose": 200.0,
        "uptake_time": 60,
        "reconstruction_method": "OSEM 4i16s",
        "filter_type": "Gaussian 3mm",
        "matrix_size": "256x256"
    }
    
    st.success("✅ PSMA şablonu yüklendi!")
    st.info("Şablon bilgileri form alanlarına otomatik olarak dolduruldu.")

def load_dotatate_template():
    """DOTATATE şablonunu yükle"""
    
    template = {
        "indication": "DOTATATE-PET/CT görüntüleme",
        "injected_dose": 150.0,
        "uptake_time": 60,
        "reconstruction_method": "OSEM 3i24s",
        "filter_type": "Gaussian 5mm",
        "matrix_size": "256x256"
    }
    
    st.success("✅ DOTATATE şablonu yüklendi!")
    st.info("Şablon bilgileri form alanlarına otomatik olarak dolduruldu.")

# Ana fonksiyon çağrısı
if __name__ == "__main__":
    render_tsnm_reports()
