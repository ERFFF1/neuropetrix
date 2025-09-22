import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import time

st.set_page_config(
    page_title="Image Analysis - NeuroPETrix",
    page_icon="🖼️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .analysis-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .analysis-section {
        background: #e8f5e8;
        border: 2px solid #28a745;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="analysis-header">
    <h1>🖼️ Image Analysis</h1>
    <p style="font-size: 1.2rem; margin: 0;">DICOM Görüntü Analizi ve SUV Trend Analizi</p>
    <p style="font-size: 1rem; margin: 0.5rem 0 0 0;">MONAI + PyRadiomics entegrasyonu</p>
</div>
""", unsafe_allow_html=True)

# Ana içerik
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📁 DICOM Görüntü Yükleme")
    
    # Dosya yükleme
    uploaded_files = st.file_uploader(
        "DICOM dosyalarını yükleyin:",
        type=['dcm', 'dicom'],
        accept_multiple_files=True,
        help="DICOM dosyalarını seçin veya sürükleyip bırakın"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} DICOM dosyası yüklendi!")
        
        # DICOM analiz butonu
        if st.button("🔬 DICOM Analizi Başlat", type="primary"):
            with st.spinner("DICOM dosyaları analiz ediliyor..."):
                # Mock DICOM analiz sonuçları
                analysis_results = {
                    "patient_id": "P001",
                    "study_date": "2025-09-12",
                    "modality": "PT",
                    "body_part": "CHEST",
                    "contrast": "FDG",
                    "dose": "370 MBq",
                    "acquisition_time": "45 min",
                    "quality": "Excellent"
                }
                
                st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
                st.markdown("### 📊 DICOM Analiz Sonuçları")
                
                for key, value in analysis_results.items():
                    st.text(f"{key.replace('_', ' ').title()}: {value}")
                
                st.success("✅ DICOM analizi tamamlandı!")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Mock DICOM verileri
    st.markdown("### 📊 Örnek DICOM Verileri")
    
    # DICOM metadata tablosu
    dicom_data = pd.DataFrame({
        "Tag": ["(0010,0010)", "(0010,0020)", "(0008,0020)", "(0008,0060)", "(0018,1074)"],
        "Description": ["Patient Name", "Patient ID", "Study Date", "Modality", "Radiopharmaceutical"],
        "Value": ["Ahmet Yılmaz", "P001", "2025-09-12", "PT", "FDG"]
    })
    
    st.dataframe(dicom_data, use_container_width=True)

with col2:
    st.markdown("### 📈 SUV Trend Analizi")
    
    # SUV trend verileri
    dates = pd.date_range(start='2025-01-01', end='2025-09-12', freq='M')
    suv_values = np.random.normal(5.2, 0.8, len(dates))
    
    # SUV trend grafiği
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=suv_values,
        mode='lines+markers',
        name='SUVmax',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="SUV Trend Analizi",
        xaxis_title="Tarih",
        yaxis_title="SUVmax",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # SUV metrikleri
    col2_1, col2_2 = st.columns(2)
    
    with col2_1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("İlk SUVmax", "5.8", "0.3")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Son SUVmax", "4.2", "-0.8")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2_2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Ortalama SUV", "5.1", "0.1")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Değişim %", "-27.6%", "-5.2%")
        st.markdown('</div>', unsafe_allow_html=True)

# Alt kısım - Gelişmiş analiz
st.markdown("### 🔬 Gelişmiş Görüntü Analizi")

col3, col4, col5 = st.columns(3)

with col3:
    st.markdown("#### 🎯 Segmentasyon")
    
    # Segmentasyon seçenekleri
    segmentation_method = st.selectbox(
        "Segmentasyon Yöntemi:",
        ["Otomatik", "Manuel", "AI Destekli"],
        help="Görüntü segmentasyon yöntemini seçin"
    )
    
    if st.button("🎯 Segmentasyon Başlat"):
        with st.spinner("Segmentasyon işlemi yapılıyor..."):
            time.sleep(2)
            st.success("✅ Segmentasyon tamamlandı!")
            
            # Mock segmentasyon sonuçları
            st.markdown("**Segmentasyon Sonuçları:**")
            st.text("Tespit edilen lezyon sayısı: 3")
            st.text("En büyük lezyon boyutu: 2.4 cm")
            st.text("Segmentasyon kalitesi: %95")

with col4:
    st.markdown("#### 📊 Radiomics")
    
    # Radiomics analizi
    if st.button("📊 Radiomics Analizi"):
        with st.spinner("Radiomics özellikleri çıkarılıyor..."):
            time.sleep(2)
            st.success("✅ Radiomics analizi tamamlandı!")
            
            # Mock radiomics sonuçları
            radiomics_features = {
                "Shape Features": 14,
                "First Order": 18,
                "GLCM": 24,
                "GLRLM": 16,
                "GLSZM": 16,
                "GLDM": 14
            }
            
            for feature, count in radiomics_features.items():
                st.text(f"{feature}: {count} özellik")

with col5:
    st.markdown("#### 🤖 AI Analizi")
    
    # AI analizi
    if st.button("🤖 AI Analizi"):
        with st.spinner("AI modeli çalıştırılıyor..."):
            time.sleep(3)
            st.success("✅ AI analizi tamamlandı!")
            
            # Mock AI sonuçları
            st.markdown("**AI Analiz Sonuçları:**")
            st.text("Malignite olasılığı: %78")
            st.text("Tedavi yanıtı: İyi")
            st.text("Prognoz: Orta")
            st.text("Önerilen takip: 3 ay")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🖼️ Image Analysis - NeuroPETRIX v3.0</p>
    <p>DICOM görüntü analizi ve SUV trend analizi</p>
</div>
""", unsafe_allow_html=True)
