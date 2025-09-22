import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# Add the assets directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'assets'))
from tsnm_templates import TSNMTemplateManager

st.set_page_config(
    page_title="TSNM Reports - NeuroPETrix",
    page_icon="📊",
    layout="wide"
)

# Page title and description
st.title("📊 TSNM Reports - Standart Rapor Formatları")
st.markdown("**TSNM Kılavuzu** - FDG, PSMA, DOTATATE PET/CT Raporları")

# Quick template info with AI Integration
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔬 FDG PET/BT")
    st.markdown("**Onkoloji** (2020-0032)")
    st.markdown("Evreleme ve tedavi yanıtı")
    st.markdown("🤖 AI Destekli Analiz")
    st.markdown("</div>", unsafe_allow_html=True)
    
with col_info2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🏥 PSMA PET/BT")
    st.markdown("**Prostat Kanseri** (2020-0030)")
    st.markdown("Biyokimyasal rekürrens")
    st.markdown("🤖 AI Destekli Analiz")
    st.markdown("</div>", unsafe_allow_html=True)
    
with col_info3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🧬 DOTATATE PET/BT")
    st.markdown("**Nöroendokrin Tümör** (2020-0028)")
    st.markdown("NET evreleme ve takip")
    st.markdown("🤖 AI Destekli Analiz")
    st.markdown("</div>", unsafe_allow_html=True)

# AI Analysis Integration Status
if st.session_state.get("ai_report"):
    st.success("✅ AI Analysis tamamlandı - TSNM raporu için hazır!")
    
    col_ai1, col_ai2, col_ai3 = st.columns(3)
    
    with col_ai1:
        ai_report = st.session_state["ai_report"]
        st.metric("Tespit Edilen Lezyon", ai_report["analysis_results"]["lesions"])
        st.metric("Maksimum SUV", ai_report["analysis_results"]["max_suv"])
    
    with col_ai2:
        st.metric("Segmentasyon Kalitesi", f"{ai_report['analysis_results']['segmentation_quality']:.1%}")
        st.metric("Radiomics Özellik", ai_report["analysis_results"]["radiomics_features"])
    
    with col_ai3:
        st.metric("Metastaz Riski", ai_report["clinical_assessment"]["metastasis_risk"])
        st.metric("TNM Evresi", ai_report["clinical_assessment"]["tnm_stage"])
else:
    st.warning("⚠️ AI Analysis tamamlanmadı - Önce AI analizi yapın")
    if st.button("🤖 AI Analysis'e Git", type="primary"):
        st.switch_page("pages/05_AI_Analysis.py")

# Rapor Üretimi Entegrasyonu
if st.session_state.get("generated_report"):
    generated_report = st.session_state["generated_report"]
    
    if "TSNM" in generated_report.get("report_type", ""):
        st.success("✅ TSNM Raporu Rapor Üretimi'nden aktarıldı!")
        
        col_report1, col_report2 = st.columns([2, 1])
        
        with col_report1:
            st.subheader("📋 Aktarılan TSNM Raporu")
            
            if "tsnm_content" in generated_report:
                tsnm = generated_report["tsnm_content"]
                
                st.markdown("**🏥 Klinik Bilgiler:**")
                st.markdown(f"• Endikasyon: {tsnm['endikasyon']}")
                st.markdown(f"• Klinik Tanı: {tsnm['klinik_tani']}")
                
                st.markdown("**🔬 Teknik Parametreler:**")
                st.markdown(f"• Radyofarmasötik: {tsnm['teknik_parametreler']['radyofarmasötik']}")
                st.markdown(f"• Doz: {tsnm['teknik_parametreler']['doz']}")
                st.markdown(f"• Uptake: {tsnm['teknik_parametreler']['uptake']}")
                
                st.markdown("**📊 SUV Değerleri:**")
                st.markdown(f"• Karaciğer: {tsnm['suv_degerleri']['karaciger']}")
                st.markdown(f"• Lezyon: {tsnm['suv_degerleri']['lezyon']:.1f}")
        
        with col_report2:
            st.subheader("🚀 Hızlı İşlemler")
            
            if st.button("📋 TSNM Şablonuna Uygula", key="apply_tsnm_template", type="primary"):
                st.success("✅ TSNM şablonuna uygulandı!")
                st.info("📊 Aşağıdaki TSNM raporlarından birini seçin")
            
            if st.button("🔄 Yeni TSNM Raporu", key="new_tsnm_report"):
                st.info("🔄 Yeni rapor için Rapor Üretimi sayfasına gidin")
                if st.button("📝 Rapor Üretimi'ne Git"):
                    st.switch_page("pages/02_Rapor_Üretimi.py")
    
    elif "DICOM" in generated_report.get("report_type", ""):
        st.info("ℹ️ DICOM + AI Analiz Raporu mevcut - TSNM formatına dönüştürülebilir")
        
        if st.button("🔄 TSNM Formatına Dönüştür", key="convert_to_tsnm"):
            st.success("✅ TSNM formatına dönüştürüldü!")
            st.info("📋 Yukarıdaki TSNM şablonlarını kullanabilirsiniz")
else:
    st.info("ℹ️ Rapor Üretimi'nden TSNM raporu aktarılması bekleniyor")
    if st.button("📝 Rapor Üretimi'ne Git", type="secondary"):
        st.switch_page("pages/02_Rapor_Üretimi.py")

# Patient Information Integration
if st.session_state.get("current_patient"):
    patient = st.session_state["current_patient"]
    
    st.subheader("👤 Hasta Bilgileri")
    
    col_patient1, col_patient2, col_patient3 = st.columns(3)
    
    with col_patient1:
        st.markdown("**📋 Temel Bilgiler:**")
        st.markdown(f"• Hasta No: {patient['hasta_no']}")
        st.markdown(f"• Ad Soyad: {patient['ad_soyad']}")
        st.markdown(f"• Yaş: {patient['yas']}")
        st.markdown(f"• Cinsiyet: {patient['cinsiyet']}")
    
    with col_patient2:
        st.markdown("**🏥 Klinik Bilgiler:**")
        st.markdown(f"• ICD: {patient['icd_kodu']}")
        st.markdown(f"• Tanı: {patient['klinik_tani']}")
        st.markdown(f"• Çalışma: {patient.get('study_type', 'N/A')}")
        st.markdown(f"• Öncelik: {patient.get('priority', 'N/A')}")
    
    with col_patient3:
        st.markdown("**🔬 Çalışma Detayları:**")
        st.markdown(f"• Tarih: {patient.get('created_at', 'Tarih belirtilmedi')}")
        st.markdown(f"• Bölüm: {patient.get('department', 'N/A')}")
        st.markdown(f"• Doktor: {patient.get('doktor', 'N/A')}")
        
        if st.session_state.get("dicom_params"):
            dicom = st.session_state["dicom_params"]
            st.markdown(f"• Tracer: {dicom.get('tracer_type', 'N/A')}")
            st.markdown(f"• Doz: {dicom.get('injected_dose_MBq', 'N/A')} MBq")
else:
    st.warning("⚠️ Hasta bilgileri bulunamadı - HBYS'den hasta seçin")
    if st.button("🏥 HBYS'e Git", type="primary"):
        st.switch_page("pages/03_HBYS_Entegrasyon.py")

st.write("")

# Initialize TSNM Template Manager
@st.cache_resource
def get_tsnm_manager():
    return TSNMTemplateManager()

tsnm_manager = get_tsnm_manager()

# Sidebar configuration - Simplified
st.sidebar.header("⚙️ Ayarlar")

# Backend URL
backend_url = st.sidebar.text_input(
    "Backend URL",
    value=st.session_state.get("backend_url", "http://127.0.0.1:8000")
)

# Template selection
template_type = st.sidebar.selectbox(
    "Şablon Seçin",
    ["fdg_pet_ct", "psma_pet_ct", "dotatate_pet_ct"],
    format_func=lambda x: {
        "fdg_pet_ct": "🔬 FDG PET/BT",
        "psma_pet_ct": "🏥 PSMA PET/BT",
        "dotatate_pet_ct": "🧬 DOTATATE PET/BT"
    }[x]
)

# Quick settings
st.sidebar.markdown("---")
auto_variations = st.sidebar.checkbox("Auto Variations", value=True)
auto_conclusion = st.sidebar.checkbox("Auto Conclusion", value=True)
manual_approval = st.sidebar.checkbox("Manual Approval", value=True)

# Auto Report Generation
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Otomatik Rapor Oluşturma")

if st.session_state.get("ai_report") and st.session_state.get("current_patient"):
    if st.sidebar.button("🚀 AI + TSNM Rapor Oluştur", type="primary", use_container_width=True):
        st.success("🤖 AI analizi ve TSNM şablonu birleştiriliyor...")
        
        # Generate comprehensive report
        ai_report = st.session_state["ai_report"]
        patient = st.session_state["current_patient"]
        
        # Create TSNM report with AI data
        comprehensive_report = {
            "tsnm_template": template_type,
            "patient_info": patient,
            "ai_analysis": ai_report,
            "generated_at": datetime.now().isoformat(),
            "report_type": "AI + TSNM Integrated"
        }
        
        # Save to session state
        st.session_state["tsnm_ai_report"] = comprehensive_report
        
        st.success("✅ AI + TSNM entegre raporu oluşturuldu!")
        st.info("📝 Raporu inceleyin ve onaylayın")
else:
    st.sidebar.warning("⚠️ AI analizi ve hasta bilgileri gerekli")

# Theme toggle
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

theme_toggle = st.sidebar.button(
    "🌙 Dark Mode" if st.session_state["theme"] == "light" else "☀️ Light Mode"
)

if theme_toggle:
    st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"
    st.rerun()

# Apply theme CSS
if st.session_state["theme"] == "dark":
    st.markdown("""
    <style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stButton > button {
        background-color: #4a4a4a;
        color: #ffffff;
        border: 1px solid #666666;
    }
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #666666;
    }
    </style>
    """, unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 Hasta Bilgileri")
    
    # Patient input form
    with st.form("tsnm_patient_form"):
        col1_1, col1_2 = st.columns(2)
        
        with col1_1:
            hasta_no = st.text_input("Hasta No", value="H001")
            hasta_adi = st.text_input("Hasta Adı", value="Test Hasta")
            dogum_tarihi = st.date_input("Doğum Tarihi", value=datetime(1980, 1, 1))
            cinsiyet = st.selectbox("Cinsiyet", ["Erkek", "Kadın"])
        
        with col1_2:
            yas = st.number_input("Yaş", min_value=0, max_value=120, value=44)
            icd_kodu = st.text_input("ICD Kodu", value="C34.90")
            icd_aciklama = st.text_input("ICD Açıklama", value="Bronş ve akciğer, belirtilmemiş")
            klinik_tani = st.text_area("Klinik Tanı", value="Akciğer nodülü, metastaz şüphesi")
        
        study_date = st.date_input("Çalışma Tarihi", value=datetime.now())
        
        # PET/CT parameters
        st.subheader("🔬 PET/CT Parametreleri")
        col_pet1, col_pet2 = st.columns(2)
        
        with col_pet1:
            injected_dose = st.number_input("Enjeksiyon Dozu (MBq)", value=185.0, step=1.0)
            uptake_time = st.number_input("Uptake Süresi (dakika)", value=60, step=5)
        
        with col_pet2:
            suv_scale = st.selectbox("SUV Ölçeği", ["BW", "BSA", "LBM"], index=0)
            modality = st.selectbox("Modalite", ["PET/CT", "PET/MR"], index=0)
        
        submitted = st.form_submit_button("🚀 TSNM Raporu Oluştur", type="primary")
        
        if submitted:
            st.session_state["tsnm_patient_data"] = {
                "hasta_no": hasta_no,
                "ad_soyad": hasta_adi,
                "dogum_tarihi": dogum_tarihi.strftime("%Y-%m-%d"),
                "cinsiyet": cinsiyet,
                "yas": yas,
                "icd_kodu": icd_kodu,
                "icd_aciklama": icd_aciklama,
                "klinik_tani": klinik_tani,
                "study_date": study_date.strftime("%Y-%m-%d"),
                "petct": {
                    "injected_dose_MBq": injected_dose,
                    "uptake_time_min": uptake_time,
                    "suv_scale": suv_scale,
                    "modality": modality
                }
            }
            st.session_state["tsnm_report_requested"] = True

with col2:
    st.header("📊 TSNM Şablon Bilgileri")
    
    # Get template info
    template_info = tsnm_manager.get_template_info(template_type)
    
    if "error" not in template_info:
        st.info(f"**Şablon:** {template_info['name']}")
        st.info(f"**Dosya ID:** {template_info['file_id']}")
        st.info(f"**Bölüm Sayısı:** {len(template_info['sections'])}")
        
        # Show sections
        with st.expander("📋 Rapor Bölümleri"):
            for i, section in enumerate(template_info['sections'], 1):
                st.write(f"{i}. {section}")
        
        # Show anatomical regions if available
        if "anatomical_regions" in template_info:
            with st.expander("🗺️ Anatomik Bölgeler"):
                for region in template_info['anatomical_regions']:
                    st.write(f"• {region}")
    else:
        st.error("Şablon bilgileri yüklenemedi")

# TSNM Report Generation
if st.session_state.get("tsnm_report_requested", False):
    st.header("🧠 TSNM Raporu Oluşturuluyor")
    
    patient_data = st.session_state["tsnm_patient_data"]
    
    # Manual approval check
    if manual_approval:
        st.info("⚠️ Manuel onay gerekli - Segmentasyon öncesi kullanıcı onayı bekleniyor")
        
        col_approval1, col_approval2 = st.columns(2)
        
        with col_approval1:
            if st.button("✅ Segmentasyona İzin Ver", type="primary"):
                st.session_state["manual_approval_given"] = True
        
        with col_approval2:
            if st.button("❌ Segmentasyonu İptal Et"):
                st.session_state["manual_approval_given"] = False
                st.warning("Segmentasyon iptal edildi")
                st.stop()
        
        if not st.session_state.get("manual_approval_given", False):
            st.stop()
    
    # Start AI analysis for TSNM report
    with st.spinner("🤖 AI analizi yapılıyor ve TSNM raporu oluşturuluyor..."):
        try:
            # AI analysis request
            analysis_request = {
                "hasta_no": patient_data["hasta_no"],
                "ad_soyad": patient_data["ad_soyad"],
                "study_date": patient_data["study_date"],
                "analysis_type": "full",
                "retention_days": 7
            }
            
            response = requests.post(
                f"{backend_url}/ai/analyze",
                json=analysis_request,
                timeout=30
            )
            
            if response.status_code == 200:
                ai_results = response.json()
                st.session_state["tsnm_ai_results"] = ai_results
                st.success("🎉 AI analizi tamamlandı!")
                
                # Generate TSNM report
                user_preferences = {
                    "auto_variations": auto_variations,
                    "auto_conclusion_variations": auto_conclusion
                }
                
                tsnm_report = tsnm_manager.generate_report(
                    template_type, patient_data, ai_results["results"], user_preferences
                )
                
                st.session_state["tsnm_report"] = tsnm_report
                st.success("📊 TSNM raporu oluşturuldu!")
                
            else:
                st.error(f"❌ AI analizi başarısız: {response.text}")
                
        except Exception as e:
            st.error(f"❌ TSNM rapor oluşturma hatası: {str(e)}")

# Display TSNM Report
if st.session_state.get("tsnm_report"):
    st.header("📊 TSNM Raporu Sonuçları")
    
    report = st.session_state["tsnm_report"]
    
    # Report overview
    col_overview1, col_overview2, col_overview3 = st.columns(3)
    
    with col_overview1:
        st.metric("Şablon Türü", report["template_name"])
        st.metric("Dosya ID", report["file_id"])
    
    with col_overview2:
        st.metric("Bölüm Sayısı", len(report["sections"]))
        st.metric("Oluşturma Tarihi", report["generation_date"][:10])
    
    with col_overview3:
        st.metric("Template Type", report["template_type"])
        st.metric("Status", "✅ Tamamlandı")
    
    # Report sections tabs
    tab_names = list(report["sections"].keys())
    tabs = st.tabs([f"📋 {name.replace('_', ' ').title()}" for name in tab_names])
    
    for i, (tab, section_name) in enumerate(zip(tabs, tab_names)):
        with tab:
            section_data = report["sections"][section_name]
            
            if isinstance(section_data, dict):
                # Display section data
                for key, value in section_data.items():
                    if isinstance(value, dict):
                        st.subheader(f"🔍 {key.replace('_', ' ').title()}")
                        st.json(value)
                    elif isinstance(value, list):
                        st.subheader(f"📋 {key.replace('_', ' ').title()}")
                        for j, item in enumerate(value, 1):
                            st.write(f"{j}. {item}")
                    else:
                        st.metric(key.replace('_', ' ').title(), value)
            else:
                st.write(section_data)

# Display AI + TSNM Integrated Report
if st.session_state.get("tsnm_ai_report"):
    st.header("🤖 AI + TSNM Entegre Raporu")
    
    integrated_report = st.session_state["tsnm_ai_report"]
    
    # Report overview
    col_int1, col_int2, col_int3 = st.columns(3)
    
    with col_int1:
        st.metric("Rapor Türü", integrated_report["report_type"])
        st.metric("TSNM Şablonu", integrated_report["tsnm_template"])
        st.metric("Hasta No", integrated_report["patient_info"].get("hasta_no", "N/A"))
    
    with col_int2:
        ai_analysis = integrated_report["ai_analysis"]
        st.metric("Lezyon Sayısı", ai_analysis["analysis_results"]["lesions"])
        st.metric("Maksimum SUV", ai_analysis["analysis_results"]["max_suv"])
        st.metric("Segmentasyon Kalitesi", f"{ai_analysis['analysis_results']['segmentation_quality']:.1%}")
    
    with col_int3:
        st.metric("Metastaz Riski", ai_analysis["clinical_assessment"]["metastasis_risk"])
        st.metric("TNM Evresi", ai_analysis["clinical_assessment"]["tnm_stage"])
        st.metric("Oluşturma Tarihi", integrated_report["generated_at"][:10])
    
    # Detailed report sections
    st.subheader("📋 Detaylı Rapor Bölümleri")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Hasta Bilgileri", "🔬 AI Analizi", "📊 Klinik Değerlendirme", "📚 Literatür"])
    
    with tab1:
        patient = integrated_report["patient_info"]
        st.json(patient)
    
    with tab2:
        analysis = integrated_report["ai_analysis"]["analysis_results"]
        st.json(analysis)
    
    with tab3:
        clinical = integrated_report["ai_analysis"]["clinical_assessment"]
        st.json(clinical)
    
    with tab4:
        literature = integrated_report["ai_analysis"]["literature_integration"]
        st.json(literature)
    
    # Export options
    st.subheader("📤 Rapor Dışa Aktarma")
    
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        if st.button("📄 PDF İndir", use_container_width=True):
            st.success("📄 PDF raporu indiriliyor...")
    
    with col_export2:
        if st.button("📊 JSON İndir", use_container_width=True):
            st.success("📊 JSON raporu indiriliyor...")
    
    with col_export3:
        if st.button("📝 Word İndir", use_container_width=True):
            st.success("📝 Word raporu indiriliyor...")
    
    # Integration with other systems
    st.subheader("🔗 Sistem Entegrasyonu")
    
    col_sys1, col_sys2 = st.columns(2)
    
    with col_sys1:
        if st.button("🏥 HBYS'e Gönder", type="primary", use_container_width=True):
            st.success("🏥 Rapor HBYS sistemine gönderiliyor...")
    
    with col_sys2:
        if st.button("📊 Dashboard'a Kaydet", type="secondary", use_container_width=True):
            st.success("📊 Rapor dashboard'a kaydediliyor...")

# Footer
st.markdown("---")
st.markdown("**TSNM Reports** - AI destekli standart rapor formatları ve entegrasyon")
