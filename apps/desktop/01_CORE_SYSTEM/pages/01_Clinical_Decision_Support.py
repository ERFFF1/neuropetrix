import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
# Plotly import - Optional dependency
PLOTLY_AVAILABLE = False
go = None
try:
    import plotly.graph_objects as go  # type: ignore
    PLOTLY_AVAILABLE = True
except ImportError:
    pass
from typing import Dict, List, Any
import sys
import os

# Whisper Engine import - Mock implementation
WHISPER_AVAILABLE = False
def create_whisper_widget():
    return st.info("Whisper Engine not available - using mock implementation")

try:
    # Try to import from the actual path
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../02_AI_ENGINES/Whisper_Engine/utils'))
    from whisper_widget import create_whisper_widget  # type: ignore
    WHISPER_AVAILABLE = True
except ImportError:
    pass

st.set_page_config(
    page_title="Clinical Decision Support - NeuroPETrix",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for Clinical Decision Support
st.markdown("""
<style>
    .clinical-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .workflow-step {
        background: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        transition: all 0.3s ease;
    }
    
    .workflow-step:hover {
        background: #e3f2fd;
        transform: translateX(5px);
    }
    
    .workflow-step.active {
        background: #e8f5e8;
        border-left-color: #28a745;
    }
    
    .workflow-step.completed {
        background: #d4edda;
        border-left-color: #28a745;
    }
    
    .icd-input-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    
    .result-box {
        background: #e8f5e8;
        border: 2px solid #28a745;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .voice-input-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="clinical-header">
    <h1>🏥 Clinical Decision Support</h1>
    <p style="font-size: 1.2rem; margin: 0;">ICD ile Başlayan Klinik Karar Destek Sistemi</p>
    <p style="font-size: 1rem; margin: 0.5rem 0 0 0;">Akıllı klinik workflow ve GRADE metodolojisi</p>
</div>
""", unsafe_allow_html=True)

# Klinik workflow konfigürasyonu
CLINICAL_WORKFLOW = {
    "branches": {
        "oncology": {
            "name": "Onkoloji",
            "icd_codes": ["C78", "C79", "C80", "C81", "C82", "C83", "C84", "C85"],
            "workflow_steps": [
                "ICD Kod Girişi",
                "Klinik Hedef Seçimi",
                "Literatür Taraması",
                "SUVmax Hesaplama",
                "Segmentasyon ve Analiz",
                "Klinik Yorumlama",
                "Rapor Üretimi",
                "Takip Planlaması"
            ],
            "clinical_targets": {
                "diagnosis": "Tanı",
                "staging": "Evreleme",
                "treatment_response": "Tedaviye Yanıt",
                "follow_up": "Takip",
                "screening": "Tarama"
            }
        },
        "cardiology": {
            "name": "Kardiyoloji",
            "icd_codes": ["I20", "I21", "I22", "I23", "I24", "I25"],
            "workflow_steps": [
                "ICD Kod Girişi",
                "Klinik Hedef Seçimi",
                "Literatür Taraması",
                "PET Perfüzyon Analizi",
                "Segmentasyon ve Analiz",
                "Klinik Yorumlama",
                "Rapor Üretimi",
                "Takip Planlaması"
            ],
            "clinical_targets": {
                "diagnosis": "Tanı",
                "prognosis": "Prognoz",
                "treatment_response": "Tedaviye Yanıt",
                "follow_up": "Takip"
            }
        },
        "neurology": {
            "name": "Nöroloji",
            "icd_codes": ["G30", "G31", "G32", "G93", "G94"],
            "workflow_steps": [
                "ICD Kod Girişi",
                "Klinik Hedef Seçimi",
                "Literatür Taraması",
                "PET Metabolik Analizi",
                "Segmentasyon ve Analiz",
                "Klinik Yorumlama",
                "Rapor Üretimi",
                "Takip Planlaması"
            ],
            "clinical_targets": {
                "diagnosis": "Tanı",
                "prognosis": "Prognoz",
                "treatment_response": "Tedaviye Yanıt",
                "follow_up": "Takip"
            }
        },
        "endocrinology": {
            "name": "Endokrinoloji",
            "icd_codes": ["E10", "E11", "E12", "E13", "E14"],
            "workflow_steps": [
                "ICD Kod Girişi",
                "Klinik Hedef Seçimi",
                "Literatür Taraması",
                "PET Metabolik Analizi",
                "Segmentasyon ve Analiz",
                "Klinik Yorumlama",
                "Rapor Üretimi",
                "Takip Planlaması"
            ],
            "clinical_targets": {
                "diagnosis": "Tanı",
                "prognosis": "Prognoz",
                "treatment_response": "Tedaviye Yanıt",
                "follow_up": "Takip"
            }
        }
    }
}

# Ana içerik
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🔍 ICD Kod Girişi")
    
    # ICD giriş yöntemi seçimi
    input_method = st.radio(
        "Giriş Yöntemi:",
        ["Manuel Giriş", "Sesli Giriş"],
        horizontal=True
    )
    
    if input_method == "Manuel Giriş":
        st.markdown('<div class="icd-input-box">', unsafe_allow_html=True)
        icd_code = st.text_input(
            "ICD-10 Kodu:",
            placeholder="Örn: C78.0, I21.9, G30.0",
            help="ICD-10 kodunu girin"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if icd_code:
            # ICD kodunu analiz et
            branch = None
            for branch_name, branch_data in CLINICAL_WORKFLOW["branches"].items():
                for code in branch_data["icd_codes"]:
                    if code in icd_code:
                        branch = branch_name
                        break
                if branch:
                    break
            
            if branch:
                st.success(f"✅ ICD kodu '{icd_code}' {CLINICAL_WORKFLOW['branches'][branch]['name']} branşında tespit edildi!")
                
                # Klinik hedef seçimi
                st.markdown("### 🎯 Klinik Hedef Seçimi")
                clinical_target = st.selectbox(
                    "Klinik Hedef:",
                    list(CLINICAL_WORKFLOW["branches"][branch]["clinical_targets"].keys()),
                    format_func=lambda x: CLINICAL_WORKFLOW["branches"][branch]["clinical_targets"][x]
                )
                
                # Workflow başlat
                if st.button("🚀 Workflow Başlat", type="primary"):
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown("### 📋 Klinik Workflow")
                    
                    for i, step in enumerate(CLINICAL_WORKFLOW["branches"][branch]["workflow_steps"]):
                        st.markdown(f'<div class="workflow-step active">', unsafe_allow_html=True)
                        st.markdown(f"**{i+1}. {step}**")
                        st.markdown('</div>', unsafe_allow_html=True)
                        time.sleep(0.5)
                    
                    st.success("✅ Workflow tamamlandı!")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ ICD kodu tanınmadı. Lütfen geçerli bir ICD-10 kodu girin.")
    
    elif input_method == "Sesli Giriş" and WHISPER_AVAILABLE:
        st.markdown('<div class="voice-input-box">', unsafe_allow_html=True)
        st.markdown("### 🎤 Sesli ICD Kod Girişi")
        
        # Whisper widget
        audio_data = create_whisper_widget()
        
        if audio_data:
            st.success("🎤 Ses kaydedildi! Transkripsiyon işleniyor...")
            
            # Basit regex ile ICD kod çıkarma
            import re
            icd_pattern = r'[A-Z]\d{2}\.?\d*'
            icd_codes = re.findall(icd_pattern, audio_data)
            
            if icd_codes:
                st.success(f"✅ Tespit edilen ICD kodları: {', '.join(icd_codes)}")
                icd_code = icd_codes[0]  # İlk kodu kullan
            else:
                st.warning("⚠️ ICD kodu tespit edilemedi. Lütfen tekrar deneyin.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif input_method == "Sesli Giriş" and not WHISPER_AVAILABLE:
        st.error("❌ Whisper Engine mevcut değil. Manuel giriş kullanın.")

with col2:
    st.markdown("### 📊 Sistem Durumu")
    
    # Sistem metrikleri
    st.metric("Aktif Workflow", "0", "0")
    st.metric("Tamamlanan Analiz", "0", "0")
    st.metric("GRADE Değerlendirme", "0", "0")
    
    st.markdown("### 🏥 Branş Seçimi")
    
    # Branş seçimi
    selected_branch = st.selectbox(
        "Branş:",
        list(CLINICAL_WORKFLOW["branches"].keys()),
        format_func=lambda x: CLINICAL_WORKFLOW["branches"][x]["name"]
    )
    
    if selected_branch:
        st.markdown(f"**{CLINICAL_WORKFLOW['branches'][selected_branch]['name']}**")
        st.markdown(f"ICD Kodları: {', '.join(CLINICAL_WORKFLOW['branches'][selected_branch]['icd_codes'])}")
        
        st.markdown("### 📋 Workflow Adımları")
        for i, step in enumerate(CLINICAL_WORKFLOW["branches"][selected_branch]["workflow_steps"]):
            st.markdown(f"{i+1}. {step}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🏥 Clinical Decision Support - NeuroPETRIX v3.0</p>
    <p>ICD-10 tabanlı klinik karar destek sistemi</p>
</div>
""", unsafe_allow_html=True)
