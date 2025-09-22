import streamlit as st
import os
import subprocess
import json
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Script Management - NeuroPETrix",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Script Management")
st.markdown("**NeuroPETrix Script Yönetim Paneli**")

# Sidebar
with st.sidebar:
    st.header("📋 Script Kategorileri")
    
    category = st.selectbox(
        "Kategori Seçin:",
        ["Tümü", "AI/ML", "Veri İşleme", "Rapor Üretimi", "Sistem", "DICOM"]
    )
    
    st.markdown("---")
    st.markdown("**Hızlı İşlemler**")
    
    if st.button("🔄 Script Listesini Yenile", key="refresh_scripts"):
        st.rerun()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📁 Mevcut Script'ler")
    
    # Script listesi
    scripts = {
        "AI/ML": [
            {"name": "whisper_enhanced.py", "path": "backend/utils/", "description": "Whisper AI ses transkripsiyonu"},
            {"name": "gpt_log_service.py", "path": "backend/services/", "description": "GPT log veritabanı yönetimi"},
        ],
        "Veri İşleme": [
            {"name": "pet_report_service.py", "path": "backend/services/", "description": "PET rapor otomasyonu"},
        ],
        "Sistem": [
            {"name": "start_system.sh", "path": "", "description": "Sistem başlatma script'i"},
        ]
    }
    
    if category == "Tümü":
        all_scripts = []
        for cat, script_list in scripts.items():
            all_scripts.extend(script_list)
        display_scripts = all_scripts
    else:
        display_scripts = scripts.get(category, [])
    
    if display_scripts:
        for i, script in enumerate(display_scripts):
            with st.expander(f"📄 {script['name']}", expanded=False):
                st.markdown(f"**Açıklama:** {script['description']}")
                st.markdown(f"**Konum:** `{script['path']}{script['name']}`")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button("▶️ Çalıştır", key=f"run_{i}"):
                        st.info(f"Script çalıştırılıyor: {script['name']}")
                
                with col_b:
                    if st.button("📝 Düzenle", key=f"edit_{i}"):
                        st.info(f"Script düzenleme: {script['name']}")
                
                with col_c:
                    if st.button("📊 Log", key=f"log_{i}"):
                        st.info(f"Script log'ları: {script['name']}")
    else:
        st.info("Bu kategoride script bulunamadı.")

with col2:
    st.header("🚀 Hızlı Çalıştır")
    
    # Script çalıştırma
    selected_script = st.selectbox(
        "Script Seçin:",
        [script["name"] for cat in scripts.values() for script in cat]
    )
    
    if st.button("▶️ Seçili Script'i Çalıştır", key="run_selected"):
        st.success(f"Script çalıştırılıyor: {selected_script}")
        
        # Mock script execution
        with st.spinner("Script çalışıyor..."):
            import time
            time.sleep(2)
            st.success("Script başarıyla tamamlandı!")

# Script istatistikleri
st.markdown("---")
st.header("📊 Script İstatistikleri")

col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)

with col_stats1:
    st.metric("Toplam Script", len([script for cat in scripts.values() for script in cat]))
    
with col_stats2:
    st.metric("AI/ML Script'leri", len(scripts.get("AI/ML", [])))
    
with col_stats3:
    st.metric("Veri İşleme", len(scripts.get("Veri İşleme", [])))
    
with col_stats4:
    st.metric("Sistem Script'leri", len(scripts.get("Sistem", [])))

# Script çalışma geçmişi
st.markdown("---")
st.header("📋 Çalışma Geçmişi")

# Mock execution history
execution_history = [
    {"script": "whisper_enhanced.py", "status": "✅ Başarılı", "timestamp": "2025-08-24 01:35", "duration": "2.3s"},
    {"script": "pet_report_service.py", "status": "✅ Başarılı", "timestamp": "2025-08-24 01:30", "duration": "1.8s"},
    {"script": "gpt_log_service.py", "status": "⚠️ Uyarı", "timestamp": "2025-08-24 01:25", "duration": "3.1s"},
]

df_history = pd.DataFrame(execution_history)
st.dataframe(df_history, use_container_width=True)

# Script ekleme
st.markdown("---")
st.header("➕ Yeni Script Ekle")

with st.form("add_script_form"):
    script_name = st.text_input("Script Adı", key="new_script_name")
    script_path = st.text_input("Script Yolu", key="new_script_path")
    script_category = st.selectbox("Kategori", list(scripts.keys()), key="new_script_category")
    script_description = st.text_area("Açıklama", key="new_script_description")
    
    if st.form_submit_button("📝 Script Ekle"):
        if script_name and script_path:
            st.success(f"Script eklendi: {script_name}")
        else:
            st.error("Lütfen tüm alanları doldurun!")

# Footer
st.markdown("---")
st.caption("🔧 Script Management Panel - NeuroPETrix v1.0.0")





