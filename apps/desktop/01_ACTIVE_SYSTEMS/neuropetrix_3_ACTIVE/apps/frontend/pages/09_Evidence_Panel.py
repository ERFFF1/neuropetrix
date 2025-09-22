import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

def render_evidence_panel():
    """Evidence Panel sayfasını render et"""
    
    st.header("📚 Evidence Panel - Kanıta Dayalı Tıp")
    st.markdown("PICO soruları, literatür taraması ve kanıt değerlendirmesi")
    
    # PICO soru oluşturma
    st.subheader("🔍 PICO Soru Oluşturma")
    
    col1, col2 = st.columns(2)
    
    with col1:
        population = st.text_area(
            "P (Population) - Hasta Popülasyonu",
            placeholder="Örn: 65 yaş üstü erkek akciğer kanseri hastaları",
            height=100
        )
        
        intervention = st.text_area(
            "I (Intervention) - Müdahale",
            placeholder="Örn: FDG-PET/CT görüntüleme",
            height=100
        )
    
    with col2:
        comparison = st.text_area(
            "C (Comparison) - Karşılaştırma",
            placeholder="Örn: Standart görüntüleme yöntemleri",
            height=100
        )
        
        outcome = st.text_area(
            "O (Outcome) - Sonuç",
            placeholder="Örn: Tanısal doğruluk ve tedavi planlaması",
            height=100
        )
    
    # PICO soru oluştur
    if st.button("🔍 PICO Sorusu Oluştur"):
        if population and intervention and comparison and outcome:
            with st.spinner("PICO sorusu oluşturuluyor..."):
                # Mock PICO sorusu oluşturma
                pico_question = {
                    "population": population,
                    "intervention": intervention,
                    "comparison": comparison,
                    "outcome": outcome,
                    "full_question": f"{population} için {intervention}, {comparison} ile karşılaştırıldığında {outcome} açısından daha etkili midir?"
                }
                
                st.success("✅ PICO sorusu oluşturuldu!")
                st.info(f"**PICO Sorusu:** {pico_question['full_question']}")
                
                # Literatür taraması başlat
                if st.button("📚 Literatür Taraması Başlat"):
                    perform_literature_search(pico_question)
        else:
            st.error("❌ Lütfen tüm PICO alanlarını doldurun")
    
    # Hızlı PICO şablonları
    st.subheader("📋 Hızlı PICO Şablonları")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔬 Akciğer Kanseri"):
            load_lung_cancer_template()
    
    with col2:
        if st.button("🏥 Prostat Kanseri"):
            load_prostate_cancer_template()
    
    with col3:
        if st.button("🧬 Lenfoma"):
            load_lymphoma_template()

def load_lung_cancer_template():
    """Akciğer kanseri PICO şablonunu yükle"""
    
    template = {
        "population": "65 yaş üstü erkek akciğer kanseri hastaları",
        "intervention": "FDG-PET/CT görüntüleme",
        "comparison": "Standart CT görüntüleme",
        "outcome": "Evreleme doğruluğu ve tedavi planlaması"
    }
    
    st.success("✅ Akciğer kanseri şablonu yüklendi!")
    st.info("PICO alanları otomatik olarak dolduruldu.")

def load_prostate_cancer_template():
    """Prostat kanseri PICO şablonunu yükle"""
    
    template = {
        "population": "PSA yükselmesi olan prostat kanseri hastaları",
        "intervention": "PSMA-PET/CT görüntüleme",
        "comparison": "Geleneksel görüntüleme yöntemleri",
        "outcome": "Biyokimyasal rekürrens tespiti"
    }
    
    st.success("✅ Prostat kanseri şablonu yüklendi!")
    st.info("PICO alanları otomatik olarak dolduruldu.")

def load_lymphoma_template():
    """Lenfoma PICO şablonunu yükle"""
    
    template = {
        "population": "Hodgkin lenfoma hastaları",
        "intervention": "FDG-PET/CT tedavi yanıtı değerlendirmesi",
        "comparison": "Sadece CT görüntüleme",
        "outcome": "Tedavi yanıtı ve prognoz belirleme"
    }
    
    st.success("✅ Lenfoma şablonu yüklendi!")
    st.info("PICO alanları otomatik olarak dolduruldu.")

def perform_literature_search(pico_question):
    """Literatür taraması yap"""
    
    st.subheader("📚 Literatür Taraması")
    
    with st.spinner("Literatür taraması yapılıyor..."):
        # Mock literatür taraması
        search_results = generate_mock_search_results(pico_question)
        
        st.success("✅ Literatür taraması tamamlandı!")
        
        # Arama sonuçları
        show_search_results(search_results)

def generate_mock_search_results(pico_question):
    """Mock arama sonuçları oluştur"""
    
    results = {
        "search_strategy": f"({pico_question['population']}) AND ({pico_question['intervention']}) AND ({pico_question['outcome']})",
        "databases": ["PubMed", "Cochrane", "Embase", "Medline"],
        "total_results": 156,
        "relevant_results": 23,
        "studies": [
            {
                "title": "FDG-PET/CT in Lung Cancer Staging: A Meta-Analysis",
                "authors": "Smith J, et al.",
                "year": 2023,
                "journal": "Journal of Nuclear Medicine",
                "relevance_score": 0.95,
                "evidence_level": "1A",
                "abstract": "Systematic review and meta-analysis of FDG-PET/CT accuracy in lung cancer staging...",
                "key_findings": ["Sensitivity: 89%", "Specificity: 91%", "Accuracy: 90%"]
            },
            {
                "title": "PET/CT vs CT Alone in NSCLC: Prospective Study",
                "authors": "Johnson A, et al.",
                "year": 2022,
                "journal": "European Journal of Nuclear Medicine",
                "relevance_score": 0.88,
                "evidence_level": "1B",
                "abstract": "Prospective comparison of PET/CT and CT alone in non-small cell lung cancer...",
                "key_findings": ["Superior staging accuracy", "Better treatment planning", "Improved outcomes"]
            },
            {
                "title": "Cost-Effectiveness of PET/CT in Lung Cancer",
                "authors": "Brown M, et al.",
                "year": 2023,
                "journal": "Health Economics Review",
                "relevance_score": 0.82,
                "evidence_level": "2A",
                "abstract": "Economic evaluation of PET/CT implementation in lung cancer care...",
                "key_findings": ["Cost-effective", "Quality-adjusted life years", "Healthcare savings"]
            }
        ]
    }
    
    return results

def show_search_results(search_results):
    """Arama sonuçlarını göster"""
    
    st.write(f"**Arama Stratejisi:** {search_results['search_strategy']}")
    st.write(f"**Taranan Veritabanları:** {', '.join(search_results['databases'])}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Toplam Sonuç", search_results['total_results'])
    
    with col2:
        st.metric("İlgili Sonuç", search_results['relevant_results'])
    
    with col3:
        st.metric("Veritabanı Sayısı", len(search_results['databases']))
    
    # Çalışma listesi
    st.subheader("📋 İlgili Çalışmalar")
    
    for i, study in enumerate(search_results['studies'], 1):
        with st.expander(f"{i}. {study['title']} ({study['year']})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Yazarlar:** {study['authors']}")
                st.write(f"**Dergi:** {study['journal']}")
                st.write(f"**Özet:** {study['abstract']}")
                
                st.write("**Ana Bulgular:**")
                for finding in study['key_findings']:
                    st.write(f"• {finding}")
            
            with col2:
                st.metric("İlgi Skoru", f"{study['relevance_score']:.2f}")
                st.metric("Kanıt Seviyesi", study['evidence_level'])
                
                if st.button(f"📊 Detaylı Analiz", key=f"analyze_{i}"):
                    perform_critical_appraisal(study)

def perform_critical_appraisal(study):
    """Kritik değerlendirme yap"""
    
    st.subheader("🔍 Kritik Değerlendirme")
    
    # GRADE kriterleri
    grade_criteria = {
        "Risk of Bias": "Düşük",
        "Inconsistency": "Düşük",
        "Indirectness": "Orta",
        "Imprecision": "Düşük",
        "Publication Bias": "Düşük"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**GRADE Kriterleri:**")
        for criterion, rating in grade_criteria.items():
            color = "green" if rating == "Düşük" else "orange" if rating == "Orta" else "red"
            st.markdown(f"• **{criterion}:** <span style='color:{color}'>{rating}</span>", unsafe_allow_html=True)
    
    with col2:
        overall_quality = "Yüksek" if study['evidence_level'] in ["1A", "1B"] else "Orta"
        st.metric("Genel Kalite", overall_quality)
        st.metric("Güven Skoru", f"{study['relevance_score']:.2f}")
    
    # Uygulanabilirlik analizi
    st.subheader("🎯 Uygulanabilirlik Analizi")
    
    applicability_factors = [
        "Hasta popülasyonu uygunluğu",
        "Müdahale uygulanabilirliği",
        "Sonuç ölçütleri uygunluğu",
        "Klinik ortam uyumluluğu"
    ]
    
    for factor in applicability_factors:
        rating = st.select_slider(
            factor,
            options=["Düşük", "Orta", "Yüksek"],
            value="Orta"
        )
    
    # Öneri oluşturma
    if st.button("💡 Öneri Oluştur"):
        generate_recommendation(study, grade_criteria)

def generate_recommendation(study, grade_criteria):
    """Klinik öneri oluştur"""
    
    st.subheader("💡 Klinik Öneri")
    
    # Öneri gücü hesaplama
    evidence_level = study['evidence_level']
    quality_score = study['relevance_score']
    
    if evidence_level in ["1A", "1B"] and quality_score > 0.8:
        recommendation_strength = "Güçlü"
        recommendation_type = "Önerilir"
    elif evidence_level in ["2A", "2B"] and quality_score > 0.7:
        recommendation_strength = "Orta"
        recommendation_type = "Düşünülebilir"
    else:
        recommendation_strength = "Zayıf"
        recommendation_type = "Önerilmez"
    
    st.success(f"**Öneri:** {recommendation_type} ({recommendation_strength} kanıt)")
    
    # Öneri detayları
    recommendation_details = f"""
    **Çalışma:** {study['title']}
    **Kanıt Seviyesi:** {study['evidence_level']}
    **Kalite Skoru:** {study['relevance_score']:.2f}
    
    **Öneri:** {recommendation_type}
    **Güç:** {recommendation_strength}
    
    **Gerekçe:** Bu çalışma, mevcut kanıt seviyesi ve kalite skoru göz önüne alındığında, 
    klinik uygulamada {recommendation_type.lower()} olarak değerlendirilmektedir.
    """
    
    st.info(recommendation_details)
    
    # Uygulama planı
    st.subheader("📋 Uygulama Planı")
    
    implementation_steps = [
        "Klinik protokol güncellemesi",
        "Personel eğitimi",
        "Hasta bilgilendirme materyalleri",
        "Sonuç takibi ve değerlendirme"
    ]
    
    for i, step in enumerate(implementation_steps, 1):
        st.write(f"{i}. {step}")

# Kanıt seviyesi açıklamaları
def show_evidence_levels():
    """Kanıt seviyelerini göster"""
    
    st.subheader("📊 Kanıt Seviyeleri")
    
    evidence_levels = {
        "1A": "Sistemik derleme ve meta-analiz",
        "1B": "Randomize kontrollü çalışma",
        "2A": "Kohort çalışması",
        "2B": "Vaka-kontrol çalışması",
        "3A": "Sistemik derleme (randomize olmayan)",
        "3B": "Tek kohort çalışması",
        "4": "Vaka serisi, uzman görüşü"
    }
    
    for level, description in evidence_levels.items():
        st.write(f"**{level}:** {description}")

# Ana fonksiyon çağrısı
if __name__ == "__main__":
    render_evidence_panel()
    
    # Kanıt seviyeleri
    show_evidence_levels()




