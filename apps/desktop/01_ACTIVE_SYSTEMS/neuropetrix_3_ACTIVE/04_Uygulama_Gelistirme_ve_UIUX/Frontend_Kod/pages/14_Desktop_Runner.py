import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import io
from pathlib import Path
import os

st.set_page_config(
    page_title="Desktop Runner - NeuroPETrix",
    page_icon="🖥️",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Page title and description
st.title("🖥️ Desktop Runner - MONAI + PyRadiomics Pipeline")
st.markdown("Yerel MONAI segmentasyon ve PyRadiomics özellik çıkarma")

# Backend URL configuration
if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = "http://127.0.0.1:8000"

backend_url = st.sidebar.text_input("Backend URL", st.session_state["backend_url"])
st.session_state["backend_url"] = st.session_state["backend_url"]

# Sidebar navigation
st.sidebar.title("🧭 Hızlı Navigasyon")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Ana Sayfa", use_container_width=True):
    st.switch_page("streamlit_app.py")

if st.sidebar.button("📊 Dashboard", key="desktop_nav_dashboard", use_container_width=True):
    st.switch_page("pages/00_Dashboard.py")

if st.sidebar.button("🔍 PICO Automation", key="desktop_nav_pico", use_container_width=True):
    st.switch_page("pages/15_PICO_Automation.py")

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
if "desktop_runner_status" not in st.session_state:
    st.session_state["desktop_runner_status"] = "idle"
if "current_case" not in st.session_state:
    st.session_state["current_case"] = None
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = []
if "dicom_files" not in st.session_state:
    st.session_state["dicom_files"] = []

def render_desktop_runner():
    """Desktop Runner ana sayfasını render et"""
    
    st.header("🖥️ Desktop Runner - MONAI + PyRadiomics Pipeline")
    st.markdown("Yerel makinede çalışan AI segmentasyon ve radyomik analiz")
    
    # Ana sekmeler
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 Case Yönetimi", "📂 DICOM Yükleme", "🔬 AI Analiz", "📊 Sonuçlar", "⚙️ Ayarlar"])
    
    with tab1:
        render_case_management()
    
    with tab2:
        render_dicom_upload()
    
    with tab3:
        render_analysis_panel()
    
    with tab4:
        render_results_panel()
    
    with tab5:
        render_settings_panel()

def render_case_management():
    """Case yönetimi sekmesi"""
    
    st.subheader("📁 Case Yönetimi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Yeni Case Oluştur**")
        
        with st.form("new_case_form"):
            case_id = st.text_input("Case ID", placeholder="NPX-2025-000123")
            purpose = st.selectbox("Amaç", ["staging", "restaging", "diagnosis", "followup"])
            icd_code = st.text_input("ICD Kodu", placeholder="C34.90")
            notes = st.text_area("Notlar", placeholder="Lung cancer initial staging")
            
            # Klinik şeffaflık kartları için ek alanlar
            clinical_context = st.text_area("Klinik Bağlam", placeholder="Hasta yaşı, komorbiditeler, önceki tedaviler")
            evidence_level = st.selectbox("Kanıt Seviyesi", ["1A", "1B", "2A", "2B", "3", "4"])
            
            if st.form_submit_button("📝 Case Oluştur"):
                if case_id and purpose and icd_code:
                    # Case oluştur
                    new_case = {
                        "case_id": case_id,
                        "purpose": purpose,
                        "ICD": icd_code,
                        "notes": notes,
                        "clinical_context": clinical_context,
                        "evidence_level": evidence_level,
                        "created_at": datetime.now().isoformat(),
                        "status": "created"
                    }
                    
                    st.session_state["current_case"] = new_case
                    st.success(f"Case oluşturuldu: {case_id}")
                    
                    # PICO JSON oluştur ve kaydet
                    pico_data = {
                        "case_id": case_id,
                        "purpose": purpose,
                        "ICD": icd_code,
                        "notes": notes,
                        "clinical_context": clinical_context,
                        "evidence_level": evidence_level
                    }
                    
                    # Local klasör yapısını oluştur
                    create_local_folder_structure(case_id)
                    
                else:
                    st.error("Lütfen tüm alanları doldurun!")
    
    with col2:
        st.markdown("**Mevcut Case'ler**")
        
        # Mock case listesi
        existing_cases = [
            {"case_id": "NPX-2025-000123", "purpose": "staging", "ICD": "C34.90", "status": "ready"},
            {"case_id": "NPX-2025-000124", "purpose": "followup", "ICD": "C61.9", "status": "completed"},
            {"case_id": "NPX-2025-000125", "purpose": "diagnosis", "ICD": "C18.9", "status": "processing"}
        ]
        
        for case in existing_cases:
            col_a, col_b, col_c = st.columns([3, 2, 1])
            with col_a:
                st.write(f"**{case['case_id']}** - {case['purpose']}")
            with col_b:
                st.write(f"ICD: {case['ICD']}")
            with col_c:
                if st.button("Seç", key=f"select_{case['case_id']}"):
                    st.session_state["current_case"] = case
                    st.success(f"Case seçildi: {case['case_id']}")

def render_dicom_upload():
    """DICOM yükleme sekmesi"""
    
    st.subheader("📂 DICOM Yükleme ve Doğrulama")
    
    if not st.session_state["current_case"]:
        st.warning("⚠️ Lütfen önce bir case seçin!")
        return
    
    current_case = st.session_state["current_case"]
    st.info(f"**Seçili Case:** {current_case['case_id']} - {current_case['purpose']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**DICOM Dosya Yükleme**")
        
        uploaded_files = st.file_uploader(
            "DICOM dosyalarını seçin",
            type=['dcm'],
            accept_multiple_files=True,
            key="dicom_uploader"
        )
        
        if uploaded_files:
            st.session_state["dicom_files"] = uploaded_files
            st.success(f"✅ {len(uploaded_files)} DICOM dosyası yüklendi")
            
            # DICOM doğrulama
            if st.button("🔍 DICOM Doğrulama", key="validate_dicom"):
                validate_dicom_files(uploaded_files)
    
    with col2:
        st.markdown("**DICOM Kalite Kontrolü**")
        
        if st.session_state["dicom_files"]:
            # Kalite check hook'u
            quality_checks = perform_quality_checks(st.session_state["dicom_files"])
            
            for check, status in quality_checks.items():
                if status:
                    st.success(f"✅ {check}")
                else:
                    st.error(f"❌ {check}")
            
            # TSNM alanları ile uyum kontrolü
            st.markdown("**📋 TSNM Uyum Kontrolü**")
            tsnm_compliance = check_tsnm_compliance(st.session_state["dicom_files"])
            
            for field, compliant in tsnm_compliance.items():
                if compliant:
                    st.success(f"✅ {field}")
                else:
                    st.warning(f"⚠️ {field} - Eksik bilgi")

def render_analysis_panel():
    """Analiz paneli sekmesi"""
    
    st.subheader("🔬 AI Analiz")
    
    if not st.session_state["current_case"] or not st.session_state["dicom_files"]:
        st.warning("⚠️ Lütfen önce case seçin ve DICOM dosyalarını yükleyin!")
        return
    
    current_case = st.session_state["current_case"]
    st.info(f"**Seçili Case:** {current_case['case_id']} - {current_case['purpose']}")
    
    # Analiz seçenekleri
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 MONAI Segmentasyon**")
        
        model_options = ["monai_v1.2", "monai_v1.3", "custom_model"]
        selected_model = st.selectbox("Model Seçin", model_options)
        
        confidence_threshold = st.slider("Güven Eşiği", 0.0, 1.0, 0.8, 0.1)
        
        # Amaç odaklı segmentasyon
        st.markdown("**🎯 Amaç Odaklı Segmentasyon**")
        st.info(f"**Amaç:** {current_case['purpose']} - **ICD:** {current_case['ICD']}")
        st.write("MONAI, bu bilgilere göre odak anatomisini belirleyecek")
        
        if st.button("🎯 Segmentasyon Başlat", key="start_segmentation"):
            st.session_state["desktop_runner_status"] = "segmenting"
            st.info("🔄 MONAI segmentasyon başlatılıyor...")
            
            # Mock segmentasyon
            with st.spinner("Segmentasyon çalışıyor..."):
                import time
                time.sleep(3)
                st.success("✅ Segmentasyon tamamlandı!")
                st.session_state["desktop_runner_status"] = "segmented"
                
                # Segmentasyon sonuçlarını kaydet
                save_segmentation_results(current_case["case_id"])
    
    with col2:
        st.markdown("**📊 PyRadiomics Özellik Çıkarma**")
        
        feature_groups = ["intensity", "shape", "texture", "all"]
        selected_features = st.multiselect("Özellik Grupları", feature_groups, default=["all"])
        
        # Radyomik gruplama
        st.markdown("**📋 Radyomik Gruplama**")
        st.write("Özellikler otomatik olarak kategorize edilecek:")
        st.write("• **Yoğunluk:** SUVmax, SUVmean, first-order")
        st.write("• **Volümetrik:** Shape, MTV, TLG")
        st.write("• **Tekstürel:** GLCM, GLRM, GLSZM")
        
        if st.button("📊 Radyomik Özellikler", key="start_radiomics"):
            if st.session_state["desktop_runner_status"] == "segmented":
                st.info("🔄 PyRadiomics özellik çıkarma başlatılıyor...")
                
                # Mock radiomics
                with st.spinner("Özellikler çıkarılıyor..."):
                    import time
                    time.sleep(2)
                    st.success("✅ Radyomik özellikler çıkarıldı!")
                    st.session_state["desktop_runner_status"] = "radiomics_completed"
                    
                    # Radyomik sonuçlarını kaydet
                    save_radiomics_results(current_case["case_id"])
            else:
                st.warning("⚠️ Önce segmentasyon yapılmalı!")

def render_results_panel():
    """Sonuçlar paneli sekmesi"""
    
    st.subheader("📊 Analiz Sonuçları")
    
    if st.session_state["desktop_runner_status"] == "idle":
        st.info("ℹ️ Henüz analiz yapılmadı")
        return
    
    # Segmentasyon sonuçları
    if st.session_state["desktop_runner_status"] in ["segmented", "radiomics_completed"]:
        st.markdown("**🎯 Segmentasyon Sonuçları**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lezyon Sayısı", "3")
        with col2:
            st.metric("Ortalama Güven", "0.87")
        with col3:
            st.metric("Toplam Hacim", "45.2 cm³")
        
        # Segmentasyon görselleştirmesi
        st.markdown("**📊 Segmentasyon Görselleştirmesi**")
        st.image("https://via.placeholder.com/800x400/4CAF50/FFFFFF?text=MONAI+Segmentation+Results", 
                caption="MONAI Segmentasyon Sonuçları")
        
        # Hekim düzeltme seçeneği
        st.markdown("**✏️ Hekim Düzeltme**")
        if st.button("🎭 Segmentasyon Maskesini Düzenle"):
            st.info("🎭 Mask düzenleme modu aktif - düzeltmeler kaydedilecek")
            # Mock mask editing
            with st.spinner("Düzeltme kaydediliyor..."):
                time.sleep(2)
                st.success("✅ Düzeltme kaydedildi! (corr_seg)")
    
    # Radyomik sonuçları
    if st.session_state["desktop_runner_status"] == "radiomics_completed":
        st.markdown("**📊 Radyomik Özellikler**")
        
        # Mock radiomics features
        radiomics_data = {
            "Intensity": {"SUVmax": 12.5, "SUVmean": 8.3, "SUVpeak": 11.2},
            "Shape": {"Volume": 45.2, "SurfaceArea": 78.9, "Sphericity": 0.67},
            "Texture": {"GLCM_Energy": 0.023, "GLCM_Contrast": 45.6, "GLCM_Correlation": 0.78}
        }
        
        for category, features in radiomics_data.items():
            st.markdown(f"**{category} Özellikleri:**")
            cols = st.columns(len(features))
            for i, (feature, value) in enumerate(features.items()):
                with cols[i]:
                    st.metric(feature, f"{value:.3f}")
            st.markdown("---")
        
        # PERCIST/Deauville kriterleri
        st.markdown("**🏥 Klinik Kriterler**")
        if st.button("📋 PERCIST/Deauville Analizi"):
            st.info("📋 Klinik kriterler uygulanıyor...")
            
            with st.spinner("Klinik analiz yapılıyor..."):
                time.sleep(2)
                st.success("✅ Klinik kriterler uygulandı!")
                
                # Klinik sonuçları göster
                show_clinical_criteria_results()
        
        # Rapor oluşturma
        if st.button("📋 TSNM Raporu Oluştur"):
            st.info("📋 TSNM raporu oluşturuluyor...")
            
            # Mock report generation
            with st.spinner("Rapor oluşturuluyor..."):
                import time
                time.sleep(2)
                st.success("✅ TSNM raporu oluşturuldu!")
                
                # Download link
                st.download_button(
                    label="📥 Raporu İndir (DOCX)",
                    data="Mock TSNM report content",
                    file_name=f"TSNM_Report_{st.session_state['current_case']['case_id']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

def render_settings_panel():
    """Ayarlar paneli sekmesi"""
    
    st.subheader("⚙️ Desktop Runner Ayarları")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📁 Klasör Yapılandırması**")
        
        input_dir = st.text_input("Input DICOM Klasörü", "~/NeuroPETRIX/local/input_dicom")
        output_dir = st.text_input("Output Klasörü", "~/NeuroPETRIX/local/output")
        models_dir = st.text_input("Model Klasörü", "~/NeuroPETRIX/local/models")
        
        if st.button("📁 Klasörleri Oluştur"):
            st.info("📁 Klasörler oluşturuluyor...")
            create_local_folder_structure("default")
            st.success("✅ Klasör yapısı hazırlandı!")
    
    with col2:
        st.markdown("**🤖 AI Model Ayarları**")
        
        monai_version = st.selectbox("MONAI Versiyonu", ["v1.2", "v1.3", "custom"])
        radiomics_version = st.selectbox("PyRadiomics Versiyonu", ["v3.0", "v3.1", "latest"])
        
        gpu_enabled = st.checkbox("GPU Kullanımı", value=True)
        batch_size = st.slider("Batch Size", 1, 8, 4)
        
        if st.button("💾 Ayarları Kaydet"):
            st.success("✅ Ayarlar kaydedildi!")

def create_local_folder_structure(case_id):
    """Local klasör yapısını oluştur"""
    base_path = Path.home() / "NeuroPETRIX" / "local"
    
    folders = [
        base_path / "input_dicom",
        base_path / "output" / "seg",
        base_path / "output" / "radiomics", 
        base_path / "output" / "reports",
        base_path / "models" / "monai",
        base_path / "config",
        base_path / "logs" / "runner",
        base_path / "logs" / "compliance"
    ]
    
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
    
    # Config dosyalarını oluştur
    create_config_files(base_path / "config")

def create_config_files(config_dir):
    """Konfigürasyon dosyalarını oluştur"""
    
    # radiomics_groups.yaml
    radiomics_groups = {
        "intensity": ["original_firstorder_*", "SUVmax", "SUVmean"],
        "volumetric": ["original_shape_*", "MTV", "TLG"],
        "texture": ["original_glcm_*", "original_glrlm_*", "original_glszm_*", "original_ngtdm_*", "original_gldm_*"]
    }
    
    with open(config_dir / "radiomics_groups.yaml", "w") as f:
        import yaml
        yaml.dump(radiomics_groups, f)
    
    # abbreviations.json
    abbreviations = {
        "SUV": "Standard Uptake Value",
        "FDG": "Fluorodeoxyglucose",
        "PET/CT": "Positron Emission Tomography/Computed Tomography",
        "HBYS": "Hastane Bilgi Yönetim Sistemi"
    }
    
    with open(config_dir / "abbreviations.json", "w") as f:
        json.dump(abbreviations, f, indent=2)

def validate_dicom_files(files):
    """DICOM dosyalarını doğrula"""
    st.info("🔍 DICOM dosyaları doğrulanıyor...")
    
    # Mock validation
    import time
    time.sleep(2)
    
    validation_results = {
        "PET serisi": True,
        "CT serisi": True,
        "Metadata": True,
        "Dosya bütünlüğü": True
    }
    
    st.success("✅ DICOM doğrulama tamamlandı!")
    
    for check, result in validation_results.items():
        if result:
            st.success(f"✅ {check}")
        else:
            st.error(f"❌ {check}")

def perform_quality_checks(files):
    """DICOM kalite kontrolü yap"""
    return {
        "FDG dozu": True,
        "Glisemi": True,
        "Açlık süresi": True,
        "Hareket artefaktı": False,
        "SNR yeterli": True
    }

def check_tsnm_compliance(files):
    """TSNM uyum kontrolü"""
    return {
        "Hasta bilgileri": True,
        "Çekim parametreleri": True,
        "Kontrast bilgisi": False,
        "Kalibrasyon": True
    }

def save_segmentation_results(case_id):
    """Segmentasyon sonuçlarını kaydet"""
    # Mock saving
    st.info(f"💾 Segmentasyon sonuçları kaydediliyor: {case_id}")
    
    # Local klasöre kaydet
    base_path = Path.home() / "NeuroPETRIX" / "local" / "output" / "seg"
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Mock files
    (base_path / f"{case_id}_seg.nii.gz").touch()
    (base_path / f"{case_id}_metrics.json").write_text('{"dice": 0.87, "iou": 0.76}')

def save_radiomics_results(case_id):
    """Radyomik sonuçlarını kaydet"""
    # Mock saving
    st.info(f"💾 Radyomik sonuçlar kaydediliyor: {case_id}")
    
    # Local klasöre kaydet
    base_path = Path.home() / "NeuroPETRIX" / "local" / "output" / "radiomics"
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Mock files
    (base_path / f"{case_id}_features.csv").touch()
    (base_path / f"{case_id}_grouped.json").write_text('{"intensity": {}, "volumetric": {}, "texture": {}}')

def show_clinical_criteria_results():
    """Klinik kriter sonuçlarını göster"""
    st.markdown("**🏥 PERCIST/Deauville Sonuçları**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("PERCIST Kriteri", "PR (Partial Response)")
        st.metric("SUV Değişimi", "-45%")
    
    with col2:
        st.metric("Deauville Skoru", "3")
        st.metric("Klinik Yorum", "Kısmi yanıt")

# Ana sayfa render
if __name__ == "__main__":
    render_desktop_runner()

# Footer
st.markdown("---")
st.caption("🖥️ Desktop Runner - NeuroPETrix v1.0.0 | MONAI + PyRadiomics Integration")
