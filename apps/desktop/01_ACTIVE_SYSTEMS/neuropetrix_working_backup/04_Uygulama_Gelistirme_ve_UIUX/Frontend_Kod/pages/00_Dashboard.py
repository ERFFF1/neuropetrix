import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from pathlib import Path
import numpy as np

st.set_page_config(
    page_title="Dashboard - NeuroPETrix",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize session state
if "dashboard_view" not in st.session_state:
    st.session_state["dashboard_view"] = "overview"
if "demo_mode" not in st.session_state:
    st.session_state["demo_mode"] = True
if "last_action" not in st.session_state:
    st.session_state["last_action"] = "none"
if "patient_data" not in st.session_state:
    st.session_state["patient_data"] = []
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = []

# Page title and hero
st.title("🏠 NeuroPETrix Dashboard")
st.markdown("**Merkezi Kontrol Paneli** - Tüm özelliklere kolay erişim ve sistem durumu")

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
    
    # Quick navigation buttons
    if st.button("🏠 Ana Sayfa", use_container_width=True):
        st.switch_page("streamlit_app.py")
    
    if st.button("🧪 GRADE Scoring", use_container_width=True):
        st.switch_page("pages/01_GRADE_Ön_Tarama.py")
    
    if st.button("📊 AI Analysis", use_container_width=True):
        st.switch_page("pages/05_AI_Analysis.py")
    
    if st.button("📈 TSNM Reports", use_container_width=True):
        st.switch_page("pages/06_TSNM_Reports.py")
    
    if st.button("🎤 ASR Panel", use_container_width=True):
        st.switch_page("pages/07_ASR_Panel.py")
    
    if st.button("📈 SUV Trend", use_container_width=True):
        st.switch_page("pages/08_SUV_Trend.py")
    
    if st.button("📚 Evidence Panel", use_container_width=True):
        st.switch_page("pages/09_Evidence_Panel.py")
    
    st.markdown("---")
    
    # Dashboard view selector
    st.header("📊 Dashboard Views")
    
    if st.button("📋 Genel Bakış", use_container_width=True):
        st.session_state["dashboard_view"] = "overview"
        st.rerun()
    
    if st.button("👥 Hasta Yönetimi", use_container_width=True):
        st.session_state["dashboard_view"] = "patients"
        st.rerun()
    
    if st.button("🔬 AI Analizler", use_container_width=True):
        st.session_state["dashboard_view"] = "analysis"
        st.rerun()
    
    if st.button("📝 Raporlar", use_container_width=True):
        st.session_state["dashboard_view"] = "reports"
        st.rerun()
    
    if st.button("📊 İstatistikler", use_container_width=True):
        st.session_state["dashboard_view"] = "statistics"
        st.rerun()
    
    if st.button("⚙️ Sistem", use_container_width=True):
        st.session_state["dashboard_view"] = "system"
        st.rerun()
    
    st.markdown("---")
    
    # System status
    st.header("📊 Sistem Durumu")
    try:
        health_response = requests.get(f"{backend_url}/health", timeout=3)
        if health_response.status_code == 200:
            st.success("🟢 Backend OK")
            health_data = health_response.json()
            st.caption(f"Son kontrol: {health_data.get('timestamp', 'N/A')}")
        else:
            st.error("🔴 Backend Error")
    except:
        st.error("🔌 Backend Offline")
        if st.session_state["demo_mode"]:
            st.info("🎭 Demo mode aktif")

# Main dashboard content
if st.session_state["dashboard_view"] == "overview":
    # ---- HERO SECTION ----
    col_hero1, col_hero2 = st.columns([2, 1])
    
    with col_hero1:
        st.markdown("""
        <div class="hero">
            <div>
                <h1>🚀 Hoş Geldiniz!</h1>
                <div class="subtitle">NeuroPETrix AI Platform'unda başarılı olmak için rehber</div>
            </div>
            <div>
                <span class="badge ok">Sistem Aktif</span>
                <span class="badge">AI Ready</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_hero2:
        st.markdown("### 🎯 Akıllı Öneriler")
        
        # Get user's last action from session state
        last_action = st.session_state.get("last_action", "none")
        
        # Dynamic recommendations based on context
        if last_action == "patient_created":
            st.info("👤 **Hasta oluşturuldu!**")
            st.markdown("**Sonraki adım:** PET-CT analizi başlatın")
            if st.button("🚀 Analizi Başlat", type="primary"):
                st.switch_page("pages/05_AI_Analysis.py")
        
        elif last_action == "analysis_completed":
            st.info("📊 **Analiz tamamlandı!**")
            st.markdown("**Sonraki adım:** TSNM raporu oluşturun")
            if st.button("📝 Rapor Oluştur", type="primary"):
                st.switch_page("pages/06_TSNM_Reports.py")
        
        elif last_action == "report_generated":
            st.info("📄 **Rapor hazır!**")
            st.markdown("**Sonraki adım:** Klinik değerlendirme")
            if st.button("🏥 Klinik Değerlendirme", type="primary"):
                st.switch_page("pages/03_HBYS_Entegrasyon.py")
        
        else:
            st.info("🎯 **Başlangıç önerisi:**")
            st.markdown("**İlk adım:** Hasta kaydı oluşturun")
            if st.button("🏥 Hasta Kaydı", type="primary"):
                st.switch_page("pages/03_HBYS_Entegrasyon.py")
    
    st.write("")
    
    # ---- QUICK STATS ----
    st.header("📊 Hızlı İstatistikler")
    
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    
    with col_stats1:
        if st.session_state["demo_mode"]:
            st.metric("👥 Toplam Hasta", "1,247", "+12%")
        else:
            st.metric("👥 Toplam Hasta", "N/A")
    
    with col_stats2:
        if st.session_state["demo_mode"]:
            st.metric("🔬 AI Analizler", "892", "+8%")
        else:
            st.metric("🔬 AI Analizler", "N/A")
    
    with col_stats3:
        if st.session_state["demo_mode"]:
            st.metric("📝 Raporlar", "1,156", "+15%")
        else:
            st.metric("📝 Raporlar", "N/A")
    
    with col_stats4:
        if st.session_state["demo_mode"]:
            st.metric("⏱️ Ort. Süre", "2.3 dk", "-18%")
        else:
            st.metric("⏱️ Ort. Süre", "N/A")
    
    st.write("")
    
    # ---- WORKFLOW STATUS ----
    st.header("🔄 Workflow Durumu")
    
    col_workflow1, col_workflow2 = st.columns(2)
    
    with col_workflow1:
        st.markdown("### 📋 Aktif İşlemler")
        
        # Active workflow items
        workflow_items = [
            {"status": "🔄", "task": "PET-CT Analizi", "patient": "Ahmet Yılmaz", "progress": 75},
            {"status": "⏳", "task": "TSNM Raporu", "patient": "Fatma Demir", "progress": 45},
            {"status": "📝", "task": "Klinik Değerlendirme", "patient": "Mehmet Kaya", "progress": 90}
        ]
        
        for item in workflow_items:
            col_wf1, col_wf2 = st.columns([1, 3])
            with col_wf1:
                st.markdown(f"**{item['status']}**")
            with col_wf2:
                st.markdown(f"**{item['task']}**")
                st.markdown(f"*{item['patient']}*")
                st.progress(item['progress'] / 100)
                st.caption(f"{item['progress']}% tamamlandı")
    
    with col_workflow2:
        st.markdown("### 🎯 Son Aktiviteler")
        
        # Recent activities
        activities = [
            {"time": "2 dk önce", "action": "Hasta kaydı oluşturuldu", "user": "Dr. Şeref"},
            {"time": "15 dk önce", "action": "AI analizi tamamlandı", "user": "Sistem"},
            {"time": "1 saat önce", "action": "TSNM raporu indirildi", "user": "Dr. Şeref"},
            {"time": "2 saat önce", "action": "GRADE değerlendirmesi", "user": "Dr. Şeref"}
        ]
        
        for activity in activities:
            st.markdown(f"**{activity['time']}** - {activity['action']}")
            st.caption(f"*{activity['user']}*")
    
    st.write("")
    
    # ---- QUICK ACTIONS ----
    st.header("⚡ Hızlı İşlemler")
    
    col_actions1, col_actions2, col_actions3, col_actions4 = st.columns(4)
    
    with col_actions1:
        if st.button("👤 Yeni Hasta", use_container_width=True, type="primary"):
            st.switch_page("pages/03_HBYS_Entegrasyon.py")
    
    with col_actions2:
        if st.button("🔬 AI Analiz", use_container_width=True):
            st.switch_page("pages/05_AI_Analysis.py")
    
    with col_actions3:
        if st.button("📝 Rapor", use_container_width=True):
            st.switch_page("pages/02_Rapor_Üretimi.py")
    
    with col_actions4:
        if st.button("📊 Dashboard", use_container_width=True):
            st.switch_page("pages/00_Dashboard.py")
    
    # ---- ADVANCED FEATURES ----
    st.header("🚀 Gelişmiş Özellikler")
    
    col_adv1, col_adv2, col_adv3 = st.columns(3)
    
    with col_adv1:
        st.markdown("**🎤 ASR Panel**")
        st.markdown("Ses tanıma ve dikte sistemi")
        if st.button("🎤 ASR'a Git", key="asr_quick"):
            st.switch_page("pages/07_ASR_Panel.py")
    
    with col_adv2:
        st.markdown("**📈 SUV Trend**")
        st.markdown("SUV değer trend analizi")
        if st.button("📈 SUV Trend'e Git", key="suv_quick"):
            st.switch_page("pages/08_SUV_Trend.py")
    
    with col_adv3:
        st.markdown("**📚 Evidence Panel**")
        st.markdown("Kanıt tabanlı karar desteği")
        if st.button("📚 Evidence'a Git", key="evidence_quick"):
            st.switch_page("pages/09_Evidence_Panel.py")

elif st.session_state["dashboard_view"] == "patients":
    # ---- PATIENT MANAGEMENT DASHBOARD ----
    st.header("👥 Hasta Yönetimi Dashboard")
    
    # Patient statistics
    col_pat1, col_pat2, col_pat3, col_pat4 = st.columns(4)
    
    with col_pat1:
        st.metric("👥 Toplam Hasta", "1,247", "+12%")
    
    with col_pat2:
        st.metric("🆕 Yeni Hasta", "23", "+5%")
    
    with col_pat3:
        st.metric("🔄 Aktif Takip", "156", "+8%")
    
    with col_pat4:
        st.metric("✅ Tamamlanan", "1,091", "+15%")
    
    st.write("")
    
    # Patient list
    st.subheader("📋 Son Hasta Kayıtları")
    
    # Mock patient data
    patients = [
        {"id": "P001", "name": "Ahmet Yılmaz", "age": 45, "diagnosis": "Akciğer Kanseri", "status": "Aktif", "last_visit": "2025-01-15"},
        {"id": "P002", "name": "Fatma Demir", "age": 52, "diagnosis": "Lenfoma", "status": "Takip", "last_visit": "2025-01-14"},
        {"id": "P003", "name": "Mehmet Kaya", "age": 38, "diagnosis": "Meme Kanseri", "status": "Tamamlandı", "last_visit": "2025-01-10"},
        {"id": "P004", "name": "Ayşe Özkan", "age": 61, "diagnosis": "Kolon Kanseri", "status": "Aktif", "last_visit": "2025-01-13"}
    ]
    
    # Create DataFrame
    df_patients = pd.DataFrame(patients)
    st.dataframe(df_patients, use_container_width=True, hide_index=True)
    
    # Patient search
    st.subheader("🔍 Hasta Arama")
    col_search1, col_search2 = st.columns(2)
    
    with col_search1:
        search_term = st.text_input("Hasta Adı veya ID")
    
    with col_search2:
        search_diagnosis = st.selectbox("Tanı", ["Tümü", "Akciğer Kanseri", "Lenfoma", "Meme Kanseri", "Kolon Kanseri"])
    
    if st.button("🔍 Ara", type="primary"):
        st.success("🔍 Arama yapılıyor...")

elif st.session_state["dashboard_view"] == "analysis":
    # ---- AI ANALYSIS DASHBOARD ----
    st.header("🔬 AI Analiz Dashboard")
    
    # Analysis statistics
    col_ana1, col_ana2, col_ana3, col_ana4 = st.columns(4)
    
    with col_ana1:
        st.metric("🔬 Toplam Analiz", "892", "+8%")
    
    with col_ana2:
        st.metric("✅ Başarılı", "856", "+12%")
    
    with col_ana3:
        st.metric("⚠️ Dikkat", "28", "-5%")
    
    with col_ana4:
        st.metric("❌ Hata", "8", "-2%")
    
    st.write("")
    
    # Analysis types
    st.subheader("📊 Analiz Türleri")
    
    col_types1, col_types2 = st.columns(2)
    
    with col_types1:
        # Analysis type distribution
        analysis_types = ["Segmentasyon", "Radiomics", "Klinik Değerlendirme", "Literatür Entegrasyonu"]
        analysis_counts = [456, 234, 156, 46]
        
        fig_types = px.pie(
            values=analysis_counts,
            names=analysis_types,
            title="Analiz Türleri Dağılımı"
        )
        st.plotly_chart(fig_types, use_container_width=True)
    
    with col_types2:
        # Success rate over time
        dates = pd.date_range(start='2025-01-01', end='2025-01-15', freq='D')
        success_rates = [95, 92, 88, 96, 94, 91, 93, 97, 95, 94, 96, 93, 95, 97, 96]
        
        fig_success = px.line(
            x=dates,
            y=success_rates,
            title="Başarı Oranı Trendi",
            labels={'x': 'Tarih', 'y': 'Başarı Oranı (%)'}
        )
        st.plotly_chart(fig_success, use_container_width=True)
    
    # Recent analyses
    st.subheader("🔄 Son Analizler")
    
    analyses = [
        {"patient": "Ahmet Yılmaz", "type": "Segmentasyon", "status": "✅ Tamamlandı", "duration": "2.3 dk", "confidence": "94%"},
        {"patient": "Fatma Demir", "type": "Radiomics", "status": "⚠️ Dikkat", "duration": "3.1 dk", "confidence": "87%"},
        {"patient": "Mehmet Kaya", "type": "Klinik Değerlendirme", "status": "✅ Tamamlandı", "duration": "1.8 dk", "confidence": "96%"}
    ]
    
    df_analyses = pd.DataFrame(analyses)
    st.dataframe(df_analyses, use_container_width=True, hide_index=True)

elif st.session_state["dashboard_view"] == "reports":
    # ---- REPORTS DASHBOARD ----
    st.header("📝 Raporlar Dashboard")
    
    # Report statistics
    col_rep1, col_rep2, col_rep3, col_rep4 = st.columns(4)
    
    with col_rep1:
        st.metric("📝 Toplam Rapor", "1,156", "+15%")
    
    with col_rep2:
        st.metric("📄 TSNM Format", "892", "+18%")
    
    with col_rep3:
        st.metric("📊 AI Destekli", "1,023", "+22%")
    
    with col_rep4:
        st.metric("⏱️ Ort. Süre", "1.8 dk", "-12%")
    
    st.write("")
    
    # Report generation workflow
    st.subheader("🔄 Rapor Üretim İş Akışı")
    
    col_work1, col_work2, col_work3, col_work4 = st.columns(4)
    
    with col_work1:
        st.markdown("**1. 📋 Veri Toplama**")
        st.progress(0.9)
        st.caption("90% tamamlandı")
    
    with col_work2:
        st.markdown("**2. 🔬 AI Analiz**")
        st.progress(0.7)
        st.caption("70% tamamlandı")
    
    with col_work3:
        st.markdown("**3. 📝 Rapor Yazma**")
        st.progress(0.5)
        st.caption("50% tamamlandı")
    
    with col_work4:
        st.markdown("**4. ✅ Kontrol**")
        st.progress(0.3)
        st.caption("30% tamamlandı")
    
    # Report templates
    st.subheader("📋 Rapor Şablonları")
    
    col_temp1, col_temp2, col_temp3 = st.columns(3)
    
    with col_temp1:
        st.markdown("**🏥 TSNM Standart**")
        st.markdown("• FDG PET/CT")
        st.markdown("• PSMA PET/CT")
        st.markdown("• DOTATATE PET/CT")
        if st.button("📝 Oluştur", key="tsnm"):
            st.info("TSNM raporu oluşturuluyor...")
    
    with col_temp2:
        st.markdown("**🤖 AI Destekli**")
        st.markdown("• Segmentasyon")
        st.markdown("• Radiomics")
        st.markdown("• Klinik Yorum")
        if st.button("📝 Oluştur", key="ai"):
            st.info("AI raporu oluşturuluyor...")
    
    with col_temp3:
        st.markdown("**📊 Özet Rapor**")
        st.markdown("• Hızlı özet")
        st.markdown("• Ana bulgular")
        st.markdown("• Öneriler")
        if st.button("📝 Oluştur", key="summary"):
            st.info("Özet rapor oluşturuluyor...")

elif st.session_state["dashboard_view"] == "statistics":
    # ---- STATISTICS DASHBOARD ----
    st.header("📊 İstatistikler Dashboard")
    
    # Performance metrics
    col_perf1, col_perf2, col_perf3, col_perf4 = st.columns(4)
    
    with col_perf1:
        st.metric("🚀 Sistem Performansı", "94.2%", "+2.1%")
    
    with col_perf2:
        st.metric("⚡ Yanıt Süresi", "1.8s", "-0.3s")
    
    with col_perf3:
        st.metric("💾 Disk Kullanımı", "67%", "+5%")
    
    with col_perf4:
        st.metric("🔄 Uptime", "99.7%", "+0.2%")
    
    st.write("")
    
    # Charts and graphs
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Monthly trends
        months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz']
        patients = [120, 135, 142, 158, 167, 180]
        analyses = [98, 112, 125, 138, 145, 156]
        
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Scatter(x=months, y=patients, name='Hastalar', mode='lines+markers'))
        fig_monthly.add_trace(go.Scatter(x=months, y=analyses, name='Analizler', mode='lines+markers'))
        fig_monthly.update_layout(title='Aylık Trend', height=400)
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col_chart2:
        # AI model performance
        models = ['Segmentasyon', 'Radiomics', 'Klinik', 'Literatür']
        accuracy = [94.2, 87.6, 91.3, 89.8]
        
        fig_models = px.bar(
            x=models,
            y=accuracy,
            title='AI Model Performansı',
            labels={'x': 'Model', 'y': 'Doğruluk (%)'}
        )
        fig_models.update_layout(height=400)
        st.plotly_chart(fig_models, use_container_width=True)
    
    # Detailed statistics
    st.subheader("📈 Detaylı İstatistikler")
    
    col_det1, col_det2 = st.columns(2)
    
    with col_det1:
        st.markdown("**👥 Hasta Demografisi**")
        age_groups = ["18-30", "31-45", "46-60", "61+"]
        age_counts = [156, 234, 456, 401]
        
        fig_age = px.pie(
            values=age_counts,
            names=age_groups,
            title="Yaş Grupları"
        )
        st.plotly_chart(fig_age, use_container_width=True)
    
    with col_det2:
        st.markdown("**🏥 Tanı Dağılımı**")
        diagnoses = ["Akciğer", "Lenfoma", "Meme", "Kolon", "Diğer"]
        diag_counts = [234, 156, 189, 145, 523]
        
        fig_diag = px.bar(
            x=diagnoses,
            y=diag_counts,
            title="Tanı Dağılımı"
        )
        fig_diag.update_layout(height=400)
        st.plotly_chart(fig_diag, use_container_width=True)

elif st.session_state["dashboard_view"] == "system":
    # ---- SYSTEM DASHBOARD ----
    st.header("⚙️ Sistem Dashboard")
    
    # System health
    col_sys1, col_sys2, col_sys3, col_sys4 = st.columns(4)
    
    with col_sys1:
        st.metric("🟢 Backend", "Aktif", "+0%")
    
    with col_sys2:
        st.metric("🟢 Frontend", "Aktif", "+0%")
    
    with col_sys3:
        st.metric("🟢 Database", "Aktif", "+0%")
    
    with col_sys4:
        st.metric("🟢 AI Models", "Aktif", "+0%")
    
    st.write("")
    
    # System resources
    st.subheader("💾 Sistem Kaynakları")
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.markdown("**🖥️ CPU Kullanımı**")
        cpu_usage = 45
        st.progress(cpu_usage / 100)
        st.caption(f"{cpu_usage}% kullanımda")
        
        st.markdown("**🧠 RAM Kullanımı**")
        ram_usage = 67
        st.progress(ram_usage / 100)
        st.caption(f"{ram_usage}% kullanımda")
    
    with col_res2:
        st.markdown("**💾 Disk Kullanımı**")
        disk_usage = 34
        st.progress(disk_usage / 100)
        st.caption(f"{disk_usage}% kullanımda")
        
        st.markdown("**🌐 Ağ Trafiği**")
        network_usage = 23
        st.progress(network_usage / 100)
        st.caption(f"{network_usage}% kullanımda")
    
    # System logs
    st.subheader("📋 Sistem Logları")
    
    logs = [
        {"time": "12:22:15", "level": "INFO", "message": "Backend başlatıldı"},
        {"time": "12:22:18", "level": "INFO", "message": "Database bağlantısı kuruldu"},
        {"time": "12:22:20", "level": "INFO", "message": "AI modelleri yüklendi"},
        {"time": "12:22:25", "level": "INFO", "message": "Frontend hazır"},
        {"time": "12:22:30", "level": "INFO", "message": "Sistem tamamen aktif"}
    ]
    
    for log in logs:
        col_log1, col_log2, col_log3 = st.columns([1, 1, 4])
        with col_log1:
            st.markdown(f"**{log['time']}**")
        with col_log2:
            if log['level'] == 'INFO':
                st.success(log['level'])
            elif log['level'] == 'WARNING':
                st.warning(log['level'])
            elif log['level'] == 'ERROR':
                st.error(log['level'])
        with col_log3:
            st.markdown(log['message'])
    
    # System actions
    st.subheader("🔧 Sistem İşlemleri")
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("🔄 Yenile", use_container_width=True):
            st.success("✅ Sistem yenilendi!")
            st.rerun()
    
    with col_action2:
        if st.button("📊 Log Temizle", use_container_width=True):
            st.info("📊 Loglar temizleniyor...")
    
    with col_action3:
        if st.button("⚡ Optimize Et", use_container_width=True):
            st.info("⚡ Sistem optimize ediliyor...")

# Footer
st.markdown("---")
st.markdown("**Dashboard** - NeuroPETrix merkezi kontrol paneli")
