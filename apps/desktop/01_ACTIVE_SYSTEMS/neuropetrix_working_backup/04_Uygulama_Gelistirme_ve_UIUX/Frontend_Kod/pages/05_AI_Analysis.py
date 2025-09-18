import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="AI Analysis - NeuroPETrix",
    page_icon="🤖",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Page title and description
st.title("🤖 AI Analysis - PET/CT Görüntü Analizi")
st.markdown("**Segmentasyon • Radiomics • Klinik Değerlendirme • Literatür Entegrasyonu**")

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

if st.sidebar.button("📁 DICOM Upload", use_container_width=True):
    st.switch_page("pages/04_DICOM_Upload.py")

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

# ---- HASTA INFORMATION - SAĞ ÜSTTE (DÜZENLEME YOK) ----
if st.session_state.get("current_patient"):
    patient = st.session_state["current_patient"]
    
    # Patient info card in top right
    col_main, col_patient = st.columns([3, 1])
    
    with col_main:
        st.markdown("""
        <div class="hero">
            <div>
                <h1>🤖 AI Analysis Pipeline</h1>
                <div class="subtitle">Segmentasyon • Radiomics • Klinik Değerlendirme • Literatür Entegrasyonu</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_patient:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 👤 Hasta Bilgileri")
        st.markdown(f"**Hasta No:** {patient['hasta_no']}")
        st.markdown(f"**Ad Soyad:** {patient['ad_soyad']}")
        st.markdown(f"**Yaş:** {patient['yas']}")
        st.markdown(f"**ICD:** {patient['icd_kodu']}")
        st.markdown(f"**Tanı:** {patient['klinik_tani'][:50]}...")
        st.markdown(f"**Çalışma:** {patient.get('study_type', 'N/A')}")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.warning("⚠️ Önce hasta bilgilerini girin")
    if st.button("🏥 HBYS'e Git", type="primary"):
        st.switch_page("pages/03_HBYS_Entegrasyon.py")
    st.stop()

st.write("")

# ---- İŞLEM AKIŞI YÖNETİMİ ----
st.header("🔄 AI Analysis İşlem Akışı")

# Workflow steps
workflow_steps = [
    "📁 DICOM Veri Kontrolü",
    "🔍 Görüntü Ön İşleme",
    "🎯 Segmentasyon",
    "🔬 Radiomics Analizi",
    "🏥 Klinik Değerlendirme",
    "📚 Literatür Entegrasyonu",
    "📝 Rapor Oluşturma"
]

# Current step from session state
current_step = st.session_state.get("ai_workflow_step", 0)

# Workflow progress
col_progress1, col_progress2 = st.columns([3, 1])

with col_progress1:
    st.subheader("📊 İşlem Durumu")
    
    # Progress bar
    progress = st.progress(current_step / (len(workflow_steps) - 1))
    
    # Step indicators
    cols = st.columns(len(workflow_steps))
    for i, (col, step) in enumerate(zip(cols, workflow_steps)):
        if i <= current_step:
            col.success(f"✅ {step}")
        elif i == current_step + 1:
            col.info(f"🔄 {step}")
        else:
            col.markdown(f"⏳ {step}")

with col_progress2:
    st.subheader("🎯 Sonraki Adım")
    
    if current_step < len(workflow_steps) - 1:
        next_step = workflow_steps[current_step + 1]
        st.info(f"**Sonraki:** {next_step}")
        
        if st.button("🚀 Sonraki Adıma Geç", type="primary"):
            st.session_state["ai_workflow_step"] = current_step + 1
            st.rerun()
    else:
        st.success("🎉 Tüm adımlar tamamlandı!")

st.write("")

# ---- DICOM VERİ KONTROLÜ (ADIM 1) ----
if current_step == 0:
    st.header("📁 DICOM Veri Kontrolü")
    
    col_check1, col_check2 = st.columns([2, 1])
    
    with col_check1:
        st.subheader("🔍 Veri Durumu")
        
        # Check DICOM data availability
        dicom_params = st.session_state.get("dicom_params", {})
        
        if dicom_params:
            st.success("✅ DICOM parametreleri mevcut")
            
            # Display DICOM info
            dicom_info = {
                "Tracer Türü": dicom_params.get("tracer_type", "N/A"),
                "Enjeksiyon Dozu": f"{dicom_params.get('injected_dose_MBq', 'N/A')} MBq",
                "Uptake Süresi": f"{dicom_params.get('uptake_time_min', 'N/A')} dakika",
                "SUV Ölçeği": dicom_params.get("suv_scale", "N/A"),
                "Reconstruction": dicom_params.get("reconstruction_method", "N/A")
            }
            
            for key, value in dicom_info.items():
                st.markdown(f"**{key}:** {value}")
        else:
            st.warning("⚠️ DICOM parametreleri bulunamadı")
            st.info("DICOM Upload sayfasından veri yükleyin")
        
        # Check image data
        if st.session_state.get("uploaded_files"):
            st.success("✅ Görüntü dosyaları mevcut")
            st.info(f"Toplam {len(st.session_state['uploaded_files'])} dosya")
        else:
            st.warning("⚠️ Görüntü dosyaları bulunamadı")
    
    with col_check2:
        st.subheader("📊 Veri Kalitesi")
        
        # Mock quality check
        quality_checks = {
            "Görüntü Çözünürlüğü": "✅ Yüksek",
            "Gürültü Seviyesi": "✅ Düşük",
            "Artefakt": "✅ Yok",
            "Hareket": "✅ Minimal"
        }
        
        for check, status in quality_checks.items():
            st.markdown(f"**{check}:** {status}")
        
        if st.button("🔍 Detaylı Kalite Analizi", type="secondary"):
            st.info("🔍 Kalite analizi yapılıyor...")
    
    # Continue to next step
    if st.button("✅ Veri Kontrolü Tamamlandı", type="primary"):
        st.session_state["ai_workflow_step"] = 1
        st.rerun()

# ---- GÖRÜNTÜ ÖN İŞLEME (ADIM 2) ----
elif current_step == 1:
    st.header("🔍 Görüntü Ön İşleme")
    
    col_pre1, col_pre2 = st.columns([2, 1])
    
    with col_pre1:
        st.subheader("⚙️ Ön İşleme Seçenekleri")
        
        # Preprocessing options
        preprocessing_options = {
            "Gürültü Azaltma": st.checkbox("Gaussian Filtre", value=True),
            "Hareket Düzeltmesi": st.checkbox("Motion Correction", value=True),
            "Attenuation Düzeltmesi": st.checkbox("Attenuation Correction", value=True),
            "Scatter Düzeltmesi": st.checkbox("Scatter Correction", value=True),
            "Normalizasyon": st.checkbox("SUV Normalizasyonu", value=True)
        }
        
        # Display options
        for option, enabled in preprocessing_options.items():
            if enabled:
                st.success(f"✅ {option}")
            else:
                st.info(f"⏳ {option}")
        
        # Start preprocessing
        if st.button("🚀 Ön İşleme Başlat", type="primary"):
            st.info("🔍 Görüntü ön işleme yapılıyor...")
            
            # Simulate preprocessing
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(101):
                progress_bar.progress(i)
                if i < 30:
                    status_text.text("🔍 Gürültü azaltılıyor...")
                elif i < 60:
                    status_text.text("📐 Geometrik düzeltmeler...")
                elif i < 90:
                    status_text.text("📊 Normalizasyon...")
                else:
                    status_text.text("✅ Ön işleme tamamlandı!")
            
            st.success("🎉 Görüntü ön işleme tamamlandı!")
    
    with col_pre2:
        st.subheader("📈 Ön İşleme Sonuçları")
        
        # Mock results
        results = {
            "SNR İyileşme": "+15%",
            "CNR İyileşme": "+22%",
            "Gürültü Azalma": "-30%",
            "İşlem Süresi": "45 saniye"
        }
        
        for metric, value in results.items():
            st.metric(metric, value)
    
    # Continue to next step
    if st.button("✅ Ön İşleme Tamamlandı", type="primary"):
        st.session_state["ai_workflow_step"] = 2
        st.rerun()

# ---- SEGMENTASYON (ADIM 3) ----
elif current_step == 2:
    st.header("🎯 Segmentasyon Analizi")
    
    col_seg1, col_seg2 = st.columns([2, 1])
    
    with col_seg1:
        st.subheader("🔍 Lezyon Tespiti")
        
        # Mock lesion detection
        lesions = [
            {"id": 1, "type": "Akciğer Nodülü", "location": "Sağ üst lob", "size": "2.5 cm", "SUVmax": 8.5, "confidence": 0.94},
            {"id": 2, "type": "Karaciğer Metastazı", "location": "Segment 6", "size": "1.8 cm", "SUVmax": 6.2, "confidence": 0.87},
            {"id": 3, "type": "Kemik Metastazı", "location": "L3 vertebra", "size": "1.2 cm", "SUVmax": 4.8, "confidence": 0.79},
            {"id": 4, "type": "Lenf Nodu", "location": "Mediastinal", "size": "1.5 cm", "SUVmax": 5.1, "confidence": 0.82}
        ]
        
        # Lesion table
        lesion_df = pd.DataFrame(lesions)
        st.dataframe(lesion_df, use_container_width=True, hide_index=True)
        
        # Segmentation visualization
        st.subheader("📊 Segmentasyon Görselleştirme")
        
        # Mock MIP image
        st.info("🖼️ MIP (Maximum Intensity Projection) Görüntüsü")
        
        # Create mock 3D visualization
        fig = go.Figure()
        
        # Add lesion markers
        for lesion in lesions:
            fig.add_trace(go.Scatter3d(
                x=[np.random.normal(0, 1)],
                y=[np.random.normal(0, 1)],
                z=[np.random.normal(0, 1)],
                mode='markers',
                marker=dict(
                    size=lesion['SUVmax'] * 2,
                    color=lesion['SUVmax'],
                    colorscale='Viridis',
                    opacity=0.8
                ),
                text=f"{lesion['type']}<br>SUVmax: {lesion['SUVmax']}",
                name=lesion['type']
            ))
        
        fig.update_layout(
            title="3D Lezyon Dağılımı",
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z"
            ),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_seg2:
        st.subheader("📊 Lezyon Özeti")
        
        # Lesion statistics
        total_lesions = len(lesions)
        avg_suv = np.mean([l['SUVmax'] for l in lesions])
        max_suv = max([l['SUVmax'] for l in lesions])
        
        st.metric("Toplam Lezyon", total_lesions)
        st.metric("Ortalama SUVmax", f"{avg_suv:.1f}")
        st.metric("Maksimum SUVmax", f"{max_suv:.1f}")
        
        # Lesion types
        st.subheader("🏷️ Lezyon Türleri")
        lesion_types = {}
        for lesion in lesions:
            lesion_type = lesion['type']
            if lesion_type in lesion_types:
                lesion_types[lesion_type] += 1
            else:
                lesion_types[lesion_type] = 1
        
        for lesion_type, count in lesion_types.items():
            st.markdown(f"**{lesion_type}:** {count}")
        
        # Segmentation quality
        st.subheader("🎯 Segmentasyon Kalitesi")
        avg_confidence = np.mean([l['confidence'] for l in lesions])
        st.metric("Ortalama Güven", f"{avg_confidence:.1%}")
        
        if avg_confidence > 0.9:
            st.success("🎉 Yüksek kalite segmentasyon")
        elif avg_confidence > 0.8:
            st.info("✅ İyi kalite segmentasyon")
        else:
            st.warning("⚠️ Orta kalite segmentasyon")
    
    # Continue to next step
    if st.button("✅ Segmentasyon Tamamlandı", type="primary"):
        st.session_state["ai_workflow_step"] = 3
        st.rerun()

# ---- RADIOMICS ANALİZİ (ADIM 4) ----
elif current_step == 3:
    st.header("🔬 Radiomics Analizi")
    
    col_rad1, col_rad2 = st.columns([2, 1])
    
    with col_rad1:
        st.subheader("📊 Radiomics Özellikleri")
        
        # Mock radiomics features
        radiomics_features = {
            "First Order": {
                "Mean": 45.2, "Std": 12.8, "Skewness": 0.34, "Kurtosis": 2.1,
                "Energy": 156.7, "Entropy": 4.2
            },
            "Shape": {
                "Volume": 12.5, "Surface Area": 28.3, "Sphericity": 0.72,
                "Compactness": 0.45, "Elongation": 1.8
            },
            "Texture": {
                "GLCM Energy": 0.23, "GLCM Contrast": 45.6, "GLCM Correlation": 0.67,
                "GLRLM SRE": 0.89, "GLRLM LRE": 0.12
            }
        }
        
        # Display features in tabs
        tab1, tab2, tab3 = st.tabs(["First Order", "Shape", "Texture"])
        
        with tab1:
            first_order_df = pd.DataFrame(list(radiomics_features["First Order"].items()), 
                                        columns=["Özellik", "Değer"])
            st.dataframe(first_order_df, use_container_width=True, hide_index=True)
        
        with tab2:
            shape_df = pd.DataFrame(list(radiomics_features["Shape"].items()), 
                                  columns=["Özellik", "Değer"])
            st.dataframe(shape_df, use_container_width=True, hide_index=True)
        
        with tab3:
            texture_df = pd.DataFrame(list(radiomics_features["Texture"].items()), 
                                    columns=["Özellik", "Değer"])
            st.dataframe(texture_df, use_container_width=True, hide_index=True)
        
        # Radiomics visualization
        st.subheader("📈 Radiomics Görselleştirme")
        
        # Feature correlation heatmap
        feature_names = list(radiomics_features["First Order"].keys())
        feature_values = list(radiomics_features["First Order"].values())
        
        fig = px.bar(
            x=feature_names,
            y=feature_values,
            title="First Order Radiomics Özellikleri",
            labels={"x": "Özellik", "y": "Değer"}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_rad2:
        st.subheader("📊 Analiz Sonuçları")
        
        # Radiomics quality metrics
        st.metric("Toplam Özellik", "18")
        st.metric("İşlem Süresi", "2.3 saniye")
        st.metric("Kalite Skoru", "94%")
        
        # Feature importance
        st.subheader("🎯 Önemli Özellikler")
        important_features = [
            "SUVmax (SUV)",
            "Volume (Shape)",
            "GLCM Contrast (Texture)",
            "Entropy (First Order)"
        ]
        
        for i, feature in enumerate(important_features, 1):
            st.markdown(f"{i}. **{feature}**")
        
        # Analysis recommendations
        st.subheader("💡 Analiz Önerileri")
        st.info("""
        • **SUVmax >8.5:** Yüksek metabolik aktivite
        • **Volume >10cm³:** Büyük lezyon
        • **GLCM Contrast >40:** Heterojen doku
        • **Entropy >4.0:** Karmaşık yapı
        """)
    
    # Continue to next step
    if st.button("✅ Radiomics Analizi Tamamlandı", type="primary"):
        st.session_state["ai_workflow_step"] = 4
        st.rerun()

# ---- KLİNİK DEĞERLENDİRME (ADIM 5) ----
elif current_step == 4:
    st.header("🏥 Klinik Değerlendirme")
    
    col_clin1, col_clin2 = st.columns([2, 1])
    
    with col_clin1:
        st.subheader("🔍 Klinik Analiz")
        
        # Patient clinical data
        clinical_data = {
            "Yaş": patient['yas'],
            "Cinsiyet": patient['cinsiyet'],
            "ICD Kodu": patient['icd_kodu'],
            "Klinik Tanı": patient['klinik_tani'],
            "Çalışma Türü": patient.get('study_type', 'N/A'),
            "Öncelik": patient.get('priority', 'N/A')
        }
        
        # Display clinical data
        for key, value in clinical_data.items():
            st.markdown(f"**{key}:** {value}")
        
        # AI clinical assessment
        st.subheader("🤖 AI Klinik Değerlendirme")
        
        # Mock AI analysis
        ai_assessment = {
            "Metastaz Riski": "Yüksek",
            "TNM Evresi": "T2N1M1",
            "Tedavi Önceliği": "Acil",
            "Prognoz": "Orta",
            "Önerilen Tetkikler": "Biyopsi, Kemik Sintigrafisi, Beyin MR"
        }
        
        for assessment, value in ai_assessment.items():
            if "Yüksek" in value or "Acil" in value:
                st.error(f"**{assessment}:** {value}")
            elif "Orta" in value:
                st.warning(f"**{assessment}:** {value}")
            else:
                st.info(f"**{assessment}:** {value}")
        
        # Clinical decision support
        st.subheader("💡 Klinik Karar Desteği")
        
        clinical_recommendations = [
            "1. **Biyopsi:** Akciğer nodülü için histopatolojik doğrulama",
            "2. **Kemik Sintigrafisi:** Kemik metastazı için tam değerlendirme",
            "3. **Beyin MR:** Beyin metastazı ekarte etmek için",
            "4. **Tedavi Planı:** Kemoterapi + Radyoterapi önerilir",
            "5. **Takip:** 3 ayda bir PET/CT kontrolü"
        ]
        
        for rec in clinical_recommendations:
            st.markdown(rec)
    
    with col_clin2:
        st.subheader("📊 Klinik Metrikler")
        
        # Clinical metrics
        st.metric("Metastaz Riski", "87%")
        st.metric("TNM Evresi", "T2N1M1")
        st.metric("Tedavi Önceliği", "Acil")
        st.metric("Prognoz", "Orta")
        
        # AI confidence
        st.subheader("🤖 AI Güven Skoru")
        ai_confidence = 0.89
        st.metric("Genel Güven", f"{ai_confidence:.1%}")
        
        if ai_confidence > 0.9:
            st.success("🎉 Çok Yüksek Güven")
        elif ai_confidence > 0.8:
            st.info("✅ Yüksek Güven")
        else:
            st.warning("⚠️ Orta Güven")
        
        # Clinical workflow
        st.subheader("🔄 Klinik İş Akışı")
        workflow_status = [
            "✅ Hasta Değerlendirmesi",
            "✅ Görüntü Analizi",
            "✅ AI Destekli Tanı",
            "🔄 Tedavi Planı",
            "⏳ Takip Protokolü"
        ]
        
        for status in workflow_status:
            st.markdown(status)
    
    # Continue to next step
    if st.button("✅ Klinik Değerlendirme Tamamlandı", type="primary"):
        st.session_state["ai_workflow_step"] = 5
        st.rerun()

# ---- LİTERATÜR ENTEGRASYONU (ADIM 6) ----
elif current_step == 5:
    st.header("📚 Literatür Entegrasyonu")
    
    col_lit1, col_lit2 = st.columns([2, 1])
    
    with col_lit1:
        st.subheader("🔍 Literatür Tarama")
        
        # Generate search queries based on patient data
        search_queries = [
            f"\"{patient['icd_kodu']}\" AND \"PET/CT\" AND \"metastasis\"",
            f"\"{patient['klinik_tani']}\" AND \"SUVmax >8\" AND \"treatment\"",
            f"\"multiple bone metastases\" AND \"{patient.get('study_type', 'PET/CT')}\"",
            f"\"lung cancer\" AND \"liver metastasis\" AND \"prognosis\""
        ]
        
        st.markdown("**🔍 Otomatik Oluşturulan Arama Sorguları:**")
        for i, query in enumerate(search_queries, 1):
            st.markdown(f"{i}. `{query}`")
        
        # Literature search results
        st.subheader("📊 Literatür Sonuçları")
        
        # Mock literature results
        literature_results = [
            {
                "title": "PET/CT in Lung Cancer Staging: A Meta-Analysis",
                "authors": "Smith et al.",
                "year": 2023,
                "journal": "Journal of Nuclear Medicine",
                "relevance": 0.94,
                "evidence_level": "A"
            },
            {
                "title": "Multiple Bone Metastases: Treatment Strategies",
                "authors": "Johnson et al.",
                "year": 2024,
                "journal": "Oncology Reports",
                "relevance": 0.87,
                "evidence_level": "B"
            },
            {
                "title": "SUVmax >8: Clinical Significance in Oncology",
                "authors": "Williams et al.",
                "year": 2023,
                "journal": "Clinical Nuclear Medicine",
                "relevance": 0.91,
                "evidence_level": "A"
            }
        ]
        
        # Display literature results
        for result in literature_results:
            with st.expander(f"📄 {result['title']}"):
                st.markdown(f"**Yazarlar:** {result['authors']}")
                st.markdown(f"**Yıl:** {result['year']}")
                st.markdown(f"**Dergi:** {result['journal']}")
                st.markdown(f"**İlgi:** {result['relevance']:.1%}")
                st.markdown(f"**Kanıt Seviyesi:** {result['evidence_level']}")
                
                if result['relevance'] > 0.9:
                    st.success("🎯 Yüksek İlgi")
                elif result['relevance'] > 0.8:
                    st.info("✅ Orta İlgi")
                else:
                    st.warning("⚠️ Düşük İlgi")
        
        # Literature integration
        st.subheader("🔗 Literatür Entegrasyonu")
        
        integration_summary = """
        **📚 Literatür Bulguları:**
        • SUVmax >8.5: %87 metastaz riski
        • Multiple bone lesions: %92 kemik metastazı
        • Liver involvement: %78 karaciğer metastazı
        
        **💡 Klinik Uygulama:**
        • Literatür bulguları hasta verileriyle uyumlu
        • Tedavi protokolleri güncel literatüre uygun
        • Takip sıklığı kanıta dayalı
        """
        
        st.info(integration_summary)
    
    with col_lit2:
        st.subheader("📊 Literatür Metrikleri")
        
        # Literature metrics
        st.metric("Toplam Makale", "3")
        st.metric("Ortalama İlgi", "91%")
        st.metric("Kanıt Seviyesi", "A-B")
        st.metric("Güncellik", "2023-2024")
        
        # Search quality
        st.subheader("🎯 Arama Kalitesi")
        search_quality = 0.89
        st.metric("Arama Kalitesi", f"{search_quality:.1%}")
        
        if search_quality > 0.9:
            st.success("🎉 Mükemmel Arama")
        elif search_quality > 0.8:
            st.info("✅ İyi Arama")
        else:
            st.warning("⚠️ Orta Arama")
        
        # Literature workflow
        st.subheader("🔄 Literatür İş Akışı")
        lit_workflow = [
            "✅ Arama Sorguları",
            "✅ Makale Bulma",
            "✅ İlgi Değerlendirme",
            "✅ Kanıt Seviyesi",
            "🔄 Klinik Entegrasyon"
        ]
        
        for step in lit_workflow:
            st.markdown(step)
    
    # Continue to next step
    if st.button("✅ Literatür Entegrasyonu Tamamlandı", type="primary"):
        st.session_state["ai_workflow_step"] = 6
        st.rerun()

# ---- RAPOR OLUŞTURMA (ADIM 7) ----
elif current_step == 6:
    st.header("📝 Rapor Oluşturma")
    
    col_report1, col_report2 = st.columns([2, 1])
    
    with col_report1:
        st.subheader("📋 Rapor Özeti")
        
        # Generate comprehensive report
        report_summary = f"""
        # AI Destekli PET/CT Analiz Raporu
        
        **Hasta Bilgileri:**
        - Hasta No: {patient['hasta_no']}
        - Ad Soyad: {patient['ad_soyad']}
        - Yaş: {patient['yas']}
        - ICD: {patient['icd_kodu']}
        - Klinik Tanı: {patient['klinik_tani']}
        
        **Görüntü Analizi:**
        - Toplam Lezyon: 4
        - Maksimum SUV: 8.5
        - Segmentasyon Kalitesi: %94
        - Radiomics Özellik: 18
        
        **Klinik Değerlendirme:**
        - Metastaz Riski: Yüksek (87%)
        - TNM Evresi: T2N1M1
        - Tedavi Önceliği: Acil
        - Önerilen Tetkikler: Biyopsi, Kemik Sintigrafisi, Beyin MR
        
        **Literatür Entegrasyonu:**
        - Bulunan Makale: 3
        - Ortalama İlgi: %91
        - Kanıt Seviyesi: A-B
        
        **Sonuç ve Öneriler:**
        1. Akciğer nodülü için acil biyopsi
        2. Kemik metastazı için tam değerlendirme
        3. Kemoterapi + Radyoterapi planı
        4. 3 ayda bir PET/CT takibi
        """
        
        st.text_area("📄 Rapor Önizleme:", value=report_summary, height=400)
        
        # Report options
        st.subheader("📤 Rapor Seçenekleri")
        
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            st.markdown("**📄 Format Seçenekleri:**")
            st.checkbox("PDF Raporu", value=True)
            st.checkbox("Word Dokümanı", value=True)
            st.checkbox("JSON Veri", value=True)
            st.checkbox("HTML Raporu", value=True)
        
        with col_opt2:
            st.markdown("**🎯 Entegrasyon:**")
            st.checkbox("TSNM Şablonu", value=True)
            st.checkbox("HBYS Entegrasyonu", value=True)
            st.checkbox("E-Rapor Sistemi", value=True)
            st.checkbox("Doktor Portalı", value=True)
    
    with col_report2:
        st.subheader("🚀 Rapor Üretimi")
        
        # Generate report
        if st.button("📝 Rapor Oluştur", type="primary", use_container_width=True):
            st.success("📝 Rapor oluşturuluyor...")
            
            # Simulate report generation
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(101):
                progress_bar.progress(i)
                if i < 30:
                    status_text.text("📊 Veri toplanıyor...")
                elif i < 60:
                    status_text.text("🔍 Analiz sonuçları...")
                elif i < 90:
                    status_text.text("📝 Rapor yazılıyor...")
                else:
                    status_text.text("✅ Rapor tamamlandı!")
            
            st.success("🎉 Rapor başarıyla oluşturuldu!")
            
            # Save to session state
            st.session_state["ai_report"] = {
                "patient_info": patient,
                "analysis_results": {
                    "lesions": 4,
                    "max_suv": 8.5,
                    "segmentation_quality": 0.94,
                    "radiomics_features": 18
                },
                "clinical_assessment": {
                    "metastasis_risk": "Yüksek",
                    "tnm_stage": "T2N1M1",
                    "treatment_priority": "Acil"
                },
                "literature_integration": {
                    "articles_found": 3,
                    "average_relevance": 0.91,
                    "evidence_level": "A-B"
                },
                "generated_at": datetime.now().isoformat()
            }
        
        # Report status
        if st.session_state.get("ai_report"):
            st.subheader("📊 Rapor Durumu")
            st.success("✅ Rapor mevcut")
            st.info("Rapor başarıyla oluşturuldu ve kaydedildi")
            
                    # Download options
        st.subheader("📥 İndirme Seçenekleri")
        
        col_download1, col_download2, col_download3, col_download4 = st.columns(4)
        
        with col_download1:
            if st.button("📄 PDF İndir", use_container_width=True):
                st.info("📄 PDF indiriliyor...")
        
        with col_download2:
            if st.button("📊 JSON İndir", use_container_width=True):
                st.info("📊 JSON indiriliyor...")
        
        with col_download3:
            if st.button("📝 Word İndir", use_container_width=True):
                st.info("📝 Word indiriliyor...")
        
        with col_download4:
            if st.button("🏥 TSNM Formatında İndir", use_container_width=True, type="primary"):
                # Generate TSNM format report from AI analysis
                ai_report = st.session_state.get("ai_report", {})
                
                tsnm_ai_report = f"""
# TSNM Formatında AI Analiz Raporu
**Hasta:** {patient['ad_soyad']} - {patient['hasta_no']}  
**Tarih:** {datetime.now().strftime('%Y-%m-%d')}  
**ICD:** {patient['icd_kodu']}  
**Modalite:** PET/CT + AI Analiz

## TSNM Standart Bölümleri

### 1. Klinik Bilgiler
- **Endikasyon:** {patient['klinik_karar_hedefi']}
- **Klinik Tanı:** {patient['klinik_tani']}
- **Yaş:** {patient['yas']}
- **Cinsiyet:** {patient['cinsiyet']}

### 2. Teknik Parametreler
- **Radyofarmasötik:** FDG-18
- **Enjeksiyon Dozu:** 185 MBq
- **Uptake Süresi:** 60 dakika
- **SUV Ölçeği:** Body Weight

### 3. AI Segmentasyon Sonuçları
- **Segmentasyon Kalitesi:** {ai_report.get('analysis_results', {}).get('segmentation_quality', 0.94):.1%}
- **Tespit Edilen Lezyon:** {ai_report.get('analysis_results', {}).get('lesions', 1)}
- **Maksimum SUV:** {ai_report.get('analysis_results', {}).get('max_suv', 8.5):.1f}
- **Radiomics Özellik:** {ai_report.get('analysis_results', {}).get('radiomics_features', 18)}

### 4. Bulgular (AI Destekli TSNM Formatı)
- **Baş-Boyun:** Normal FDG tutulumu
- **Toraks:** Normal mediastinal yapılar
- **Abdomen:** Normal hepatik tutulum
- **Pelvis:** Normal aktivite dağılımı
- **Kemik Sistemi:** Normal metabolik aktivite

### 5. SUV Değerleri
- **Karaciğer:** 2.1 (Referans)
- **Mediastinum:** 1.8 (Referans)
- **Lezyon SUVmax:** {ai_report.get('analysis_results', {}).get('max_suv', 8.5):.1f}

### 6. AI Klinik Değerlendirme
- **Metastaz Riski:** {ai_report.get('clinical_assessment', {}).get('metastasis_risk', 'Düşük')}
- **TNM Evresi:** {ai_report.get('clinical_assessment', {}).get('tnm_stage', 'T2N0M0')}
- **AI Güven Skoru:** {ai_report.get('analysis_results', {}).get('segmentation_quality', 0.94):.1%}

### 7. Literatür Entegrasyonu
- **Kanıt Seviyesi:** {ai_report.get('literature_integration', {}).get('evidence_level', 'A-B')}
- **Ortalama İlgi:** {ai_report.get('literature_integration', {}).get('average_relevance', 0.91):.1%}
- **Önerilen Kaynaklar:** 15+ makale

### 8. Sonuç ve Öneriler
- **Evreleme:** {ai_report.get('clinical_assessment', {}).get('tnm_stage', 'T2N0M0')}
- **Tedavi Yanıtı:** Değerlendirilemedi
- **Takip:** 3 ay sonra kontrol
- **AI Önerisi:** {ai_report.get('clinical_assessment', {}).get('metastasis_risk', 'Düşük')} metastaz riski

---
*TSNM Kılavuzlarına Uygun + AI Analiz - NeuroPETrix Sistemi*
                """
                
                # Download TSNM AI report
                st.download_button(
                    label="🏥 TSNM AI Raporu İndir",
                    data=tsnm_ai_report,
                    file_name=f"TSNM_AI_Rapor_{patient['hasta_no']}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
                st.success("✅ TSNM formatında AI analiz raporu hazırlandı!")
        
        # TSNM Formatında Çıktı Alma Bilgisi
        st.divider()
        st.subheader("🏥 TSNM Formatında Çıktı Alma")
        st.info("💡 AI analiz sonuçlarını TSNM kılavuzlarına uygun formatta alabilirsiniz!")
        
        col_tsnm_info1, col_tsnm_info2 = st.columns(2)
        
        with col_tsnm_info1:
            st.markdown("**🎯 TSNM Formatı Avantajları:**")
            st.markdown("• Standart tıbbi raporlama")
            st.markdown("• Klinik uygulamada kolay kullanım")
            st.markdown("• HBYS entegrasyonu için uygun")
            st.markdown("• Yasal ve etik uyumluluk")
        
        with col_tsnm_info2:
            st.markdown("**🤖 AI + TSNM Entegrasyonu:**")
            st.markdown("• AI segmentasyon sonuçları")
            st.markdown("• Radiomics özellikler")
            st.markdown("• Klinik değerlendirme")
            st.markdown("• Literatür entegrasyonu")
    
    # Complete workflow
    if st.button("🎉 İş Akışı Tamamlandı", type="primary"):
        st.session_state["ai_workflow_step"] = 7
        st.rerun()

# ---- İŞ AKIŞI TAMAMLANDI ----
elif current_step == 7:
    st.header("🎉 AI Analysis İş Akışı Tamamlandı!")
    
    col_complete1, col_complete2 = st.columns([2, 1])
    
    with col_complete1:
        st.success("🎯 Tüm AI analiz adımları başarıyla tamamlandı!")
        
        # Summary of completed work
        st.subheader("📋 Tamamlanan İşlemler")
        
        completed_work = [
            "✅ DICOM veri kontrolü ve kalite analizi",
            "✅ Görüntü ön işleme ve optimizasyon",
            "✅ Multi-lezyon segmentasyon ve analiz",
            "✅ Radiomics özellik çıkarımı (18 özellik)",
            "✅ AI destekli klinik değerlendirme",
            "✅ Literatür entegrasyonu ve kanıt analizi",
            "✅ Kapsamlı rapor oluşturma"
        ]
        
        for work in completed_work:
            st.markdown(work)
        
        # Next steps
        st.subheader("🚀 Sonraki Adımlar")
        
        next_steps = [
            "📝 Raporu inceleyin ve onaylayın",
            "🏥 Klinik ekiple paylaşın",
            "📊 TSNM rapor formatına entegre edin",
            "💾 Verileri HBYS sistemine kaydedin",
            "📅 Takip planını oluşturun"
        ]
        
        for step in next_steps:
            st.markdown(step)
    
    with col_complete2:
        st.subheader("📊 İş Akışı Özeti")
        
        # Workflow metrics
        st.metric("Toplam Adım", "7")
        st.metric("Tamamlanan", "7")
        st.metric("Başarı Oranı", "100%")
        st.metric("Toplam Süre", "~15 dakika")
        
        # Quality metrics
        st.subheader("🎯 Kalite Metrikleri")
        st.metric("Segmentasyon", "94%")
        st.metric("Radiomics", "96%")
        st.metric("Klinik", "89%")
        st.metric("Literatür", "91%")
        
        # Navigation options
        st.subheader("🧭 Navigasyon")
        
        if st.button("📝 Report Generation", use_container_width=True):
            st.switch_page("pages/02_Rapor_Üretimi.py")
        
        if st.button("📊 TSNM Reports", use_container_width=True):
            st.switch_page("pages/06_TSNM_Reports.py")
        
        if st.button("🏠 Ana Sayfa", use_container_width=True):
            st.switch_page("streamlit_app.py")

# Footer
st.markdown("---")
st.markdown("**AI Analysis** - PET/CT görüntü analizi ve AI destekli klinik değerlendirme")
