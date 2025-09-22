import streamlit as st
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="SUV Trend - NeuroPETrix",
    page_icon="📈",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Page title and description
st.title("📈 SUV Trend Analizi - Zaman İçinde SUV Değer Takibi")
st.markdown("**SUVmax • SUVmean • SUVpeak • Trend Analizi • Klinik Karar Desteği**")

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

if st.button("📊 Dashboard", use_container_width=True):
    st.switch_page("pages/00_Dashboard.py")

if st.button("🤖 AI Analysis", use_container_width=True):
    st.switch_page("pages/05_AI_Analysis.py")

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
if "suv_data" not in st.session_state:
    st.session_state["suv_data"] = []
if "selected_patient" not in st.session_state:
    st.session_state["selected_patient"] = None
if "trend_analysis" not in st.session_state:
    st.session_state["trend_analysis"] = None

# ---- HERO SECTION ----
col_hero1, col_hero2 = st.columns([2, 1])

with col_hero1:
    st.markdown("""
    <div class="hero">
        <div>
            <h1>📈 SUV Trend Analizi</h1>
            <div class="subtitle">Zaman içinde SUV değerlerinin takibi ve klinik anlam analizi</div>
        </div>
        <div>
            <span class="badge ok">Real-time</span>
            <span class="badge">Trend Analysis</span>
            <span class="badge">Clinical Decision</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    st.markdown("### 🎯 Hızlı İşlemler")
    
    # Quick actions
    if st.button("📊 Trend Analizi", type="primary", use_container_width=True):
        st.session_state["trend_analysis"] = "auto"
        st.rerun()
    
    if st.button("📁 Veri Yükle", type="secondary", use_container_width=True):
        st.info("📁 Veri yükleme özelliği yakında eklenecek")

st.write("")

# ---- PATIENT SELECTION ----
st.header("👤 Hasta Seçimi ve SUV Veri Girişi")

col_patient1, col_patient2 = st.columns(2)

with col_patient1:
    st.subheader("👤 Hasta Bilgileri")
    
    # Patient selection
    patient_id = st.text_input(
        "Hasta ID",
        value="P001",
        help="Hasta kimlik numarası"
    )
    
    patient_name = st.text_input(
        "Hasta Adı",
        value="Test Hasta",
        help="Hasta adı ve soyadı"
    )
    
    diagnosis = st.selectbox(
        "Tanı",
        ["Akciğer Kanseri", "Lenfoma", "Meme Kanseri", "Kolon Kanseri", "Prostat Kanseri"],
        index=0,
        help="Hasta tanısı"
    )
    
    study_type = st.selectbox(
        "Çalışma Türü",
        ["FDG PET/CT", "PSMA PET/CT", "DOTATATE PET/CT", "FAPI PET/CT"],
        index=0,
        help="PET/CT çalışma türü"
    )

with col_patient2:
    st.subheader("📅 Çalışma Parametreleri")
    
    # Study parameters
    study_date = st.date_input(
        "Çalışma Tarihi",
        value=datetime.now(),
        help="PET/CT çalışma tarihi"
    )
    
    injected_dose = st.number_input(
        "Enjeksiyon Dozu (MBq)",
        value=185.0,
        step=1.0,
        help="Radyofarmasötik dozu"
    )
    
    uptake_time = st.number_input(
        "Uptake Süresi (dakika)",
        value=60,
        step=5,
        help="Enjeksiyon-scan arası süre"
    )

st.write("")

# ---- SUV DATA ENTRY ----
st.header("🔬 SUV Veri Girişi")

col_suv1, col_suv2 = st.columns(2)

with col_suv1:
    st.subheader("📊 SUV Değerleri")
    
    # SUV measurements
    suvmax = st.number_input(
        "SUVmax",
        value=8.5,
        step=0.1,
        help="Maksimum SUV değeri"
    )
    
    suvmean = st.number_input(
        "SUVmean",
        value=6.2,
        step=0.1,
        help="Ortalama SUV değeri"
    )
    
    suvpeak = st.number_input(
        "SUVpeak",
        value=7.8,
        step=0.1,
        help="Peak SUV değeri"
    )
    
    # Lesion information
    lesion_size = st.number_input(
        "Lezyon Boyutu (cm)",
        value=3.2,
        step=0.1,
        help="Lezyon çapı"
    )
    
    lesion_location = st.text_input(
        "Lezyon Lokalizasyonu",
        value="Sağ üst lob",
        help="Lezyon anatomik yeri"
    )

with col_suv2:
    st.subheader("📋 Ek Parametreler")
    
    # Additional parameters
    background_suv = st.number_input(
        "Background SUV (Karaciğer)",
        value=2.1,
        step=0.1,
        help="Referans background SUV"
    )
    
    tbr_ratio = st.number_input(
        "TBR (Tumor/Background)",
        value=suvmax/2.1 if suvmax else 0,
        step=0.1,
        help="Tümör/Background oranı"
    )
    
    # Quality indicators
    image_quality = st.selectbox(
        "Görüntü Kalitesi",
        ["Mükemmel", "İyi", "Orta", "Düşük"],
        index=0,
        help="PET görüntü kalitesi"
    )
    
    motion_artifact = st.selectbox(
        "Hareket Artefaktı",
        ["Yok", "Minimal", "Orta", "Belirgin"],
        index=0,
        help="Hasta hareketi artefaktı"
    )

# Add data button
if st.button("➕ SUV Verisi Ekle", type="primary", use_container_width=True):
    new_data = {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "diagnosis": diagnosis,
        "study_type": study_type,
        "study_date": study_date.strftime("%Y-%m-%d"),
        "suvmax": suvmax,
        "suvmean": suvmean,
        "suvpeak": suvpeak,
        "lesion_size": lesion_size,
        "lesion_location": lesion_location,
        "background_suv": background_suv,
        "tbr_ratio": tbr_ratio,
        "image_quality": image_quality,
        "motion_artifact": motion_artifact,
        "timestamp": datetime.now().isoformat()
    }
    
    st.session_state["suv_data"].append(new_data)
    st.success(f"✅ {patient_name} için SUV verisi eklendi!")
    st.rerun()

st.write("")

# ---- TREND ANALYSIS ----
st.header("📈 SUV Trend Analizi")

if st.session_state["suv_data"]:
    # Convert to DataFrame for analysis
    df = pd.DataFrame(st.session_state["suv_data"])
    df['study_date'] = pd.to_datetime(df['study_date'])
    df = df.sort_values('study_date')
    
    # Display data table
    st.subheader("📊 Mevcut SUV Verileri")
    st.dataframe(df[['patient_name', 'study_date', 'suvmax', 'suvmean', 'lesion_size', 'image_quality']], use_container_width=True)
    
    # Trend analysis
    if len(df) > 1:
        st.subheader("📈 SUV Trend Grafikleri")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # SUVmax trend
            fig_suvmax = px.line(
                df, 
                x='study_date', 
                y='suvmax',
                title='SUVmax Trend',
                labels={'suvmax': 'SUVmax', 'study_date': 'Tarih'},
                markers=True
            )
            fig_suvmax.update_layout(height=400)
            st.plotly_chart(fig_suvmax, use_container_width=True)
        
        with col_chart2:
            # Lesion size trend
            fig_size = px.line(
                df, 
                x='study_date', 
                y='lesion_size',
                title='Lezyon Boyutu Trend',
                labels={'lesion_size': 'Boyut (cm)', 'study_date': 'Tarih'},
                markers=True
            )
            fig_size.update_layout(height=400)
            st.plotly_chart(fig_size, use_container_width=True)
        
        # Combined analysis
        st.subheader("🔍 Trend Analizi Sonuçları")
        
        col_analysis1, col_analysis2, col_analysis3 = st.columns(3)
        
        with col_analysis1:
            # SUVmax change
            suvmax_change = df['suvmax'].iloc[-1] - df['suvmax'].iloc[0]
            suvmax_pct = (suvmax_change / df['suvmax'].iloc[0]) * 100 if df['suvmax'].iloc[0] != 0 else 0
            
            st.metric("📈 SUVmax Değişimi", f"{suvmax_change:+.1f}")
            st.metric("📊 Yüzde Değişim", f"{suvmax_pct:+.1f}%")
            
            if suvmax_pct > 20:
                st.success("🚀 **Progresyon** - Belirgin artış")
            elif suvmax_pct < -20:
                st.success("📉 **Yanıt** - Belirgin azalma")
            else:
                st.info("➡️ **Stabil** - Minimal değişim")
        
        with col_analysis2:
            # Size change
            size_change = df['lesion_size'].iloc[-1] - df['lesion_size'].iloc[0]
            size_pct = (size_change / df['lesion_size'].iloc[0]) * 100 if df['lesion_size'].iloc[0] != 0 else 0
            
            st.metric("📏 Boyut Değişimi", f"{size_change:+.1f} cm")
            st.metric("📊 Yüzde Değişim", f"{size_pct:+.1f}%")
            
            if size_pct > 15:
                st.warning("⚠️ **Büyüme** - Lezyon büyüyor")
            elif size_pct < -15:
                st.success("✅ **Küçülme** - Lezyon küçülüyor")
            else:
                st.info("➡️ **Stabil** - Boyut değişimi minimal")
        
        with col_analysis3:
            # Quality assessment
            avg_quality = df['image_quality'].value_counts().index[0]
            quality_score = {"Mükemmel": 4, "İyi": 3, "Orta": 2, "Düşük": 1}[avg_quality]
            
            st.metric("🎯 Ortalama Kalite", avg_quality)
            st.metric("📊 Kalite Skoru", f"{quality_score}/4")
            
            if quality_score >= 3:
                st.success("✅ **Yüksek Kalite** - Güvenilir veri")
            elif quality_score >= 2:
                st.warning("⚠️ **Orta Kalite** - Dikkatli değerlendir")
            else:
                st.error("❌ **Düşük Kalite** - Veri güvenilir değil")
        
        # Clinical interpretation
        st.subheader("🏥 Klinik Yorum")
        
        col_clinical1, col_clinical2 = st.columns(2)
        
        with col_clinical1:
            st.markdown("**📋 Trend Yorumu:**")
            
            if suvmax_pct > 20 and size_pct > 15:
                st.error("🚨 **PROGRESYON** - Hastalık ilerliyor, tedavi değişikliği gerekebilir")
            elif suvmax_pct < -20 and size_pct < -15:
                st.success("✅ **YANIT** - Tedavi etkili, devam edilmeli")
            elif abs(suvmax_pct) < 20 and abs(size_pct) < 15:
                st.info("➡️ **STABİL** - Hastalık stabil, mevcut tedavi devam edilmeli")
            else:
                st.warning("⚠️ **KARMAŞIK** - Karışık bulgular, detaylı değerlendirme gerekli")
        
        with col_clinical2:
            st.markdown("**🎯 Öneriler:**")
            
            if suvmax_pct > 20:
                st.markdown("• Tedavi değişikliği değerlendirilmeli")
                st.markdown("• Ek görüntüleme gerekebilir")
                st.markdown("• Multidisipliner konsültasyon")
            elif suvmax_pct < -20:
                st.markdown("• Mevcut tedavi devam edilmeli")
                st.markdown("• Takip aralığı kısaltılabilir")
                st.markdown("• Yanıt kriterleri değerlendirilmeli")
            else:
                st.markdown("• Mevcut takip protokolü devam")
                st.markdown("• 3-6 ay sonra tekrar değerlendirme")
                st.markdown("• Klinik bulgularla korelasyon")
    
    else:
        st.info("📊 Trend analizi için en az 2 ölçüm gerekli")
        
else:
    st.info("📊 SUV verisi ekleyerek trend analizi yapabilirsiniz")

st.write("")

# ---- ADVANCED ANALYTICS ----
st.header("🔬 Gelişmiş Analitik")

if st.session_state["suv_data"] and len(st.session_state["suv_data"]) > 1:
    df = pd.DataFrame(st.session_state["suv_data"])
    df['study_date'] = pd.to_datetime(df['study_date'])
    
    col_adv1, col_adv2 = st.columns(2)
    
    with col_adv1:
        st.subheader("📊 İstatistiksel Analiz")
        
        # Statistical summary
        stats_data = {
            "Metrik": ["SUVmax", "SUVmean", "SUVpeak", "Lezyon Boyutu"],
            "Ortalama": [
                df['suvmax'].mean(),
                df['suvmean'].mean(),
                df['suvpeak'].mean(),
                df['lesion_size'].mean()
            ],
            "Standart Sapma": [
                df['suvmax'].std(),
                df['suvmean'].std(),
                df['suvpeak'].std(),
                df['lesion_size'].std()
            ],
            "Min": [
                df['suvmax'].min(),
                df['suvmean'].min(),
                df['suvpeak'].min(),
                df['lesion_size'].min()
            ],
            "Max": [
                df['suvmax'].max(),
                df['suvmean'].max(),
                df['suvpeak'].max(),
                df['lesion_size'].max()
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)
    
    with col_adv2:
        st.subheader("📈 Korelasyon Analizi")
        
        # Correlation analysis
        if len(df) >= 3:
            # Calculate correlations
            suv_corr = df['suvmax'].corr(df['lesion_size'])
            time_corr = df['study_date'].dt.dayofyear.corr(df['suvmax'])
            
            st.metric("🔗 SUVmax vs Boyut", f"{suv_corr:.3f}")
            st.metric("⏰ Zaman vs SUVmax", f"{time_corr:.3f}")
            
            # Correlation interpretation
            if abs(suv_corr) > 0.7:
                st.success("✅ **Güçlü Korelasyon** - SUV ve boyut ilişkili")
            elif abs(suv_corr) > 0.3:
                st.info("➡️ **Orta Korelasyon** - Kısmen ilişkili")
            else:
                st.warning("⚠️ **Zayıf Korelasyon** - İlişki belirsiz")
            
            # Scatter plot
            fig_scatter = px.scatter(
                df, 
                x='lesion_size', 
                y='suvmax',
                title='SUVmax vs Lezyon Boyutu',
                labels={'lesion_size': 'Boyut (cm)', 'suvmax': 'SUVmax'}
            )
            fig_scatter.update_layout(height=300)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("📊 Korelasyon analizi için en az 3 ölçüm gerekli")

# ---- EXPORT AND REPORTING ----
st.header("📤 Dışa Aktarma ve Raporlama")

col_export1, col_export2, col_export3 = st.columns(3)

with col_export1:
    st.subheader("📊 Veri Dışa Aktarma")
    
    export_format = st.selectbox(
        "Format",
        ["Excel (.xlsx)", "CSV", "JSON", "PDF Report"],
        index=0
    )
    
    if st.button("📥 İndir", use_container_width=True):
        st.success(f"📥 {export_format} formatında indiriliyor...")

with col_export2:
    st.subheader("📋 Rapor Oluşturma")
    
    report_type = st.selectbox(
        "Rapor Türü",
        ["Trend Özeti", "Detaylı Analiz", "Klinik Özet", "Tam Rapor"],
        index=0
    )
    
    if st.button("📝 Rapor Oluştur", use_container_width=True):
        st.success("📝 Rapor oluşturuluyor...")

with col_export3:
    st.subheader("🏥 Klinik Entegrasyon")
    
    if st.button("🏥 HBYS'e Gönder", use_container_width=True):
        st.info("🏥 HBYS entegrasyonu yakında eklenecek")
    
    if st.button("📧 E-posta Gönder", use_container_width=True):
        st.info("📧 E-posta özelliği yakında eklenecek")

# Footer
st.markdown("---")
st.markdown("**SUV Trend Analizi** - Zaman içinde SUV değer takibi ve klinik karar desteği")
