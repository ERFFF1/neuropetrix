import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import numpy as np

st.set_page_config(
    page_title="Reports & Analytics - NeuroPETrix",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .reports-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .report-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .report-card:hover {
        background: #e3f2fd;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .performance-metric {
        background: #e8f5e8;
        border: 2px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="reports-header">
    <h1>📊 Reports & Analytics</h1>
    <p style="font-size: 1.2rem; margin: 0;">Rapor Üretimi ve Sistem Analitiği</p>
    <p style="font-size: 1rem; margin: 0.5rem 0 0 0;">TSNM raporları ve performans monitörü</p>
</div>
""", unsafe_allow_html=True)

# Ana içerik
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📋 Rapor Üretimi")
    
    # Rapor türü seçimi
    report_type = st.selectbox(
        "Rapor Türü:",
        ["TSNM Kısa Rapor", "TSNM Detaylı Rapor", "Araştırma Raporu", "Klinik Rapor"],
        help="Üretilecek rapor türünü seçin"
    )
    
    # Hasta bilgileri
    col1_1, col1_2 = st.columns(2)
    
    with col1_1:
        patient_name = st.text_input("Hasta Adı:", "Ahmet Yılmaz")
        patient_id = st.text_input("Hasta ID:", "P001")
        study_date = st.date_input("Çalışma Tarihi:", datetime.now().date())
    
    with col1_2:
        age = st.number_input("Yaş:", min_value=0, max_value=120, value=65)
        gender = st.selectbox("Cinsiyet:", ["Erkek", "Kadın"])
        diagnosis = st.text_input("Tanı:", "Akciğer kanseri şüphesi")
    
    # SUV analiz verileri
    st.markdown("### 📈 SUV Analiz Verileri")
    
    # Mock SUV verileri
    suv_data = {
        "Lezyon": ["L001", "L002", "L003"],
        "İlk SUVmax": [5.8, 4.2, 6.1],
        "Son SUVmax": [4.2, 3.1, 4.8],
        "Değişim %": [-27.6, -26.2, -21.3],
        "Trend": ["Azalma", "Azalma", "Azalma"]
    }
    
    suv_df = pd.DataFrame(suv_data)
    st.dataframe(suv_df, use_container_width=True)
    
    # Rapor üret butonu
    if st.button("📋 Rapor Üret", type="primary"):
        with st.spinner("Rapor üretiliyor..."):
            # Mock rapor üretimi
            time.sleep(2)
            
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.markdown("### 📄 TSNM Kısa Rapor")
            
            st.markdown(f"""
            **Hasta Bilgileri:**
            - Adı: {patient_name}
            - ID: {patient_id}
            - Yaş: {age}
            - Cinsiyet: {gender}
            - Tanı: {diagnosis}
            - Çalışma Tarihi: {study_date}
            
            **SUV Analiz Sonuçları:**
            - Toplam lezyon sayısı: 3
            - Ortalama SUVmax değişimi: -25.0%
            - Genel trend: Azalma (iyi yanıt)
            
            **Sonuç:**
            PET-CT incelemesinde tespit edilen lezyonlarda tedaviye yanıt gözlenmiştir.
            SUVmax değerlerinde belirgin azalma tespit edilmiştir.
            """)
            
            st.success("✅ Rapor başarıyla üretildi!")
            st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 Sistem Performansı")
    
    # Performans metrikleri
    st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
    st.metric("Aktif Kullanıcı", "12", "3")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
    st.metric("Günlük Rapor", "47", "8")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
    st.metric("Sistem Uptime", "99.8%", "0.1%")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
    st.metric("Ortalama Yanıt", "1.2s", "-0.3s")
    st.markdown('</div>', unsafe_allow_html=True)

# Alt kısım - Analytics
st.markdown("### 📈 Sistem Analitiği")

col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 📊 Günlük Aktivite")
    
    # Mock günlük aktivite verileri
    dates = pd.date_range(start='2025-09-05', end='2025-09-12', freq='D')
    activity_data = np.random.poisson(25, len(dates))
    
    fig = px.bar(
        x=dates,
        y=activity_data,
        title="Günlük Rapor Sayısı",
        labels={'x': 'Tarih', 'y': 'Rapor Sayısı'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.markdown("#### 🎯 Rapor Türü Dağılımı")
    
    # Mock rapor türü verileri
    report_types = ["TSNM Kısa", "TSNM Detaylı", "Araştırma", "Klinik"]
    report_counts = [35, 28, 15, 22]
    
    fig = px.pie(
        values=report_counts,
        names=report_types,
        title="Rapor Türü Dağılımı"
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Performans monitörü
st.markdown("### 🔍 Performans Monitörü")

col5, col6, col7 = st.columns(3)

with col5:
    st.markdown("#### 💾 Bellek Kullanımı")
    
    # Mock bellek verileri
    memory_data = {
        "Kullanılan": "2.1 GB",
        "Toplam": "8.0 GB",
        "Yüzde": "26.3%"
    }
    
    for key, value in memory_data.items():
        st.text(f"{key}: {value}")
    
    # Bellek grafiği
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 26.3,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Bellek Kullanımı (%)"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.markdown("#### ⚡ CPU Kullanımı")
    
    # Mock CPU verileri
    cpu_data = {
        "Kullanılan": "45.2%",
        "Ortalama": "38.7%",
        "Maksimum": "78.1%"
    }
    
    for key, value in cpu_data.items():
        st.text(f"{key}: {value}")
    
    # CPU grafiği
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 45.2,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "CPU Kullanımı (%)"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)

with col7:
    st.markdown("#### 🌐 Ağ Trafiği")
    
    # Mock ağ verileri
    network_data = {
        "Gelen": "125.3 MB/s",
        "Giden": "89.7 MB/s",
        "Toplam": "215.0 MB/s"
    }
    
    for key, value in network_data.items():
        st.text(f"{key}: {value}")
    
    # Ağ grafiği
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 215.0,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Ağ Trafiği (MB/s)"},
        gauge = {
            'axis': {'range': [None, 500]},
            'bar': {'color': "darkred"},
            'steps': [
                {'range': [0, 200], 'color': "lightgray"},
                {'range': [200, 400], 'color': "yellow"},
                {'range': [400, 500], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 450
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>📊 Reports & Analytics - NeuroPETRIX v3.0</p>
    <p>Rapor üretimi ve sistem analitiği</p>
</div>
""", unsafe_allow_html=True)
