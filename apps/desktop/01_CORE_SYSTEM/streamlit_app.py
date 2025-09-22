import streamlit as st
import sys
import os
from pathlib import Path

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="NeuroPETRIX v3.0 - Complete AI System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ana başlık
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 2rem;">
    <h1 style="margin: 0; font-size: 3rem;">🧠 NeuroPETRIX v3.0</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem;">Complete AI Clinical Decision Support System</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">Birleşik Sistem - Eski + Yeni + Gelişmiş Özellikler</p>
</div>
""", unsafe_allow_html=True)

# Sistem durumu
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Sistem Durumu", "✅ Aktif", "Çalışıyor")
    
with col2:
    st.metric("Entegrasyon", "✅ Tamamlandı", "Eski + Yeni")
    
with col3:
    st.metric("AI Modelleri", "✅ Hazır", "MONAI + GPT4All")
    
with col4:
    st.metric("API Endpoints", "✅ Aktif", "31 Router")

# Ana içerik
st.markdown("## 🎯 Sistem Özellikleri")

# Özellikler grid
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔬 Klinik Özellikler
    - **DICOM Görüntüleme**: Gelişmiş DICOM analizi
    - **SUV Trend Analizi**: PERCIST ve Deauville kriterleri
    - **PICO Otomasyonu**: Kanıta dayalı tıp
    - **GRADE Değerlendirme**: Kanıt kalitesi analizi
    - **TSNM Raporları**: Standart rapor üretimi
    - **Klinik Workflow**: 8 adımlı süreç
    - **Gemini AI Studio**: Gelişmiş AI analizi
    - **Multimodal Fusion**: Çoklu veri entegrasyonu
    """)

with col2:
    st.markdown("""
    ### 🤖 AI ve Teknoloji
    - **MONAI Engine**: Medical image analysis
    - **GPT4All**: Local LLM
    - **Whisper Engine**: Speech-to-text
    - **PyRadiomics**: Radiomic features
    - **HBYS Entegrasyonu**: HL7 FHIR
    - **Real-time Monitoring**: Sistem takibi
    - **Desktop Runner**: MONAI + PyRadiomics Pipeline
    - **Evidence Panel**: Literatür ve kanıt arama
    """)

# Sayfa seçimi
st.markdown("## 📋 Sistem Modülleri")

# Sayfa butonları
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏥 Klinik Karar Destek", use_container_width=True):
        st.switch_page("pages/01_Clinical_Decision_Support.py")
    
    if st.button("🖼️ Görüntü Analizi", use_container_width=True):
        st.switch_page("pages/02_Image_Analysis.py")

with col2:
    if st.button("📊 Raporlar & Analytics", use_container_width=True):
        st.switch_page("pages/03_Reports_Analytics.py")
    
    if st.button("⚙️ Sistem Ayarları", use_container_width=True):
        st.switch_page("pages/04_System_Settings.py")

with col3:
    if st.button("🔬 AI Engines", use_container_width=True):
        st.switch_page("pages/05_Advanced_Features.py")
    
    if st.button("📈 Performans Monitörü", use_container_width=True):
        st.info("Performans monitörü aktif - Sistem takibi")

# Sistem bilgileri
st.markdown("## 📊 Sistem Bilgileri")

# Sistem durumu
system_info = {
    "Python Versiyonu": sys.version.split()[0],
    "Streamlit Versiyonu": st.__version__,
    "Çalışma Dizini": os.getcwd(),
    "Sistem Platformu": os.name,
    "Virtual Environment": "✅ Aktif" if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else "❌ Pasif"
}

for key, value in system_info.items():
    st.text(f"{key}: {value}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧠 NeuroPETRIX v3.0 - Complete AI Clinical Decision Support System</p>
    <p>Geliştirici: NeuroPETRIX Team | Versiyon: 3.0.0 | Tarih: 2025</p>
</div>
""", unsafe_allow_html=True)
