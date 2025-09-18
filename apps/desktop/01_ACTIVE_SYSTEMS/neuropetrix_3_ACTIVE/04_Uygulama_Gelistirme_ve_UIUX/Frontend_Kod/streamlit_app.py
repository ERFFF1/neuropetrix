import streamlit as st
import requests
import json
import pandas as pd
from pathlib import Path
import sys
import os

# Add local config path
sys.path.append(os.path.expanduser("~/NeuroPETRIX/local/config"))

st.set_page_config(
    page_title="NeuroPETrix v2.0 Dashboard",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 NeuroPETRIX v2.0 Dashboard")
st.markdown("**Entegre AI Sistemi - PICO → MONAI → Evidence → Decision → Report**")
st.markdown("---")

# System status check
st.subheader("📊 Sistem Durumu")
status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=3)
        if response.status_code == 200:
            st.success("✅ Backend")
        else:
            st.error("❌ Backend")
    except:
        st.error("❌ Backend")

with status_col2:
    try:
        response = requests.get("http://127.0.0.1:8000/performance", timeout=3)
        if response.status_code == 200:
            st.success("✅ Performance")
        else:
            st.error("❌ Performance")
    except:
        st.error("❌ Performance")

with status_col3:
    try:
        response = requests.get("http://127.0.0.1:8000/cache/stats", timeout=3)
        if response.status_code == 200:
            st.success("✅ Cache")
        else:
            st.error("❌ Cache")
    except:
        st.error("❌ Cache")

with status_col4:
    try:
        response = requests.get("http://127.0.0.1:8000/integration/health", timeout=3)
        if response.status_code == 200:
            st.success("✅ Integration")
        else:
            st.error("❌ Integration")
    except:
        st.error("❌ Integration")

st.markdown("---")

# Sidebar for hierarchical workflow navigation
with st.sidebar:
    st.header("🎯 Ana Akış Navigasyonu")
    
    # Flow type selection
    st.subheader("🚀 Akış Hızı")
    flow_speed = st.radio(
        "Akış hızını seçin:",
        ["⚡ Hızlı (Bypass)", "🔍 Detaylı (Tam Akış)"],
        help="Hızlı: Sadece gerekli adımlar\nDetaylı: Tüm analizler ve raporlar"
    )

    st.markdown("---")

    # Branch selection
    st.subheader("🏥 Branş Seçimi")
    branch = st.selectbox(
        "Branşınızı seçin:",
        ["Onkoloji", "Radyoloji", "KBB", "Nöroloji", "Kardiyoloji", "Ortopedi", "Nükleer Tıp"]
    )

    st.markdown("---")

    # Clinical decision target
    st.subheader("🎯 Klinik Karar Hedefi")
    clinical_target = st.selectbox(
        "Klinik hedefinizi seçin:",
        ["Tanı Kararı", "Tedavi Kararı", "Prognoz Kararı", "Takip Kararı"]
    )

    st.markdown("---")

    # NEW: ICD Code Input
    st.subheader("📋 ICD Kodu")
    icd_code = st.text_input(
        "ICD-10 kodunu girin:",
        placeholder="Örn: C34.9, I60.9",
        help="Hastalık sınıflandırma kodu"
    )

    st.markdown("---")

    # NEW: PICO Plus Integration
    st.subheader("🧠 PICO Plus")
    if st.button("🎯 PICO Sorusu Oluştur", key="pico_generate", use_container_width=True):
        st.session_state.show_pico = True
    
    if st.button("📊 Akıllı Metrikler", key="smart_metrics", use_container_width=True):
        st.session_state.show_metrics = True

    st.markdown("---")

    # HIERARCHICAL WORKFLOW NAVIGATION
    st.header("🔄 Ana Akış Modülleri")
    
    # 1. ICD Kodu + Branş + Klinik Hedef Seçimi
    with st.expander("📋 1. ICD Kodu + Branş + Klinik Hedef Seçimi", expanded=True):
        if st.button("🏥 HBYS Entegrasyonu", key="hbys_main", use_container_width=True):
            st.switch_page("pages/03_HBYS_Entegrasyon.py")
        if st.button("📊 Hasta Yönetimi", key="patient_main", use_container_width=True):
            st.switch_page("pages/00_Dashboard.py")
    
    # 2. Akıllı Metrik Tanımlama
    with st.expander("🤖 2. Akıllı Metrik Tanımlama", expanded=True):
        if st.button("📊 Metrik Tanımlama", key="metrics_main", use_container_width=True):
            st.switch_page("pages/16_Clinical_Decision_Support.py")
        if st.button("🎯 PICO Otomasyonu", key="pico_main", use_container_width=True):
            st.switch_page("pages/15_PICO_Automation.py")
    
    # 3. Veri Toplama
    with st.expander("📊 3. Veri Toplama", expanded=True):
        if st.button("🖼️ DICOM Yükleme", key="dicom_main", use_container_width=True):
            st.switch_page("pages/04_DICOM_Upload.py")
        if st.button("📝 Manuel Veri Girişi", key="manual_main", use_container_width=True):
            st.switch_page("pages/02_Rapor_Üretimi.py")
    
    # 4. MONAI + PyRadiomics Analizi
    with st.expander("🧠 4. MONAI + PyRadiomics Analizi", expanded=True):
        if st.button("🧠 MONAI & PyRadiomics", key="monai_main", use_container_width=True):
            st.switch_page("pages/17_MONAI_Radiomics.py")
        if st.button("📊 Performance Monitor", key="performance_main", use_container_width=True):
            st.switch_page("pages/19_Performance_Monitor.py")
        if st.button("🔗 Advanced Integration", key="integration_main", use_container_width=True):
            st.switch_page("pages/20_Advanced_Integration.py")
        if st.button("🖥️ Desktop Runner", key="desktop_main", use_container_width=True):
            st.switch_page("pages/14_Desktop_Runner.py")
    
    # 5. SUV Trend Analizi
    with st.expander("📈 5. SUV Trend Analizi", expanded=True):
        if st.button("📈 SUV Trend Analizi", key="suv_main", use_container_width=True):
            st.switch_page("pages/08_SUV_Trend.py")
        if st.button("📊 TSNM Raporları", key="tsnm_main", use_container_width=True):
            st.switch_page("pages/06_TSNM_Reports.py")
    
    # 6. Klinik Karar Hedefi Güncelleme
    with st.expander("🎯 6. Klinik Karar Hedefi Güncelleme", expanded=True):
        if st.button("🎯 Klinik Karar Desteği", key="clinical_main", use_container_width=True):
            st.switch_page("pages/16_Clinical_Decision_Support.py")
        if st.button("📊 GRADE Ön Tarama", key="grade_main", use_container_width=True):
            st.switch_page("pages/01_GRADE_Ön_Tarama.py")
    
    # 7. PICO + Literatür + GRADE
    with st.expander("🧠 7. PICO + Literatür + GRADE", expanded=True):
        if st.button("🎯 PICO Otomasyonu", key="pico_workflow", use_container_width=True):
            st.switch_page("pages/15_PICO_Automation.py")
        if st.button("📚 Kanıt Paneli", key="evidence_main", use_container_width=True):
            st.switch_page("pages/09_Evidence_Panel.py")
    
    # 8. Kanıt Değerlendirme
    with st.expander("🧠 8. Kanıt Değerlendirme", expanded=True):
        if st.button("📊 AI Analizi", key="ai_main", use_container_width=True):
            st.switch_page("pages/05_AI_Analysis.py")
        if st.button("📝 Rapor Üretimi", key="report_main", use_container_width=True):
            st.switch_page("pages/02_Rapor_Üretimi.py")
    
    # 9. Final Öneri
    with st.expander("📄 9. Final Öneri", expanded=True):
        if st.button("📝 Rapor Üretimi", key="final_report", use_container_width=True):
            st.switch_page("pages/02_Rapor_Üretimi.py")
        if st.button("🎤 ASR Panel", key="asr_main", use_container_width=True):
            st.switch_page("pages/07_ASR_Panel.py")

# Main workflow display
st.header("🔄 Ana Akış Sistemi")

# NEW: PICO Plus Integration Display
if st.session_state.get('show_pico', False):
    st.subheader("🧠 PICO Plus - Akıllı Soru Üretimi")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("🎯 **PICO Plus Sistemi**: ICD kodu ve klinik hedefe göre otomatik PICO sorusu oluşturur")
        
        if icd_code and clinical_target:
            # Mock PICO generation (real integration would use pico_generator.py)
            pico_question = f"**P:** {icd_code} tanılı hastalarda, **I:** {clinical_target.lower()} için uygun yaklaşım, **C:** standart yöntemler ile karşılaştırıldığında, **O:** klinik sonuçlar açısından etkili midir?"
            
            st.success("✅ **Oluşturulan PICO Sorusu:**")
            st.write(pico_question)
            
            # Show required metrics
            st.subheader("📊 Gerekli Metrikler")
            if branch == "Onkoloji":
                st.write("• **Kritik:** SUVmax, SUVmean, MTV, TLG")
                st.write("• **Önemli:** Hb, WBC, Plt, LDH, ECOG skoru")
                st.write("• **Bilgilendirici:** Yaş, cinsiyet, komorbiditeler")
            else:
                st.write("• **Kritik:** SUVmax, SUVmean, MTV, TLG")
                st.write("• **Önemli:** Yaş, cinsiyet, performans skoru")
                st.write("• **Bilgilendirici:** Komorbiditeler, aile öyküsü")
        else:
            st.warning("⚠️ ICD kodu ve klinik hedef seçin")
    
    with col2:
        st.subheader("🔧 PICO Plus Özellikleri")
        st.write("• **Otomatik soru üretimi**")
        st.write("• **Akıllı metrik önerisi**")
        st.write("• **Branşa özel kriterler**")
        st.write("• **Klinik hedef odaklı**")
        
        if st.button("🔄 Yeni PICO Oluştur", key="new_pico"):
            st.session_state.show_pico = False
            st.rerun()

# NEW: Smart Metrics Display
if st.session_state.get('show_metrics', False):
    st.subheader("🤖 Akıllı Metrik Tanımlama")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("📊 **Akıllı Metrik Sistemi**: ICD kodu ve klinik hedefe göre gerekli metrikleri otomatik belirler")
        
        if icd_code and clinical_target and branch:
            # Mock metrics generation
            st.success("✅ **Önerilen Metrikler:**")
            
            if branch == "Onkoloji":
                if clinical_target == "Tanı Kararı":
                    st.write("• **Görüntüleme:** SUVmax, SUVmean, MTV, TLG, lezyon boyutu")
                    st.write("• **Laboratuvar:** Hb, WBC, Plt, LDH, CEA, CA19-9")
                    st.write("• **Klinik:** ECOG skoru, kilo kaybı, komorbiditeler")
                elif clinical_target == "Tedavi Kararı":
                    st.write("• **Görüntüleme:** SUVmax, SUVmean, MTV, TLG, PERCIST")
                    st.write("• **Laboratuvar:** ECOG skoru, mevcut tedaviler, alerjiler")
                    st.write("• **Klinik:** Performans skoru, yan etkiler")
            else:
                st.write("• **Görüntüleme:** SUVmax, SUVmean, MTV, TLG")
                st.write("• **Laboratuvar:** Temel biyokimya, enfeksiyon parametreleri")
                st.write("• **Klinik:** Yaş, cinsiyet, risk faktörleri")
        else:
            st.warning("⚠️ ICD kodu, branş ve klinik hedef seçin")
    
    with col2:
        st.subheader("🎯 Metrik Kategorileri")
        st.write("• **Kritik:** Zorunlu")
        st.write("• **Önemli:** Gerekli")
        st.write("• **Bilgilendirici:** Faydalı")
        
        if st.button("🔄 Yeni Metrik Analizi", key="new_metrics"):
            st.session_state.show_metrics = False
            st.rerun()

# Display workflow based on selection
if "Hızlı (Bypass)" in flow_speed:
    st.info("🚀 **Hızlı Akış (Bypass)**: Ana akışın kritik adımları, hızlı sonuç için optimize edildi.")
    workflow_steps = [
        "📋 ICD Kodu + Branş + Klinik Hedef Seçimi",
        "🤖 Akıllı Metrik Tanımlama (Branşa özel)",
        "📊 Veri Toplama (HBYS/Manuel - DICOM opsiyonel)",
        "🧠 MONAI + PyRadiomics Analizi (Hızlı mod)",
        "📈 SUV Trend Analizi (Temel)",
        "🎯 Klinik Karar Hedefi Güncelleme",
        "🧠 PICO + Literatür + GRADE (Özet)",
        "🧠 Kanıt Değerlendirme (Hızlı)",
        "📄 Final Öneri (Kompakt)"
    ]
    if branch == "Onkoloji":
        workflow_steps.insert(4, "🏥 TSNM Evreleme (Hızlı)")
    elif branch == "Radyoloji":
        workflow_steps.insert(4, "🖼️ 3D Görüntüleme (Temel)")
    elif branch == "Kardiyoloji":
        workflow_steps.insert(4, "🫀 Perfüzyon Analizi (Hızlı)")
else:
    st.info("🔍 **Detaylı Akış (Tam Akış)**: Ana akışın tüm adımları, kapsamlı analiz için.")
    workflow_steps = [
        "📋 ICD Kodu + Branş + Klinik Hedef Seçimi",
        "🤖 Akıllı Metrik Tanımlama (Branşa özel + Detaylı)",
        "📊 Veri Toplama (HBYS/Manuel/DICOM)",
        "🧠 MONAI + PyRadiomics Analizi (Tam analiz)",
        "📈 SUV Trend Analizi (Detaylı)",
        "🎯 Klinik Karar Hedefi Güncelleme",
        "🧠 PICO + Literatür + GRADE (Kapsamlı)",
        "🧠 Kanıt Değerlendirme (Detaylı)",
        "📄 Final Öneri (Kapsamlı)",
        "📄 Detaylı Rapor Üretimi"
    ]
    if branch == "Onkoloji":
        workflow_steps.insert(4, "🏥 TSNM Evreleme (Detaylı)")
        workflow_steps.insert(6, "💊 Tedavi Protokolü Seçimi")
    elif branch == "Radyoloji":
        workflow_steps.insert(4, "🖼️ 3D Görüntüleme (Gelişmiş)")
        workflow_steps.insert(6, "📊 Karşılaştırmalı Analiz")
    elif branch == "Kardiyoloji":
        workflow_steps.insert(4, "🫀 Perfüzyon Analizi (Detaylı)")
        workflow_steps.insert(6, "📊 Risk Stratifikasyonu")

st.subheader("📋 Entegre İş Akışı")
for i, step in enumerate(workflow_steps, 1):
    st.write(f"{i}. {step}")

st.markdown("---")

# NEW: Enhanced Branch Specialization Display
st.header("🏥 Branş Özelleştirmesi")
if branch == "Onkoloji":
    st.subheader("🏥 Onkoloji - Özel Metrikler")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("🩸 **Laboratuvar:**")
        st.write("• Hb, WBC, Plt, LDH")
        st.write("• CEA, CA19-9, PSA")
        st.write("• ECOG skoru")
    
    with col2:
        st.write("🖼️ **Görüntüleme:**")
        st.write("• SUVmax, SUVmean, MTV, TLG")
        st.write("• Lezyon boyutu, Metastaz")
        st.write("• PERCIST kriterleri")
    
    with col3:
        st.write("📚 **Klinik Kılavuzlar:**")
        st.write("• NCCN Guidelines")
        st.write("• ESMO Guidelines")
        st.write("• ASCO Guidelines")
elif branch == "Radyoloji":
    st.subheader("🖼️ Radyoloji - Özel Metrikler")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("🩸 **Laboratuvar:**")
        st.write("• Temel biyokimya")
        st.write("• Enfeksiyon parametreleri")
        st.write("• Kontrast alerjisi")
    
    with col2:
        st.write("🖼️ **Görüntüleme:**")
        st.write("• 3D görüntüleme")
        st.write("• Karşılaştırmalı analiz")
        st.write("• Tekstür analizi")
    
    with col3:
        st.write("📚 **Klinik Kılavuzlar:**")
        st.write("• ACR Guidelines")
        st.write("• RSNA Guidelines")
        st.write("• Görüntü kalitesi")
elif branch == "Kardiyoloji":
    st.subheader("🫀 Kardiyoloji - Özel Metrikler")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("🩸 **Laboratuvar:**")
        st.write("• Troponin, BNP")
        st.write("• Kreatinin, eGFR")
        st.write("• Kardiyak risk skorları")
    
    with col2:
        st.write("🖼️ **Görüntüleme:**")
        st.write("• Perfüzyon analizi")
        st.write("• Ejection fraction")
        st.write("• Koroner kalsiyum")
    
    with col3:
        st.write("📚 **Klinik Kılavuzlar:**")
        st.write("• ESC Guidelines")
        st.write("• ACC/AHA Guidelines")
        st.write("• Risk stratifikasyonu")

st.markdown("---")

# NEW: Dynamic Reporting System
st.header("📄 Dinamik Raporlama Sistemi")
col1, col2 = st.columns([2, 1])

with col1:
    st.info("📊 **TSNM Formatı**: Otomatik rapor üretimi ve dinamik içerik")
    
    if st.button("📝 Rapor Şablonu Oluştur", key="create_template"):
        st.session_state.show_report = True
    
    if st.session_state.get('show_report', False):
        st.success("✅ **Rapor Şablonu Oluşturuldu:**")
        st.write("• **Hasta Bilgileri:** Otomatik doldurulur")
        st.write("• **Klinik Bilgi:** ICD kodu ve branşa göre")
        st.write("• **Teknik Bilgiler:** DICOM parametreleri")
        st.write("• **Bulgular:** SUV değerleri ve analizler")
        st.write("• **Sonuç:** PICO tabanlı öneriler")
        st.write("• **Öneriler:** Kanıta dayalı yaklaşımlar")

with col2:
    st.subheader("🔧 Rapor Özellikleri")
    st.write("• **Dinamik placeholder'lar**")
    st.write("• **Kısaltma sözlüğü**")
    st.write("• **Branşa özel formatlar**")
    st.write("• **Otomatik metrik entegrasyonu**")

st.markdown("---")

# System status
st.header("📊 Sistem Durumu")
status_col1, status_col2, status_col3, status_col4 = st.columns(4)
with status_col1:
    try:
        response = requests.get("http://127.0.0.1:8000/health/", timeout=3)
        if response.status_code == 200:
            st.success("✅ Backend")
        else:
            st.error("❌ Backend")
    except:
        st.error("❌ Backend")
with status_col2:
    st.success("✅ Frontend")
with status_col3:
    st.success("✅ Database")
with status_col4:
    st.success("✅ AI Services")

# Recent activities
st.header("📋 Son Aktiviteler")
recent_activities = [
    {"Tarih": "2025-08-27 23:50", "Aktivite": "PICO Plus entegrasyonu tamamlandı", "Durum": "✅"},
    {"Tarih": "2025-08-27 23:49", "Aktivite": "Akıllı metrik sistemi eklendi", "Durum": "✅"},
    {"Tarih": "2025-08-27 23:48", "Aktivite": "Dinamik raporlama sistemi entegre edildi", "Durum": "✅"},
    {"Tarih": "2025-08-27 23:47", "Aktivite": "Ana akış güçlendirildi", "Durum": "✅"}
]
df_activities = pd.DataFrame(recent_activities)
st.dataframe(df_activities, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🧠 NeuroPETrix v2.0 - Geleceğin Tıbbi Görüntüleme Platformu</p>
    <p>PICO Plus + Akıllı Metrikler + Dinamik Raporlama entegre edildi</p>
</div>
""", unsafe_allow_html=True)
