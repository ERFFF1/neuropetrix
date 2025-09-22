import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import requests

st.set_page_config(
    page_title="Veri Girişi ve DICOM Upload - NeuroPETrix",
    page_icon="📁",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Page title and description
st.title("📁 Çoklu Veri Girişi ve DICOM İşleme Merkezi")
st.markdown("**DICOM • Manuel Veri • AI Destekli Analiz** - PET/CT Görüntü İşleme ve Parametre Analizi")

# Backend URL configuration
if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = "http://127.0.0.1:8000"

backend_url = st.sidebar.text_input("Backend URL", st.session_state["backend_url"])
st.session_state["backend_url"] = backend_url

# Sidebar navigation
st.sidebar.title("🧭 Hızlı Navigasyon")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Ana Sayfa", use_container_width=True):
    st.switch_page("streamlit_app.py")

if st.sidebar.button("📊 Dashboard", use_container_width=True):
    st.switch_page("pages/00_Dashboard.py")

if st.sidebar.button("🏥 HBYS Integration", use_container_width=True):
    st.switch_page("pages/03_HBYS_Entegrasyon.py")

if st.sidebar.button("🤖 AI Analysis", use_container_width=True):
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

# ---- DARK MODE TOGGLE - SAĞ ÜSTTE KÜÇÜK SİMGE ----
col_header1, col_header2, col_header3 = st.columns([3, 1, 1])

with col_header1:
    st.markdown("""
    <div class="hero">
        <div>
            <h1>🔬 Çoklu Veri Girişi Merkezi</h1>
            <div class="subtitle">DICOM dosyaları, manuel veri girişi ve AI destekli analiz seçenekleri</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_header2:
    st.write("")  # Spacer
    st.write("")  # Spacer
    
    # Dark Mode Toggle - Küçük simge
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False
    
    if st.button("🌙" if not st.session_state["dark_mode"] else "☀️", 
                 key="dark_mode_toggle", 
                 help="Dark/Light Mode Toggle"):
        st.session_state["dark_mode"] = not st.session_state["dark_mode"]
        st.rerun()

with col_header3:
    st.write("")  # Spacer
    st.write("")  # Spacer
    
    # Workflow Status
    if st.session_state.get("current_workflow_step"):
        st.info(f"📊 Adım: {st.session_state['current_workflow_step']}/7")

st.write("")

# ---- HASTA KONTROLÜ ----
if not st.session_state.get("current_patient"):
    st.error("⚠️ Önce hasta bilgilerini girin!")
    col_patient1, col_patient2 = st.columns([2, 1])
    
    with col_patient1:
        st.info("🔍 Hasta bilgileri olmadan veri girişi yapılamaz.")
        st.markdown("**Gerekli adımlar:**")
        st.markdown("1. 🏥 HBYS Integration sayfasına gidin")
        st.markdown("2. 👤 Yeni hasta ekleyin veya demo hasta oluşturun")
        st.markdown("3. 📁 Bu sayfaya geri dönün")
    
    with col_patient2:
        if st.button("🏥 HBYS'e Git", type="primary", use_container_width=True):
            st.switch_page("pages/03_HBYS_Entegrasyon.py")
    
    st.stop()

# Display current patient info
patient = st.session_state["current_patient"]
st.header(f"👤 Hasta: {patient['ad_soyad']} - {patient['icd_kodu']}")

col_patient_info1, col_patient_info2, col_patient_info3 = st.columns(3)

with col_patient_info1:
    st.markdown("**📋 Temel Bilgiler:**")
    st.markdown(f"• Hasta No: {patient['hasta_no']}")
    st.markdown(f"• Yaş: {patient['yas']}")
    st.markdown(f"• Cinsiyet: {patient['cinsiyet']}")

with col_patient_info2:
    st.markdown("**🏥 Klinik Bilgiler:**")
    st.markdown(f"• ICD: {patient['icd_kodu']}")
    st.markdown(f"• Hedef: {patient['klinik_karar_hedefi']}")
    st.markdown(f"• Tanı: {patient['klinik_tani']}")

with col_patient_info3:
    st.markdown("**🎯 İş Akışı:**")
    st.markdown(f"• Adım: {st.session_state.get('workflow_step', 1)}/4")
    st.markdown(f"• Durum: Veri Toplama")
    st.markdown(f"• Sonraki: Final PICO")

st.write("")

# ---- ÇOKLU VERİ GİRİŞİ SEÇENEKLERİ ----
st.header("📊 Veri Girişi Seçenekleri")

# Tab selection for different data input methods
tab1, tab2, tab3, tab4 = st.tabs([
    "📁 DICOM Dosya Yükleme", 
    "✏️ Manuel Veri Girişi", 
    "🤖 AI Destekli Veri", 
    "📊 Veri Önizleme"
])

# ---- TAB 1: DICOM DOSYA YÜKLEME ----
with tab1:
    st.subheader("📁 DICOM Dosya Yükleme ve İşleme")
    
    col_dicom1, col_dicom2 = st.columns([2, 1])
    
    with col_dicom1:
        st.markdown("**📂 DICOM Dosya Seçimi:**")
        
        # Multiple file upload
        uploaded_files = st.file_uploader(
            "DICOM dosyalarını seçin (birden fazla seçebilirsiniz)",
            type=['dcm', 'dicom'],
            accept_multiple_files=True,
            help="DICOM dosyalarını sürükleyip bırakın veya seçin"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} DICOM dosyası yüklendi!")
            
            # File info display
            for i, file in enumerate(uploaded_files):
                st.markdown(f"**Dosya {i+1}:** {file.name} ({file.size} bytes)")
            
            # DICOM processing options
            st.subheader("🔧 DICOM İşleme Seçenekleri")
            
            col_process1, col_process2 = st.columns(2)
            
            with col_process1:
                st.markdown("**📊 Görüntü İşleme:**")
                st.checkbox("✅ Görüntü kalitesi kontrolü", value=True)
                st.checkbox("✅ Gürültü azaltma", value=True)
                st.checkbox("✅ Kontrast iyileştirme", value=True)
                st.checkbox("✅ Segmentasyon hazırlığı", value=True)
            
            with col_process2:
                st.markdown("**🔬 PET/CT Parametreleri:**")
                st.checkbox("✅ SUV hesaplama", value=True)
                st.checkbox("✅ Hacim analizi", value=True)
                st.checkbox("✅ Metastaz tespiti", value=True)
                st.checkbox("✅ TNM evreleme", value=True)
            
            # Process button
            if st.button("🚀 DICOM İşlemeyi Başlat", type="primary"):
                st.info("🔄 DICOM dosyaları işleniyor...")
                
                # Mock processing
                import time
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(101):
                    time.sleep(0.05)
                    progress_bar.progress(i)
                    if i < 30:
                        status_text.text("📁 Dosyalar okunuyor...")
                    elif i < 60:
                        status_text.text("🔧 Görüntü işleniyor...")
                    elif i < 90:
                        status_text.text("📊 Parametreler hesaplanıyor...")
                    else:
                        status_text.text("✅ İşlem tamamlandı!")
                
                st.success("🎉 DICOM işleme başarıyla tamamlandı!")
                st.session_state["dicom_processed"] = True
                st.session_state["current_workflow_step"] = 3
    
    with col_dicom2:
        st.subheader("📊 DICOM Durumu")
        
        if st.session_state.get("dicom_processed"):
            st.success("✅ DICOM işlendi")
            st.info("🚀 AI analizi için hazır")
        else:
            st.warning("⚠️ DICOM bekleniyor")
        
        # DICOM metadata preview
        if uploaded_files:
            st.subheader("📋 Dosya Bilgileri")
            for file in uploaded_files[:3]:  # Show first 3 files
                st.markdown(f"• **{file.name}**")
                st.markdown(f"  - Boyut: {file.size:,} bytes")
                st.markdown(f"  - Tip: DICOM")
        
        # Quick actions
        st.subheader("🚀 Hızlı İşlemler")
        
        if st.button("📊 AI Analizi", use_container_width=True):
            st.switch_page("pages/05_AI_Analysis.py")

# ---- TAB 2: MANUEL VERİ GİRİŞİ ----
with tab2:
    st.subheader("✏️ Manuel Veri Girişi ve Parametre Analizi")
    
    col_manual1, col_manual2 = st.columns([2, 1])
    
    with col_manual1:
        st.markdown("**📊 PET/CT Parametreleri:**")
        
        # Manual data entry form
        with st.form("manual_data_form"):
            col_param1, col_param2 = st.columns(2)
            
            with col_param1:
                st.markdown("**🔬 PET Parametreleri:**")
                suv_max = st.number_input("SUVmax", min_value=0.0, max_value=50.0, value=8.5, step=0.1)
                suv_mean = st.number_input("SUVmean", min_value=0.0, max_value=50.0, value=6.2, step=0.1)
                suv_peak = st.number_input("SUVpeak", min_value=0.0, max_value=50.0, value=7.8, step=0.1)
                tbr = st.number_input("TBR (Tumor-to-Background Ratio)", min_value=0.0, max_value=20.0, value=3.5, step=0.1)
            
            with col_param2:
                st.markdown("**📏 Hacim Parametreleri:**")
                tumor_volume = st.number_input("Tümör Hacmi (cm³)", min_value=0.0, max_value=1000.0, value=45.2, step=0.1)
                lesion_count = st.number_input("Lezyon Sayısı", min_value=1, max_value=100, value=3)
                max_diameter = st.number_input("Maksimum Çap (cm)", min_value=0.0, max_value=50.0, value=2.8, step=0.1)
                location = st.selectbox("Lokasyon", ["Sağ üst lob", "Sol üst lob", "Sağ alt lob", "Sol alt lob", "Mediastinum"])
            
            st.markdown("**📊 CT Parametreleri:**")
            col_ct1, col_ct2 = st.columns(2)
            
            with col_ct1:
                ct_hu = st.number_input("CT HU Değeri", min_value=-1000, max_value=1000, value=45)
                calcification = st.checkbox("Kalsifikasyon var")
                cavitation = st.checkbox("Kavite var")
            
            with col_ct2:
                lymph_nodes = st.checkbox("Lenf nodu tutulumu")
                pleural_effusion = st.checkbox("Plevral efüzyon")
                bone_metastasis = st.checkbox("Kemik metastazı")
            
            # Additional clinical data
            st.markdown("**🏥 Klinik Ek Veriler:**")
            col_clinical1, col_clinical2 = st.columns(2)
            
            with col_clinical1:
                performance_status = st.selectbox("Performance Status", ["0", "1", "2", "3", "4"])
                weight_loss = st.number_input("Kilo Kaybı (%)", min_value=0, max_value=50, value=8)
                smoking_history = st.selectbox("Sigara Geçmişi", ["Hiç içmedi", "Bıraktı", "Aktif içici"])
            
            with col_ct2:
                comorbidities = st.multiselect("Komorbiditeler", ["DM", "HT", "KOAH", "Kardiyak", "Böbrek", "Karaciğer"])
                family_history = st.checkbox("Aile öyküsü var")
                previous_treatment = st.checkbox("Önceki tedavi var")
            
            # Form submit
            submitted = st.form_submit_button("💾 Verileri Kaydet", type="primary")
            
            if submitted:
                # Create manual data
                manual_data = {
                    "pet_params": {
                        "suv_max": suv_max,
                        "suv_mean": suv_mean,
                        "suv_peak": suv_peak,
                        "tbr": tbr
                    },
                    "volume_params": {
                        "tumor_volume": tumor_volume,
                        "lesion_count": lesion_count,
                        "max_diameter": max_diameter,
                        "location": location
                    },
                    "ct_params": {
                        "ct_hu": ct_hu,
                        "calcification": calcification,
                        "cavitation": cavitation,
                        "lymph_nodes": lymph_nodes,
                        "pleural_effusion": pleural_effusion,
                        "bone_metastasis": bone_metastasis
                    },
                    "clinical_params": {
                        "performance_status": performance_status,
                        "weight_loss": weight_loss,
                        "smoking_history": smoking_history,
                        "comorbidities": comorbidities,
                        "family_history": family_history,
                        "previous_treatment": previous_treatment
                    },
                    "created_at": datetime.now().isoformat()
                }
                
                # Save to session state
                st.session_state["manual_data"] = manual_data
                st.session_state["data_source"] = "manual"
                st.session_state["current_workflow_step"] = 3
                
                st.success("✅ Manuel veriler başarıyla kaydedildi!")
                st.info("🚀 AI analizi için hazır!")
    
    with col_manual2:
        st.subheader("📊 Veri Durumu")
        
        if st.session_state.get("manual_data"):
            st.success("✅ Manuel veri mevcut")
            st.info("🚀 AI analizi için hazır")
        else:
            st.warning("⚠️ Manuel veri bekleniyor")
        
        # Data summary
        if st.session_state.get("manual_data"):
            data = st.session_state["manual_data"]
            st.markdown("**📋 Veri Özeti:**")
            st.markdown(f"• SUVmax: {data['pet_params']['suv_max']}")
            st.markdown(f"• Tümör Hacmi: {data['volume_params']['tumor_volume']} cm³")
            st.markdown(f"• Lezyon Sayısı: {data['volume_params']['lesion_count']}")
            st.markdown(f"• Lokasyon: {data['volume_params']['location']}")

# ---- TAB 3: AI DESTEKLİ VERİ ----
with tab3:
    st.subheader("🤖 AI Destekli Veri İşleme ve Analiz")
    
    col_ai1, col_ai2 = st.columns([2, 1])
    
    with col_ai1:
        st.markdown("**🧠 AI Destekli Veri İşleme Seçenekleri:**")
        
        # AI processing options
        ai_options = st.multiselect(
            "AI İşlem Seçenekleri:",
            [
                "🔍 Otomatik lezyon tespiti",
                "📊 SUV hesaplama optimizasyonu",
                "🎯 Metastaz risk skorlaması",
                "📏 Hacim hesaplama",
                "🔬 Radiomics özellik çıkarma",
                "📈 Prognostik skorlama",
                "💊 Tedavi yanıtı tahmini",
                "📊 Literatür karşılaştırması"
            ],
            default=["🔍 Otomatik lezyon tespiti", "📊 SUV hesaplama optimizasyonu", "🎯 Metastaz risk skorlaması"]
        )
        
        if ai_options:
            st.info(f"🤖 {len(ai_options)} AI işlem seçildi")
            
            # AI processing parameters
            st.subheader("⚙️ AI İşlem Parametreleri")
            
            col_ai_param1, col_ai_param2 = st.columns(2)
            
            with col_ai_param1:
                confidence_threshold = st.slider("Güven Eşiği (%)", 0, 100, 80)
                processing_quality = st.selectbox("İşlem Kalitesi", ["Hızlı", "Standart", "Yüksek"], index=1)
                auto_correction = st.checkbox("Otomatik düzeltme", value=True)
            
            with col_ai_param2:
                validation_method = st.selectbox("Doğrulama Yöntemi", ["Cross-validation", "Hold-out", "Bootstrap"])
                uncertainty_estimation = st.checkbox("Belirsizlik tahmini", value=True)
                explainability = st.checkbox("Açıklanabilirlik", value=True)
            
            # Start AI processing
            if st.button("🚀 AI İşlemi Başlat", type="primary"):
                st.info("🤖 AI işlemi başlatılıyor...")
                
                # Mock AI processing
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(101):
                    time.sleep(0.03)
                    progress_bar.progress(i)
                    if i < 25:
                        status_text.text("🔍 Lezyon tespiti yapılıyor...")
                    elif i < 50:
                        status_text.text("📊 SUV hesaplanıyor...")
                    elif i < 75:
                        status_text.text("🎯 Risk skorlaması...")
                    elif i < 95:
                        status_text.text("📈 Sonuçlar analiz ediliyor...")
                    else:
                        status_text.text("✅ AI işlemi tamamlandı!")
                
                st.success("🎉 AI destekli veri işleme tamamlandı!")
                st.session_state["ai_processed"] = True
                st.session_state["current_workflow_step"] = 4
                
                # Show AI results
                st.subheader("📊 AI Analiz Sonuçları")
                
                col_results1, col_results2 = st.columns(2)
                
                with col_results1:
                    st.markdown("**🎯 Lezyon Tespiti:**")
                    st.success("✅ 3 lezyon tespit edildi")
                    st.info("🔍 Güven: 92%")
                    st.warning("⚠️ 1 şüpheli alan")
                
                with col_results2:
                    st.markdown("**📊 Risk Skorlaması:**")
                    st.error("🔴 Yüksek risk: 78%")
                    st.info("📈 Metastaz olasılığı: 65%")
                    st.success("💊 Tedavi yanıtı: İyi")
    
    with col_ai2:
        st.subheader("🤖 AI Durumu")
        
        if st.session_state.get("ai_processed"):
            st.success("✅ AI işlemi tamamlandı")
            st.info("🚀 Sonuç değerlendirmesi için hazır")
        else:
            st.warning("⚠️ AI işlemi bekleniyor")
        
        # AI processing summary
        if ai_options:
            st.markdown("**📋 Seçilen İşlemler:**")
            for option in ai_options:
                st.markdown(f"• {option}")
        
        # Quick actions
        st.subheader("🚀 Hızlı İşlemler")
        
        if st.button("📊 Sonuç Değerlendirme", use_container_width=True):
            st.switch_page("pages/05_AI_Analysis.py")

# ---- TAB 4: VERİ ÖNİZLEME ----
with tab4:
    st.subheader("📊 Veri Önizleme ve Durum Kontrolü")
    
    col_preview1, col_preview2 = st.columns([2, 1])
    
    with col_preview1:
        # Data source summary
        st.markdown("**📋 Veri Kaynakları:**")
        
        data_sources = []
        if st.session_state.get("dicom_processed"):
            data_sources.append("✅ DICOM Dosyaları")
        if st.session_state.get("manual_data"):
            data_sources.append("✅ Manuel Veri")
        if st.session_state.get("ai_processed"):
            data_sources.append("✅ AI İşlemi")
        
        if data_sources:
            for source in data_sources:
                st.markdown(f"• {source}")
        else:
            st.warning("⚠️ Henüz veri kaynağı yok")
        
        # Data quality assessment
        if data_sources:
            st.subheader("🔍 Veri Kalite Değerlendirmesi")
            
            # Mock quality assessment
            quality_scores = {
                "Veri Bütünlüğü": 95,
                "Görüntü Kalitesi": 88,
                "Parametre Doğruluğu": 92,
                "AI İşlem Kalitesi": 89
            }
            
            for metric, score in quality_scores.items():
                if score >= 90:
                    st.success(f"✅ {metric}: {score}%")
                elif score >= 80:
                    st.warning(f"⚠️ {metric}: {score}%")
                else:
                    st.error(f"❌ {metric}: {score}%")
            
            # Overall quality
            overall_quality = sum(quality_scores.values()) / len(quality_scores)
            st.metric("📊 Genel Kalite Skoru", f"{overall_quality:.1f}%")
            
            if overall_quality >= 90:
                st.success("🎉 Veri kalitesi mükemmel! AI analizi için hazır!")
            elif overall_quality >= 80:
                st.warning("⚠️ Veri kalitesi iyi, ancak iyileştirme önerilir")
            else:
                st.error("❌ Veri kalitesi düşük, yeniden işlem gerekli")
    
    with col_preview2:
        st.subheader("📊 İş Akışı Durumu")
        
        current_step = st.session_state.get("current_workflow_step", 1)
        steps = [
            "✅ Hasta Kaydı",
            "🔍 PICO Oluşturma",
            "📁 Veri Girişi",
            "🤖 AI Analizi",
            "📊 Sonuç Değerlendirme",
            "📝 Rapor Oluşturma",
            "🎯 Klinik Karar"
        ]
        
        for i, step in enumerate(steps, 1):
            if i <= current_step:
                st.success(step)
            elif i == current_step + 1:
                st.info(step)
            else:
                st.markdown(f"⏳ {step}")
        
        # Next step recommendation
        if current_step >= 3:
            st.subheader("🚀 Sonraki Adım")
            if st.button("🤖 AI Analizi Başlat", use_container_width=True):
                st.switch_page("pages/05_AI_Analysis.py")

# Footer
st.markdown("---")
st.markdown("**Çoklu Veri Girişi Merkezi** - DICOM, Manuel Veri ve AI Destekli İşleme")
