import streamlit as st
import requests
import json
from datetime import datetime

def render_dashboard():
    """Dashboard sayfasını render et"""
    
    st.header("📊 Dashboard")
    
    # Sistem durumu
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Toplam Vaka", "1,247", "+12")
    
    with col2:
        st.metric("Tamamlanan Rapor", "892", "+8")
    
    with col3:
        st.metric("PICO Analizi", "156", "+5")
    
    with col4:
        st.metric("Füzyon İşlemi", "89", "+3")
    
    # Son aktiviteler
    st.subheader("Son Aktiviteler")
    activities = [
        {"action": "Yeni vaka oluşturuldu", "time": "2 dakika önce", "type": "create"},
        {"action": "PET raporu tamamlandı", "time": "15 dakika önce", "type": "complete"},
        {"action": "SUV analizi güncellendi", "time": "1 saat önce", "type": "update"},
        {"action": "Evidence araması yapıldı", "time": "2 saat önce", "type": "search"}
    ]
    
    for activity in activities:
        st.write(f"• {activity['action']} - {activity['time']}")
    
    # Sistem durumu kartları
    st.subheader("Sistem Durumu")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("🟢 Backend API\nÇalışıyor")
    
    with col2:
        st.info("🟢 Veritabanı\nAktif")
    
    with col3:
        st.info("🟢 AI Servisleri\nHazır")
    
    with col4:
        st.warning("🟡 Uyum Kontrolü\nKontrol ediliyor")
    
    # Hızlı erişim
    st.subheader("Hızlı Erişim")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 PICO Otomatikleştirme", use_container_width=True):
            st.session_state.page = "pico_automation"
    
    with col2:
        if st.button("🔗 Multimodal Füzyon", use_container_width=True):
            st.session_state.page = "multimodal_fusion"
    
    with col3:
        if st.button("💬 Klinik Geri Bildirim", use_container_width=True):
            st.session_state.page = "clinical_feedback"
    
    with col4:
        if st.button("⚖️ Uyum Paneli", use_container_width=True):
            st.session_state.page = "compliance_panel"


