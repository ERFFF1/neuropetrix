import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import io
from pathlib import Path

st.set_page_config(
    page_title="Clinical Decision Support - NeuroPETrix",
    page_icon="🏥",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Page title and description
st.title("🏥 Clinical Decision Support - Klinik Karar Desteği")
st.markdown("PERCIST/Deauville kriterleri, otomatik klinik kurallar ve hekim geri bildirimi")

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

if st.sidebar.button("🖥️ Desktop Runner", key="cds_nav_desktop", use_container_width=True):
    st.switch_page("pages/14_Desktop_Runner.py")

if st.sidebar.button("🔍 PICO Automation", key="cds_nav_pico", use_container_width=True):
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
if "clinical_cases" not in st.session_state:
    st.session_state["clinical_cases"] = []
if "current_clinical_case" not in st.session_state:
    st.session_state["current_clinical_case"] = None
if "clinical_rules" not in st.session_state:
    st.session_state["clinical_rules"] = []

def render_clinical_decision_support():
    """Clinical Decision Support ana sayfasını render et"""
    
    st.header("🏥 Clinical Decision Support - Klinik Karar Desteği")
    st.markdown("PERCIST/Deauville kriterleri, otomatik klinik kurallar ve hekim geri bildirimi")
    
    # Ana sekmeler
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Klinik Vaka", "🔬 PERCIST/Deauville", "🤖 AI Kurallar", "💬 Hekim Geri Bildirimi"])
    
    with tab1:
        render_clinical_case()
    
    with tab2:
        render_percist_deauville()
    
    with tab3:
        render_ai_rules()
    
    with tab4:
        render_physician_feedback()

def render_clinical_case():
    """Klinik vaka sekmesi"""
    
    st.subheader("📋 Klinik Vaka Yönetimi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Yeni Klinik Vaka**")
        
        with st.form("new_clinical_case_form"):
            case_id = st.text_input("Vaka ID", placeholder="CDS-2025-000123")
            patient_age = st.number_input("Hasta Yaşı", min_value=18, max_value=100, value=65)
            patient_gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın"])
            diagnosis = st.text_input("Tanı", placeholder="Non-small cell lung cancer")
            stage = st.selectbox("Evre", ["I", "II", "III", "IV"])
            
            # SUV değerleri
            st.markdown("**📊 SUV Değerleri**")
            baseline_suvmax = st.number_input("Baseline SUVmax", min_value=0.0, max_value=50.0, value=12.5, step=0.1)
            followup_suvmax = st.number_input("Follow-up SUVmax", min_value=0.0, value=baseline_suvmax, step=0.1)
            
            if st.form_submit_button("📝 Vaka Oluştur"):
                if case_id and diagnosis:
                    # Vaka oluştur
                    new_case = {
                        "case_id": case_id,
                        "patient_age": patient_age,
                        "patient_gender": patient_gender,
                        "diagnosis": diagnosis,
                        "stage": stage,
                        "baseline_suvmax": baseline_suvmax,
                        "followup_suvmax": followup_suvmax,
                        "created_at": datetime.now().isoformat(),
                        "status": "created"
                    }
                    
                    st.session_state["clinical_cases"].append(new_case)
                    st.success(f"Klinik vaka oluşturuldu: {case_id}")
                else:
                    st.error("Lütfen tüm alanları doldurun!")
    
    with col2:
        st.markdown("**Mevcut Klinik Vakalar**")
        
        if st.session_state["clinical_cases"]:
            for case in st.session_state["clinical_cases"]:
                with st.expander(f"🏥 {case['case_id']}", expanded=False):
                    st.markdown(f"**Tanı:** {case['diagnosis']} - Evre {case['stage']}")
                    st.markdown(f"**Hasta:** {case['patient_age']} yaş, {case['patient_gender']}")
                    st.markdown(f"**SUV:** {case['baseline_suvmax']:.1f} → {case['followup_suvmax']:.1f}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🔬 Analiz Et", key=f"analyze_cds_{case['case_id']}"):
                            st.session_state["current_clinical_case"] = case
                            st.success(f"Klinik analiz başlatılıyor: {case['case_id']}")
                    with col_b:
                        if st.button("🗑️ Sil", key=f"delete_cds_{case['case_id']}"):
                            st.session_state["clinical_cases"].remove(case)
                            st.success(f"Vaka silindi: {case['case_id']}")
                            st.rerun()
        else:
            st.info("Henüz klinik vaka oluşturulmadı")

def render_percist_deauville():
    """PERCIST/Deauville sekmesi"""
    
    st.subheader("🔬 PERCIST/Deauville Kriterleri")
    
    if not st.session_state["current_clinical_case"]:
        st.warning("⚠️ Lütfen önce bir klinik vaka seçin!")
        return
    
    current_case = st.session_state["current_clinical_case"]
    st.info(f"**Analiz Edilen Vaka:** {current_case['case_id']} - {current_case['diagnosis']}")
    
    # PERCIST analizi
    st.markdown("**📊 PERCIST Kriterleri**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # SUV değişimi hesapla
        suv_change = ((current_case['followup_suvmax'] - current_case['baseline_suvmax']) / current_case['baseline_suvmax']) * 100
        
        st.metric("Baseline SUVmax", f"{current_case['baseline_suvmax']:.1f}")
        st.metric("Follow-up SUVmax", f"{current_case['followup_suvmax']:.1f}")
        st.metric("SUV Değişimi", f"{suv_change:.1f}%")
        
        # PERCIST kriteri belirle
        percist_criteria = determine_percist_criteria(suv_change)
        st.metric("PERCIST Kriteri", percist_criteria)
    
    with col2:
        # Deauville skoru
        st.markdown("**🏥 Deauville Skoru**")
        
        deauville_score = st.selectbox(
            "Deauville Skoru",
            ["1", "2", "3", "4", "5"],
            key="deauville_score"
        )
        
        if st.button("🔬 Deauville Analizi"):
            deauville_interpretation = interpret_deauville_score(int(deauville_score))
            st.success(f"✅ Deauville analizi: {deauville_interpretation}")
    
    # Klinik yorum
    st.markdown("**💡 Klinik Yorum**")
    
    if st.button("📋 Klinik Yorum Oluştur"):
        clinical_comment = generate_clinical_comment(percist_criteria, int(deauville_score), suv_change)
        st.success("✅ Klinik yorum oluşturuldu!")
        
        st.markdown("**📋 Klinik Yorum Detayları**")
        st.write(clinical_comment)

def render_ai_rules():
    """AI kurallar sekmesi"""
    
    st.subheader("🤖 AI Klinik Kurallar Motoru")
    
    if not st.session_state["current_clinical_case"]:
        st.warning("⚠️ Lütfen önce bir klinik vaka seçin!")
        return
    
    current_case = st.session_state["current_clinical_case"]
    st.info(f"**Analiz Edilen Vaka:** {current_case['case_id']}")
    
    # AI kurallar
    st.markdown("**🔍 AI Kural Analizi**")
    
    # Kural motoru
    clinical_rules = [
        {
            "rule_id": "RULE_001",
            "name": "SUV Değişim Kuralı",
            "condition": "SUV değişimi > 30%",
            "action": "Yanıt değerlendir",
            "priority": "Yüksek"
        },
        {
            "rule_id": "RULE_002", 
            "name": "Evre Uyum Kuralı",
            "condition": "Evre III-IV",
            "action": "Sistemik tedavi öner",
            "priority": "Orta"
        },
        {
            "rule_id": "RULE_003",
            "name": "Yaş Kuralı",
            "condition": "Yaş > 70",
            "action": "Toksisite riski değerlendir",
            "priority": "Orta"
        }
    ]
    
    # Kuralları uygula
    if st.button("🤖 AI Kuralları Uygula"):
        st.info("🤖 AI kurallar uygulanıyor...")
        
        with st.spinner("Kurallar değerlendiriliyor..."):
            import time
            time.sleep(2)
            
            # Kural sonuçları
            rule_results = apply_clinical_rules(current_case, clinical_rules)
            
            st.success("✅ AI kurallar uygulandı!")
            
            # Sonuçları göster
            show_rule_results(rule_results)

def render_physician_feedback():
    """Hekim geri bildirimi sekmesi"""
    
    st.subheader("💬 Hekim Geri Bildirimi ve Öğrenme")
    
    if not st.session_state["current_clinical_case"]:
        st.warning("⚠️ Lütfen önce bir klinik vaka seçin!")
        return
    
    current_case = st.session_state["current_clinical_case"]
    st.info(f"**Geri Bildirim Vakası:** {current_case['case_id']}")
    
    # Geri bildirim formu
    st.markdown("**📝 AI Önerisi Geri Bildirimi**")
    
    with st.form("physician_feedback_form"):
        ai_recommendation = st.text_area(
            "AI Önerisi",
            value="SUV değişimi %25, PERCIST kriteri SD. Deauville skoru 3. Kısmi yanıt önerisi.",
            height=100
        )
        
        feedback_type = st.selectbox(
            "Geri Bildirim Tipi",
            ["Agree (Kabul)", "Disagree (Red)", "Edit (Düzenle)", "Neutral (Nötr)"]
        )
        
        feedback_comment = st.text_area(
            "Hekim Yorumu",
            placeholder="AI önerisi hakkında detaylı yorumunuz..."
        )
        
        confidence_level = st.slider(
            "Güven Seviyesi",
            min_value=1,
            max_value=10,
            value=7,
            help="1: Çok düşük güven, 10: Çok yüksek güven"
        )
        
        if st.form_submit_button("💾 Geri Bildirimi Kaydet"):
            if feedback_comment:
                # Geri bildirimi kaydet
                feedback_data = {
                    "case_id": current_case["case_id"],
                    "ai_recommendation": ai_recommendation,
                    "feedback_type": feedback_type,
                    "feedback_comment": feedback_comment,
                    "confidence_level": confidence_level,
                    "timestamp": datetime.now().isoformat()
                }
                
                st.success("✅ Geri bildirim kaydedildi!")
                
                # Öğrenme döngüsü
                if feedback_type in ["Disagree", "Edit"]:
                    st.info("🔄 AI modeli bu geri bildirimle öğreniyor...")
                    
                    # Mock learning
                    with st.spinner("Model güncelleniyor..."):
                        import time
                        time.sleep(2)
                        st.success("✅ Model güncellendi!")

def determine_percist_criteria(suv_change):
    """PERCIST kriterini belirle"""
    if suv_change <= -30:
        return "PR (Partial Response)"
    elif suv_change >= 30:
        return "PD (Progressive Disease)"
    else:
        return "SD (Stable Disease)"

def interpret_deauville_score(score):
    """Deauville skorunu yorumla"""
    interpretations = {
        1: "Normal",
        2: "Normal (minimal uptake)",
        3: "Belirsiz",
        4: "Pozitif (orta uptake)",
        5: "Pozitif (yüksek uptake)"
    }
    return interpretations.get(score, "Bilinmiyor")

def generate_clinical_comment(percist, deauville, suv_change):
    """Klinik yorum oluştur"""
    comment = f"""
    **PERCIST Kriteri:** {percist}
    **Deauville Skoru:** {deauville}
    **SUV Değişimi:** {suv_change:.1f}%
    
    **Klinik Yorum:**
    """
    
    if percist == "PR (Partial Response)":
        comment += "Hasta tedaviye yanıt veriyor. Mevcut tedaviye devam edilmeli."
    elif percist == "PD (Progressive Disease)":
        comment += "Hastalık ilerliyor. Tedavi değişikliği değerlendirilmeli."
    else:
        comment += "Hastalık stabil. Yakın takip gerekli."
    
    return comment

def apply_clinical_rules(case, rules):
    """Klinik kuralları uygula"""
    results = []
    
    for rule in rules:
        triggered = False
        action = ""
        
        if rule["rule_id"] == "RULE_001":
            suv_change = ((case['followup_suvmax'] - case['baseline_suvmax']) / case['baseline_suvmax']) * 100
            if abs(suv_change) > 30:
                triggered = True
                action = "SUV değişimi anlamlı, yanıt değerlendir"
        
        elif rule["rule_id"] == "RULE_002":
            if case['stage'] in ["III", "IV"]:
                triggered = True
                action = "Sistemik tedavi öner"
        
        elif rule["rule_id"] == "RULE_003":
            if case['patient_age'] > 70:
                triggered = True
                action = "Toksisite riski değerlendir"
        
        results.append({
            "rule": rule["name"],
            "triggered": triggered,
            "action": action,
            "priority": rule["priority"]
        })
    
    return results

def show_rule_results(results):
    """Kural sonuçlarını göster"""
    st.markdown("**📊 Kural Sonuçları**")
    
    for result in results:
        if result["triggered"]:
            st.warning(f"⚠️ **{result['rule']}** - {result['action']} (Öncelik: {result['priority']})")
        else:
            st.success(f"✅ **{result['rule']}** - Tetiklenmedi")

# Ana sayfa render
if __name__ == "__main__":
    render_clinical_decision_support()

# Footer
st.markdown("---")
st.caption("🏥 Clinical Decision Support - NeuroPETrix v1.0.0 | AI-Powered Clinical Rules Engine")

