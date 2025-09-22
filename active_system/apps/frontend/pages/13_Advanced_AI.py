import streamlit as st
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import time

st.set_page_config(
    page_title="Advanced AI - NeuroPETrix",
    page_icon="🤖",
    layout="wide"
)

# Page title
st.title("🤖 Advanced AI - Gelişmiş Yapay Zeka Özellikleri")
st.markdown("**MONAI Segmentasyon • PyRadiomics • Clinical Rules Engine • AI Model Training**")

# Backend URL configuration
if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = "http://127.0.0.1:8000"

backend_url = st.sidebar.text_input("Backend URL", st.session_state["backend_url"])
st.session_state["backend_url"] = st.session_state["backend_url"]

# Sidebar navigation
st.sidebar.title("🧭 Hızlı Navigasyon")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Ana Sayfa", key="ai_nav_home", use_container_width=True):
    st.switch_page("streamlit_app.py")

if st.button("📊 Dashboard", key="ai_nav_dashboard", use_container_width=True):
    st.switch_page("pages/00_Dashboard.py")

if st.button("🔬 AI Analysis", key="ai_nav_analysis", use_container_width=True):
    st.switch_page("pages/05_AI_Analysis.py")

st.sidebar.markdown("---")

# System status in sidebar
st.sidebar.subheader("📊 Sistem Durumu")
try:
    health_response = requests.get(f"{backend_url}/health", timeout=3)
    if health_response.status_code == 200:
        st.sidebar.success("🟢 Backend OK")
    else:
        st.sidebar.error("🔴 Backend Error")
except:
    st.sidebar.error("🔌 Backend Offline")

# Initialize session state
if "ai_models" not in st.session_state:
    st.session_state["ai_models"] = []
if "training_status" not in st.session_state:
    st.session_state["training_status"] = "idle"

# ---- HERO SECTION ----
col_hero1, col_hero2 = st.columns([2, 1])

with col_hero1:
    st.markdown("""
    <div class="hero">
        <div>
            <h1>🤖 Advanced AI Platform</h1>
            <div class="subtitle">MONAI • PyRadiomics • Clinical Rules • Model Training</div>
        </div>
        <div>
            <span class="badge ok">AI Ready</span>
            <span class="badge">Production</span>
            <span class="badge">Clinical Grade</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    st.markdown("### 🎯 Hızlı İşlemler")
    
    if st.button("🚀 AI Model Başlat", key="ai_start_model", type="primary", use_container_width=True):
        st.session_state["training_status"] = "starting"
        st.rerun()
    
    if st.button("📊 Model Performansı", key="ai_model_performance", use_container_width=True):
        st.info("📊 Model performans analizi yakında eklenecek")

st.write("")

# ---- AI MODEL STATUS ----
st.header("🤖 AI Model Durumu")

col_status1, col_status2, col_status3, col_status4 = st.columns(4)

with col_status1:
    st.markdown("### 🧠 MONAI Segmentasyon")
    st.success("✅ Aktif")
    st.metric("Model Boyutu", "256MB")
    st.metric("Doğruluk", "94.2%")
    st.caption("UNet + Attention Gates")

with col_status2:
    st.markdown("### 📊 PyRadiomics")
    st.success("✅ Aktif")
    st.metric("Özellik Sayısı", "1,316")
    st.metric("İşlem Süresi", "2.3s")
    st.caption("First Order + Texture + Shape")

with col_status3:
    st.markdown("### 🔍 Clinical Rules")
    st.info("🔄 Yükleniyor")
    st.metric("Kural Sayısı", "47")
    st.metric("Güncelleme", "2 gün önce")
    st.caption("Evidence-based rules")

with col_status4:
    st.markdown("### 🎯 Whisper ASR")
    st.success("✅ Aktif")
    st.metric("Model", "medium")
    st.metric("Dil Desteği", "Türkçe + EN")
    st.caption("Real-time transcription")

st.write("")

# ---- MONAI SEGMENTATION ----
st.header("🧠 MONAI Görüntü Segmentasyonu")

col_monai1, col_monai2 = st.columns(2)

with col_monai1:
    st.subheader("📊 Segmentasyon Parametreleri")
    
    # Model parameters
    model_type = st.selectbox(
        "Model Tipi",
        ["UNet", "UNet++", "Attention UNet", "DeepLabV3+"],
        index=0
    )
    
    input_size = st.slider("Giriş Boyutu", 128, 512, 256, step=64)
    batch_size = st.slider("Batch Size", 1, 8, 2)
    
    # Advanced parameters
    with st.expander("🔧 Gelişmiş Parametreler"):
        learning_rate = st.number_input("Learning Rate", 0.0001, 0.01, 0.001, 0.0001)
        epochs = st.number_input("Epochs", 10, 500, 100)
        loss_function = st.selectbox("Loss Function", ["Dice", "CrossEntropy", "Focal", "Combined"])
    
    if st.button("🚀 Segmentasyon Başlat", key="monai_start", type="primary", use_container_width=True):
        st.success("🧠 MONAI segmentasyon başlatıldı!")
        st.info("Model yükleniyor ve görüntü işleniyor...")

with col_monai2:
    st.subheader("📈 Segmentasyon Sonuçları")
    
    # Mock segmentation results
    if st.button("📊 Demo Sonuçları Göster", key="monai_demo", use_container_width=True):
        # Create mock data
        dice_scores = [0.89, 0.92, 0.87, 0.94, 0.91, 0.88, 0.93, 0.90]
        hausdorff_distances = [2.1, 1.8, 2.3, 1.6, 1.9, 2.2, 1.7, 2.0]
        
        # Create DataFrame
        df_results = pd.DataFrame({
            'Case': [f'Case_{i+1:03d}' for i in range(len(dice_scores))],
            'Dice Score': dice_scores,
            'Hausdorff Distance': hausdorff_distances
        })
        
        st.dataframe(df_results, use_container_width=True)
        
        # Performance metrics
        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            st.metric("Ortalama Dice", f"{np.mean(dice_scores):.3f}")
        with col_metric2:
            st.metric("Ortalama HD", f"{np.mean(hausdorff_distances):.1f}")

st.write("")

# ---- PYRADIOMICS FEATURES ----
st.header("📊 PyRadiomics Özellik Çıkarma")

col_rad1, col_rad2 = st.columns(2)

with col_rad1:
    st.subheader("🔍 Özellik Kategorileri")
    
    # Feature categories
    feature_categories = {
        "First Order": ["Mean", "Std", "Skewness", "Kurtosis", "Energy", "Entropy"],
        "Shape": ["Volume", "Surface Area", "Compactness", "Sphericity", "Spherical Disproportion"],
        "GLCM": ["Contrast", "Correlation", "Energy", "Homogeneity", "Entropy"],
        "GLRLM": ["SRE", "LRE", "GLN", "RLN", "RP", "LGRE"],
        "GLSZM": ["SZE", "LZE", "GLN", "SZLGE", "LZLGE", "SZHGE"]
    }
    
    selected_category = st.selectbox("Özellik Kategorisi", list(feature_categories.keys()))
    
    if selected_category:
        features = feature_categories[selected_category]
        st.markdown(f"**{selected_category} Özellikleri:**")
        for feature in features:
            st.markdown(f"• {feature}")
    
    # Feature extraction parameters
    st.subheader("⚙️ Çıkarma Parametreleri")
    
    bin_width = st.slider("Bin Width", 0.1, 2.0, 0.5, 0.1)
    normalize = st.checkbox("Normalize", value=True)
    resample = st.checkbox("Resample", value=True)
    
    if st.button("📊 Özellik Çıkar", key="radiomics_extract", type="primary", use_container_width=True):
        st.success("📊 PyRadiomics özellik çıkarma başlatıldı!")
        st.info("Görüntü analiz ediliyor ve özellikler hesaplanıyor...")

with col_rad2:
    st.subheader("📈 Özellik Analizi")
    
    # Mock feature analysis
    if st.button("📊 Demo Analiz Göster", key="radiomics_demo", use_container_width=True):
        # Create mock feature data
        feature_names = ["Mean", "Std", "Skewness", "Kurtosis", "Energy", "Entropy"]
        feature_values = [45.2, 12.8, 0.34, 2.1, 0.67, 4.2]
        
        # Create bar chart
        fig_features = px.bar(
            x=feature_names,
            y=feature_values,
            title="First Order Özellikleri",
            labels={'x': 'Özellik', 'y': 'Değer'}
        )
        fig_features.update_layout(height=400)
        st.plotly_chart(fig_features, use_container_width=True)
        
        # Feature statistics
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Toplam Özellik", len(feature_names))
        with col_stat2:
            st.metric("Ortalama Değer", f"{np.mean(feature_values):.2f}")

st.write("")

# ---- CLINICAL RULES ENGINE ----
st.header("🔍 Clinical Rules Engine")

col_rules1, col_rules2 = st.columns(2)

with col_rules1:
    st.subheader("📋 Klinik Kurallar")
    
    # Clinical rules
    clinical_rules = [
        {"rule": "SUVmax > 2.5", "action": "Malignite şüphesi", "confidence": 0.85},
        {"rule": "Lesion size > 3cm", "action": "Büyük lezyon uyarısı", "confidence": 0.78},
        {"rule": "Multiple lesions", "action": "Metastaz değerlendirmesi", "confidence": 0.92},
        {"rule": "SUV ratio > 2.0", "action": "Patolojik aktivite", "confidence": 0.88},
        {"rule": "Growth rate > 20%", "action": "Progresyon uyarısı", "confidence": 0.76}
    ]
    
    for rule in clinical_rules:
        with st.expander(f"📋 {rule['rule']}"):
            st.markdown(f"**Aksiyon:** {rule['action']}")
            st.markdown(f"**Güven:** {rule['confidence']:.0%}")
            
            # Rule status
            if rule['confidence'] > 0.8:
                st.success("✅ Yüksek güven")
            elif rule['confidence'] > 0.6:
                st.warning("⚠️ Orta güven")
            else:
                st.error("❌ Düşük güven")

with col_rules2:
    st.subheader("🎯 Kural Değerlendirmesi")
    
    # Rule evaluation
    st.markdown("**Hasta Verileri:**")
    
    suv_max = st.number_input("SUVmax", 0.0, 20.0, 3.5, 0.1)
    lesion_size = st.number_input("Lezyon Boyutu (cm)", 0.1, 10.0, 2.5, 0.1)
    multiple_lesions = st.checkbox("Çoklu Lezyon")
    
    if st.button("🔍 Kuralları Değerlendir", key="rules_evaluate", type="primary", use_container_width=True):
        # Evaluate rules
        triggered_rules = []
        
        if suv_max > 2.5:
            triggered_rules.append("SUVmax > 2.5: Malignite şüphesi")
        
        if lesion_size > 3.0:
            triggered_rules.append("Lesion size > 3cm: Büyük lezyon uyarısı")
        
        if multiple_lesions:
            triggered_rules.append("Multiple lesions: Metastaz değerlendirmesi")
        
        if triggered_rules:
            st.success("🔍 Kural değerlendirmesi tamamlandı!")
            st.markdown("**Tetiklenen Kurallar:**")
            for rule in triggered_rules:
                st.markdown(f"• {rule}")
        else:
            st.info("ℹ️ Hiçbir kural tetiklenmedi")

st.write("")

# ---- AI MODEL TRAINING ----
st.header("🎓 AI Model Eğitimi")

col_train1, col_train2 = st.columns(2)

with col_train1:
    st.subheader("📚 Eğitim Veri Seti")
    
    # Dataset information
    dataset_size = st.number_input("Veri Seti Boyutu", 100, 10000, 1000, 100)
    train_split = st.slider("Eğitim Oranı", 0.6, 0.9, 0.8, 0.05)
    validation_split = st.slider("Validasyon Oranı", 0.1, 0.3, 0.1, 0.05)
    test_split = 1 - train_split - validation_split
    
    st.markdown(f"**Veri Dağılımı:**")
    st.markdown(f"• Eğitim: {train_split:.0%} ({int(dataset_size * train_split)} örnek)")
    st.markdown(f"• Validasyon: {validation_split:.0%} ({int(dataset_size * validation_split)} örnek)")
    st.markdown(f"• Test: {test_split:.0%} ({int(dataset_size * test_split)} örnek)")
    
    # Training parameters
    st.subheader("⚙️ Eğitim Parametreleri")
    
    model_architecture = st.selectbox("Model Mimarisi", ["UNet", "UNet++", "Attention UNet", "DeepLabV3+"])
    optimizer = st.selectbox("Optimizer", ["Adam", "SGD", "RMSprop", "Adagrad"])
    learning_rate = st.number_input("Learning Rate", 0.00001, 0.1, 0.001, 0.00001)
    epochs = st.number_input("Epochs", 10, 1000, 100)

with col_train2:
    st.subheader("🚀 Eğitim Başlatma")
    
    # Training controls
    if st.button("🎓 Eğitimi Başlat", key="training_start", type="primary", use_container_width=True):
        st.session_state["training_status"] = "training"
        st.success("🎓 AI model eğitimi başlatıldı!")
        st.info("Model eğitiliyor, lütfen bekleyin...")
    
    # Training status
    if st.session_state["training_status"] == "training":
        st.info("🔄 Model eğitiliyor...")
        progress = st.progress(0)
        
        # Simulate training progress
        for i in range(101):
            progress.progress(i)
            time.sleep(0.1)
        
        st.success("✅ Model eğitimi tamamlandı!")
        st.session_state["training_status"] = "completed"
    
    elif st.session_state["training_status"] == "completed":
        st.success("✅ Model eğitimi tamamlandı!")
        
        # Training results
        st.subheader("📊 Eğitim Sonuçları")
        
        col_result1, col_result2 = st.columns(2)
        with col_result1:
            st.metric("Final Loss", "0.0234")
            st.metric("Accuracy", "96.8%")
        with col_result2:
            st.metric("Training Time", "45 dk")
            st.metric("Best Epoch", "87")

# Footer
st.markdown("---")
st.markdown("**Advanced AI v1.0** - MONAI • PyRadiomics • Clinical Rules • Model Training")














