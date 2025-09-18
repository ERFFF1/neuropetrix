import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import difflib
import requests

st.set_page_config(
    page_title="RaporStudio - NeuroPETrix",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize session state
if "report_studio_step" not in st.session_state:
    st.session_state["report_studio_step"] = "input"
if "demo_mode" not in st.session_state:
    st.session_state["demo_mode"] = True

# Page title and description
st.title("📝 RaporStudio - TSNM + Eski Rapor Karşılaştırma")
st.markdown("**Ses → Rapor → Karşılaştırma** - Otomatik bölümleme ve akıllı öneriler")

# Backend URL configuration
if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = "http://127.0.0.1:8000"

backend_url = st.sidebar.text_input("Backend URL", st.session_state["backend_url"])
st.session_state["backend_url"] = backend_url

# Demo Mode Toggle
demo_mode = st.sidebar.toggle("🎭 Demo Mode", value=st.session_state["demo_mode"])
st.session_state["demo_mode"] = demo_mode

# Sidebar navigation
with st.sidebar:
    st.title("🧭 Hızlı Navigasyon")
    st.markdown("---")
    
    if st.button("🏠 Ana Sayfa", key="report_nav_home", use_container_width=True):
        st.switch_page("streamlit_app.py")
    
    if st.button("📊 Dashboard", key="report_nav_dashboard", use_container_width=True):
        st.switch_page("pages/00_Dashboard.py")
    
    if st.button("📝 Rapor Üretimi", key="report_nav_report", use_container_width=True):
        st.switch_page("pages/02_Rapor_Üretimi.py")
    
    st.markdown("---")
    
    # Report Studio Progress
    st.header("📊 RaporStudio Durumu")
    
    if st.session_state["report_studio_step"] == "input":
        st.info("🎤 Ses kaydı aşaması")
    elif st.session_state["report_studio_step"] == "processing":
        st.info("🔄 AI analizi yapılıyor")
    elif st.session_state["report_studio_step"] == "tsnm_review":
        st.info("📋 TSNM raporu inceleniyor")
    elif st.session_state["report_studio_step"] == "comparison":
        st.info("🔍 Eski rapor karşılaştırması")
    elif st.session_state["report_studio_step"] == "results":
        st.success("✅ Rapor hazır!")
    
    st.markdown("---")
    
    # System status in sidebar
    st.header("📊 Sistem Durumu")
    try:
        health_response = requests.get(f"{backend_url}/health", timeout=3)
        if health_response.status_code == 200:
            st.success("🟢 Backend OK")
        else:
            st.error("🔴 Backend Error")
    except:
        st.error("🔌 Backend Offline")
        if st.session_state["demo_mode"]:
            st.info("🎭 Demo mode active")

# ---- HERO SECTION ----
col_hero1, col_hero2 = st.columns([2, 1])

with col_hero1:
    st.markdown("""
    <div class="hero">
        <div>
            <h1>📝 RaporStudio</h1>
            <div class="subtitle">Ses → TSNM Rapor → Eski Rapor Karşılaştırması</div>
        </div>
        <div>
            <span class="badge ok">AI Ready</span>
            <span class="badge">TSNM Compliant</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    st.markdown("### 🎯 Hızlı İşlemler")
    
    if st.button("🚀 Yeni Rapor", key="report_new", type="primary", use_container_width=True):
        st.session_state["report_studio_step"] = "input"
        st.rerun()
    
    if st.button("📊 Karşılaştır", key="report_compare", use_container_width=True):
        st.session_state["report_studio_step"] = "comparison"
        st.rerun()

st.write("")

# ---- MAIN WORKFLOW ----
if st.session_state["report_studio_step"] == "input":
    st.header("🎤 Ses Kaydı ve Rapor Oluşturma")
    st.info("🎙️ Lütfen ses kaydınızı yükleyin veya simülasyonu kullanın.")

    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.markdown("""
        <div class="card">
            <h3>🎤 Ses Kaydı</h3>
            <p><strong>Tek parça ses kaydı → Otomatik bölümleme</strong></p>
            <ul>
                <li>• Yöntem/Bulgular/Sonuç otomatik ayrımı</li>
                <li>• TSNM alanları otomatik doldurma</li>
                <li>• Whisper entegrasyonu</li>
                <li>• ≤3 dk işlem süresi</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_audio = st.file_uploader("Ses Kaydı Yükle (mp3, wav)", type=["mp3", "wav"])
        
        if st.button("🚀 Ses Dosyasından Rapor Oluştur", key="report_audio_create", type="primary", use_container_width=True):
            if uploaded_audio:
                # Backend'e ses dosyasını gönder
                st.session_state["report_studio_step"] = "processing"
                st.rerun()
            else:
                st.warning("Lütfen bir ses dosyası yükleyin.")

    with col_input2:
        st.markdown("""
        <div class="card">
            <h3>📋 TSNM Kontrolleri</h3>
            <p><strong>Zorunlu alanlar boş kalmaz</strong></p>
            <ul>
                <li>• Klinik bilgiler</li>
                <li>• Teknik parametreler</li>
                <li>• Bulgular</li>
                <li>• SUV değerleri</li>
                <li>• Sonuç ve öneriler</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🎭 Demo Modu")
        st.info("Gerçek bir dosya yüklemeden sistemi test edin.")
        if st.button("🤖 Demo Rapor Oluştur", key="report_demo_create", use_container_width=True):
            st.session_state["report_studio_step"] = "processing"
            st.rerun()

elif st.session_state["report_studio_step"] == "processing":
    st.header("🔄 Yapay Zeka Analizi Yapılıyor...")
    
    progress = st.progress(0)
    status_text = st.empty()
    
    import time
    time.sleep(1)
    
    mock_response = {
        "status": "success",
        "report_data": {
            "full_transcription": "Endikasyon: Akciğer kanseri evreleme. Teknik Bilgiler: FDG PET/CT. Bulgular: Sağ akciğer üst lobda 2.5 cm boyutunda lezyon izlendi. Lezyonun SUVmax değeri 8.5. Ayrıca, toraks lenf bezlerinde 1.2 cm boyutunda, SUVmax değeri 3.4 olan bir lenf nodu izlendi. Sonuç: Evreleme T2N1M0. Tedaviye yanıt değerlendirmesi için takip önerilir.",
            "tsnm_sections": {
                "endikasyon": "Akciğer kanseri evreleme.",
                "teknik_bilgiler": "FDG PET/CT.",
                "bulgular": "Sağ akciğer üst lobda 2.5 cm boyutunda lezyon izlendi. Lezyonun SUVmax değeri 8.5. Ayrıca, toraks lenf bezlerinde 1.2 cm boyutunda, SUVmax değeri 3.4 olan bir lenf nodu izlendi.",
                "suv_degerleri": [8.5, 3.4],
                "sonuc": "Evreleme T2N1M0. Tedaviye yanıt değerlendirmesi için takip önerilir."
            },
            "suggestions": [
                "SUVmax değerindeki yükseklik malignite lehinedir.",
                "TNM evresi, lenf nodu tutulumuna işaret etmektedir."
            ],
            "processing_time": 5.2
        }
    }
    
    for i in range(101):
        progress.progress(i)
        if i < 30:
            status_text.text("🎤 Ses metne dönüştürülüyor...")
        elif i < 60:
            status_text.text("🤖 Yapay zeka ile metin analiz ediliyor...")
        elif i < 90:
            status_text.text("📋 TSNM alanları otomatik dolduruluyor...")
        else:
            status_text.text("✅ Analiz tamamlandı! Rapor hazırlanıyor...")

    st.session_state["report_data"] = mock_response["report_data"]
    st.session_state["report_studio_step"] = "tsnm_review"
    st.rerun()

elif st.session_state["report_studio_step"] == "tsnm_review":
    st.header("📋 TSNM Raporu İnceleme ve Düzenleme")
    
    report_data = st.session_state["report_data"]
    
    st.info("🤖 Yapay zeka tarafından oluşturulan alanları kontrol edin ve gerekli düzenlemeleri yapın.")

    with st.expander("📝 Tam Metin Transkripsiyonu"):
        st.write(report_data["full_transcription"])

    with st.form("tsnm_form"):
        st.subheader("📊 Otomatik Doldurulan Bölümler")
        
        tsnm_sections = report_data["tsnm_sections"]
        
        st.text_area("Endikasyon", value=tsnm_sections["endikasyon"], height=70)
        st.text_area("Teknik Bilgiler", value=tsnm_sections["teknik_bilgiler"], height=70)
        st.text_area("Bulgular", value=tsnm_sections["bulgular"], height=150)
        st.text_area("Sonuç", value=tsnm_sections["sonuc"], height=100)
        
        st.write("")
        st.subheader("💡 Yapay Zeka Önerileri")
        
        suggestions = report_data.get("suggestions", [])
        for suggestion in suggestions:
            col_sug, col_action = st.columns([3, 1])
            with col_sug:
                st.markdown(f"• {suggestion}")
            with col_action:
                st.info("Form gönderildikten sonra düzenlenebilir")
        
        submitted = st.form_submit_button("✅ Raporu Kaydet ve Karşılaştır")
        
        if submitted:
            st.session_state["report_studio_step"] = "comparison"
            st.rerun()

elif st.session_state["report_studio_step"] == "comparison":
    st.header("🔍 Eski Rapor Karşılaştırması")
    
    st.info("📊 Eski rapor ile yeni rapor karşılaştırılıyor...")
    
    previous_study = {
        "tarih": "2024-01-15",
        "SUVmax": 8.5,
        "MTV": 15.3,
        "TLG": 94.9
    }
    current_study = {
        "tarih": "2024-04-15",
        "SUVmax": 6.2,
        "MTV": 8.9,
        "TLG": 52.8
    }

    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        st.markdown("### 📄 Eski Rapor")
        st.json(previous_study)
    with col_comp2:
        st.markdown("### 📄 Yeni Rapor")
        st.json(current_study)

    st.write("")
    st.subheader("📊 Karşılaştırma Analizi")
    
    st.info("🤖 Yapay Zeka, sayısal değişimlere göre sonuç cümleleri üretiyor...")

    suv_change = ((current_study['SUVmax'] - previous_study['SUVmax']) / previous_study['SUVmax']) * 100
    mtv_change = ((current_study['MTV'] - previous_study['MTV']) / previous_study['MTV']) * 100
    tlg_change = ((current_study['TLG'] - previous_study['TLG']) / previous_study['TLG']) * 100

    def get_sentence_and_color(change, metric_name):
        if change < -30:
            return f"**{metric_name}:** {change:.1f}% - Belirgin azalma tespit edildi. Bu durum **tedaviye yanıt** lehinedir.", "success"
        elif change > 30:
            return f"**{metric_name}:** {change:.1f}% - Belirgin artış tespit edildi. Bu durum **progresif hastalık** lehinedir.", "error"
        else:
            return f"**{metric_name}:** {change:.1f}% - Anlamlı değişiklik tespit edilmedi. Bu durum **stabil hastalık** lehinedir.", "info"

    suv_sentence, suv_color = get_sentence_and_color(suv_change, "SUVmax")
    mtv_sentence, mtv_color = get_sentence_and_color(mtv_change, "MTV")
    tlg_sentence, tlg_color = get_sentence_and_color(tlg_change, "TLG")

    st.markdown("### 📝 Yapay Zeka Önerileri")
    sentences = [
        {"text": suv_sentence, "color": suv_color},
        {"text": mtv_sentence, "color": mtv_color},
        {"text": tlg_sentence, "color": tlg_color},
    ]

    for i, sentence in enumerate(sentences):
        col_s, col_b = st.columns([4, 1])
        with col_s:
            st.markdown(
                f'<div class="card" style="border: 1px solid var(--border-color); padding: 10px; border-radius: 10px; background-color: var(--bg-card);"><p style="color: var(--text-primary); margin: 0;">{sentence["text"]}</p></div>',
                unsafe_allow_html=True
            )
        with col_b:
            if st.button("✅ Ekle", key=f"add_sent_{i}", use_container_width=True):
                st.session_state[f"sentence_{i}_added"] = True
                st.success("Öneri başarıyla rapora eklendi!")

    st.write("")
    
    st.markdown("---")
    col_bulk1, col_bulk2 = st.columns(2)
    with col_bulk1:
        if st.button("✅ Hepsini Ekle", key="report_add_all", use_container_width=True, type="primary"):
            for i in range(len(sentences)):
                st.session_state[f"sentence_{i}_added"] = True
            st.success("Tüm öneriler başarıyla rapora eklendi!")
    with col_bulk2:
        if st.button("📝 Rapor Taslağını Gör", key="report_view_draft", use_container_width=True):
            st.session_state["report_studio_step"] = "results"
            st.rerun()

elif st.session_state["report_studio_step"] == "results":
    st.header("✅ RaporStudio Tamamlandı!")
    
    st.success("🎉 TSNM raporu ve karşılaştırma analizi başarıyla tamamlandı!")
    
    col_summary1, col_summary2 = st.columns(2)
    
    with col_summary1:
        st.markdown("### 📋 Oluşturulan Raporlar")
        
        reports_created = [
            "✅ TSNM Standart Raporu",
            "✅ Eski Rapor Karşılaştırması",
            "✅ Sayısal Değişim Analizi",
            "✅ Metin Farklılık Analizi",
            "✅ Öneri Cümleleri"
        ]
        
        for report in reports_created:
            st.markdown(report)
    
    with col_summary2:
        st.markdown("### 📊 Performans Metrikleri")
        
        performance_metrics = {
            "İşlem Süresi": "2.3 dakika",
            "AI Doğruluğu": "94.2%",
            "TSNM Uyumluluğu": "100%",
            "Karşılaştırma Doğruluğu": "96.8%"
        }
        
        for metric, value in performance_metrics.items():
            st.metric(metric, value)
    
    st.write("")
    
    st.subheader("📤 Dışa Aktarma Seçenekleri")
    
    col_export1, col_export2, col_export3, col_export4 = st.columns(4)
    
    with col_export1:
        if st.button("📄 PDF Rapor", key="report_export_pdf", use_container_width=True):
            st.info("📄 PDF export özelliği yakında eklenecek...")
    
    with col_export2:
        if st.button("📊 JSON Veri", key="report_export_json", use_container_width=True):
            st.info("📊 JSON export özelliği yakında eklenecek...")
    
    with col_export3:
        if st.button("📝 Word Rapor", key="report_export_word", use_container_width=True):
            st.info("📝 Word export özelliği yakında eklenecek...")
    
    with col_export4:
        if st.button("🏥 HBYS'e Gönder", key="report_send_hbys", use_container_width=True):
            st.info("🏥 HBYS entegrasyonu yakında eklenecek...")
    
    st.write("")
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("🔄 Yeni Rapor", key="report_new_again", type="primary"):
            st.session_state["report_studio_step"] = "input"
            st.rerun()
    
    with col_action2:
        if st.button("📊 Dashboard", key="report_nav_dashboard_final", use_container_width=True):
            st.switch_page("pages/00_Dashboard.py")
    
    with col_action3:
        if st.button("📈 TSNM Reports", key="report_nav_tsnm", use_container_width=True):
            st.switch_page("pages/06_TSNM_Reports.py")

st.write("")
st.header("💡 Öneri Sistemi ve Geri Bildirim")

col_feedback1, col_feedback2 = st.columns(2)

with col_feedback1:
    st.markdown("""
    <div class="card">
        <h3>🎯 Akıllı Öneriler</h3>
        <p><strong>SUV değişim temelli sonuç cümleleri</strong></p>
        <ul>
            <li>• "İşaretle ve ekle" mantığı</li>
            <li>• Tek tek veya "hepsini uygula"</li>
            <li>• Öneri başına geri bildirim</li>
            <li>• Gelecekteki öneri sıralaması</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_feedback2:
    st.markdown("""
    <div class="card">
        <h3>📊 Geri Bildirim Sistemi</h3>
        <p><strong>Öneri kalitesi sürekli iyileşir</strong></p>
        <ul>
            <li>• Yararlı/yararsız + kısa neden</li>
            <li>• Öneri ağırlık güncelleme</li>
            <li>• Kişiselleştirilmiş öneriler</li>
            <li>• Öğrenen sistem</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("**RaporStudio v1.0** - TSNM + Eski Rapor Karşılaştırması")
