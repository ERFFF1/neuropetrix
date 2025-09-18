import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="System Settings - NeuroPETrix",
    page_icon="⚙️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .settings-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .settings-section {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .integration-card {
        background: #e8f5e8;
        border: 2px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .status-active {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-inactive {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="settings-header">
    <h1>⚙️ System Settings</h1>
    <p style="font-size: 1.2rem; margin: 0;">Sistem Ayarları ve Entegrasyonlar</p>
    <p style="font-size: 1rem; margin: 0.5rem 0 0 0;">HBYS, PACS ve diğer sistem entegrasyonları</p>
</div>
""", unsafe_allow_html=True)

# Ana içerik
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🔧 Sistem Ayarları")
    
    # Genel ayarlar
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown("#### 🌐 Genel Ayarlar")
    
    col1_1, col1_2 = st.columns(2)
    
    with col1_1:
        system_name = st.text_input("Sistem Adı:", "NeuroPETRIX v3.0")
        system_version = st.text_input("Versiyon:", "3.0.0")
        language = st.selectbox("Dil:", ["Türkçe", "English", "Deutsch"])
    
    with col1_2:
        timezone = st.selectbox("Saat Dilimi:", ["Europe/Istanbul", "UTC", "America/New_York"])
        date_format = st.selectbox("Tarih Formatı:", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        time_format = st.selectbox("Saat Formatı:", ["24 Saat", "12 Saat"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # HBYS entegrasyonu
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown("#### 🏥 HBYS Entegrasyonu")
    
    col2_1, col2_2 = st.columns(2)
    
    with col2_1:
        hbys_enabled = st.checkbox("HBYS Entegrasyonu Aktif", value=True)
        hbys_url = st.text_input("HBYS URL:", "https://hbys.hastane.gov.tr")
        hbys_username = st.text_input("Kullanıcı Adı:", "neuropetrix_user")
    
    with col2_2:
        hbys_password = st.text_input("Şifre:", type="password")
        hbys_timeout = st.number_input("Timeout (saniye):", min_value=5, max_value=300, value=30)
        hbys_retry = st.number_input("Tekrar Deneme:", min_value=1, max_value=10, value=3)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # PACS entegrasyonu
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown("#### 🖼️ PACS Entegrasyonu")
    
    col3_1, col3_2 = st.columns(2)
    
    with col3_1:
        pacs_enabled = st.checkbox("PACS Entegrasyonu Aktif", value=True)
        pacs_url = st.text_input("PACS URL:", "http://pacs.hastane.gov.tr:8042")
        pacs_username = st.text_input("PACS Kullanıcı:", "orthanc")
    
    with col3_2:
        pacs_password = st.text_input("PACS Şifre:", type="password")
        pacs_port = st.number_input("Port:", min_value=1, max_value=65535, value=8042)
        pacs_ssl = st.checkbox("SSL Kullan", value=False)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI ayarları
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown("#### 🤖 AI Ayarları")
    
    col4_1, col4_2 = st.columns(2)
    
    with col4_1:
        ai_enabled = st.checkbox("AI Modelleri Aktif", value=True)
        monai_enabled = st.checkbox("MONAI Engine", value=True)
        gpt4all_enabled = st.checkbox("GPT4All Engine", value=True)
    
    with col4_2:
        whisper_enabled = st.checkbox("Whisper Engine", value=True)
        auto_analysis = st.checkbox("Otomatik Analiz", value=False)
        confidence_threshold = st.slider("Güven Eşiği:", 0.0, 1.0, 0.8)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 Sistem Durumu")
    
    # Sistem durumu
    st.markdown('<div class="integration-card">', unsafe_allow_html=True)
    st.markdown("#### 🟢 Sistem Durumu")
    st.markdown('<span class="status-active">✅ Aktif</span>', unsafe_allow_html=True)
    st.text("Uptime: 99.8%")
    st.text("Son güncelleme: 2 dakika önce")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Entegrasyon durumu
    st.markdown('<div class="integration-card">', unsafe_allow_html=True)
    st.markdown("#### 🔗 Entegrasyonlar")
    
    integrations = {
        "HBYS": "🟢 Aktif",
        "PACS": "🟢 Aktif",
        "MONAI": "🟢 Aktif",
        "GPT4All": "🟡 Yükleniyor",
        "Whisper": "🟢 Aktif"
    }
    
    for integration, status in integrations.items():
        st.text(f"{integration}: {status}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Performans metrikleri
    st.markdown('<div class="integration-card">', unsafe_allow_html=True)
    st.markdown("#### ⚡ Performans")
    
    st.metric("CPU", "45%", "5%")
    st.metric("Bellek", "2.1 GB", "0.3 GB")
    st.metric("Disk", "125 GB", "15 GB")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Alt kısım - Gelişmiş ayarlar
st.markdown("### 🔧 Gelişmiş Ayarlar")

col5, col6 = st.columns(2)

with col5:
    st.markdown("#### 🔐 Güvenlik Ayarları")
    
    # Güvenlik ayarları
    security_settings = {
        "SSL/TLS": st.checkbox("SSL/TLS Aktif", value=True),
        "Firewall": st.checkbox("Firewall Aktif", value=True),
        "Logging": st.checkbox("Detaylı Logging", value=True),
        "Backup": st.checkbox("Otomatik Yedekleme", value=True),
        "Encryption": st.checkbox("Veri Şifreleme", value=True)
    }
    
    # Güvenlik seviyesi
    security_level = st.selectbox(
        "Güvenlik Seviyesi:",
        ["Düşük", "Orta", "Yüksek", "Maksimum"],
        index=2
    )
    
    st.info(f"Seçilen güvenlik seviyesi: **{security_level}**")

with col6:
    st.markdown("#### 📊 Veritabanı Ayarları")
    
    # Veritabanı ayarları
    db_settings = {
        "Host": st.text_input("DB Host:", "localhost"),
        "Port": st.number_input("DB Port:", min_value=1, max_value=65535, value=5432),
        "Name": st.text_input("DB Name:", "neuropetrix"),
        "User": st.text_input("DB User:", "postgres"),
        "Password": st.text_input("DB Password:", type="password")
    }
    
    # Veritabanı durumu
    st.markdown("**Veritabanı Durumu:**")
    st.success("✅ Bağlantı başarılı")
    st.text("Son yedekleme: 2 saat önce")
    st.text("Boyut: 125 MB")

# Ayarları kaydet
st.markdown("### 💾 Ayarları Kaydet")

col7, col8, col9 = st.columns(3)

with col7:
    if st.button("💾 Ayarları Kaydet", type="primary"):
        # Mock ayar kaydetme
        settings_data = {
            "system_name": system_name,
            "system_version": system_version,
            "language": language,
            "timezone": timezone,
            "hbys_enabled": hbys_enabled,
            "pacs_enabled": pacs_enabled,
            "ai_enabled": ai_enabled,
            "security_level": security_level,
            "timestamp": datetime.now().isoformat()
        }
        
        # Ayarları dosyaya kaydet
        with open("system_settings.json", "w") as f:
            json.dump(settings_data, f, indent=2)
        
        st.success("✅ Ayarlar başarıyla kaydedildi!")

with col8:
    if st.button("🔄 Varsayılan Ayarlar"):
        st.warning("⚠️ Varsayılan ayarlara dönülecek. Devam etmek istediğinizden emin misiniz?")
        
        if st.button("✅ Evet, Devam Et"):
            st.success("✅ Varsayılan ayarlar yüklendi!")

with col9:
    if st.button("📤 Ayarları Dışa Aktar"):
        # Mock ayar dışa aktarma
        st.download_button(
            label="📥 İndir",
            data=json.dumps(settings_data, indent=2),
            file_name="neuropetrix_settings.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>⚙️ System Settings - NeuroPETRIX v3.0</p>
    <p>Sistem ayarları ve entegrasyonlar</p>
</div>
""", unsafe_allow_html=True)
