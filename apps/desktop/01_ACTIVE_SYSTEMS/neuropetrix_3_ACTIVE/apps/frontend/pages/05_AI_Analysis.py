import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def render_ai_analysis():
    """AI Analiz sayfasını render et"""
    
    st.header("🤖 Yapay Zeka Analizi")
    
    # Analiz türü seçimi
    st.subheader("Analiz Türü")
    
    analysis_type = st.selectbox(
        "Analiz Türünü Seçin",
        ["Multimodal Füzyon", "Radyomik Analiz", "Segmentasyon", "SUV Trend Analizi", "PICO Otomatikleştirme"]
    )
    
    # Hasta seçimi
    st.subheader("Hasta Bilgileri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_id = st.text_input("Hasta ID", "P-001")
        patient_name = st.text_input("Hasta Adı", "ANONYMOUS")
        patient_age = st.number_input("Yaş", min_value=0, max_value=120, value=65)
    
    with col2:
        patient_gender = st.selectbox("Cinsiyet", ["M", "F"])
        study_date = st.date_input("Çalışma Tarihi", value=datetime.now().date())
        modality = st.selectbox("Modalite", ["PET/CT", "PET/MR", "CT", "MR"])
    
    # Analiz parametreleri
    st.subheader("Analiz Parametreleri")
    
    if analysis_type == "Multimodal Füzyon":
        render_multimodal_fusion_params()
    elif analysis_type == "Radyomik Analiz":
        render_radiomics_params()
    elif analysis_type == "Segmentasyon":
        render_segmentation_params()
    elif analysis_type == "SUV Trend Analizi":
        render_suv_trend_params()
    elif analysis_type == "PICO Otomatikleştirme":
        render_pico_params()
    
    # Analiz başlatma
    if st.button("🚀 Analizi Başlat"):
        with st.spinner("AI analizi yapılıyor..."):
            # Mock analiz süreci
            progress_bar = st.progress(0)
            
            for i in range(100):
                progress_bar.progress(i + 1)
                if i % 25 == 0:
                    st.write(f"Analiz ilerlemesi: {i + 1}%")
            
            st.success("✅ AI analizi tamamlandı!")
            
            # Sonuçları göster
            show_analysis_results(analysis_type)

def render_multimodal_fusion_params():
    """Multimodal Füzyon parametrelerini render et"""
    
    st.write("**Veri Kaynakları:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_imaging = st.checkbox("Görüntü Verileri", value=True)
        include_clinical = st.checkbox("Klinik Veriler", value=True)
        include_lab = st.checkbox("Laboratuvar Sonuçları", value=True)
    
    with col2:
        include_medications = st.checkbox("İlaç Listesi", value=True)
        include_biomarkers = st.checkbox("Biyobelirteçler", value=True)
        include_notes = st.checkbox("Klinik Notlar", value=True)
    
    st.write("**Füzyon Parametreleri:**")
    
    fusion_method = st.selectbox(
        "Füzyon Yöntemi",
        ["Cross-Attention", "Early Fusion", "Late Fusion", "Hybrid"]
    )
    
    confidence_threshold = st.slider(
        "Güven Eşiği",
        min_value=0.0,
        max_value=1.0,
        value=0.8,
        step=0.1
    )

def render_radiomics_params():
    """Radyomik analiz parametrelerini render et"""
    
    st.write("**Radyomik Özellikler:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        shape_features = st.checkbox("Şekil Özellikleri", value=True)
        texture_features = st.checkbox("Doku Özellikleri", value=True)
        intensity_features = st.checkbox("Yoğunluk Özellikleri", value=True)
    
    with col2:
        filter_features = st.checkbox("Filtre Özellikleri", value=True)
        wavelet_features = st.checkbox("Dalga Özellikleri", value=True)
        statistical_features = st.checkbox("İstatistiksel Özellikler", value=True)
    
    st.write("**Analiz Parametreleri:**")
    
    bin_width = st.slider("Bin Genişliği", min_value=1, max_value=50, value=25)
    normalize = st.checkbox("Normalizasyon", value=True)
    resample = st.checkbox("Yeniden Örnekleme", value=True)

def render_segmentation_params():
    """Segmentasyon parametrelerini render et"""
    
    st.write("**Segmentasyon Yöntemi:**")
    
    segmentation_method = st.selectbox(
        "Yöntem",
        ["U-Net", "DeepLab", "Mask R-CNN", "3D U-Net", "Hybrid"]
    )
    
    st.write("**Parametreler:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        threshold = st.slider("Eşik Değeri", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        min_size = st.number_input("Minimum Boyut (mm³)", min_value=1, value=100)
    
    with col2:
        max_size = st.number_input("Maksimum Boyut (mm³)", min_value=1000, value=10000)
        smooth_factor = st.slider("Yumuşatma Faktörü", min_value=0.0, max_value=2.0, value=1.0, step=0.1)

def render_suv_trend_params():
    """SUV Trend analizi parametrelerini render et"""
    
    st.write("**Trend Analizi Parametreleri:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trend_period = st.selectbox(
            "Trend Periyodu",
            ["3 Ay", "6 Ay", "1 Yıl", "2 Yıl", "Özel"]
        )
        
        if trend_period == "Özel":
            custom_period = st.number_input("Gün Sayısı", min_value=30, value=365)
    
    with col2:
        suv_type = st.selectbox("SUV Tipi", ["SUVmax", "SUVmean", "SUVpeak"])
        normalization = st.selectbox("Normalizasyon", ["Yok", "Vücut Ağırlığı", "Vücut Yüzeyi"])

def render_pico_params():
    """PICO parametrelerini render et"""
    
    st.write("**PICO Soru Parametreleri:**")
    
    clinical_context = st.text_area(
        "Klinik Bağlam",
        "65 yaşında erkek hasta, akciğer kanseri şüphesi ile FDG-PET/CT çekildi."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        evidence_level = st.selectbox(
            "Kanıt Seviyesi",
            ["1A", "1B", "2A", "2B", "3A", "3B", "4"]
        )
        
        databases = st.multiselect(
            "Veritabanları",
            ["PubMed", "Cochrane", "Embase", "Medline", "Scopus"],
            default=["PubMed", "Cochrane"]
        )
    
    with col2:
        publication_year = st.slider(
            "Yayın Yılı",
            min_value=2000,
            max_value=2024,
            value=(2010, 2024)
        )
        
        language = st.selectbox("Dil", ["İngilizce", "Türkçe", "Tümü"])

def show_analysis_results(analysis_type):
    """Analiz sonuçlarını göster"""
    
    st.subheader("📊 Analiz Sonuçları")
    
    if analysis_type == "Multimodal Füzyon":
        show_multimodal_results()
    elif analysis_type == "Radyomik Analiz":
        show_radiomics_results()
    elif analysis_type == "Segmentasyon":
        show_segmentation_results()
    elif analysis_type == "SUV Trend Analizi":
        show_suv_trend_results()
    elif analysis_type == "PICO Otomatikleştirme":
        show_pico_results()

def show_multimodal_results():
    """Multimodal füzyon sonuçlarını göster"""
    
    # Mock sonuçlar
    results = {
        "confidence_score": 0.87,
        "fusion_method": "Cross-Attention",
        "data_sources": ["Görüntü", "Klinik", "Laboratuvar"],
        "key_findings": [
            "Akciğer nodülü malignite riski: %85",
            "Lenf nodu metastazı olasılığı: %72",
            "Tedavi yanıtı tahmini: İyi"
        ]
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Güven Skoru", f"{results['confidence_score']:.2f}")
    
    with col2:
        st.metric("Füzyon Yöntemi", results['fusion_method'])
    
    with col3:
        st.metric("Veri Kaynağı", len(results['data_sources']))
    
    st.write("**Ana Bulgular:**")
    for finding in results['key_findings']:
        st.info(f"🔍 {finding}")
    
    # Görselleştirme
    st.subheader("📈 Görselleştirme")
    
    # Mock grafik
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Görüntü', 'Klinik', 'Laboratuvar'],
        y=[0.85, 0.72, 0.78],
        name='Veri Kaynağı Güvenilirliği'
    ))
    
    fig.update_layout(
        title="Veri Kaynağı Güvenilirliği",
        xaxis_title="Veri Kaynağı",
        yaxis_title="Güvenilirlik Skoru"
    )
    
    st.plotly_chart(fig)

def show_radiomics_results():
    """Radyomik analiz sonuçlarını göster"""
    
    # Mock sonuçlar
    results = {
        "total_features": 1218,
        "significant_features": 45,
        "classification_accuracy": 0.89,
        "top_features": [
            {"name": "GLCM_Contrast", "importance": 0.92},
            {"name": "GLRLM_LongRunEmphasis", "importance": 0.87},
            {"name": "Shape_Sphericity", "importance": 0.84}
        ]
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Toplam Özellik", results['total_features'])
    
    with col2:
        st.metric("Anlamlı Özellik", results['significant_features'])
    
    with col3:
        st.metric("Sınıflandırma Doğruluğu", f"{results['classification_accuracy']:.2f}")
    
    st.write("**En Önemli Özellikler:**")
    
    for feature in results['top_features']:
        st.write(f"🔹 **{feature['name']}**: {feature['importance']:.2f}")
    
    # Özellik önem grafiği
    fig = px.bar(
        x=[f['name'] for f in results['top_features']],
        y=[f['importance'] for f in results['top_features']],
        title="En Önemli Radyomik Özellikler"
    )
    
    st.plotly_chart(fig)

def show_segmentation_results():
    """Segmentasyon sonuçlarını göster"""
    
    # Mock sonuçlar
    results = {
        "total_lesions": 3,
        "dice_score": 0.89,
        "hausdorff_distance": 2.3,
        "lesions": [
            {"id": 1, "volume": 15.2, "location": "Sağ üst lob"},
            {"id": 2, "volume": 8.7, "location": "Sol alt lob"},
            {"id": 3, "volume": 12.1, "location": "Mediastinum"}
        ]
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Toplam Lezyon", results['total_lesions'])
    
    with col2:
        st.metric("Dice Skoru", f"{results['dice_score']:.2f}")
    
    with col3:
        st.metric("Hausdorff Mesafesi", f"{results['hausdorff_distance']:.1f} mm")
    
    st.write("**Lezyon Detayları:**")
    
    for lesion in results['lesions']:
        st.write(f"🔹 **Lezyon {lesion['id']}**: {lesion['volume']} cm³ - {lesion['location']}")

def show_suv_trend_results():
    """SUV Trend analizi sonuçlarını göster"""
    
    # Mock sonuçlar
    results = {
        "trend_direction": "Azalma",
        "trend_strength": 0.76,
        "p_value": 0.002,
        "data_points": [
            {"date": "2023-01", "suv": 8.5},
            {"date": "2023-04", "suv": 6.2},
            {"date": "2023-07", "suv": 4.8},
            {"date": "2023-10", "suv": 3.1}
        ]
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Trend Yönü", results['trend_direction'])
    
    with col2:
        st.metric("Trend Gücü", f"{results['trend_strength']:.2f}")
    
    with col3:
        st.metric("P Değeri", f"{results['p_value']:.3f}")
    
    # Trend grafiği
    df = pd.DataFrame(results['data_points'])
    
    fig = px.line(
        df,
        x='date',
        y='suv',
        title="SUV Trend Analizi",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Tarih",
        yaxis_title="SUV Değeri"
    )
    
    st.plotly_chart(fig)

def show_pico_results():
    """PICO analizi sonuçlarını göster"""
    
    # Mock sonuçlar
    results = {
        "pico_question": {
            "population": "65 yaşında erkek akciğer kanseri hastaları",
            "intervention": "FDG-PET/CT görüntüleme",
            "comparison": "Standart görüntüleme yöntemleri",
            "outcome": "Tanısal doğruluk ve tedavi planlaması"
        },
        "evidence_level": "1A",
        "studies_found": 15,
        "relevant_studies": 8,
        "recommendation": "Güçlü öneri"
    }
    
    st.write("**PICO Sorusu:**")
    
    pico = results['pico_question']
    st.info(f"**P (Population):** {pico['population']}")
    st.info(f"**I (Intervention):** {pico['intervention']}")
    st.info(f"**C (Comparison):** {pico['comparison']}")
    st.info(f"**O (Outcome):** {pico['outcome']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Kanıt Seviyesi", results['evidence_level'])
    
    with col2:
        st.metric("Bulunan Çalışma", results['studies_found'])
    
    with col3:
        st.metric("İlgili Çalışma", results['relevant_studies'])
    
    st.success(f"**Öneri:** {results['recommendation']}")
    
    # Çalışma listesi
    st.write("**İlgili Çalışmalar:**")
    
    studies = [
        {"title": "FDG-PET/CT in Lung Cancer Staging", "year": 2023, "relevance": 0.95},
        {"title": "PET/CT vs CT in NSCLC", "year": 2022, "relevance": 0.88},
        {"title": "Metabolic Imaging in Oncology", "year": 2023, "relevance": 0.82}
    ]
    
    for study in studies:
        st.write(f"🔹 **{study['title']}** ({study['year']}) - İlgi: {study['relevance']:.2f}")
