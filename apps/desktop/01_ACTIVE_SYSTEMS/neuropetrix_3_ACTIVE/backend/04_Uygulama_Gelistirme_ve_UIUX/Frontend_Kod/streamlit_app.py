import streamlit as st
import requests
import json
from datetime import datetime

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="NeuroPETrix - Streamlit Interface",
    page_icon="🧠",
    layout="wide"
)

# Ana başlık
st.title("🧠 NeuroPETrix - AI Destekli PET/CT Analizi")
st.markdown("---")

# Sidebar
st.sidebar.title("Navigasyon")
page = st.sidebar.selectbox(
    "Sayfa Seçin",
    ["Dashboard", "PICO Otomatikleştirme", "Multimodal Füzyon", "Klinik Geri Bildirim", "Uyum Paneli"]
)

if page == "Dashboard":
    st.header("📊 Dashboard")
    
    # Sistem durumu
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Toplam Vaka", "1,247", "+12")
    
    with col2:
        st.metric("Tamamlanan Rapor", "892", "+8")
    
    with col3:
        st.metric("PICO Analizi", "156", "+5")
    
    with col4:
        st.metric("Füzyon İşlemi", "89", "+3")
    
    # Son aktiviteler
    st.subheader("Son Aktiviteler")
    activities = [
        {"action": "Yeni vaka oluşturuldu", "time": "2 dakika önce", "type": "create"},
        {"action": "PET raporu tamamlandı", "time": "15 dakika önce", "type": "complete"},
        {"action": "SUV analizi güncellendi", "time": "1 saat önce", "type": "update"},
        {"action": "Evidence araması yapıldı", "time": "2 saat önce", "type": "search"}
    ]
    
    for activity in activities:
        st.write(f"• {activity['action']} - {activity['time']}")

elif page == "PICO Otomatikleştirme":
    st.header("🔍 PICO Otomatikleştirme")
    
    # Hasta bilgileri
    st.subheader("Hasta Bilgileri")
    col1, col2 = st.columns(2)
    
    with col1:
        patient_name = st.text_input("Hasta Adı", "Ahmet Yılmaz")
        patient_age = st.number_input("Yaş", min_value=0, max_value=120, value=65)
    
    with col2:
        patient_gender = st.selectbox("Cinsiyet", ["M", "F"])
        diagnosis = st.text_input("Tanı", "Lung cancer")
    
    # Klinik bağlam
    clinical_context = st.text_area(
        "Klinik Bağlam",
        "Suspicious lung nodule on CT scan, need for PET/CT evaluation"
    )
    
    if st.button("PICO Soru Oluştur"):
        with st.spinner("PICO soru oluşturuluyor..."):
            # Mock PICO soru
            pico_question = {
                "population": f"{patient_age} yaşında {patient_gender} hasta",
                "intervention": "FDG-PET/CT görüntüleme",
                "comparison": "Standart görüntüleme yöntemleri",
                "outcome": "Tanısal doğruluk ve tedavi planlaması"
            }
            
            st.success("PICO Soru Oluşturuldu!")
            st.json(pico_question)

elif page == "Multimodal Füzyon":
    st.header("🔗 Multimodal Füzyon")
    
    # Dosya yükleme
    st.subheader("Veri Yükleme")
    
    uploaded_files = st.file_uploader(
        "DICOM Dosyaları Yükle",
        type=['dcm'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} dosya yüklendi")
    
    # Klinik veriler
    st.subheader("Klinik Veriler")
    col1, col2 = st.columns(2)
    
    with col1:
        glucose = st.number_input("Glikoz (mg/dL)", value=110.0)
        creatinine = st.number_input("Kreatinin (mg/dL)", value=0.9)
    
    with col2:
        egfr = st.number_input("eGFR (mL/min)", value=90)
        psa = st.number_input("PSA (ng/mL)", value=0.0)
    
    if st.button("Füzyon İşlemini Başlat"):
        with st.spinner("Multimodal füzyon işleniyor..."):
            # Mock füzyon sonucu
            fusion_result = {
                "integrated_analysis": {
                    "diagnosis": "Lung cancer, stage IIIA",
                    "confidence": 0.87,
                    "key_findings": [
                        "SUVmax 12.5 in right upper lobe",
                        "Lymph node involvement detected"
                    ]
                }
            }
            
            st.success("Füzyon tamamlandı!")
            st.json(fusion_result)

elif page == "Klinik Geri Bildirim":
    st.header("💬 Klinik Geri Bildirim")
    
    # Mevcut öneri
    st.subheader("Mevcut AI Önerisi")
    st.info("""
    **Öneri:** Biyopsi ile histopatolojik doğrulama önerilir.
    **Güven:** 87%
    **Kanıt Seviyesi:** 1A
    """)
    
    # Geri bildirim formu
    st.subheader("Geri Bildirim")
    
    feedback_type = st.selectbox(
        "Geri Bildirim Türü",
        ["supportive_positive", "hard_negative", "neutral"]
    )
    
    feedback_details = st.text_area(
        "Geri Bildirim Detayları",
        "AI önerisi klinik durumla uyumlu ve yararlı."
    )
    
    confidence_level = st.slider(
        "Güven Seviyesi",
        min_value=1,
        max_value=10,
        value=8
    )
    
    if st.button("Geri Bildirim Gönder"):
        st.success("Geri bildirim başarıyla gönderildi!")

elif page == "Uyum Paneli":
    st.header("⚖️ Uyum Paneli")
    
    # Veri gizliliği
    st.subheader("Veri Gizliliği")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Anonimleştirme", "Tam", "✅")
        st.metric("Maskeleme", "Uygulandı", "✅")
    
    with col2:
        st.metric("Şifreleme", "Yüksek", "✅")
        st.metric("Saklama Süresi", "7 yıl", "📅")
    
    # Regülasyon uyumluluğu
    st.subheader("Regülasyon Uyumluluğu")
    
    compliance_data = {
        "KVKK": "✅ Uyumlu",
        "HIPAA": "✅ Uyumlu", 
        "GDPR": "✅ Uyumlu",
        "CE-MDR": "⏳ Beklemede",
        "FDA 510k": "⏳ Beklemede"
    }
    
    for regulation, status in compliance_data.items():
        st.write(f"**{regulation}:** {status}")
    
    # Denetim izi
    st.subheader("Denetim İzi")
    audit_log = [
        {"user": "radiologist_001", "action": "View case", "time": "2024-01-15T09:00:00Z"},
        {"user": "radiologist_001", "action": "Generate report", "time": "2024-01-15T09:30:00Z"}
    ]
    
    for log in audit_log:
        st.write(f"• {log['user']} - {log['action']} - {log['time']}")

# Footer
st.markdown("---")
st.markdown("*NeuroPETrix v1.0.0 - AI Destekli PET/CT Analizi Platformu*")


