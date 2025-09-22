import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import io
from pathlib import Path
import os

st.set_page_config(
    page_title="PICO Automation - NeuroPETrix",
    page_icon="🔍",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Page title and description
st.title("🔍 PICO Automation - Kanıta Dayalı Tıp Otomasyonu")
st.markdown("PICO framework ile otomatik literatür taraması, GRADE metodolojisi ve klinik karar desteği")

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

if st.sidebar.button("📊 Dashboard", key="pico_nav_dashboard", use_container_width=True):
    st.switch_page("pages/00_Dashboard.py")

if st.sidebar.button("🖥️ Desktop Runner", key="pico_nav_desktop", use_container_width=True):
    st.switch_page("pages/14_Desktop_Runner.py")

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
if "pico_questions" not in st.session_state:
    st.session_state["pico_questions"] = []
if "current_analysis" not in st.session_state:
    st.session_state["current_analysis"] = None
if "evidence_results" not in st.session_state:
    st.session_state["evidence_results"] = []
if "clinical_recommendations" not in st.session_state:
    st.session_state["clinical_recommendations"] = []

def render_pico_automation():
    """PICO Automation ana sayfasını render et"""
    
    st.header("🔍 PICO Automation - Kanıta Dayalı Tıp Otomasyonu")
    st.markdown("PICO framework ile otomatik literatür taraması, GRADE metodolojisi ve klinik karar desteği")
    
    # Ana sekmeler
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 PICO Soru Oluştur", "🔬 Kanıt Arama", "📊 GRADE Analizi", "💡 Klinik Öneriler", "🏥 Uygulanabilirlik"])
    
    with tab1:
        render_pico_question_creator()
    
    with tab2:
        render_evidence_search()
    
    with tab3:
        render_grade_analysis()
    
    with tab4:
        render_clinical_recommendations()
    
    with tab5:
        render_applicability_analysis()

def render_pico_question_creator():
    """PICO soru oluşturucu sekmesi"""
    
    st.subheader("📝 PICO Soru Oluştur")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Yeni PICO Sorusu**")
        
        with st.form("new_pico_form"):
            population = st.text_input("Population (P)", placeholder="Lung cancer patients")
            intervention = st.text_input("Intervention (I)", placeholder="Immunotherapy")
            comparison = st.text_input("Comparison (C)", placeholder="Chemotherapy")
            outcome = st.text_input("Outcome (O)", placeholder="Overall survival")
            clinical_context = st.text_area("Clinical Context", placeholder="First-line treatment for advanced NSCLC")
            
            # GRADE metodolojisi için ek alanlar
            study_type = st.selectbox("Çalışma Tipi", ["RCT", "Systematic Review", "Meta-analysis", "Cohort", "Case-control", "Case series"])
            risk_of_bias = st.selectbox("Yanlılık Riski", ["Düşük", "Orta", "Yüksek"])
            imprecision = st.selectbox("Kesinlik", ["Düşük", "Orta", "Yüksek"])
            inconsistency = st.selectbox("Tutarsızlık", ["Düşük", "Orta", "Yüksek"])
            
            if st.form_submit_button("🔍 PICO Sorusu Oluştur"):
                if population and intervention and comparison and outcome:
                    # PICO sorusu oluştur
                    new_pico = {
                        "id": f"PICO_{len(st.session_state['pico_questions']) + 1}",
                        "population": population,
                        "intervention": intervention,
                        "comparison": comparison,
                        "outcome": outcome,
                        "clinical_context": clinical_context,
                        "study_type": study_type,
                        "risk_of_bias": risk_of_bias,
                        "imprecision": imprecision,
                        "inconsistency": inconsistency,
                        "created_at": datetime.now().isoformat(),
                        "status": "created"
                    }
                    
                    st.session_state["pico_questions"].append(new_pico)
                    st.success(f"PICO sorusu oluşturuldu: {new_pico['id']}")
                else:
                    st.error("Lütfen tüm PICO alanlarını doldurun!")
    
    with col2:
        st.markdown("**Mevcut PICO Soruları**")
        
        if st.session_state["pico_questions"]:
            for pico in st.session_state["pico_questions"]:
                with st.expander(f"🔍 {pico['id']}", expanded=False):
                    st.markdown(f"**Population:** {pico['population']}")
                    st.markdown(f"**Intervention:** {pico['intervention']}")
                    st.markdown(f"**Comparison:** {pico['comparison']}")
                    st.markdown(f"**Outcome:** {pico['outcome']}")
                    st.markdown(f"**Context:** {pico['clinical_context']}")
                    st.markdown(f"**Study Type:** {pico['study_type']}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🔬 Analiz Et", key=f"analyze_{pico['id']}"):
                            st.session_state["current_analysis"] = pico
                            st.success(f"PICO analizi başlatılıyor: {pico['id']}")
                    with col_b:
                        if st.button("🗑️ Sil", key=f"delete_{pico['id']}"):
                            st.session_state["pico_questions"].remove(pico)
                            st.success(f"PICO sorusu silindi: {pico['id']}")
                            st.rerun()
        else:
            st.info("Henüz PICO sorusu oluşturulmadı")

def render_evidence_search():
    """Kanıt arama sekmesi"""
    
    st.subheader("🔬 Kanıt Arama ve Değerlendirme")
    
    if not st.session_state["current_analysis"]:
        st.warning("⚠️ Lütfen önce bir PICO sorusu seçin!")
        return
    
    current_pico = st.session_state["current_analysis"]
    st.info(f"**Analiz Edilen PICO:** {current_pico['id']}")
    
    # Arama parametreleri
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Arama Parametreleri**")
        
        databases = st.multiselect(
            "Veritabanları",
            ["PubMed", "Cochrane", "Embase", "ClinicalTrials.gov", "Europe PMC"],
            default=["PubMed", "Cochrane"]
        )
        
        date_range = st.selectbox(
            "Tarih Aralığı",
            ["Son 5 yıl", "Son 10 yıl", "Tüm zamanlar", "Özel aralık"]
        )
        
        study_types = st.multiselect(
            "Çalışma Tipleri",
            ["RCT", "Systematic Review", "Meta-analysis", "Cohort", "Case-control"],
            default=["RCT", "Systematic Review"]
        )
    
    with col2:
        st.markdown("**Arama Stratejisi**")
        
        search_strategy = st.text_area(
            "Otomatik Arama Stratejisi",
            value=f"({current_pico['population']}) AND ({current_pico['intervention']}) AND ({current_pico['comparison']}) AND ({current_pico['outcome']})",
            height=100
        )
        
        if st.button("🔍 Kanıt Ara", key="start_evidence_search"):
            st.info("🔍 Kanıt arama başlatılıyor...")
            
            # Mock evidence search
            with st.spinner("Kanıtlar aranıyor..."):
                import time
                time.sleep(3)
                
                # Mock evidence results
                mock_evidence = [
                    {
                        "title": "Immunotherapy vs Chemotherapy in Advanced NSCLC",
                        "authors": "Smith J, et al.",
                        "year": 2023,
                        "journal": "NEJM",
                        "study_type": "RCT",
                        "sample_size": 1200,
                        "evidence_level": "1A",
                        "key_findings": "Immunotherapy showed 15% improvement in OS",
                        "relevance_score": 0.95,
                        "risk_of_bias": "Düşük",
                        "imprecision": "Düşük",
                        "inconsistency": "Düşük"
                    },
                    {
                        "title": "Meta-analysis of Immunotherapy Trials",
                        "authors": "Johnson A, et al.",
                        "year": 2022,
                        "journal": "Lancet Oncology",
                        "study_type": "Meta-analysis",
                        "sample_size": 5000,
                        "evidence_level": "1A",
                        "key_findings": "Pooled analysis confirms OS benefit",
                        "relevance_score": 0.92,
                        "risk_of_bias": "Düşük",
                        "imprecision": "Düşük",
                        "inconsistency": "Orta"
                    }
                ]
                
                st.session_state["evidence_results"] = mock_evidence
                st.success(f"✅ {len(mock_evidence)} kanıt bulundu!")

def render_grade_analysis():
    """GRADE analizi sekmesi"""
    
    st.subheader("📊 GRADE Metodolojisi ve Kanıt Değerlendirmesi")
    
    if not st.session_state["evidence_results"]:
        st.info("ℹ️ Henüz kanıt arama yapılmadı")
        return
    
    evidence_results = st.session_state["evidence_results"]
    
    # GRADE analizi
    st.markdown("**🔍 GRADE Analizi**")
    
    for i, evidence in enumerate(evidence_results):
        with st.expander(f"📄 {evidence['title']}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Yazarlar:** {evidence['authors']}")
                st.markdown(f"**Yıl:** {evidence['year']}")
                st.markdown(f"**Dergi:** {evidence['journal']}")
                st.markdown(f"**Çalışma Tipi:** {evidence['study_type']}")
                st.markdown(f"**Kanıt Seviyesi:** {evidence['evidence_level']}")
            
            with col2:
                st.markdown(f"**Örnek Boyutu:** {evidence['sample_size']}")
                st.markdown(f"**İlgi Skoru:** {evidence['relevance_score']:.2f}")
                st.markdown(f"**Ana Bulgular:** {evidence['key_findings']}")
            
            # GRADE kalite değerlendirmesi
            st.markdown("**🔍 GRADE Kalite Değerlendirmesi**")
            
            grade_criteria = {
                "Risk of Bias": st.selectbox(f"Yanlılık Riski", ["Düşük", "Orta", "Yüksek"], key=f"bias_{i}"),
                "Inconsistency": st.selectbox(f"Tutarsızlık", ["Düşük", "Orta", "Yüksek"], key=f"inconsistency_{i}"),
                "Indirectness": st.selectbox(f"Dolaylılık", ["Düşük", "Orta", "Yüksek"], key=f"indirectness_{i}"),
                "Imprecision": st.selectbox(f"Kesinlik", ["Düşük", "Orta", "Yüksek"], key=f"precision_{i}"),
                "Publication Bias": st.selectbox(f"Yayın Yanlılığı", ["Düşük", "Orta", "Yüksek"], key=f"pub_bias_{i}")
            }
            
            # GRADE skoru hesapla
            grade_score = calculate_grade_score(grade_criteria)
            st.metric("GRADE Skoru", grade_score)
            
            # Kanıt seviyesi güncelleme
            updated_evidence_level = update_evidence_level(evidence['evidence_level'], grade_criteria)
            st.metric("Güncellenmiş Kanıt Seviyesi", updated_evidence_level)

def render_clinical_recommendations():
    """Klinik öneriler sekmesi"""
    
    st.subheader("💡 Kanıta Dayalı Klinik Öneriler")
    
    if not st.session_state["evidence_results"]:
        st.info("ℹ️ Henüz kanıt analizi yapılmadı")
        return
    
    current_pico = st.session_state["current_analysis"]
    evidence_results = st.session_state["evidence_results"]
    
    # Öneri oluşturma
    if st.button("💡 Öneri Oluştur", key="generate_recommendation"):
        st.info("💡 Kanıta dayalı öneri oluşturuluyor...")
        
        with st.spinner("Öneri oluşturuluyor..."):
            import time
            time.sleep(2)
            
            # Mock recommendation
            recommendation = {
                "strength": "Güçlü",
                "evidence_level": "1A",
                "recommendation_text": f"Immunotherapy ({current_pico['intervention']}) önerilir çünkü mevcut kanıtlar OS'de anlamlı iyileşme göstermektedir.",
                "confidence": "Yüksek",
                "limitations": "Çalışmaların çoğu belirli hasta alt gruplarında yapılmıştır.",
                "clinical_implications": "İlk basamak tedavi olarak değerlendirilmelidir.",
                "supporting_evidence": f"Bu öneri {len(evidence_results)} kanıta dayanır",
                "grade_justification": "Düşük yanlılık riski, yüksek kesinlik, tutarlı sonuçlar"
            }
            
            st.session_state["clinical_recommendations"] = [recommendation]
            st.success("✅ Öneri oluşturuldu!")
            
            # Öneri detayları
            st.markdown("**📋 Öneri Detayları**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Öneri Gücü", recommendation["strength"])
                st.metric("Kanıt Seviyesi", recommendation["evidence_level"])
                st.metric("Güven", recommendation["confidence"])
            
            with col2:
                st.markdown(f"**Öneri:** {recommendation['recommendation_text']}")
                st.markdown(f"**Kısıtlamalar:** {recommendation['limitations']}")
                st.markdown(f"**Klinik Etkiler:** {recommendation['clinical_implications']}")
            
            # Klinik şeffaflık kartı
            st.markdown("**🔍 Klinik Şeffaflık Kartı**")
            st.info(f"**{recommendation['supporting_evidence']}** - {recommendation['grade_justification']}")
            
            # Rapor oluşturma
            if st.button("📋 PICO Raporu Oluştur"):
                st.info("📋 PICO raporu oluşturuluyor...")
                
                with st.spinner("Rapor oluşturuluyor..."):
                    time.sleep(2)
                    st.success("✅ PICO raporu oluşturuldu!")
                    
                    # Download link
                    st.download_button(
                        label="📥 Raporu İndir (PDF)",
                        data="Mock PICO report content",
                        file_name=f"PICO_Report_{current_pico['id']}.pdf",
                        mime="application/pdf"
                    )

def render_applicability_analysis():
    """Uygulanabilirlik analizi sekmesi"""
    
    st.subheader("🏥 Klinik Uygulanabilirlik Analizi")
    
    if not st.session_state["clinical_recommendations"]:
        st.info("ℹ️ Henüz klinik öneri oluşturulmadı")
        return
    
    current_pico = st.session_state["current_analysis"]
    
    st.markdown("**🔍 Hasta Özelinde Uygulanabilirlik**")
    
    # Hasta özellikleri
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Hasta Demografik Bilgileri**")
        patient_age = st.number_input("Yaş", min_value=18, max_value=100, value=65)
        patient_gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın"])
        patient_comorbidities = st.multiselect(
            "Komorbiditeler",
            ["Hipertansiyon", "Diyabet", "Kardiyovasküler", "Böbrek yetmezliği", "Karaciğer yetmezliği"]
        )
    
    with col2:
        st.markdown("**Klinik Durum**")
        disease_stage = st.selectbox("Hastalık Evresi", ["I", "II", "III", "IV"])
        performance_status = st.selectbox("Performance Status", ["0", "1", "2", "3", "4"])
        previous_treatments = st.multiselect(
            "Önceki Tedaviler",
            ["Cerrahi", "Radyoterapi", "Kemoterapi", "Hedefli tedavi"]
        )
    
    # Uygulanabilirlik analizi
    if st.button("🔍 Uygulanabilirlik Analizi", key="analyze_applicability"):
        st.info("🔍 Uygulanabilirlik analiz ediliyor...")
        
        with st.spinner("Analiz yapılıyor..."):
            import time
            time.sleep(2)
            
            # Uygulanabilirlik sonuçları
            applicability_results = analyze_patient_applicability(
                current_pico, patient_age, patient_gender, patient_comorbidities,
                disease_stage, performance_status, previous_treatments
            )
            
            st.success("✅ Uygulanabilirlik analizi tamamlandı!")
            
            # Sonuçları göster
            show_applicability_results(applicability_results)

def calculate_grade_score(grade_criteria):
    """GRADE skorunu hesapla"""
    score_mapping = {"Düşük": 0, "Orta": 1, "Yüksek": 2}
    total_score = sum(score_mapping[value] for value in grade_criteria.values())
    
    if total_score <= 2:
        return "A (Yüksek)"
    elif total_score <= 4:
        return "B (Orta)"
    else:
        return "C (Düşük)"

def update_evidence_level(original_level, grade_criteria):
    """Kanıt seviyesini güncelle"""
    # GRADE kriterlerine göre seviye düşürme
    downgrade_factors = 0
    
    if grade_criteria["Risk of Bias"] == "Yüksek":
        downgrade_factors += 1
    if grade_criteria["Inconsistency"] == "Yüksek":
        downgrade_factors += 1
    if grade_criteria["Imprecision"] == "Yüksek":
        downgrade_factors += 1
    
    if downgrade_factors >= 2:
        return "B (Orta)"
    elif downgrade_factors >= 1:
        return "A (Yüksek)"
    else:
        return original_level

def analyze_patient_applicability(pico, age, gender, comorbidities, stage, ps, treatments):
    """Hasta özelinde uygulanabilirlik analizi"""
    applicability_score = 100
    
    # Yaş faktörü
    if age > 75:
        applicability_score -= 10
    
    # Komorbiditeler
    if "Kardiyovasküler" in comorbidities:
        applicability_score -= 15
    if "Böbrek yetmezliği" in comorbidities:
        applicability_score -= 20
    
    # Performance status
    if int(ps) > 2:
        applicability_score -= 25
    
    # Önceki tedaviler
    if "Kemoterapi" in treatments:
        applicability_score -= 10
    
    return {
        "score": max(0, applicability_score),
        "recommendation": "Önerilir" if applicability_score >= 70 else "Dikkatli değerlendir",
        "risk_factors": [c for c in comorbidities if c in ["Kardiyovasküler", "Böbrek yetmezliği"]],
        "monitoring_needs": applicability_score < 80
    }

def show_applicability_results(results):
    """Uygulanabilirlik sonuçlarını göster"""
    st.markdown("**📊 Uygulanabilirlik Sonuçları**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Uygulanabilirlik Skoru", f"{results['score']}/100")
        st.metric("Öneri", results['recommendation'])
    
    with col2:
        if results['risk_factors']:
            st.warning(f"⚠️ Risk Faktörleri: {', '.join(results['risk_factors'])}")
        if results['monitoring_needs']:
            st.info("📋 Yakın takip gerekli")
    
    # Klinik karar desteği
    st.markdown("**💡 Klinik Karar Desteği**")
    if results['score'] >= 80:
        st.success("✅ Güvenle uygulanabilir")
    elif results['score'] >= 60:
        st.warning("⚠️ Dikkatli değerlendir ve yakın takip et")
    else:
        st.error("❌ Alternatif tedavi seçeneklerini değerlendir")

# Ana sayfa render
if __name__ == "__main__":
    render_pico_automation()

# Footer
st.markdown("---")
st.caption("🔍 PICO Automation - NeuroPETrix v1.0.0 | Evidence-Based Medicine Automation")
