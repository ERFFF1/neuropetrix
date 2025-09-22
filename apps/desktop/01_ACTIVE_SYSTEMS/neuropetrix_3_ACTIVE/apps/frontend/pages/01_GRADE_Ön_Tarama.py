import streamlit as st
import requests
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="GRADE Scoring - NeuroPETrix",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize session state
if "grade_analysis_step" not in st.session_state:
    st.session_state["grade_analysis_step"] = "input"
if "demo_mode" not in st.session_state:
    st.session_state["demo_mode"] = True

# Page title and description
st.title("🧪 GRADE Ön Tarama - Literatür Kalite Değerlendirmesi")
st.markdown("**GRADE Metodolojisi** - Araştırma makalelerinin kanıt seviyesi ve kalite analizi")

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
    
    if st.button("🏠 Ana Sayfa", key="grade_nav_home", use_container_width=True):
        st.switch_page("streamlit_app.py")
    
    if st.button("📊 Dashboard", key="grade_nav_dashboard", use_container_width=True):
        st.switch_page("pages/00_Dashboard.py")
    
    if st.button("📝 Report Generation", key="grade_nav_report", use_container_width=True):
        st.switch_page("pages/02_Rapor_Üretimi.py")
    
    st.markdown("---")
    
    # GRADE Analysis Progress
    st.header("📊 GRADE Analiz Durumu")
    
    if st.session_state["grade_analysis_step"] == "input":
        st.info("📝 Veri girişi aşaması")
    elif st.session_state["grade_analysis_step"] == "processing":
        st.info("🔄 AI analizi yapılıyor")
    elif st.session_state["grade_analysis_step"] == "results":
        st.success("✅ Analiz tamamlandı")
    
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
            <h1>🔬 GRADE Metodolojisi</h1>
            <div class="subtitle">Araştırma makalelerinin kanıt seviyesi ve güvenilirlik analizi</div>
        </div>
        <div>
            <span class="badge ok">Evidence Based</span>
            <span class="badge">Quality Assessment</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    st.markdown("### 🎯 Ne İşe Yarar?")
    
    st.info("""
    **GRADE (Grading of Recommendations Assessment, Development and Evaluation):**
    
    • **Literatür taraması** sırasında makale kalitesi
    • **Kanıt seviyesi** değerlendirmesi (A, B, C, D)
    • **Meta-analiz** ve **sistematik derlemeler** için
    • **Klinik karar** desteği ve **rehber** oluşturma
    """)

st.write("")

# ---- GRADE AÇIKLAMASI ----
st.header("📚 GRADE Metodolojisi Nedir?")

col_explain1, col_explain2 = st.columns(2)

with col_explain1:
    st.markdown("""
    <div class="card">
        <h3>🎯 Amaç</h3>
        <p><strong>GRADE sistemi, tıbbi literatürde:</strong></p>
        <ul>
            <li>• <strong>Kanıt kalitesini</strong> standartlaştırır</li>
            <li>• <strong>Öneri gücünü</strong> belirler</li>
            <li>• <strong>Klinik kararları</strong> destekler</li>
            <li>• <strong>Rehber geliştirmeyi</strong> kolaylaştırır</li>
        </ul>
        
        <p><strong>Kullanım Alanları:</strong></p>
        <ul>
            <li>🧪 <strong>Araştırma makaleleri</strong> değerlendirmesi</li>
            <li>📊 <strong>Meta-analiz</strong> kalite kontrolü</li>
            <li>🏥 <strong>Klinik rehber</strong> geliştirme</li>
            <li>📈 <strong>Sistematik derlemeler</strong> için standart</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_explain2:
    st.markdown("""
    <div class="card">
        <h3>📊 Kanıt Seviyeleri</h3>
        <div style="margin-bottom: 1rem;">
            <div style="background: #ecfdf5; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                <strong style="color: #166534;">A (Yüksek)</strong> - Randomize kontrollü çalışmalar, büyük örneklem
            </div>
            <div style="background: #eff6ff; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                <strong style="color: #1e40af;">B (Orta)</strong> - Kohort çalışmaları, vaka-kontrol çalışmaları
            </div>
            <div style="background: #fef3c7; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                <strong style="color: #92400e;">C (Düşük)</strong> - Vaka serileri, uzman görüşleri
            </div>
            <div style="background: #fee2e2; padding: 12px; border-radius: 8px;">
                <strong style="color: #991b1b;">D (Çok Düşük)</strong> - Tek vaka raporları, anekdotlar
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---- GRADE DEĞERLENDİRME FORMU ----
if st.session_state["grade_analysis_step"] == "input":
    st.header("📝 GRADE Değerlendirme Formu")
    
    st.info("""
    **Bu form ile araştırma makalelerinin kalitesini değerlendirin:**
    1. Makale bilgilerini girin
    2. GRADE kriterlerini değerlendirin
    3. AI destekli skorlama alın
    4. Sonuçları analiz edin
    """)
    
    # Form section
    with st.form("grade_evaluation"):
        st.subheader("📄 Makale Bilgileri")
        
        col_article1, col_article2 = st.columns(2)
        
        with col_article1:
            title = st.text_input(
                "Makale Başlığı*",
                value="Effectiveness of PET/CT in lung cancer staging",
                help="Değerlendirilecek makalenin başlığı"
            )
            
            authors = st.text_input(
                "Yazarlar",
                value="Smith J, Johnson A, Williams B",
                help="Makale yazarları"
            )
            
            journal = st.text_input(
                "Dergi",
                value="Journal of Nuclear Medicine",
                help="Yayınlandığı dergi"
            )
        
        with col_article2:
            year = st.number_input(
                "Yayın Yılı*",
                min_value=1990,
                max_value=2025,
                value=2024,
                help="Makalenin yayın yılı"
            )
            
            doi = st.text_input(
                "DOI",
                value="10.1000/example.2024.001",
                help="Makale DOI numarası"
            )
            
            study_type = st.selectbox(
                "Çalışma Türü*",
                ["Randomized Controlled Trial", "Cohort Study", "Case-Control Study", 
                 "Case Series", "Systematic Review", "Meta-analysis", "Expert Opinion"],
                help="Araştırma tasarımı türü"
            )
        
        st.subheader("📋 Özet ve Anahtar Kelimeler")
        
        abstract = st.text_area(
            "Özet*",
            value="This study evaluated the effectiveness of PET/CT in staging lung cancer patients. A total of 150 patients were included in this prospective study...",
            height=150,
            help="Makale özeti (abstract)"
        )
        
        keywords = st.text_input(
            "Anahtar Kelimeler (virgül ile)*",
            value="PET/CT, lung cancer, staging, diagnostic accuracy",
            help="Makale anahtar kelimeleri, virgül ile ayırın"
        )
        
        st.subheader("🔬 GRADE Kriterleri")
        
        col_criteria1, col_criteria2 = st.columns(2)
        
        with col_criteria1:
            st.markdown("**📊 Çalışma Kalitesi:**")
            
            randomization = st.selectbox(
                "Randomizasyon",
                ["Var", "Yok", "Belirsiz"],
                help="Çalışmada randomizasyon kullanıldı mı?"
            )
            
            blinding = st.selectbox(
                "Körleme",
                ["Çift kör", "Tek kör", "Yok", "Belirsiz"],
                help="Çalışmada körleme yapıldı mı?"
            )
            
            sample_size = st.selectbox(
                "Örneklem Büyüklüğü",
                ["Yeterli (>100)", "Orta (50-100)", "Küçük (<50)", "Belirsiz"],
                help="Çalışma örneklem büyüklüğü"
            )
        
        with col_criteria2:
            st.markdown("**📈 Sonuç Kalitesi:**")
            
            follow_up = st.selectbox(
                "Takip Süresi",
                ["Uzun (>2 yıl)", "Orta (1-2 yıl)", "Kısa (<1 yıl)", "Belirsiz"],
                help="Hasta takip süresi"
            )
            
            outcome_measurement = st.selectbox(
                "Sonuç Ölçümü",
                ["Standart", "Validasyonlu", "Subjektif", "Belirsiz"],
                help="Sonuç ölçüm yöntemi"
            )
            
            statistical_analysis = st.selectbox(
                "İstatistiksel Analiz",
                ["Uygun", "Kısmen uygun", "Uygun değil", "Belirsiz"],
                help="İstatistiksel analiz yeterliliği"
            )
        
        st.subheader("🤖 AI Destekli Değerlendirme")
        
        use_ai = st.checkbox(
            "AI destekli GRADE skorlama kullan",
            value=True,
            help="Yapay zeka ile otomatik GRADE skorlama"
        )
        
        ai_confidence = st.slider(
            "AI Güven Eşiği",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.1,
            help="AI değerlendirme güven eşiği"
        )
        
        submitted = st.form_submit_button("🚀 GRADE Değerlendirmesi Başlat", type="primary")
        
        if submitted:
            st.session_state["grade_analysis_step"] = "processing"
            st.session_state["grade_form_data"] = {
                "title": title,
                "authors": authors,
                "journal": journal,
                "year": year,
                "study_type": study_type,
                "abstract": abstract,
                "keywords": keywords,
                "randomization": randomization,
                "blinding": blinding,
                "sample_size": sample_size,
                "follow_up": follow_up,
                "outcome_measurement": outcome_measurement,
                "statistical_analysis": statistical_analysis,
                "use_ai": use_ai,
                "ai_confidence": ai_confidence
            }
            st.rerun()

elif st.session_state["grade_analysis_step"] == "processing":
    st.header("🔄 GRADE Analizi Yapılıyor")
    
    # Progress simulation
    progress = st.progress(0)
    status_text = st.empty()
    
    # Simulate AI processing
    for i in range(101):
        progress.progress(i)
        if i < 30:
            status_text.text("🔍 Makale analizi yapılıyor...")
        elif i < 60:
            status_text.text("📊 GRADE kriterleri değerlendiriliyor...")
        elif i < 90:
            status_text.text("🧮 AI skorlama hesaplanıyor...")
        else:
            status_text.text("✅ GRADE değerlendirmesi tamamlandı!")
    
    # Move to results
    st.session_state["grade_analysis_step"] = "results"
    st.rerun()

elif st.session_state["grade_analysis_step"] == "results":
    st.header("📊 GRADE Değerlendirme Sonuçları")
    
    st.success("🎯 GRADE Değerlendirmesi Tamamlandı!")
    
    # Results display
    col_results1, col_results2 = st.columns([2, 1])
    
    with col_results1:
        st.subheader("📋 Değerlendirme Sonuçları")
        
        # Mock results
        results_data = {
            "Kriter": [
                "Çalışma Tasarımı",
                "Randomizasyon",
                "Körleme",
                "Örneklem Büyüklüğü",
                "Takip Süresi",
                "Sonuç Ölçümü",
                "İstatistiksel Analiz"
            ],
            "Skor": [8, 7, 6, 9, 7, 8, 9],
            "Maksimum": [10, 10, 10, 10, 10, 10, 10],
            "Kalite": ["Yüksek", "Orta", "Orta", "Yüksek", "Orta", "Yüksek", "Yüksek"]
        }
        
        results_df = pd.DataFrame(results_data)
        st.dataframe(results_df, use_container_width=True, hide_index=True)
        
        # Overall GRADE score
        overall_score = sum(results_data["Skor"]) / len(results_data["Skor"])
        st.metric("📊 Genel GRADE Skoru", f"{overall_score:.1f}/10")
        
        if overall_score >= 8:
            st.success("🎉 **Yüksek Kalite** - Bu makale güvenilir kanıt sağlar")
        elif overall_score >= 6:
            st.info("✅ **Orta Kalite** - Bu makale kabul edilebilir kanıt sağlar")
        elif overall_score >= 4:
            st.warning("⚠️ **Düşük Kalite** - Bu makale sınırlı kanıt sağlar")
        else:
            st.error("❌ **Çok Düşük Kalite** - Bu makale güvenilir değil")
    
    with col_results2:
        st.subheader("🎯 AI Önerileri")
        
        st.markdown("**📈 Güçlü Yönler:**")
        st.markdown("• Büyük örneklem")
        st.markdown("• Uygun istatistik")
        st.markdown("• Standart ölçümler")
        
        st.markdown("**⚠️ İyileştirme Alanları:**")
        st.markdown("• Körleme eksikliği")
        st.markdown("• Takip süresi kısa")
        
        st.markdown("**🔬 Klinik Uygulama:**")
        if overall_score >= 7:
            st.success("**Önerilir** - Klinik kararlarda kullanılabilir")
        else:
            st.warning("**Dikkatli kullanım** - Ek kanıtlarla desteklenmeli")
    
    # Visualization
    st.write("")
    st.subheader("📊 Görsel Analiz")
    
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        # Radar chart for criteria scores
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=results_data["Skor"],
            theta=results_data["Kriter"],
            fill='toself',
            name='GRADE Skorları',
            line_color='#2563eb'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=False,
            title="GRADE Kriter Skorları (Radar Chart)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_viz2:
        # Bar chart for quality levels
        quality_counts = pd.Series(results_data["Kalite"]).value_counts()
        
        fig = px.bar(
            x=quality_counts.index,
            y=quality_counts.values,
            title="Kalite Seviyesi Dağılımı",
            labels={'x': 'Kalite Seviyesi', 'y': 'Kriter Sayısı'},
            color=quality_counts.index,
            color_discrete_map={
                'Yüksek': '#10b981',
                'Orta': '#f59e0b',
                'Düşük': '#ef4444'
            }
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Action buttons
    st.write("")
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("🔄 Yeni Analiz", key="grade_new_analysis", use_container_width=True):
            st.session_state["grade_analysis_step"] = "input"
            st.rerun()
    
    with col_action2:
        if st.button("📝 Rapor Oluştur", key="grade_create_report", use_container_width=True):
            st.switch_page("pages/02_Rapor_Üretimi.py")
    
    with col_action3:
        if st.button("📊 Dashboard'a Dön", key="grade_back_dashboard", use_container_width=True):
            st.switch_page("pages/00_Dashboard.py")

st.write("")

# ---- LİTERATÜR TARAMA ÖNERİLERİ ----
st.header("🔍 Literatür Tarama Önerileri")

col_lit1, col_lit2 = st.columns(2)

with col_lit1:
    st.markdown("""
    <div class="card">
        <h3>📚 GRADE Sonrası Adımlar</h3>
        <p><strong>1. 📊 Sonuç Analizi:</strong></p>
        <ul>
            <li>• GRADE skorunu değerlendirin</li>
            <li>• Güçlü ve zayıf yönleri belirleyin</li>
            <li>• Klinik uygulanabilirliği değerlendirin</li>
        </ul>
        
        <p><strong>2. 🔍 Ek Literatür:</strong></p>
        <ul>
            <li>• Benzer çalışmaları bulun</li>
            <li>• Meta-analiz yapın</li>
            <li>• Çelişkili bulguları analiz edin</li>
        </ul>
        
        <p><strong>3. 📝 Rapor Entegrasyonu:</strong></p>
        <ul>
            <li>• GRADE sonuçlarını rapora ekleyin</li>
            <li>• Kanıt seviyesini belirtin</li>
            <li>• Klinik önerileri güncelleyin</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_lit2:
    st.markdown("""
    <div class="card">
        <h3>🎯 GRADE Kullanım Alanları</h3>
        <p><strong>🏥 Klinik Uygulama:</strong></p>
        <ul>
            <li>• Tedavi kararları</li>
            <li>• Tanı algoritmaları</li>
            <li>• Takip protokolleri</li>
        </ul>
        
        <p><strong>📚 Akademik Çalışma:</strong></p>
        <ul>
            <li>• Sistematik derlemeler</li>
            <li>• Meta-analizler</li>
            <li>• Klinik rehberler</li>
        </ul>
        
        <p><strong>🔬 Araştırma:</strong></p>
        <ul>
            <li>• Çalışma tasarımı</li>
            <li>• Protokol geliştirme</li>
            <li>• Kalite kontrol</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("**GRADE Scoring v2.0** - Literatür kalite değerlendirmesi ve kanıt seviyesi analizi")
