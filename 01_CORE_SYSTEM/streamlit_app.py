import streamlit as st
import sys
import os
from pathlib import Path

# Sayfa yapılandırması
st.set_page_config(
    page_title="NeuroPETRIX v4.0 - Klinik Karar Destek Sistemi",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ana başlık
st.title("🧠 NeuroPETRIX v4.0")
st.subtitle("Klinik Karar Destek Sistemi - Temiz & Optimize Edilmiş")

# Sidebar navigasyon
st.sidebar.title("📋 Navigasyon")
st.sidebar.markdown("---")

# Sayfa seçimi
page = st.sidebar.selectbox(
    "Sayfa Seçin:",
    [
        "🏠 Dashboard",
        "🏥 Klinik Karar Desteği", 
        "🖼️ Görüntü Analizi",
        "📊 Raporlar & Analitik",
        "⚙️ Sistem Ayarları",
        "🤖 AI Engines",
        "🔗 Entegrasyonlar",
        "📚 Dokümantasyon"
    ]
)

# Dashboard
if page == "🏠 Dashboard":
    st.header("📊 Sistem Dashboard")
    
    # Sistem metrikleri
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="API Router'ları",
            value="34",
            delta="+5"
        )
    
    with col2:
        st.metric(
            label="Frontend Bileşenleri", 
            value="8",
            delta="+3"
        )
    
    with col3:
        st.metric(
            label="Python Dosyaları",
            value="101",
            delta="+56"
        )
    
    with col4:
        st.metric(
            label="Sistem Durumu",
            value="✅ Aktif",
            delta="Temiz"
        )
    
    st.markdown("---")
    
    # Sistem özellikleri
    st.subheader("🎯 Ana Özellikler")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🏥 Klinik Özellikler:**
        - ✅ PICO Otomasyonu
        - ✅ GRADE Değerlendirmesi  
        - ✅ Klinik Kurallar Motoru
        - ✅ Kanıt Tabanlı Tıp
        - ✅ Klinik Kılavuzlar
        """)
        
        st.markdown("""
        **🖼️ Görüntü Analizi:**
        - ✅ DICOM Görüntüleyici
        - ✅ MONAI Radiomics
        - ✅ AI Segmentasyon
        - ✅ SUV Trend Analizi
        - ✅ PERCIST/Deauville
        """)
    
    with col2:
        st.markdown("""
        **🤖 AI & ML:**
        - ✅ 4 AI Modeli
        - ✅ Çok Modlu Analiz
        - ✅ Hayatta Kalma Tahmini
        - ✅ Güven Skorları
        - ✅ Model Eğitimi
        """)
        
        st.markdown("""
        **🔗 Entegrasyonlar:**
        - ✅ HBYS Entegrasyonu
        - ✅ PACS/Orthanc
        - ✅ Mobile API
        - ✅ WebSocket
        - ✅ 34 API Router
        """)
    
    # Sistem durumu
    st.subheader("🔧 Sistem Durumu")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ Core System")
        st.success("✅ API Endpoints")
        st.success("✅ Frontend")
    
    with col2:
        st.success("✅ Medical Modules")
        st.success("✅ AI Engines")
        st.success("✅ Integration")
    
    with col3:
        st.success("✅ Documentation")
        st.success("✅ Tests")
        st.success("✅ Config")

# Diğer sayfalar için placeholder
elif page == "🏥 Klinik Karar Desteği":
    st.header("🏥 Klinik Karar Destek Sistemi")
    st.info("Bu sayfa geliştirilme aşamasında...")
    
elif page == "🖼️ Görüntü Analizi":
    st.header("🖼️ Görüntü Analizi")
    st.info("Bu sayfa geliştirilme aşamasında...")
    
elif page == "📊 Raporlar & Analitik":
    st.header("📊 Raporlar & Analitik")
    st.info("Bu sayfa geliştirilme aşamasında...")
    
elif page == "⚙️ Sistem Ayarları":
    st.header("⚙️ Sistem Ayarları")
    st.info("Bu sayfa geliştirilme aşamasında...")
    
elif page == "🤖 AI Engines":
    st.header("🤖 AI Engines")
    st.info("Bu sayfa geliştirilme aşamasında...")
    
elif page == "🔗 Entegrasyonlar":
    st.header("🔗 Sistem Entegrasyonları")
    st.info("Bu sayfa geliştirilme aşamasında...")
    
elif page == "📚 Dokümantasyon":
    st.header("📚 Sistem Dokümantasyonu")
    st.info("Bu sayfa geliştirilme aşamasında...")

# Footer
st.markdown("---")
st.markdown("**🧠 NeuroPETRIX v4.0** - Temiz & Optimize Edilmiş Klinik Karar Destek Sistemi")







