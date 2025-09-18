import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="ASR Panel - NeuroPETrix",
    page_icon="🎤",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Page title and description
st.title("🎤 ASR Panel - Ses Tanıma ve Dikte Sistemi")
st.markdown("**Ses Kaydı • Whisper AI • Otomatik Transkripsiyon • Klinik Not Entegrasyonu**")

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

if st.sidebar.button("📊 Dashboard", use_container_width=True):
    st.switch_page("pages/00_Dashboard.py")

if st.button("📝 Report Generation", use_container_width=True):
    st.switch_page("pages/02_Rapor_Üretimi.py")

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
if "asr_sessions" not in st.session_state:
    st.session_state["asr_sessions"] = []
if "current_session" not in st.session_state:
    st.session_state["current_session"] = None
if "is_recording" not in st.session_state:
    st.session_state["is_recording"] = False

# ---- HERO SECTION ----
col_hero1, col_hero2 = st.columns([2, 1])

with col_hero1:
    st.markdown("""
    <div class="hero">
        <div>
            <h1>🎤 ASR Ses Tanıma Sistemi</h1>
            <div class="subtitle">Whisper AI ile otomatik ses tanıma ve klinik not oluşturma</div>
        </div>
        <div>
            <span class="badge ok">Whisper AI</span>
            <span class="badge">Real-time</span>
            <span class="badge">Multi-language</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    st.markdown("### 🎯 Hızlı İşlemler")
    
    # Quick recording controls
    if st.button("🎙️ Hızlı Kayıt", type="primary", use_container_width=True):
        st.session_state["is_recording"] = True
        st.rerun()
    
    if st.button("⏹️ Durdur", type="secondary", use_container_width=True):
        st.session_state["is_recording"] = False
        st.rerun()

st.write("")

# ---- ASR CONTROLS ----
st.header("🎙️ Ses Kayıt Kontrolleri")

col_controls1, col_controls2, col_controls3 = st.columns(3)

with col_controls1:
    st.subheader("🎤 Kayıt Ayarları")
    
    # Recording settings
    sample_rate = st.selectbox(
        "Örnekleme Hızı",
        ["16 kHz", "44.1 kHz", "48 kHz"],
        index=0,
        help="Ses kayıt kalitesi"
    )
    
    language = st.selectbox(
        "Dil",
        ["Türkçe", "English", "Auto-detect"],
        index=0,
        help="Ses tanıma dili"
    )
    
    model_size = st.selectbox(
        "Whisper Model",
        ["tiny", "base", "small", "medium", "large"],
        index=2,
        help="AI model boyutu (büyük = daha doğru)"
    )

with col_controls2:
    st.subheader("🎯 Klinik Bağlam")
    
    # Clinical context
    clinical_context = st.selectbox(
        "Klinik Bağlam",
        ["Genel", "Onkoloji", "Kardiyoloji", "Nöroloji", "Radyoloji"],
        index=0,
        help="Ses tanıma için klinik alan"
    )
    
    report_type = st.selectbox(
        "Rapor Türü",
        ["Hasta Öyküsü", "Fizik Muayene", "Görüntü Yorumu", "Tedavi Planı", "Takip Notu"],
        index=0,
        help="Oluşturulacak rapor türü"
    )
    
    urgency = st.selectbox(
        "Acil Durum",
        ["Normal", "Acil", "Kritik"],
        index=0,
        help="Rapor aciliyeti"
    )

with col_controls3:
    st.subheader("⚙️ Gelişmiş Ayarlar")
    
    # Advanced settings
    noise_reduction = st.checkbox(
        "Gürültü Azaltma",
        value=True,
        help="Otomatik gürültü temizleme"
    )
    
    auto_punctuation = st.checkbox(
        "Otomatik Noktalama",
        value=True,
        help="AI ile noktalama ekleme"
    )
    
    medical_terms = st.checkbox(
        "Tıbbi Terim Desteği",
        value=True,
        help="Tıbbi terminoloji optimizasyonu"
    )

st.write("")

# ---- RECORDING INTERFACE ----
st.header("🎙️ Ses Kayıt Arayüzü")

# Recording status
if st.session_state["is_recording"]:
    st.success("🎙️ **KAYIT YAPILIYOR** - Konuşmaya başlayın...")
    
    # Recording visualization
    col_viz1, col_viz2, col_viz3 = st.columns(3)
    
    with col_viz1:
        st.markdown("**📊 Ses Seviyesi**")
        # Simulate audio level
        audio_level = st.progress(0.7)
        st.markdown("**70%** - Normal seviye")
    
    with col_viz2:
        st.markdown("**⏱️ Kayıt Süresi**")
        st.markdown("**00:02:34**")
        st.markdown("*Devam ediyor...*")
    
    with col_viz3:
        st.markdown("**🎯 Tanıma Durumu**")
        st.success("🟢 Aktif")
        st.markdown("*Gerçek zamanlı*")
    
    # Stop recording button
    if st.button("⏹️ Kaydı Durdur", type="primary", use_container_width=True):
        st.session_state["is_recording"] = False
        st.rerun()

else:
    st.info("🎙️ **Kayıt bekleniyor** - Başlatmak için yukarıdaki kontrolleri kullanın")
    
    # Recording controls
    col_rec1, col_rec2, col_rec3 = st.columns(3)
    
    with col_rec1:
        if st.button("🎙️ Yeni Kayıt", type="primary", use_container_width=True):
            st.session_state["is_recording"] = True
            st.rerun()
    
    with col_rec2:
        if st.button("📁 Dosya Yükle", type="secondary", use_container_width=True):
            st.info("📁 Ses dosyası yükleme özelliği yakında eklenecek")
    
    with col_rec3:
        if st.button("🔄 Son Kaydı Tekrarla", type="secondary", use_container_width=True):
            if st.session_state["asr_sessions"]:
                st.success("🔄 Son kayıt tekrarlanıyor...")
            else:
                st.warning("⚠️ Henüz kayıt yapılmamış")

st.write("")

# ---- TRANSCRIPTION RESULTS ----
st.header("📝 Transkripsiyon Sonuçları")

# Mock transcription results (in real system, this would come from Whisper API)
if st.session_state["is_recording"] or st.session_state["asr_sessions"]:
    
    # Simulate live transcription
    if st.session_state["is_recording"]:
        st.info("🎙️ **Canlı Transkripsiyon** - Konuşma devam ediyor...")
        
        # Live transcript
        live_transcript = """
        Hasta 45 yaşında erkek, akciğer kanseri tanısı ile başvurdu. 
        PET-CT incelemesinde sağ üst lobda 3.2 cm çapında nodül tespit edildi. 
        SUVmax değeri 8.5 olarak ölçüldü. Mediastinal lenf nodlarında patolojik 
        tutulum gözlenmedi. Kemik metastazı bulgusu yok.
        """
        
        st.text_area(
            "Canlı Transkript",
            value=live_transcript,
            height=200,
            help="Gerçek zamanlı ses tanıma sonucu"
        )
        
        # Confidence score
        col_conf1, col_conf2 = st.columns(2)
        
        with col_conf1:
            st.metric("🎯 Tanıma Güveni", "87%")
            st.metric("📊 Kelime Doğruluğu", "92%")
        
        with col_conf2:
            st.metric("⏱️ Gecikme", "0.3s")
            st.metric("🌐 Dil", "Türkçe")
    
    # Previous sessions
    if st.session_state["asr_sessions"]:
        st.subheader("📚 Önceki Kayıtlar")
        
        for i, session in enumerate(st.session_state["asr_sessions"]):
            with st.expander(f"🎙️ {session['title']} - {session['timestamp']}"):
                col_sess1, col_sess2 = st.columns([3, 1])
                
                with col_sess1:
                    st.markdown(f"**Transkript:** {session['transcript']}")
                    st.markdown(f"**Bağlam:** {session['context']}")
                
                with col_sess2:
                    st.metric("Güven", f"{session['confidence']}%")
                    st.metric("Süre", session['duration'])
                    
                    if st.button(f"📝 Düzenle", key=f"edit_{i}"):
                        st.session_state["current_session"] = i
                        st.rerun()

st.write("")

# ---- EDITING AND EXPORT ----
st.header("✏️ Düzenleme ve Dışa Aktarma")

col_edit1, col_edit2 = st.columns(2)

with col_edit1:
    st.subheader("📝 Transkript Düzenleme")
    
    # Edit current transcript
    if st.session_state["current_session"] is not None:
        session = st.session_state["asr_sessions"][st.session_state["current_session"]]
        
        edited_transcript = st.text_area(
            "Düzenlenmiş Transkript",
            value=session["transcript"],
            height=150,
            help="Transkripti düzenleyin"
        )
        
        if st.button("💾 Değişiklikleri Kaydet"):
            st.session_state["asr_sessions"][st.session_state["current_session"]]["transcript"] = edited_transcript
            st.success("✅ Değişiklikler kaydedildi!")
            st.session_state["current_session"] = None
            st.rerun()
    else:
        st.info("📝 Düzenlemek için bir kayıt seçin")

with col_edit2:
    st.subheader("📤 Dışa Aktarma")
    
    # Export options
    export_format = st.selectbox(
        "Format",
        ["Markdown", "Word (.docx)", "PDF", "JSON", "Plain Text"],
        index=0
    )
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        if st.button("📥 İndir", use_container_width=True):
            st.success(f"📥 {export_format} formatında indiriliyor...")
    
    with col_exp2:
        if st.button("📧 E-posta Gönder", use_container_width=True):
            st.info("📧 E-posta gönderme özelliği yakında eklenecek")

st.write("")

# ---- AI ENHANCEMENT ----
st.header("🤖 AI Geliştirme Özellikleri")

col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.subheader("🔍 Otomatik Düzeltme")
    
    # AI correction options
    auto_correct_medical = st.checkbox(
        "Tıbbi Terim Düzeltmesi",
        value=True,
        help="AI ile tıbbi terminoloji düzeltme"
    )
    
    auto_correct_grammar = st.checkbox(
        "Dilbilgisi Düzeltmesi",
        value=True,
        help="AI ile dilbilgisi kontrolü"
    )
    
    auto_summarize = st.checkbox(
        "Otomatik Özetleme",
        value=True,
        help="Uzun transkriptleri özetleme"
    )
    
    if st.button("🤖 AI Düzeltme Uygula"):
        st.success("🤖 AI düzeltme uygulanıyor...")
        # Simulate AI processing
        progress = st.progress(0)
        for i in range(101):
            progress.progress(i)
        st.success("✅ AI düzeltme tamamlandı!")

with col_ai2:
    st.subheader("📊 Analiz ve İstatistikler")
    
    # Analysis metrics
    if st.session_state["asr_sessions"]:
        total_duration = sum(session["duration"] for session in st.session_state["asr_sessions"])
        avg_confidence = sum(session["confidence"] for session in st.session_state["asr_sessions"]) / len(st.session_state["asr_sessions"])
        
        st.metric("📈 Toplam Kayıt Süresi", f"{total_duration} dakika")
        st.metric("🎯 Ortalama Güven", f"{avg_confidence:.1f}%")
        st.metric("📝 Toplam Transkript", len(st.session_state["asr_sessions"]))
        
        # Confidence trend
        if len(st.session_state["asr_sessions"]) > 1:
            st.markdown("**📈 Güven Trendi:**")
            confidences = [s["confidence"] for s in st.session_state["asr_sessions"]]
            st.line_chart(pd.DataFrame({"Güven": confidences}))
    else:
        st.info("📊 Analiz için kayıt gerekli")

# Footer
st.markdown("---")
st.markdown("**ASR Panel** - Whisper AI destekli ses tanıma ve dikte sistemi")
