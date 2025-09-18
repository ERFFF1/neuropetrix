import streamlit as st
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Evidence Panel - NeuroPETrix",
    page_icon="📚",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Page title and description
st.title("📚 Evidence Panel - Kanıt Tabanlı Klinik Karar Desteği")
st.markdown("**PICO Sorguları • Literatür Taraması • GRADE Değerlendirmesi • Klinik Öneriler**")

# Backend URL configuration
if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = "http://127.0.0.1:8000"

backend_url = st.sidebar.text_input("Backend URL", st.session_state["backend_url"])
st.session_state["backend_url"] = st.session_state["backend_url"]

# Sidebar navigation
st.sidebar.title("🧭 Hızlı Navigasyon")
st.sidebar.markdown("---")

if st.session_state.sidebar.button("🏠 Ana Sayfa", use_container_width=True):
    st.switch_page("streamlit_app.py")

if st.session_state.sidebar.button("📊 Dashboard", use_container_width=True):
    st.switch_page("pages/00_Dashboard.py")

if st.session_state.sidebar.button("🧪 GRADE Scoring", use_container_width=True):
    st.switch_page("pages/01_GRADE_Ön_Tarama.py")

st.session_state.sidebar.markdown("---")

# System status in sidebar
st.session_state.sidebar.subheader("📊 Sistem Durumu")
try:
    health_response = requests.get(f"{backend_url}/health", timeout=3)
    if health_response.status_code == 200:
        st.session_state.sidebar.success("🟢 Backend OK")
    else:
        st.session_state.sidebar.error("🔴 Backend Error")
except:
    st.session_state.sidebar.error("🔌 Backend Offline")

# Initialize session state
if "evidence_queries" not in st.session_state:
    st.session_state["evidence_queries"] = []
if "current_query" not in st.session_state:
    st.session_state["current_query"] = None
if "literature_results" not in st.session_state:
    st.session_state["literature_results"] = []

# ---- HERO SECTION ----
col_hero1, col_hero2 = st.columns([2, 1])

with col_hero1:
    st.markdown("""
    <div class="hero">
        <div>
            <h1>📚 Evidence Panel</h1>
            <div class="subtitle">Kanıt tabanlı klinik karar desteği ve literatür entegrasyonu</div>
        </div>
        <div>
            <span class="badge ok">PICO Ready</span>
            <span class="badge">GRADE Active</span>
            <span class="badge">AI Powered</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    st.markdown("### 🎯 Hızlı İşlemler")
    
    # Quick actions
    if st.button("🔍 Hızlı Sorgu", type="primary", use_container_width=True):
        st.session_state["current_query"] = "quick"
        st.rerun()
    
    if st.button("📚 Literatür Tarama", type="secondary", use_container_width=True):
        st.session_state["current_query"] = "literature"
        st.rerun()

st.write("")

# ---- PICO QUERY FORM ----
st.header("🔍 PICO Sorgu Formu")

# PICO framework
col_pico1, col_pico2, col_pico3, col_pico4 = st.columns(4)

with col_pico1:
    st.subheader("👥 **P** - Population")
    
    population = st.text_area(
        "Hasta Popülasyonu",
        value="Yetişkin akciğer kanseri hastaları",
        height=100,
        help="Hedef hasta grubu"
    )
    
    age_range = st.selectbox(
        "Yaş Aralığı",
        ["18-65", "18-75", "65+", "Tüm yaşlar"],
        index=0
    )
    
    disease_stage = st.multiselect(
        "Hastalık Evresi",
        ["Erken evre", "Lokal ileri", "Metastatik", "Rekürrent"],
        default=["Erken evre", "Lokal ileri"]
    )

with col_pico2:
    st.subheader("🔬 **I** - Intervention")
    
    intervention = st.text_area(
        "Müdahale",
        value="FDG PET/CT ile evreleme",
        height=100,
        help="Uygulanan müdahale veya test"
    )
    
    intervention_type = st.selectbox(
        "Müdahale Türü",
        ["Tanısal", "Tedavi", "Takip", "Evreleme", "Prognoz"],
        index=3
    )
    
    modality = st.multiselect(
        "Modalite",
        ["PET/CT", "PET/MR", "SPECT/CT", "CT", "MR"],
        default=["PET/CT"]
    )

with col_pico3:
    st.subheader("⚖️ **C** - Comparison")
    
    comparison = st.text_area(
        "Karşılaştırma",
        value="Geleneksel evreleme yöntemleri",
        height=100,
        help="Karşılaştırılan alternatif"
    )
    
    comparison_type = st.selectbox(
        "Karşılaştırma Türü",
        ["Standard of care", "Placebo", "Alternatif test", "Hiçbir şey", "Diğer"],
        index=0
    )
    
    control_group = st.text_input(
        "Kontrol Grubu",
        value="Geleneksel evreleme",
        help="Kontrol grubu tanımı"
    )

with col_pico4:
    st.subheader("🎯 **O** - Outcome")
    
    outcome = st.text_area(
        "Sonuç",
        value="Evreleme doğruluğu ve tedavi planı değişikliği",
        height=100,
        help="Ölçülen sonuç"
    )
    
    outcome_type = st.selectbox(
        "Sonuç Türü",
        ["Birincil", "İkincil", "Surrogate", "Klinik"],
        index=0
    )
    
    outcome_measures = st.multiselect(
        "Sonuç Ölçümleri",
        ["Hassasiyet", "Özgüllük", "Doğruluk", "Survival", "Yaşam kalitesi"],
        default=["Hassasiyet", "Özgüllük"]
    )

st.write("")

# Additional query parameters
col_params1, col_params2 = st.columns(2)

with col_params1:
    st.subheader("📅 Zaman Parametreleri")
    
    publication_year = st.slider(
        "Yayın Yılı Aralığı",
        min_value=2000,
        max_value=2025,
        value=(2015, 2025),
        help="Literatür tarama yıl aralığı"
    )
    
    study_design = st.multiselect(
        "Çalışma Tasarımı",
        ["Randomized Controlled Trial", "Cohort Study", "Case-Control Study", 
         "Systematic Review", "Meta-analysis", "Expert Opinion"],
        default=["Randomized Controlled Trial", "Systematic Review"]
    )

with col_params2:
    st.subheader("🌐 Dil ve Veritabanı")
    
    language = st.multiselect(
        "Dil",
        ["İngilizce", "Türkçe", "Almanca", "Fransızca", "İspanyolca"],
        default=["İngilizce", "Türkçe"]
    )
    
    database = st.multiselect(
        "Veritabanı",
        ["PubMed", "Embase", "Cochrane", "Scopus", "Web of Science"],
        default=["PubMed", "Cochrane"]
    )

# Search button
if st.button("🔍 PICO Sorgusu Başlat", type="primary", use_container_width=True):
    # Create PICO query
    pico_query = {
        "population": population,
        "intervention": intervention,
        "comparison": comparison,
        "outcome": outcome,
        "age_range": age_range,
        "disease_stage": disease_stage,
        "intervention_type": intervention_type,
        "modality": modality,
        "comparison_type": comparison_type,
        "control_group": control_group,
        "outcome_type": outcome_type,
        "outcome_measures": outcome_measures,
        "publication_year": publication_year,
        "study_design": study_design,
        "language": language,
        "database": database,
        "timestamp": datetime.now().isoformat()
    }
    
    st.session_state["evidence_queries"].append(pico_query)
    st.session_state["current_query"] = len(st.session_state["evidence_queries"]) - 1
    st.success("✅ PICO sorgusu oluşturuldu! Literatür taraması başlatılıyor...")
    st.rerun()

st.write("")

# ---- LITERATURE SEARCH RESULTS ----
if st.session_state["current_query"] is not None:
    st.header("📚 Literatür Tarama Sonuçları")
    
    current_query = st.session_state["evidence_queries"][st.session_state["current_query"]]
    
    # Display current query
    with st.expander("🔍 Mevcut PICO Sorgusu", expanded=True):
        col_query1, col_query2 = st.columns(2)
        
        with col_query1:
            st.markdown(f"**👥 Population:** {current_query['population']}")
            st.markdown(f"**🔬 Intervention:** {current_query['intervention']}")
            st.markdown(f"**⚖️ Comparison:** {current_query['comparison']}")
            st.markdown(f"**🎯 Outcome:** {current_query['outcome']}")
        
        with col_query2:
            st.markdown(f"**📅 Yıl Aralığı:** {current_query['publication_year'][0]}-{current_query['publication_year'][1]}")
            st.markdown(f"**🔬 Çalışma Tasarımı:** {', '.join(current_query['study_design'])}")
            st.markdown(f"**🌐 Dil:** {', '.join(current_query['language'])}")
            st.markdown(f"**📊 Veritabanı:** {', '.join(current_query['database'])}")
    
    # Simulate literature search
    if not st.session_state["literature_results"]:
        st.info("🔍 Literatür taraması yapılıyor...")
        
        # Progress simulation
        progress = st.progress(0)
        status_text = st.empty()
        
        for i in range(101):
            progress.progress(i)
            if i < 30:
                status_text.text("🔍 Veritabanları taranıyor...")
            elif i < 60:
                status_text.text("📊 Makaleler filtreleniyor...")
            elif i < 90:
                status_text.text("📋 Sonuçlar değerlendiriliyor...")
            else:
                status_text.text("✅ Literatür taraması tamamlandı!")
        
        # Mock results
        st.session_state["literature_results"] = [
            {
                "title": "FDG PET/CT in Lung Cancer Staging: A Meta-analysis",
                "authors": "Smith J, Johnson A, Williams B",
                "journal": "Journal of Nuclear Medicine",
                "year": 2024,
                "study_type": "Meta-analysis",
                "sample_size": 1250,
                "grade_level": "1A",
                "relevance_score": 0.95,
                "abstract": "This meta-analysis evaluated the diagnostic accuracy of FDG PET/CT in lung cancer staging...",
                "key_findings": "FDG PET/CT showed 89% sensitivity and 92% specificity in detecting distant metastases",
                "limitations": "Heterogeneity among studies, limited follow-up data"
            },
            {
                "title": "Comparative Effectiveness of PET/CT vs Conventional Staging",
                "authors": "Brown K, Davis L, Wilson M",
                "journal": "European Journal of Nuclear Medicine",
                "year": 2023,
                "study_type": "Randomized Controlled Trial",
                "sample_size": 450,
                "grade_level": "1B",
                "relevance_score": 0.88,
                "abstract": "Randomized trial comparing PET/CT with conventional staging methods...",
                "key_findings": "PET/CT changed treatment plan in 23% of cases",
                "limitations": "Single-center study, limited generalizability"
            },
            {
                "title": "Systematic Review: PET/CT in Early Stage Lung Cancer",
                "authors": "Miller R, Anderson S, Taylor P",
                "journal": "Cochrane Database of Systematic Reviews",
                "year": 2023,
                "study_type": "Systematic Review",
                "sample_size": 800,
                "grade_level": "1A",
                "relevance_score": 0.92,
                "abstract": "Systematic review of PET/CT use in early stage lung cancer...",
                "key_findings": "PET/CT upstaged 15% of patients, downstaged 8%",
                "limitations": "Inconsistent reporting, publication bias"
            }
        ]
    
    # Display results
    if st.session_state["literature_results"]:
        st.success(f"📚 {len(st.session_state['literature_results'])} makale bulundu!")
        
        # Results overview
        col_results1, col_results2, col_results3 = st.columns(3)
        
        with col_results1:
            st.metric("📊 Toplam Makale", len(st.session_state["literature_results"]))
            st.metric("🎯 Ortalama İlgi", f"{np.mean([r['relevance_score'] for r in st.session_state['literature_results']]):.2f}")
        
        with col_results2:
            study_types = [r['study_type'] for r in st.session_state["literature_results"]]
            st.metric("🔬 Çalışma Türleri", len(set(study_types)))
            st.metric("📈 Toplam Örneklem", sum([r['sample_size'] for r in st.session_state["literature_results"]]))
        
        with col_results3:
            grade_levels = [r['grade_level'] for r in st.session_state["literature_results"]]
            st.metric("📚 GRADE Seviyeleri", len(set(grade_levels)))
            high_quality = len([g for g in grade_levels if g in ['1A', '1B']])
            st.metric("⭐ Yüksek Kalite", high_quality)
        
        # Detailed results
        st.subheader("📋 Makale Detayları")
        
        for i, result in enumerate(st.session_state["literature_results"]):
            with st.expander(f"📄 {result['title']} ({result['year']})", expanded=False):
                col_art1, col_art2 = st.columns([3, 1])
                
                with col_art1:
                    st.markdown(f"**Yazarlar:** {result['authors']}")
                    st.markdown(f"**Dergi:** {result['journal']}")
                    st.markdown(f"**Çalışma Türü:** {result['study_type']}")
                    st.markdown(f"**Örneklem:** {result['sample_size']} hasta")
                    st.markdown(f"**GRADE Seviyesi:** {result['grade_level']}")
                    st.markdown(f"**İlgi Skoru:** {result['relevance_score']:.2f}")
                    
                    st.markdown("**Özet:**")
                    st.markdown(result['abstract'])
                    
                    st.markdown("**Ana Bulgular:**")
                    st.markdown(result['key_findings'])
                    
                    st.markdown("**Sınırlamalar:**")
                    st.markdown(result['limitations'])
                
                with col_art2:
                    # GRADE level indicator
                    grade_colors = {"1A": "green", "1B": "green", "2A": "blue", "2B": "blue", "3": "yellow", "Expert": "purple"}
                    grade_color = grade_colors.get(result['grade_level'], "gray")
                    
                    st.markdown(f"<div style='background-color: {grade_color}; color: white; padding: 10px; border-radius: 5px; text-align: center;'>")
                    st.markdown(f"**GRADE {result['grade_level']}**")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Relevance score
                    st.markdown(f"**İlgi Skoru:** {result['relevance_score']:.2f}")
                    
                    # Action buttons
                    if st.button(f"📝 GRADE Değerlendir", key=f"grade_{i}"):
                        st.info("🧪 GRADE değerlendirmesi için GRADE Scoring sayfasına yönlendiriliyorsunuz...")
                    
                    if st.button(f"📊 Detaylı Analiz", key=f"analyze_{i}"):
                        st.info("📊 Detaylı analiz özelliği yakında eklenecek")

st.write("")

# ---- EVIDENCE SYNTHESIS ----
if st.session_state["literature_results"]:
    st.header("🔬 Kanıt Sentezi ve Klinik Öneriler")
    
    col_synth1, col_synth2 = st.columns(2)
    
    with col_synth1:
        st.subheader("📊 Kanıt Kalitesi Özeti")
        
        # Evidence quality summary
        grade_counts = {}
        for result in st.session_state["literature_results"]:
            grade = result['grade_level']
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        # Create pie chart
        if grade_counts:
            fig_grade = px.pie(
                values=list(grade_counts.values()),
                names=list(grade_counts.keys()),
                title="GRADE Seviyeleri Dağılımı"
            )
            fig_grade.update_layout(height=400)
            st.plotly_chart(fig_grade, use_container_width=True)
        
        # Quality assessment
        high_quality_count = sum(1 for g in grade_counts.keys() if g in ['1A', '1B'])
        total_count = len(st.session_state["literature_results"])
        
        if high_quality_count / total_count >= 0.7:
            st.success(f"✅ **Yüksek Kalite** - {high_quality_count}/{total_count} makale yüksek kalitede")
        elif high_quality_count / total_count >= 0.4:
            st.warning(f"⚠️ **Orta Kalite** - {high_quality_count}/{total_count} makale yüksek kalitede")
        else:
            st.error(f"❌ **Düşük Kalite** - Sadece {high_quality_count}/{total_count} makale yüksek kalitede")
    
    with col_synth2:
        st.subheader("🎯 Klinik Öneriler")
        
        # Clinical recommendations based on evidence
        if st.session_state["literature_results"]:
            # Analyze evidence strength
            strong_evidence = any(r['grade_level'] in ['1A', '1B'] for r in st.session_state["literature_results"])
            consistent_findings = len(set(r['key_findings'][:50] for r in st.session_state["literature_results"])) <= 2
            
            if strong_evidence and consistent_findings:
                st.success("**💪 Güçlü Öneri** - Kanıt güçlü ve tutarlı")
                st.markdown("• FDG PET/CT akciğer kanseri evrelemesinde önerilir")
                st.markdown("• Tedavi planı değişikliği için rutin kullanım")
                st.markdown("• Takip protokollerinde standart olarak dahil edilmeli")
            elif strong_evidence:
                st.info("**📋 Koşullu Öneri** - Kanıt güçlü ama tutarsız")
                st.markdown("• FDG PET/CT kullanımı önerilir")
                st.markdown("• Sonuçlar dikkatli değerlendirilmeli")
                st.markdown("• Ek görüntüleme gerekebilir")
            else:
                st.warning("**⚠️ Zayıf Öneri** - Kanıt yetersiz")
                st.markdown("• FDG PET/CT kullanımı dikkatli değerlendirilmeli")
                st.markdown("• Bireysel hasta bazında karar verilmeli")
                st.markdown("• Daha fazla araştırma gerekli")
        
        # Limitations and gaps
        st.markdown("**📋 Sınırlamalar ve Boşluklar:**")
        st.markdown("• Heterojen hasta popülasyonları")
        st.markdown("• Farklı PET/CT protokolleri")
        st.markdown("• Uzun vadeli sonuç verisi eksik")
        st.markdown("• Maliyet-etkinlik analizi yetersiz")

# ---- EXPORT AND INTEGRATION ----
st.header("📤 Dışa Aktarma ve Entegrasyon")

col_export1, col_export2, col_export3 = st.columns(3)

with col_export1:
    st.subheader("📊 Rapor Oluşturma")
    
    report_type = st.selectbox(
        "Rapor Türü",
        ["Kanıt Özeti", "Klinik Öneri", "Literatür Analizi", "Tam Rapor"],
        index=0
    )
    
    if st.button("📝 Rapor Oluştur", use_container_width=True):
        st.success("📝 Rapor oluşturuluyor...")

with col_export2:
    st.subheader("🔗 Sistem Entegrasyonu")
    
    if st.button("🧪 GRADE Scoring'e Gönder", use_container_width=True):
        st.info("🧪 GRADE Scoring sayfasına yönlendiriliyorsunuz...")
    
    if st.button("🤖 AI Analysis'e Entegre Et", use_container_width=True):
        st.info("🤖 AI Analysis entegrasyonu yakında eklenecek")

with col_export3:
    st.subheader("📤 Dışa Aktarma")
    
    export_format = st.selectbox(
        "Format",
        ["PDF", "Word (.docx)", "Markdown", "JSON"],
        index=0
    )
    
    if st.button("📥 İndir", use_container_width=True):
        st.success(f"📥 {export_format} formatında indiriliyor...")

# Footer
st.markdown("---")
st.markdown("**Evidence Panel** - Kanıt tabanlı klinik karar desteği ve literatür entegrasyonu")
