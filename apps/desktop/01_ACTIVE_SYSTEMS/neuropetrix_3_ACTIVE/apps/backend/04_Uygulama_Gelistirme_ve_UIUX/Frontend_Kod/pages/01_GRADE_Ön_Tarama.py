import streamlit as st
import requests
import json
from datetime import datetime

def render_grade_screening():
    """GRADE Ön Tarama sayfasını render et"""
    
    st.header("🔍 GRADE Ön Tarama")
    
    # Hasta bilgileri
    st.subheader("Hasta Bilgileri")
    col1, col2 = st.columns(2)
    
    with col1:
        patient_name = st.text_input("Hasta Adı", "Ahmet Yılmaz")
        patient_age = st.number_input("Yaş", min_value=0, max_value=120, value=65)
    
    with col2:
        patient_gender = st.selectbox("Cinsiyet", ["M", "F"])
        diagnosis = st.text_input("Tanı", "Lung cancer")
    
    # Klinik bağlam
    clinical_context = st.text_area(
        "Klinik Bağlam",
        "Suspicious lung nodule on CT scan, need for PET/CT evaluation"
    )
    
    # GRADE kriterleri
    st.subheader("GRADE Kriterleri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        study_design = st.selectbox(
            "Çalışma Tasarımı",
            ["Randomized controlled trial", "Cohort study", "Case-control study", "Cross-sectional study"]
        )
        
        risk_of_bias = st.selectbox(
            "Yanlılık Riski",
            ["Low", "Some concerns", "High"]
        )
    
    with col2:
        inconsistency = st.selectbox(
            "Tutarsızlık",
            ["Not serious", "Serious", "Very serious"]
        )
        
        indirectness = st.selectbox(
            "Dolaylılık",
            ["Not serious", "Serious", "Very serious"]
        )
    
    imprecision = st.selectbox(
        "Hassasiyet",
        ["Not serious", "Serious", "Very serious"]
    )
    
    publication_bias = st.selectbox(
        "Yayın Yanlılığı",
        ["Not serious", "Serious", "Very serious"]
    )
    
    # GRADE hesaplama
    if st.button("GRADE Seviyesini Hesapla"):
        with st.spinner("GRADE seviyesi hesaplanıyor..."):
            
            # Basit GRADE hesaplama
            grade_score = 0
            
            if study_design == "Randomized controlled trial":
                grade_score += 4
            elif study_design == "Cohort study":
                grade_score += 3
            elif study_design == "Case-control study":
                grade_score += 2
            else:
                grade_score += 1
            
            # Yanlılık riski
            if risk_of_bias == "Low":
                grade_score += 0
            elif risk_of_bias == "Some concerns":
                grade_score -= 1
            else:
                grade_score -= 2
            
            # Diğer kriterler
            for criterion in [inconsistency, indirectness, imprecision, publication_bias]:
                if criterion == "Serious":
                    grade_score -= 1
                elif criterion == "Very serious":
                    grade_score -= 2
            
            # GRADE seviyesi belirleme
            if grade_score >= 4:
                grade_level = "High"
                grade_color = "success"
            elif grade_score >= 2:
                grade_level = "Moderate"
                grade_color = "info"
            elif grade_score >= 0:
                grade_level = "Low"
                grade_color = "warning"
            else:
                grade_level = "Very Low"
                grade_color = "error"
            
            st.success(f"GRADE Seviyesi: {grade_level}")
            st.info(f"Toplam Skor: {grade_score}")
            
            # Detaylı açıklama
            st.subheader("Detaylı Açıklama")
            st.write(f"""
            **Çalışma Tasarımı:** {study_design}
            **Yanlılık Riski:** {risk_of_bias}
            **Tutarsızlık:** {inconsistency}
            **Dolaylılık:** {indirectness}
            **Hassasiyet:** {imprecision}
            **Yayın Yanlılığı:** {publication_bias}
            """)
    
    # PICO soru oluşturma
    st.subheader("PICO Soru Oluşturma")
    
    if st.button("PICO Soru Oluştur"):
        with st.spinner("PICO soru oluşturuluyor..."):
            # Mock PICO soru
            pico_question = {
                "population": f"{patient_age} yaşında {patient_gender} hasta",
                "intervention": "FDG-PET/CT görüntüleme",
                "comparison": "Standart görüntüleme yöntemleri",
                "outcome": "Tanısal doğruluk ve tedavi planlaması"
            }
            
            st.success("PICO Soru Oluşturuldu!")
            st.json(pico_question)
    
    # Literatür arama
    st.subheader("Literatür Arama")
    
    search_databases = st.multiselect(
        "Arama Veritabanları",
        ["PubMed", "Cochrane", "Embase", "Scopus", "Web of Science"],
        default=["PubMed", "Cochrane"]
    )
    
    date_range = st.slider(
        "Yayın Tarihi Aralığı",
        min_value=2010,
        max_value=2024,
        value=(2020, 2024)
    )
    
    if st.button("Literatür Ara"):
        with st.spinner("Literatür arama yapılıyor..."):
            # Mock arama sonuçları
            search_results = [
                {
                    "title": "FDG-PET/CT in Lung Cancer Diagnosis: A Meta-Analysis",
                    "authors": "Smith J, et al.",
                    "journal": "Journal of Nuclear Medicine",
                    "year": 2023,
                    "doi": "10.1000/jnm.2023.001",
                    "evidence_level": "1A",
                    "relevance_score": 0.95
                },
                {
                    "title": "PET/CT vs CT Alone in Cancer Staging",
                    "authors": "Johnson A, et al.",
                    "journal": "European Journal of Nuclear Medicine",
                    "year": 2022,
                    "doi": "10.1000/ejnm.2022.002",
                    "evidence_level": "1B",
                    "relevance_score": 0.87
                }
            ]
            
            st.success(f"{len(search_results)} sonuç bulundu")
            
            for i, result in enumerate(search_results, 1):
                with st.expander(f"{i}. {result['title']}"):
                    st.write(f"**Yazarlar:** {result['authors']}")
                    st.write(f"**Dergi:** {result['journal']} ({result['year']})")
                    st.write(f"**DOI:** {result['doi']}")
                    st.write(f"**Kanıt Seviyesi:** {result['evidence_level']}")
                    st.write(f"**İlgi Skoru:** {result['relevance_score']}")


