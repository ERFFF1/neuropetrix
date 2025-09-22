import streamlit as st
import requests
from pathlib import Path
import sys
import os

# Add the assets directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'assets'))

st.set_page_config(
    page_title="NeuroPETrix - Home",
    page_icon="🧠",
    layout="wide"
)

# CSS yükle
css_path = Path(__file__).parent / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Backend URL configuration
if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = "http://127.0.0.1:8000"

backend = st.sidebar.text_input("Backend URL", st.session_state["backend_url"])
st.session_state["backend_url"] = backend

# Sidebar configuration
st.sidebar.title("🧠 NeuroPETrix")
st.sidebar.markdown("AI-Powered PET-CT Analysis Platform")

# Theme toggle
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

theme_toggle = st.sidebar.toggle(
    "🌙 Dark Mode", 
    value=st.session_state["theme"] == "dark",
    help="Toggle between light and dark themes"
)

if theme_toggle != (st.session_state["theme"] == "dark"):
    st.session_state["theme"] = "dark" if theme_toggle else "light"
    st.rerun()

# Backend health check
try:
    health_response = requests.get(f"{backend}/health", timeout=3)
    backend_status = "ok" if health_response.status_code == 200 else "error"
except:
    backend_status = "error"

# ---- HERO SECTION ----
colL, colR = st.columns([1, 1], gap="large")

with colL:
    st.markdown(f"""
    <div class="hero">
        <div>
            <h1>🚀 NeuroPETrix</h1>
            <div class="subtitle">AI-Powered PET-CT Analysis Platform</div>
        </div>
        <div>
            <span class="badge {'ok' if backend_status == 'ok' else 'error'}">
                {'Backend OK' if backend_status == 'ok' else 'Backend Error'}
            </span>
            <span class="badge">TSNM Reports</span>
            <span class="badge">AI Analysis</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with colR:
    st.markdown("### 🔧 Quick Actions")
    
    # Quick health check
    if st.button("🔍 Check Backend", type="primary"):
        try:
            response = requests.get(f"{backend}/health", timeout=3)
            if response.status_code == 200:
                st.success("✅ Backend is healthy!")
            else:
                st.error(f"❌ Backend error: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Cannot connect: {str(e)}")
    
    # Version info
    if st.button("ℹ️ API Version"):
        try:
            response = requests.get(f"{backend}/version", timeout=3)
            if response.status_code == 200:
                version_data = response.json()
                st.info(f"**API:** {version_data.get('api', 'N/A')}")
                st.info(f"**Build:** {version_data.get('build', 'N/A')}")
            else:
                st.warning("⚠️ Version info unavailable")
        except Exception as e:
            st.warning(f"⚠️ Cannot get version: {str(e)}")

st.write("")  # boşluk

# ---- ANA ÖZELLİKLER ----
st.subheader("🚀 Ana Özellikler")

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="icon">🧪</div>', unsafe_allow_html=True)
    st.markdown("### 🧪 GRADE Scoring")
    st.markdown("Research paper evaluation using GRADE methodology")
    if st.button("Go to GRADE", key="grade", type="primary"):
        st.switch_page("pages/01_GRADE_Ön_Tarama.py")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="icon">📊</div>', unsafe_allow_html=True)
    st.markdown("### 📊 Multimodal Analysis")
    st.markdown("Text + SUV data analysis with AI")
    if st.button("Go to Analysis", key="analysis", type="primary"):
        st.switch_page("pages/05_AI_Analysis.py")
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="icon">📝</div>', unsafe_allow_html=True)
    st.markdown("### 📝 Report Generation")
    st.markdown("Clinical report creation and management")
    if st.button("Go to Reports", key="reports", type="primary"):
        st.switch_page("pages/02_Rapor_Üretimi.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ---- GELİŞMİŞ ÖZELLİKLER ----
st.subheader("🔧 Gelişmiş Özellikler")

d1, d2, d3 = st.columns(3, gap="large")

with d1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="icon">🏥</div>', unsafe_allow_html=True)
    st.markdown("### 🏥 HBYS Integration")
    st.markdown("Hospital information system integration")
    if st.button("Go to HBYS", key="hbys", type="secondary"):
        st.switch_page("pages/03_HBYS_Entegrasyon.py")
    st.markdown("</div>", unsafe_allow_html=True)

with d2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="icon">📁</div>', unsafe_allow_html=True)
    st.markdown("### 📁 DICOM Processing")
    st.markdown("DICOM file upload and processing")
    if st.button("Go to DICOM", key="dicom", type="secondary"):
        st.switch_page("pages/04_DICOM_Upload.py")
    st.markdown("</div>", unsafe_allow_html=True)

with d3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="icon">📈</div>', unsafe_allow_html=True)
    st.markdown("### 📈 TSNM Reports")
    st.markdown("Standard compliant medical reports")
    if st.button("Go to TSNM", key="tsnm", type="secondary"):
        st.switch_page("pages/06_TSNM_Reports.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ---- YENİ ÖZELLİKLER ----
st.subheader("🚀 Yeni Özellikler")

e1, e2, e3 = st.columns(3, gap="large")

with e1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="icon">🎤</div>', unsafe_allow_html=True)
    st.markdown("### 🎤 ASR Panel")
    st.markdown("Speech recognition and dictation system")
    if st.button("Go to ASR", key="asr", type="primary"):
        st.switch_page("pages/07_ASR_Panel.py")
    st.markdown("</div>", unsafe_allow_html=True)

with e2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="icon">📈</div>', unsafe_allow_html=True)
    st.markdown("### 📈 SUV Trend")
    st.markdown("SUV value tracking and trend analysis")
    if st.button("Go to SUV Trend", key="suv", type="primary"):
        st.switch_page("pages/08_SUV_Trend.py")
    st.markdown("</div>", unsafe_allow_html=True)

with e3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="icon">📚</div>', unsafe_allow_html=True)
    st.markdown("### 📚 Evidence Panel")
    st.markdown("Evidence-based clinical decision support")
    if st.button("Go to Evidence", key="evidence", type="primary"):
        st.switch_page("pages/09_Evidence_Panel.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ---- SİSTEM DURUMU ----
st.subheader("📊 Sistem Durumu")

col_status1, col_status2, col_status3 = st.columns(3, gap="large")

with col_status1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔧 Backend")
    if backend_status == "ok":
        st.success("🟢 Çalışıyor")
        try:
            health_data = health_response.json()
            st.caption(f"Last check: {health_data.get('timestamp', 'N/A')}")
        except:
            pass
    else:
        st.error("🔴 Kapalı")
    st.markdown("</div>", unsafe_allow_html=True)

with col_status2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💾 Database")
    try:
        feedback_response = requests.post(
            f"{backend}/feedback",
            json={"endpoint": "status_check", "useful": True},
            timeout=3
        )
        if feedback_response.status_code == 200:
            feedback_data = feedback_response.json()
            st.success(f"🟢 {feedback_data.get('count', 0)} feedback")
        else:
            st.warning("🟡 Bilinmiyor")
    except:
        st.error("🔌 Kapalı")
    st.markdown("</div>", unsafe_allow_html=True)

with col_status3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🌐 Frontend")
    st.success("🟢 Çalışıyor")
    st.caption("Streamlit v1.28.0")
    st.markdown("</div>", unsafe_allow_html=True)

# ---- ALT KÜÇÜK BİLGİ ŞERİDİ ----
st.caption("© NeuroPETrix · PET-CT AI · Built for clinicians")

# Footer
st.markdown("---")
st.markdown("**NeuroPETrix v1.0.0** - AI-Powered Medical Imaging Analysis Platform")


