import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import io
from pathlib import Path

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
st.title("🎤 ASR Panel - Otomatik Konuşma Tanıma")
st.markdown("Whisper AI ile sesli notları metne dönüştürme")

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

if st.sidebar.button("📊 Dashboard", key="asr_nav_dashboard", use_container_width=True):
    st.switch_page("pages/00_Dashboard.py")

if st.button("📝 Report Generation", key="asr_nav_report", use_container_width=True):
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

def render_asr_panel():
    """ASR Panel sayfasını render et"""
    
    st.header("🎤 ASR Panel - Otomatik Konuşma Tanıma")
    st.markdown("Whisper AI ile sesli notları metne dönüştürme")
    
    # ASR modu seçimi
    st.subheader("ASR Modu")
    
    asr_mode = st.selectbox(
        "ASR Modunu Seçin",
        ["Gerçek Zamanlı", "Dosya Yükleme", "Mikrofon Kaydı"]
    )
    
    if asr_mode == "Gerçek Zamanlı":
        render_realtime_asr()
    elif asr_mode == "Dosya Yükleme":
        render_file_upload_asr()
    elif asr_mode == "Mikrofon Kaydı":
        render_microphone_asr()

def render_realtime_asr():
    """Gerçek zamanlı ASR"""
    
    st.subheader("🔴 Gerçek Zamanlı ASR")
    
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox(
            "Dil",
            ["Türkçe", "İngilizce", "Otomatik Algılama"]
        )
        
        model_size = st.selectbox(
            "Model Boyutu",
            ["base", "small", "medium", "large"]
        )
    
    with col2:
        temperature = st.slider("Sıcaklık", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
        enable_timestamps = st.checkbox("Zaman Damgaları", value=True)
    
    # Gerçek zamanlı kayıt simülasyonu
    if st.button("🎤 Kayıt Başlat"):
        with st.spinner("Gerçek zamanlı ASR başlatılıyor..."):
            # Mock gerçek zamanlı transkripsiyon
            st.success("✅ Gerçek zamanlı ASR başlatıldı!")
            
            # Simüle edilmiş transkripsiyon
            transcription_text = """
            Hasta 65 yaşında erkek, akciğer kanseri şüphesi ile başvurdu. 
            Sağ üst lobda 2.5 santimetre nodül tespit edildi. 
            SUV değeri 8.5 olarak ölçüldü. 
            Lenf nodlarında metastaz şüphesi var.
            """
            
            st.text_area("Transkripsiyon Sonucu:", transcription_text, height=200)
            
            # Zaman damgaları
            if enable_timestamps:
                timestamps = [
                    {"start": "0:00", "end": "0:05", "text": "Hasta 65 yaşında erkek"},
                    {"start": "0:05", "end": "0:10", "text": "akciğer kanseri şüphesi ile başvurdu"},
                    {"start": "0:10", "end": "0:15", "text": "Sağ üst lobda 2.5 santimetre nodül tespit edildi"}
                ]
                
                st.write("**Zaman Damgaları:**")
                for ts in timestamps:
                    st.write(f"[{ts['start']}-{ts['end']}] {ts['text']}")

def render_file_upload_asr():
    """Dosya yükleme ASR"""
    
    st.subheader("📁 Dosya Yükleme ASR")
    
    # Dosya yükleme
    uploaded_file = st.file_uploader(
        "Ses Dosyası Yükleyin",
        type=['wav', 'mp3', 'm4a', 'flac'],
        help="Desteklenen formatlar: WAV, MP3, M4A, FLAC"
    )
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} yüklendi ({uploaded_file.size} bytes)")
        
        # ASR parametreleri
        col1, col2 = st.columns(2)
        
        with col1:
            language = st.selectbox(
                "Dil",
                ["Türkçe", "İngilizce", "Otomatik Algılama"],
                key="file_lang"
            )
            
            model_size = st.selectbox(
                "Model Boyutu",
                ["base", "small", "medium", "large"],
                key="file_model"
            )
        
        with col2:
            temperature = st.slider("Sıcaklık", min_value=0.0, max_value=1.0, value=0.0, step=0.1, key="file_temp")
            enable_timestamps = st.checkbox("Zaman Damgaları", value=True, key="file_timestamps")
        
        # Transkripsiyon başlat
        if st.button("🎤 Transkripsiyon Başlat"):
            with st.spinner("Ses dosyası transkripsiyonu yapılıyor..."):
                # Mock transkripsiyon süreci
                progress_bar = st.progress(0)
                
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i % 25 == 0:
                        st.write(f"Transkripsiyon ilerlemesi: {i + 1}%")
                
                st.success("✅ Transkripsiyon tamamlandı!")
                
                # Mock sonuç
                transcription_result = {
                    "text": "Hasta 65 yaşında erkek, akciğer kanseri şüphesi ile başvurdu. Sağ üst lobda 2.5 santimetre nodül tespit edildi. SUV değeri 8.5 olarak ölçüldü. Lenf nodlarında metastaz şüphesi var.",
                    "language": "tr",
                    "confidence": 0.92,
                    "duration": 45.2,
                    "word_count": 28
                }
                
                show_transcription_result(transcription_result, enable_timestamps)

def render_microphone_asr():
    """Mikrofon kaydı ASR"""
    
    st.subheader("🎙️ Mikrofon Kaydı ASR")
    
    st.info("Bu özellik tarayıcı mikrofon erişimi gerektirir")
    
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox(
            "Dil",
            ["Türkçe", "İngilizce", "Otomatik Algılama"],
            key="mic_lang"
        )
        
        recording_duration = st.slider(
            "Kayıt Süresi (saniye)",
            min_value=5,
            max_value=300,
            value=30,
            step=5
        )
    
    with col2:
        model_size = st.selectbox(
            "Model Boyutu",
            ["base", "small", "medium", "large"],
            key="mic_model"
        )
        
        enable_timestamps = st.checkbox("Zaman Damgaları", value=True, key="mic_timestamps")
    
    # Kayıt kontrolleri
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎤 Kayıt Başlat", type="primary"):
            st.success("🎤 Kayıt başlatıldı!")
            st.session_state["recording"] = True
    
    with col2:
        if st.button("⏸️ Duraklat"):
            if st.session_state.get("recording"):
                st.info("⏸️ Kayıt duraklatıldı")
                st.session_state["recording"] = False
    
    with col3:
        if st.button("⏹️ Kayıt Durdur"):
            if st.session_state.get("recording"):
                st.success("⏹️ Kayıt durduruldu!")
                st.session_state["recording"] = False
                
                # Mock transkripsiyon
                with st.spinner("Kayıt transkripsiyonu yapılıyor..."):
                    transcription_result = {
                        "text": "Hasta 65 yaşında erkek, akciğer kanseri şüphesi ile başvurdu. Sağ üst lobda 2.5 santimetre nodül tespit edildi.",
                        "language": "tr",
                        "confidence": 0.89,
                        "duration": 15.3,
                        "word_count": 18
                    }
                    
                    show_transcription_result(transcription_result, enable_timestamps)

def show_transcription_result(result, enable_timestamps=False):
    """Transkripsiyon sonucunu göster"""
    
    st.subheader("📝 Transkripsiyon Sonucu")
    
    # Sonuç metrikleri
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Güven Skoru", f"{result['confidence']:.2f}")
    
    with col2:
        st.metric("Süre", f"{result['duration']:.1f} s")
    
    with col3:
        st.metric("Kelime Sayısı", result['word_count'])
    
    with col4:
        st.metric("Dil", result['language'].upper())
    
    # Transkripsiyon metni
    st.text_area(
        "Transkripsiyon Metni:",
        result['text'],
        height=150,
        key="transcription_text"
    )
    
    # Düzenleme seçenekleri
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✏️ Metni Düzenle"):
            st.info("Metin düzenleme modu aktif")
    
    with col2:
        if st.button("🔄 Yeniden Transkripsiyon"):
            st.info("Yeniden transkripsiyon başlatılıyor...")
    
    # Zaman damgaları
    if enable_timestamps:
        st.subheader("⏰ Zaman Damgaları")
        
        timestamps = [
            {"start": 0.0, "end": 3.2, "text": "Hasta 65 yaşında erkek"},
            {"start": 3.2, "end": 6.8, "text": "akciğer kanseri şüphesi ile başvurdu"},
            {"start": 6.8, "end": 10.5, "text": "Sağ üst lobda 2.5 santimetre nodül tespit edildi"},
            {"start": 10.5, "end": 15.3, "text": "SUV değeri 8.5 olarak ölçüldü"}
        ]
        
        for ts in timestamps:
            st.write(f"[{ts['start']:.1f}s - {ts['end']:.1f}s] {ts['text']}")
    
    # İşlem seçenekleri
    st.subheader("🔄 İşlem Seçenekleri")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Rapor Oluştur"):
            st.success("📝 Rapor oluşturuldu!")
    
    with col2:
        if st.button("💾 Kaydet"):
            st.success("💾 Transkripsiyon kaydedildi!")
    
    with col3:
        if st.button("📤 Dışa Aktar"):
            st.info("📤 Dışa aktarma seçenekleri:")
            st.write("• TXT dosyası")
            st.write("• JSON formatı")
            st.write("• SRT altyazı")
    
    with col4:
        if st.button("🤖 AI Analiz"):
            st.info("🤖 AI analizi başlatılıyor...")

# Geçmiş transkripsiyonlar
def show_transcription_history():
    """Geçmiş transkripsiyonları göster"""
    
    st.subheader("📚 Geçmiş Transkripsiyonlar")
    
    # Mock geçmiş verisi
    history = [
        {
            "id": "TXN-001",
            "date": "2024-01-15 10:30:00",
            "filename": "hasta_raporu_001.wav",
            "duration": 45.2,
            "word_count": 28,
            "confidence": 0.92,
            "status": "Completed"
        },
        {
            "id": "TXN-002",
            "date": "2024-01-15 09:15:00",
            "filename": "konsultasyon_002.wav",
            "duration": 32.1,
            "word_count": 22,
            "confidence": 0.89,
            "status": "Completed"
        },
        {
            "id": "TXN-003",
            "date": "2024-01-14 16:45:00",
            "filename": "hasta_raporu_003.wav",
            "duration": 28.7,
            "word_count": 19,
            "confidence": 0.85,
            "status": "Failed"
        }
    ]
    
    # Geçmiş tablosu
    df = pd.DataFrame(history)
    st.dataframe(df, use_container_width=True)
    
    # Geçmiş işlemleri
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Geçmişi Yenile"):
            st.success("🔄 Geçmiş yenilendi!")
    
    with col2:
        if st.button("🗑️ Geçmişi Temizle"):
            st.warning("🗑️ Geçmiş temizlendi!")

# Ana fonksiyon çağrısı
if __name__ == "__main__":
    render_asr_panel()
    
    # Geçmiş transkripsiyonlar
    show_transcription_history()

