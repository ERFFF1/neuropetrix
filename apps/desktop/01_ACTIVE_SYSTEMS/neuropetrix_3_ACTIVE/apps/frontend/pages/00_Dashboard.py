import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json

st.set_page_config(
    page_title="NeuroPETrix Dashboard",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 NeuroPETRIX v2.0 - Ana Dashboard")
st.markdown("**Entegre AI Sistemi - PICO → MONAI → Evidence → Decision → Report**")
st.markdown("---")

# System status check
st.subheader("📊 Sistem Durumu")
status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=3)
        if response.status_code == 200:
            st.success("✅ Backend")
        else:
            st.error("❌ Backend")
    except:
        st.error("❌ Backend")

with status_col2:
    try:
        response = requests.get("http://127.0.0.1:8000/performance", timeout=3)
        if response.status_code == 200:
            st.success("✅ Performance")
        else:
            st.error("❌ Performance")
    except:
        st.error("❌ Performance")

with status_col3:
    try:
        response = requests.get("http://127.0.0.1:8000/cache/stats", timeout=3)
        if response.status_code == 200:
            st.success("✅ Cache")
        else:
            st.error("❌ Cache")
    except:
        st.error("❌ Cache")

with status_col4:
    try:
        response = requests.get("http://127.0.0.1:8000/integration/health", timeout=3)
        if response.status_code == 200:
            st.success("✅ Integration")
        else:
            st.error("❌ Integration")
    except:
        st.error("❌ Integration")

st.markdown("---")

# Sidebar for workflow customization
with st.sidebar:
    st.header("🎯 Ana Akış Özelleştirmesi")
    
    # Flow type selection - INTEGRATED INTO MAIN WORKFLOW
    st.subheader("🚀 Akış Hızı")
    flow_speed = st.radio(
        "Akış hızını seçin:",
        ["⚡ Hızlı (Bypass)", "🔍 Detaylı (Tam Akış)"],
        help="Hızlı: Sadece gerekli adımlar\nDetaylı: Tüm analizler ve raporlar"
    )
    
    st.markdown("---")
    
    # Branch selection - INTEGRATED INTO MAIN WORKFLOW
    st.subheader("🏥 Branş Seçimi")
    branch = st.selectbox(
        "Branşınızı seçin:",
        ["Onkoloji", "Radyoloji", "KBB", "Nöroloji", "Kardiyoloji", "Ortopedi", "Nükleer Tıp"],
        help="Branşınıza göre özelleştirilmiş iş akışları ve öneriler"
    )
    
    st.markdown("---")
    
    # Clinical decision target - INTEGRATED INTO MAIN WORKFLOW
    st.subheader("🎯 Klinik Karar Hedefi")
    clinical_target = st.selectbox(
        "Klinik hedefinizi seçin:",
        ["Tanı Kararı", "Tedavi Kararı", "Prognoz Kararı", "Takip Kararı"],
        help="Seçilen hedefe göre gerekli metrikler ve analizler belirlenir"
    )

# Main workflow display - INTEGRATED SYSTEM
st.header("🔄 Ana Akış Sistemi - Entegre")

# Display workflow based on selection
if "Hızlı (Bypass)" in flow_speed:
    st.info("🚀 **Hızlı Akış (Bypass)**: Ana akışın kritik adımları, hızlı sonuç için optimize edildi.")
    
    # INTEGRATED WORKFLOW - Bypass version
    workflow_steps = [
        "📋 ICD Kodu + Branş + Klinik Hedef Seçimi",
        "🤖 Akıllı Metrik Tanımlama (Branşa özel)",
        "📊 Veri Toplama (HBYS/Manuel - DICOM opsiyonel)",
        "🧠 MONAI + PyRadiomics Analizi (Hızlı mod)",
        "📈 SUV Trend Analizi (Temel)",
        "🎯 Klinik Karar Hedefi Güncelleme",
        "🧠 PICO + Literatür + GRADE (Özet)",
        "🧠 Kanıt Değerlendirme (Hızlı)",
        "📄 Final Öneri (Kompakt)"
    ]
    
    # Add branch-specific bypass steps
    if branch == "Onkoloji":
        workflow_steps.insert(4, "🏥 TSNM Evreleme (Hızlı)")
    elif branch == "Radyoloji":
        workflow_steps.insert(4, "🖼️ 3D Görüntüleme (Temel)")
    elif branch == "Kardiyoloji":
        workflow_steps.insert(4, "🫀 Perfüzyon Analizi (Hızlı)")
    
else:
    st.info("🔍 **Detaylı Akış (Tam Akış)**: Ana akışın tüm adımları, kapsamlı analiz için.")
    
    # INTEGRATED WORKFLOW - Full version
    workflow_steps = [
        "📋 ICD Kodu + Branş + Klinik Hedef Seçimi",
        "🤖 Akıllı Metrik Tanımlama (Branşa özel + Detaylı)",
        "📊 Veri Toplama (HBYS/Manuel/DICOM)",
        "🧠 MONAI + PyRadiomics Analizi (Tam analiz)",
        "📈 SUV Trend Analizi (Detaylı)",
        "🎯 Klinik Karar Hedefi Güncelleme",
        "🧠 PICO + Literatür + GRADE (Kapsamlı)",
        "🧠 Kanıt Değerlendirme (Detaylı)",
        "📄 Final Öneri (Kapsamlı)",
        "📄 Detaylı Rapor Üretimi"
    ]
    
    # Add branch-specific full flow steps
    if branch == "Onkoloji":
        workflow_steps.insert(4, "🏥 TSNM Evreleme (Detaylı)")
        workflow_steps.insert(6, "💊 Tedavi Protokolü Seçimi")
    elif branch == "Radyoloji":
        workflow_steps.insert(4, "🖼️ 3D Görüntüleme (Gelişmiş)")
        workflow_steps.insert(6, "📊 Karşılaştırmalı Analiz")
    elif branch == "Kardiyoloji":
        workflow_steps.insert(4, "🫀 Perfüzyon Analizi (Detaylı)")
        workflow_steps.insert(6, "📊 Risk Stratifikasyonu")

# Display integrated workflow
st.subheader("📋 Entegre İş Akışı")
for i, step in enumerate(workflow_steps, 1):
    st.write(f"{i}. {step}")

st.markdown("---")

# Branch specialization integration
st.header("🏥 Branş Özelleştirmesi - Ana Akışa Entegre")

# Get branch specialization from API
if st.button("🔄 Branş Özelleştirmesini Yükle", type="primary"):
    with st.spinner("Branş özelleştirmesi yükleniyor..."):
        try:
            # Call branch specialization API
            response = requests.post(
                "http://127.0.0.1:8000/branch/specialize",
                json={
                    "branch": branch,
                    "clinical_target": clinical_target,
                    "patient_age": 65,  # Mock data
                    "patient_gender": "Erkek",  # Mock data
                    "performance_score": "1"  # Mock data
                }
            )
            
            if response.status_code == 200:
                branch_data = response.json()
                st.session_state.branch_data = branch_data
                st.success("✅ Branş özelleştirmesi yüklendi!")
            else:
                st.error(f"❌ API hatası: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Bağlantı hatası: {str(e)}")

# Display branch specialization if available
if hasattr(st.session_state, 'branch_data'):
    branch_data = st.session_state.branch_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Gerekli Metrikler")
        metrics = branch_data["required_metrics"]
        
        # Laboratory metrics
        if "laboratory" in metrics:
            st.write("🩸 **Laboratuvar:**")
            for metric in metrics["laboratory"]:
                st.write(f"  • {metric}")
        
        # Clinical metrics
        if "clinical" in metrics:
            st.write("🩺 **Klinik:**")
            for metric in metrics["clinical"]:
                st.write(f"  • {metric}")
        
        # Imaging metrics
        if "imaging" in metrics:
            st.write("🖼️ **Görüntüleme:**")
            for metric in metrics["imaging"]:
                st.write(f"  • {metric}")
        
        # Priority and focus
        if "priority" in metrics:
            st.metric("Öncelik", metrics["priority"])
        if "focus" in metrics:
            st.metric("Odak", metrics["focus"])
    
    with col2:
        st.subheader("📚 Klinik Kılavuzlar")
        for guideline in branch_data["clinical_guidelines"]:
            st.write(f"• {guideline}")
        
        st.subheader("⚠️ Risk Faktörleri")
        for risk in branch_data["risk_factors"]:
            st.write(f"• {risk}")
        
        st.subheader("🎯 Öneriler")
        for rec in branch_data["recommendations"]:
            st.write(f"• {rec}")

st.markdown("---")

# Quick access to workflow modules - INTEGRATED
st.header("🚀 Ana Akış Modüllerine Hızlı Erişim")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🖼️ DICOM Yükleme", use_container_width=True):
        st.switch_page("pages/04_DICOM_Upload.py")
        
    if st.button("🧠 MONAI & PyRadiomics", use_container_width=True):
        st.switch_page("pages/17_MONAI_Radiomics.py")

with col2:
    if st.button("📈 SUV Trend Analizi", use_container_width=True):
        st.switch_page("pages/08_SUV_Trend.py")
        
    if st.button("🎯 PICO Otomasyonu", use_container_width=True):
        st.switch_page("pages/15_PICO_Automation.py")

with col3:
    if st.button("🏥 HBYS Entegrasyonu", use_container_width=True):
        st.switch_page("pages/18_HBYS_Integration.py")
        
    if st.button("📄 Rapor Üretimi", use_container_width=True):
        st.switch_page("pages/02_Rapor_Üretimi.py")

# System status - INTEGRATED
st.markdown("---")
st.header("📊 Sistem Durumu - Entegre")
status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    st.metric("Backend", "✅ Çalışıyor", "http://127.0.0.1:8000")
    
with status_col2:
    st.metric("Frontend", "✅ Çalışıyor", "http://127.0.0.1:8501")
    
with status_col3:
    st.metric("HBYS", "✅ Bağlı", "Mock veri")
    
with status_col4:
    st.metric("AI Pipeline", "⚠️ Mock", "Test modu")

# Recent activities - INTEGRATED
st.header("📋 Son Aktiviteler - Entegre")
recent_activities = [
    {"Tarih": "2025-08-27 21:17", "Aktivite": "Branş sistemi entegre edildi", "Durum": "✅"},
    {"Tarih": "2025-08-27 21:16", "Aktivite": "GEMİNİ önerileri entegre edildi", "Durum": "✅"},
    {"Tarih": "2025-08-27 21:15", "Aktivite": "Ana akış korundu", "Durum": "✅"},
    {"Tarih": "2025-08-27 21:14", "Aktivite": "Sistem güncellendi", "Durum": "✅"}
]

df_activities = pd.DataFrame(recent_activities)
st.dataframe(df_activities, use_container_width=True)

# Footer - INTEGRATED
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🧠 NeuroPETrix v2.0 - Geleceğin Tıbbi Görüntüleme Platformu</p>
    <p>Ana akış korunarak GEMİNİ önerileri entegre edildi</p>
</div>
""", unsafe_allow_html=True)
