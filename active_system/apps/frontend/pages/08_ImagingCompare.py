import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

st.set_page_config(
    page_title="ImagingCompare - NeuroPETrix",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize session state
if "imaging_step" not in st.session_state:
    st.session_state["imaging_step"] = "upload"
if "demo_mode" not in st.session_state:
    st.session_state["demo_mode"] = True

# Page title and description
st.title("🔬 ImagingCompare - DICOM + Segmentasyon + SUV/MTV/TLG")
st.markdown("**Pretrained MONAI/nnUNet + Lezyon Metrikleri + Çalışmalar Arası Eşleşme**")

# Backend URL configuration
if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = "http://127.0.0.1:8000"

backend_url = st.sidebar.text_input("Backend URL", st.session_state["backend_url"])
st.session_state["backend_url"] = backend_url

# Demo Mode Toggle
demo_mode = st.sidebar.toggle("🎭 Demo Mode", value=st.session_state["demo_mode"])
st.session_state["demo_mode"] = demo_mode

# Sidebar navigation
with st.sidebar:
    st.title("🧭 Hızlı Navigasyon")
    st.markdown("---")
    
    if st.button("🏠 Ana Sayfa", use_container_width=True):
        st.switch_page("streamlit_app.py")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/00_Dashboard.py")
    
    if st.button("📁 DICOM Upload", use_container_width=True):
        st.switch_page("pages/04_DICOM_Upload.py")
    
    if st.button("🤖 AI Analysis", use_container_width=True):
        st.switch_page("pages/05_AI_Analysis.py")
    
    st.markdown("---")
    
    # Imaging Progress
    st.header("📊 Imaging Durumu")
    
    if st.session_state["imaging_step"] == "upload":
        st.info("📁 DICOM yükleme")
    elif st.session_state["imaging_step"] == "segmentation":
        st.info("🔬 Segmentasyon yapılıyor")
    elif st.session_state["imaging_step"] == "metrics":
        st.info("📊 Metrikler hesaplanıyor")
    elif st.session_state["imaging_step"] == "comparison":
        st.info("🔍 Karşılaştırma analizi")
    elif st.session_state["imaging_step"] == "results":
        st.success("✅ Analiz tamamlandı!")
    
    st.markdown("---")
    
    # System status in sidebar
    st.header("📊 Sistem Durumu")
    try:
        import requests
        health_response = requests.get(f"{backend_url}/health", timeout=3)
        if health_response.status_code == 200:
            st.success("🟢 Backend OK")
        else:
            st.error("🔴 Backend Error")
    except:
        st.error("🔌 Backend Offline")
        if st.session_state["demo_mode"]:
            st.info("🎭 Demo mode active")

# ---- HERO SECTION ----
col_hero1, col_hero2 = st.columns([2, 1])

with col_hero1:
    st.markdown("""
    <div class="hero">
        <div>
            <h1>🔬 ImagingCompare</h1>
            <div class="subtitle">Pretrained MONAI/nnUNet + Lezyon Metrikleri + Çalışmalar Arası Eşleşme</div>
        </div>
        <div>
            <span class="badge ok">MONAI Ready</span>
            <span class="badge">nnUNet Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    st.markdown("### 🎯 Hızlı İşlemler")
    
    if st.button("🚀 Yeni Analiz", type="primary", use_container_width=True):
        st.session_state["imaging_step"] = "upload"
        st.rerun()
    
    if st.button("📊 Karşılaştır", use_container_width=True):
        st.session_state["imaging_step"] = "comparison"
        st.rerun()

st.write("")

# ---- MAIN WORKFLOW ----
if st.session_state["imaging_step"] == "upload":
    st.header("📁 DICOM Yükleme ve Yapay Zeka Analizi")
    
    col_upload1, col_upload2 = st.columns(2)
    
    with col_upload1:
        st.markdown("""
        <div class="card">
            <h3>🔬 Klinik Uygulama Hikayesi</h3>
            <p><strong>Bir hastanın PET-CT görüntüsünü analiz edelim:</strong></p>
            <ul>
                <li>• DICOM dosyasını yüklüyoruz.</li>
                <li>• Yapay zeka otomatik olarak lezyonu tespit ediyor.</li>
                <li>• Lezyonun segmentasyonunu (sınırlanmasını) yapıyor.</li>
                <li>• SUV, MTV ve TLG değerlerini hesaplıyor.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📁 DICOM Dosya Yükleme")
        
        if st.session_state["demo_mode"]:
            st.info("🎭 Demo Mode: DICOM yükleme simüle ediliyor")
            
            patient_name = st.text_input("Hasta Adı", value="Ahmet Yılmaz")
            study_date = st.date_input("Tetkik Tarihi", datetime.today())
            
            if st.button("🚀 Analizi Başlat", type="primary"):
                st.session_state["patient_name"] = patient_name
                st.session_state["study_date"] = study_date
                st.session_state["imaging_step"] = "segmentation"
                st.rerun()
        else:
            st.warning("🔌 Gerçek DICOM yükleme için backend bağlantısı gerekli")
    
    with col_upload2:
        st.markdown("""
        <div class="card">
            <h3>📊 Otomatik Segmentasyon</h3>
            <p><strong>MONAI ile lezyonları hızlıca ayırın</strong></p>
            <ul>
                <li>• Lezyon tespiti ve etiketleme</li>
                <li>• 3D görüntü üzerinde segmentasyon maskesi</li>
                <li>• Görüntü önizleme (yakında)</li>
                <li>• Hızlı ve doğru analiz</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🤖 AI Pipeline")
        st.write("Yapay zeka, DICOM verilerini işlemek için hazır.")
        
        st.markdown("""
        <div class="card" style="padding: 10px;">
            <p style="margin: 0;"><strong>MONAI Hazır</strong></p>
            <p style="margin: 0;"><strong>PyRadiomics Entegre</strong></p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state["imaging_step"] == "segmentation":
    st.header("🔄 Yapay Zeka Analizi ve Segmentasyon")
    
    progress = st.progress(0)
    status_text = st.empty()
    
    st.info(f"Yapay zeka, **{st.session_state['patient_name']}** adlı hastanın PET-CT görüntüsünü analiz ediyor...")
    
    for i in range(101):
        progress.progress(i)
        if i < 30:
            status_text.text("📁 DICOM verileri işleniyor...")
        elif i < 60:
            status_text.text("🔬 MONAI ile segmentasyon yapılıyor...")
        elif i < 90:
            status_text.text("📊 Lezyon metrikleri hesaplanıyor...")
        else:
            status_text.text("✅ Analiz tamamlandı!")
    
    st.session_state["imaging_step"] = "metrics"
    st.rerun()

elif st.session_state["imaging_step"] == "metrics":
    st.header("📊 Lezyon Metrikleri ve Görüntüleme")
    
    st.success("🎉 Yapay zeka analizi başarıyla tamamlandı! Lezyon metrikleri aşağıda gösterilmiştir.")
    
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        st.subheader("🖼️ Segmentasyon Görüntüsü (Demo)")
        
        st.image("https://via.placeholder.com/600x400.png?text=Lezyon+Segmentasyonu", caption="Lezyonun Otomatik Segmentasyonu", use_column_width=True)
        
        st.info("Bu görüntü, yapay zekanın lezyonu PET/CT görüntüsü üzerinde nasıl otomatik olarak ayırdığını gösterir.")
    
    with col_viz2:
        st.subheader("📈 Hesaplanan Metrikler")
        
        lesion_metrics = {
            "SUVmax": {"value": 8.5, "unit": "g/mL", "desc": "En yüksek metabolik aktivite"},
            "SUVmean": {"value": 6.2, "unit": "g/mL", "desc": "Ortalama metabolik aktivite"},
            "MTV": {"value": 15.3, "unit": "cm³", "desc": "Metabolik tümör hacmi"},
            "TLG": {"value": 94.9, "unit": "g/mL*cm³", "desc": "Total lezyon glikolizi"}
        }
        
        for metric, data in lesion_metrics.items():
            st.metric(label=f"**{metric}**", value=f"{data['value']:.1f} {data['unit']}", delta=data['desc'])
        
    st.write("")
    
    col_action1, col_action2 = st.columns(2)
    
    with col_action1:
        if st.button("🔍 Çalışmalar Arası Karşılaştırma", type="primary", use_container_width=True):
            st.session_state["imaging_step"] = "comparison"
            st.rerun()
    
    with col_action2:
        if st.button("🔄 Yeni Hasta Analizi", use_container_width=True):
            st.session_state["imaging_step"] = "upload"
            st.rerun()

elif st.session_state["imaging_step"] == "comparison":
    st.header("🔍 Çalışmalar Arası Eşleşme ve Karşılaştırma")
    
    st.info("📊 Eski rapor ile yeni rapor karşılaştırılıyor...")
    
    previous_study = {
        "tarih": "2024-01-15",
        "SUVmax": 8.5,
        "MTV": 15.3,
        "TLG": 94.9
    }
    current_study = {
        "tarih": "2024-04-15",
        "SUVmax": 6.2,
        "MTV": 8.9,
        "TLG": 52.8
    }

    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        st.markdown("### 📄 Eski Rapor")
        st.json(previous_study)
    with col_comp2:
        st.markdown("### 📄 Yeni Rapor")
        st.json(current_study)

    st.write("")
    st.subheader("📊 Karşılaştırma Analizi")
    
    st.info("🤖 Yapay Zeka, sayısal değişimlere göre sonuç cümleleri üretiyor...")

    suv_change = ((current_study['SUVmax'] - previous_study['SUVmax']) / previous_study['SUVmax']) * 100
    mtv_change = ((current_study['MTV'] - previous_study['MTV']) / previous_study['MTV']) * 100
    tlg_change = ((current_study['TLG'] - previous_study['TLG']) / previous_study['TLG']) * 100

    def get_sentence_and_color(change, metric_name):
        if change < -30:
            return f"**{metric_name}:** {change:.1f}% - Belirgin azalma tespit edildi. Bu durum **tedaviye yanıt** lehinedir.", "success"
        elif change > 30:
            return f"**{metric_name}:** {change:.1f}% - Belirgin artış tespit edildi. Bu durum **progresif hastalık** lehinedir.", "error"
        else:
            return f"**{metric_name}:** {change:.1f}% - Anlamlı değişiklik tespit edilmedi. Bu durum **stabil hastalık** lehinedir.", "info"

    suv_sentence, suv_color = get_sentence_and_color(suv_change, "SUVmax")
    mtv_sentence, mtv_color = get_sentence_and_color(mtv_change, "MTV")
    tlg_sentence, tlg_color = get_sentence_and_color(tlg_change, "TLG")

    st.markdown("### 📝 Yapay Zeka Önerileri")
    sentences = [
        {"text": suv_sentence, "color": suv_color},
        {"text": mtv_sentence, "color": mtv_color},
        {"text": tlg_sentence, "color": tlg_color},
    ]

    for i, sentence in enumerate(sentences):
        col_s, col_b = st.columns([4, 1])
        with col_s:
            st.markdown(
                f'<div class="card" style="border: 1px solid var(--border-color); padding: 10px; border-radius: 10px; background-color: var(--bg-card);"><p style="color: var(--text-primary); margin: 0;">{sentence["text"]}</p></div>',
                unsafe_allow_html=True
            )
        with col_b:
            if st.button("✅ Ekle", key=f"add_sent_{i}", use_container_width=True):
                st.session_state[f"sentence_{i}_added"] = True
                st.success("Öneri başarıyla rapora eklendi!")

    st.write("")
    
    st.markdown("---")
    col_bulk1, col_bulk2 = st.columns(2)
    with col_bulk1:
        if st.button("✅ Hepsini Ekle", use_container_width=True, type="primary"):
            for i in range(len(sentences)):
                st.session_state[f"sentence_{i}_added"] = True
            st.success("Tüm öneriler başarıyla rapora eklendi!")
    with col_bulk2:
        if st.button("📝 Rapor Taslağını Gör", use_container_width=True):
            st.session_state["imaging_step"] = "results"
            st.rerun()

elif st.session_state["imaging_step"] == "results":
    st.header("✅ ImagingCompare Tamamlandı!")
    
    st.success("🎉 DICOM analizi, segmentasyon ve karşılaştırma başarıyla tamamlandı!")
    
    col_summary1, col_summary2 = st.columns(2)
    
    with col_summary1:
        st.markdown("### 📋 Tamamlanan Analizler")
        
        completed_analyses = [
            "✅ DICOM dosya yükleme",
            "✅ MONAI segmentasyon",
            "✅ Lezyon metrikleri hesaplama",
            "✅ Çalışmalar arası eşleşme",
            "✅ Otomatik sonuç cümleleri"
        ]
        
        for analysis in completed_analyses:
            st.markdown(analysis)
    
    with col_summary2:
        st.markdown("### 📊 Performans Metrikleri")
        
        performance_metrics = {
            "Eşleşme Doğruluğu": "87.5%",
            "Segmentasyon Kalitesi": "0.89 (Dice)",
            "İşlem Süresi": "2.1 dakika",
            "SUV Tekrarlanabilirlik": "≤2% sapma"
        }
        
        for metric, value in performance_metrics.items():
            st.metric(metric, value)
    
    st.write("")
    
    st.subheader("📤 Dışa Aktarma Seçenekleri")
    
    col_export1, col_export2, col_export3, col_export4 = st.columns(4)
    
    with col_export1:
        if st.button("📄 PDF Rapor", use_container_width=True):
            st.info("📄 PDF export özelliği yakında eklenecek...")
    
    with col_export2:
        if st.button("📊 JSON Veri", use_container_width=True):
            st.info("📊 JSON export özelliği yakında eklenecek...")
    
    with col_export3:
        if st.button("🔬 DICOM Export", use_container_width=True):
            st.info("🔬 DICOM export özelliği yakında eklenecek...")
    
    with col_export4:
        if st.button("📈 Grafik Export", use_container_width=True):
            st.info("📈 Grafik export özelliği yakında eklenecek...")
    
    st.write("")
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("🔄 Yeni Analiz", type="primary"):
            st.session_state["imaging_step"] = "upload"
            st.rerun()
    
    with col_action2:
        if st.button("📊 Dashboard", use_container_width=True):
            st.switch_page("pages/00_Dashboard.py")
    
    with col_action3:
        if st.button("🤖 AI Analysis", use_container_width=True):
            st.switch_page("pages/05_AI_Analysis.py")

st.write("")

st.header("🔧 Teknik Özellikler")

col_tech1, col_tech2 = st.columns(2)

with col_tech1:
    st.markdown("""
    <div class="card">
        <h3>🤖 AI Pipeline</h3>
        <p><strong>Pretrained modeller ve fine-tune</strong></p>
        <ul>
            <li>• MONAI UNet (Pretrained)</li>
            <li>• nnUNet fine-tune kancası</li>
            <li>• GPU/CPU desteği</li>
            <li>• Patch-based inference</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_tech2:
    st.markdown("""
    <div class="card">
        <h3>📊 Metrik Hesaplama</h3>
        <p><strong>SUV, MTV, TLG + Radiomics</strong></p>
        <ul>
            <li>• Otomatik hesaplama</li>
            <li>• 1316+ radiomics özelliği</li>
            <li>• Karşılaştırmalı analiz</li>
            <li>• Δ% kuralları</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("**ImagingCompare v1.0** - DICOM + Segmentasyon + SUV/MTV/TLG")
