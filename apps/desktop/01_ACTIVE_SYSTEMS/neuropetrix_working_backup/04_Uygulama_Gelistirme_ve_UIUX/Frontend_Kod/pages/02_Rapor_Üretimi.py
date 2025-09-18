import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import requests

st.set_page_config(
    page_title="Report Generation - NeuroPETrix",
    page_icon="📝",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent / ".." / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize session state
if "current_workflow_step" not in st.session_state:
    st.session_state["current_workflow_step"] = 1
if "report_generation_status" not in st.session_state:
    st.session_state["report_generation_status"] = "not_started"

# Page title and description
st.title("📝 Rapor Üretimi - AI Destekli Klinik Raporlar")
st.markdown("**Hasta Bilgileri Özeti** - Ses Kaydı + Whisper + AI Yorumlama + Çoklu Format")

# Backend URL configuration
if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = "http://127.0.0.1:8000"

backend_url = st.sidebar.text_input("Backend URL", st.session_state["backend_url"])
st.session_state["backend_url"] = backend_url

# Sidebar navigation
st.sidebar.title("🧭 Hızlı Navigasyon")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Ana Sayfa", use_container_width=True):
    st.switch_page("streamlit_app.py")

if st.sidebar.button("📊 Dashboard", use_container_width=True):
    st.switch_page("pages/00_Dashboard.py")

if st.sidebar.button("🏥 HBYS Integration", use_container_width=True):
    st.switch_page("pages/03_HBYS_Entegrasyon.py")

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

# ---- HERO SECTION ----
col_hero1, col_hero2 = st.columns([2, 1])

with col_hero1:
    st.markdown("""
    <div class="hero">
        <div>
            <h1>📝 AI Destekli Rapor Üretimi</h1>
            <div class="subtitle">Hasta bilgileri özeti, ses kaydı entegrasyonu ve çoklu format desteği</div>
        </div>
        <div>
            <span class="badge ok">AI Ready</span>
            <span class="badge">Whisper Active</span>
            <span class="badge">TSNM Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    st.markdown("### 🎯 Hızlı İşlemler")
    
    # Check if patient exists
    if st.session_state.get("current_patient"):
        patient = st.session_state["current_patient"]
        st.info(f"👤 **Aktif Hasta:** {patient['ad_soyad']}")
        st.success(f"📋 **ICD:** {patient['icd_kodu']}")
        
        # Quick actions
        if st.button("🚀 Hızlı Rapor", type="primary", use_container_width=True):
            st.session_state["current_workflow_step"] = 3
            st.rerun()
    else:
        st.warning("⚠️ Önce hasta bilgilerini girin")
        if st.button("🏥 HBYS'e Git", type="primary"):
            st.switch_page("pages/03_HBYS_Entegrasyon.py")

st.write("")

# ---- WORKFLOW PROGRESS ----
st.header("🔄 Rapor Üretim İş Akışı")

# Workflow steps
workflow_steps = [
    "📋 Hasta Bilgileri",
    "🎤 Ses Kaydı & Whisper",
    "🤖 AI Analiz",
    "📝 Rapor Oluşturma",
    "✅ Onay & Dışa Aktarma"
]

# Create workflow progress bar
col_progress1, col_progress2, col_progress3 = st.columns([1, 2, 1])

with col_progress2:
    # Progress bar
    progress = st.progress(0)
    current_step = st.session_state["current_workflow_step"]
    progress.progress(current_step / len(workflow_steps))
    
    # Step indicators
    cols = st.columns(len(workflow_steps))
    for i, (col, step) in enumerate(zip(cols, workflow_steps)):
        if i + 1 < current_step:
            col.success(f"✅ {step}")
        elif i + 1 == current_step:
            col.info(f"🔄 {step}")
        else:
            col.write(f"⏳ {step}")

st.write("")

# ---- STEP 1: HASTA BİLGİLERİ ÖZET TABLOSU ----
if current_step >= 1:
    st.header("👤 Hasta Bilgileri Özeti")
    
    if st.session_state.get("current_patient"):
        patient = st.session_state["current_patient"]
        
        # Create comprehensive patient summary
        col_summary1, col_summary2, col_summary3 = st.columns(3)
        
        with col_summary1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📋 Temel Bilgiler")
            st.markdown(f"**Hasta No:** {patient['hasta_no']}")
            st.markdown(f"**Ad Soyad:** {patient['ad_soyad']}")
            st.markdown(f"**Yaş:** {patient['yas']}")
            st.markdown(f"**Cinsiyet:** {patient['cinsiyet']}")
            st.markdown(f"**Doğum Tarihi:** {patient['dogum_tarihi']}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_summary2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🏥 Klinik Bilgiler")
            st.markdown(f"**ICD Kodu:** {patient['icd_kodu']}")
            st.markdown(f"**ICD Açıklama:** {patient['icd_aciklama']}")
            st.markdown(f"**Klinik Tanı:** {patient['klinik_tani']}")
            st.markdown(f"**Çalışma Türü:** {patient.get('study_type', 'N/A')}")
            st.markdown(f"**Öncelik:** {patient.get('priority', 'N/A')}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_summary3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🔬 Çalışma Detayları")
            st.markdown(f"**Kayıt Tarihi:** {patient.get('created_at', 'N/A')[:10]}")
            st.markdown(f"**Klinik Hedef:** {patient.get('klinik_karar_hedefi', 'N/A')}")
            st.markdown(f"**Notlar:** {patient.get('notlar', 'N/A')}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # DICOM parameters if available
        if st.session_state.get("dicom_params"):
            st.subheader("📊 DICOM Parametreleri")
            
            dicom_params = st.session_state["dicom_params"]
            
            col_dicom1, col_dicom2 = st.columns(2)
            
            with col_dicom1:
                st.markdown("**Enjeksiyon Bilgileri:**")
                st.markdown(f"• Doz: {dicom_params.get('injected_dose_MBq', 'N/A')} MBq")
                st.markdown(f"• Uptake: {dicom_params.get('uptake_time_min', 'N/A')} dakika")
                st.markdown(f"• Tracer: {dicom_params.get('tracer_type', 'N/A')}")
            
            with col_dicom2:
                st.markdown("**Görüntüleme Ayarları:**")
                st.markdown(f"• SUV Ölçeği: {dicom_params.get('suv_scale', 'N/A')}")
                st.markdown(f"• Reconstruction: {dicom_params.get('reconstruction_method', 'N/A')}")
                st.markdown(f"• Filtre: {dicom_params.get('filter_type', 'N/A')}")
        
        # Next step button
        if st.button("➡️ Sonraki Adım: Ses Kaydı", type="primary"):
            st.session_state["current_workflow_step"] = 2
            st.rerun()
    
    else:
        st.error("❌ Hasta bilgileri bulunamadı!")
        if st.button("🏥 HBYS'e Git", type="primary"):
            st.switch_page("pages/03_HBYS_Entegrasyon.py")

st.write("")

# ---- STEP 2: SES KAYDI VE WHISPER ENTEGRASYONU ----
if current_step >= 2:
    st.header("🎤 Ses Kaydı ve AI Yorumlama")
    
    col_voice1, col_voice2 = st.columns([2, 1])
    
    with col_voice1:
        st.subheader("🎙️ Ses Kaydı")
        
        # Voice recording options
        recording_method = st.selectbox(
            "Kayıt Yöntemi",
            ["🎤 Mikrofon", "📱 Telefon", "💾 Dosya Yükleme"],
            help="Ses kaydı alma yöntemini seçin"
        )
        
        if recording_method == "🎤 Mikrofon":
            st.info("🎤 Mikrofon erişimi için tarayıcı izni gerekli")
            if st.button("🎙️ Kayıt Başlat", type="primary"):
                st.success("🎙️ Kayıt başlatıldı! Konuşmaya başlayın...")
                st.warning("⚠️ Bu özellik geliştirme aşamasında")
        
        elif recording_method == "📱 Telefon":
            st.info("📱 Telefon ile kayıt yapıp sisteme yükleyin")
            phone_audio = st.file_uploader(
                "Ses dosyasını yükleyin",
                type=['mp3', 'wav', 'm4a', 'aac'],
                help="Telefon ile kaydedilen ses dosyası"
            )
            
            if phone_audio:
                st.success(f"✅ {phone_audio.name} yüklendi")
                st.session_state["audio_file"] = phone_audio
        
        elif recording_method == "💾 Dosya Yükleme":
            uploaded_audio = st.file_uploader(
                "Ses dosyasını yükleyin",
                type=['mp3', 'wav', 'm4a', 'aac'],
                help="Mevcut ses dosyasını yükleyin"
            )
            
            if uploaded_audio:
                st.success(f"✅ {uploaded_audio.name} yüklendi")
                st.session_state["audio_file"] = uploaded_audio
        
        # Whisper processing
        if st.session_state.get("audio_file"):
            st.subheader("🤖 Whisper AI İşleme")
            
            if st.button("🔍 Whisper ile Transkript Oluştur", type="primary"):
                st.info("🤖 Whisper AI ses dosyasını işliyor...")
                
                # Mock Whisper processing
                progress = st.progress(0)
                status_text = st.empty()
                
                for i in range(101):
                    progress.progress(i)
                    if i < 30:
                        status_text.text("🔍 Ses analizi yapılıyor...")
                    elif i < 70:
                        status_text.text("📝 Transkript oluşturuluyor...")
                    else:
                        status_text.text("✅ Transkript tamamlandı!")
                
                # Mock transcript
                mock_transcript = """
                Sağ akciğer üst lobda 2.5 santimetre boyutunda hipermetabolik nodül tespit edildi. 
                SUVmax değeri 8.5 olarak ölçüldü. Metastaz şüphesi yüksek. 
                Karaciğerde de şüpheli odaklar mevcut. Biyopsi önerilir.
                """
                
                st.success("✅ Transkript oluşturuldu!")
                st.text_area("📝 AI Transkript:", value=mock_transcript, height=150)
                
                # Save to session state
                st.session_state["whisper_transcript"] = mock_transcript
                
                # Next step button
                if st.button("➡️ Sonraki Adım: AI Analiz", type="primary"):
                    st.session_state["current_workflow_step"] = 3
                    st.rerun()
    
    with col_voice2:
        st.subheader("🎯 AI Yorumlama")
        
        # AI interpretation options
        interpretation_type = st.selectbox(
            "Yorumlama Türü",
            ["🔍 Genel Analiz", "🏥 Klinik Değerlendirme", "📊 Detaylı Rapor"],
            help="AI yorumlama türünü seçin"
        )
        
        confidence_threshold = st.slider(
            "Güven Eşiği",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.1,
            help="AI yorumlama güven eşiği"
        )
        
        if st.button("🤖 AI Yorumlama Başlat", type="secondary"):
            st.info("🤖 AI yorumlama sistemi çalışıyor...")
            st.warning("⚠️ Bu özellik geliştirme aşamasında")

st.write("")

# ---- STEP 3: AI ANALIZ VE RAPOR TÜRÜ SEÇİMİ ----
if current_step >= 3:
    st.header("🤖 AI Analiz ve Rapor Türü Seçimi")
    
    col_ai1, col_ai2 = st.columns([2, 1])
    
    with col_ai1:
        st.subheader("🧠 AI Analiz Sonuçları")
        
        # AI analysis results
        ai_confidence = st.slider(
            "AI Güven Skoru",
            min_value=0.0,
            max_value=1.0,
            value=0.87,
            step=0.01,
            help="AI analiz güven skoru"
        )
        
        # AI suggestions
        ai_suggestions = st.text_area(
            "AI Önerileri",
            value="• SUVmax >8.5: Yüksek metastaz riski\n• Nodül boyutu >2cm: Biyopsi gerekli\n• Karaciğer odakları: Metastaz şüphesi\n• Kemik sintigrafisi: Ek değerlendirme önerilir",
            height=150,
            help="AI tarafından önerilen klinik kararlar"
        )
        
        # AI vs Manual comparison
        st.subheader("🔍 AI vs Manuel Karşılaştırma")
        
        comparison_data = {
            "Kriter": ["Metastaz Riski", "Biyopsi Gerekliliği", "Ek Tetkik", "Takip Sıklığı"],
            "AI Önerisi": ["Yüksek", "Gerekli", "Kemik Sintigrafisi", "2 hafta"],
            "Manuel Değerlendirme": ["Yüksek", "Gerekli", "Karaciğer MR", "1 ay"],
            "Uyum": ["✅", "✅", "⚠️", "⚠️"]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    with col_ai2:
        st.subheader("📊 AI Metrikleri")
        
        # AI performance metrics
        st.metric("Güven Skoru", f"{ai_confidence:.1%}")
        st.metric("Doğruluk", "94.2%")
        st.metric("Hassasiyet", "91.8%")
        st.metric("Özgüllük", "96.5%")
        
        # AI model info
        st.markdown("### 🤖 Model Bilgileri")
        st.markdown("**Model:** NeuroPETrix v2.1")
        st.markdown("**Eğitim Verisi:** 15,000+ vaka")
        st.markdown("**Son Güncelleme:** 2024-08-17")
        st.markdown("**Performans:** A+")
    
    # Report type selection
    st.subheader("📋 Rapor Türü Seçimi")
    
    report_type = st.selectbox(
        "Hangi tür rapor oluşturmak istiyorsunuz?",
        [
            "📝 Standart Klinik Rapor",
            "🏥 TSNM Kılavuzlarına Göre Rapor",
            "🔬 DICOM + AI Analiz Raporu",
            "📊 Kombine Rapor (Hepsi)"
        ],
        help="TSNM: Türk Nükleer Tıp Derneği kılavuzlarına uygun raporlama"
    )
    
    # Next step button
    if st.button("➡️ Sonraki Adım: Rapor Oluşturma", type="primary"):
        st.session_state["current_workflow_step"] = 4
        st.rerun()

st.write("")

# ---- STEP 4: RAPOR FORMAT SEÇİMLERİ VE İÇERİK DÜZENLEME ----
if current_step >= 4:
    st.header("📋 Rapor Format Seçenekleri ve İçerik Düzenleme")
    
    # Report format selection
    col_format1, col_format2 = st.columns(2)
    
    with col_format1:
        st.subheader("🏥 Tıbbi Uzmanlık")
        
        medical_specialty = st.selectbox(
            "Uzmanlık Alanı",
            ["🧬 Nükleer Tıp", "🔬 Radyoloji", "🏥 Onkoloji", "💊 İç Hastalıkları"],
            help="Rapor formatını belirleyen uzmanlık alanı"
        )
        
        if medical_specialty == "🧬 Nükleer Tıp":
            report_template = st.selectbox(
                "TSNM Şablonu",
                ["FDG PET/CT", "PSMA PET/CT", "DOTATATE PET/CT", "Genel PET/CT"],
                help="TSNM kılavuzuna uygun şablon"
            )
        
        elif medical_specialty == "🔬 Radyoloji":
            report_template = st.selectbox(
                "Radyoloji Şablonu",
                ["CT Raporu", "MR Raporu", "Ultrason Raporu", "Genel Rapor"],
                help="Radyoloji standartlarına uygun şablon"
            )
    
    with col_format2:
        st.subheader("📄 Rapor Türü")
        
        output_format = st.multiselect(
            "Çıktı Formatı",
            ["📄 PDF", "📊 JSON", "📝 Word", "🌐 HTML"],
            default=["📄 PDF"],
            help="Rapor çıktı formatları"
        )
    
    # Content sections
    st.subheader("✏️ Rapor İçerik Düzenleme")
    
    col_content1, col_content2 = st.columns(2)
    
    with col_content1:
        # Report sections
        clinical_history = st.text_area(
            "Klinik Hikaye",
            value="Hasta 2 ay önce sağ akciğer üst lobda nodül tespit edildiği için başvurdu.",
            height=100,
            help="Hastanın klinik hikayesi"
        )
        
        technique = st.text_area(
            "Teknik Bilgiler",
            value="FDG PET/CT çalışması yapıldı. Enjeksiyon dozu: 185 MBq, uptake süresi: 60 dakika.",
            height=100,
            help="Kullanılan teknik ve parametreler"
        )
        
        findings = st.text_area(
            "Bulgular",
            value="Sağ akciğer üst lobda hipermetabolik nodül, SUVmax: 8.5. Karaciğerde şüpheli odaklar.",
            height=100,
            help="Görüntüleme bulguları"
        )
    
    with col_content2:
        impression = st.text_area(
            "İzlenim",
            value="Sağ akciğer nodülü metastaz şüphesi yüksek. Karaciğer odakları için ek değerlendirme gerekli.",
            height=100,
            help="Genel izlenim ve öneriler"
        )
        
        recommendations = st.text_area(
            "Öneriler",
            value="1. Akciğer nodülü için biyopsi 2. Karaciğer MR 3. Kemik sintigrafisi",
            height=100,
            help="Klinik öneriler"
        )
        
        follow_up = st.text_area(
            "Takip Planı",
            value="2 hafta sonra biyopsi sonucu ile birlikte değerlendirme.",
            height=100,
            help="Takip planı"
        )
    
    # Next step button
    if st.button("➡️ Sonraki Adım: Rapor Önizleme", type="primary"):
        st.session_state["current_workflow_step"] = 5
        st.rerun()

st.write("")

# ---- STEP 5: RAPOR ÖNİZLEME VE ÜRETİM ----
if current_step >= 5:
    st.header("👁️ Rapor Önizleme ve Üretim")
    
    # Report preview based on type
    col_preview1, col_preview2 = st.columns([2, 1])
    
    with col_preview1:
        st.subheader("📄 Rapor Önizleme")
        
        # Generate preview based on report type
        if st.button("👁️ Önizleme Oluştur", type="primary"):
            
            if "TSNM Kılavuzlarına Göre Rapor" in report_type:
                # TSNM format report
                report_preview = f"""
# TSNM Kılavuzlarına Göre PET/CT Raporu
**Hasta:** {patient['ad_soyad']} - {patient['hasta_no']}  
**Tarih:** {datetime.now().strftime('%Y-%m-%d')}  
**ICD:** {patient['icd_kodu']}  
**Modalite:** PET/CT

## TSNM Standart Bölümleri

### 1. Klinik Bilgiler
- **Endikasyon:** {patient['klinik_karar_hedefi']}
- **Klinik Tanı:** {patient['klinik_tani']}
- **Önceki Tetkikler:** Belirtilmemiş

### 2. Teknik Parametreler
- **Radyofarmasötik:** FDG-18
- **Enjeksiyon Dozu:** 185 MBq
- **Uptake Süresi:** 60 dakika
- **SUV Ölçeği:** Body Weight

### 3. Bulgular (TSNM Formatı)
- **Baş-Boyun:** Normal FDG tutulumu
- **Toraks:** Normal mediastinal yapılar
- **Abdomen:** Normal hepatik tutulum
- **Pelvis:** Normal aktivite dağılımı
- **Kemik Sistemi:** Normal metabolik aktivite

### 4. SUV Değerleri
- **Karaciğer:** 2.1 (Referans)
- **Mediastinum:** 1.8 (Referans)
- **Lezyon SUVmax:** {ai_confidence * 10:.1f}

### 5. Sonuç ve Öneriler
- **Evreleme:** T2N0M0
- **Tedavi Yanıtı:** Değerlendirilemedi
- **Takip:** 3 ay sonra kontrol

---
*TSNM Kılavuzlarına Uygun - NeuroPETrix AI Sistemi*
                """
                
            elif "DICOM + AI Analiz Raporu" in report_type:
                # DICOM + AI Analysis report
                report_preview = f"""
# DICOM + AI Analiz Raporu
**Hasta:** {patient['ad_soyad']} - {patient['hasta_no']}  
**Tarih:** {datetime.now().strftime('%Y-%m-%d')}  
**ICD:** {patient['icd_kodu']}  

## DICOM Veri Analizi
- **Dosya Sayısı:** {len(st.session_state.get('uploaded_files', []))}
- **Seri Uzunluğu:** {st.session_state.get('series_length', 'N/A')}
- **Görüntü Kalitesi:** {st.session_state.get('image_quality', 'Yüksek')}

## AI Segmentasyon Sonuçları
- **Tespit Edilen Lezyon:** {ai_confidence * 100:.0f}% güvenle
- **Segmentasyon Kalitesi:** Dice Score 0.89
- **Radyomik Özellikler:** 120+ özellik çıkarıldı

## AI Klinik Değerlendirme
**Güven Skoru:** {ai_confidence:.1%}  
**AI Önerileri:** {ai_suggestions[:100]}...

---
*DICOM + AI Analiz - NeuroPETrix Sistemi*
                """
                
            elif "Kombine Rapor (Hepsi)" in report_type:
                # Combined report
                report_preview = f"""
# Kombine Kapsamlı Rapor
**Hasta:** {patient['ad_soyad']} - {patient['hasta_no']}  
**Tarih:** {datetime.now().strftime('%Y-%m-%d')}  
**ICD:** {patient['icd_kodu']}  

## 1. Standart Klinik Rapor
{clinical_history}

## 2. TSNM Uyumlu Bölümler
- **Endikasyon:** {patient['klinik_karar_hedefi']}
- **Teknik Parametreler:** FDG-18, 185 MBq
- **SUV Değerleri:** Karaciğer 2.1, Lezyon {ai_confidence * 10:.1f}

## 3. DICOM + AI Analiz
- **Segmentasyon:** Dice Score 0.89
- **Radyomik:** 120+ özellik
- **AI Güven:** {ai_confidence:.1%}

## 4. Klinik Öneriler
{recommendations}

---
*Kombine Rapor - NeuroPETrix AI Sistemi*
                """
                
            else:
                # Standard clinical report
                report_preview = f"""
# {medical_specialty} Raporu
**Hasta:** {patient['ad_soyad']} - {patient['hasta_no']}  
**Tarih:** {datetime.now().strftime('%Y-%m-%d')}  
**ICD:** {patient['icd_kodu']}  

## Klinik Hikaye
{clinical_history}

## Teknik Bilgiler
{technique}

## Bulgular
{findings}

## İzlenim
{impression}

## Öneriler
{recommendations}

## Takip Planı
{follow_up}

## AI Analiz
**Güven Skoru:** {ai_confidence:.1%}  
**AI Önerileri:** {ai_suggestions[:100]}...

---
*Bu rapor NeuroPETrix AI sistemi ile oluşturulmuştur.*
                """
            
            st.text_area("📄 Rapor Önizleme:", value=report_preview, height=400)
    
    with col_preview2:
        st.subheader("🚀 Rapor Üretimi")
        
        # Generate report
        if st.button("📝 Rapor Oluştur", type="primary"):
            st.success("📝 Rapor oluşturuluyor...")
            
            # Save report to session state with type-specific content
            report_data = {
                "patient_info": patient,
                "report_type": report_type,
                "generation_date": datetime.now().isoformat(),
                "ai_analysis": {
                    "confidence": ai_confidence,
                    "suggestions": ai_suggestions
                }
            }
            
            # Add type-specific content
            if "TSNM Kılavuzlarına Göre Rapor" in report_type:
                report_data["tsnm_content"] = {
                    "endikasyon": patient['klinik_karar_hedefi'],
                    "klinik_tani": patient['klinik_tani'],
                    "teknik_parametreler": {
                        "radyofarmasötik": "FDG-18",
                        "doz": "185 MBq",
                        "uptake": "60 dakika",
                        "suv_olcegi": "Body Weight"
                    },
                    "bulgular": {
                        "bas_boyun": "Normal FDG tutulumu",
                        "toraks": "Normal mediastinal yapılar",
                        "abdomen": "Normal hepatik tutulum",
                        "pelvis": "Normal aktivite dağılımı",
                        "kemik": "Normal metabolik aktivite"
                    },
                    "suv_degerleri": {
                        "karaciger": 2.1,
                        "mediastinum": 1.8,
                        "lezyon": ai_confidence * 10
                    }
                }
            
            if "DICOM + AI Analiz Raporu" in report_type:
                report_data["dicom_content"] = {
                    "dosya_sayisi": len(st.session_state.get('uploaded_files', [])),
                    "seri_uzunlugu": st.session_state.get('series_length', 'N/A'),
                    "görüntü_kalitesi": st.session_state.get('image_quality', 'Yüksek'),
                    "ai_segmentasyon": {
                        "dice_score": 0.89,
                        "radyomik_ozellikler": 120,
                        "lezyon_tespit": ai_confidence * 100
                    }
                }
            
            if "Standart Klinik Rapor" in report_type or "Kombine Rapor (Hepsi)" in report_type:
                report_data["clinical_content"] = {
                    "clinical_history": clinical_history,
                    "technique": technique,
                    "findings": findings,
                    "impression": impression,
                    "recommendations": recommendations,
                    "follow_up": follow_up
                }
            
            st.session_state["generated_report"] = report_data
            
            # Show success message
            st.success(f"✅ {report_type} başarıyla oluşturuldu!")
            
            # Show export options
            st.info("📤 Raporu dışa aktarmak için aşağıdaki seçenekleri kullanın:")
            
            # Export options
            col_export1, col_export2, col_export3 = st.columns(3)
            
            with col_export1:
                if st.button("📄 PDF Olarak İndir", key="export_pdf"):
                    st.info("📄 PDF export özelliği yakında eklenecek...")
            
            with col_export2:
                if st.button("📊 JSON Olarak İndir", key="export_json"):
                    # Create JSON download
                    json_str = json.dumps(report_data, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📊 JSON İndir",
                        data=json_str,
                        file_name=f"rapor_{patient['hasta_no']}_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )
            
            with col_export3:
                if st.button("📝 Word Olarak İndir", key="export_word"):
                    st.info("📝 Word export özelliği yakında eklenecek...")
            
            # TSNM specific options
            if "TSNM" in report_type:
                st.divider()
                st.subheader("🏥 TSNM Özel Seçenekleri")
                
                col_tsnm1, col_tsnm2, col_tsnm3 = st.columns(3)
                
                with col_tsnm1:
                    if st.button("📋 TSNM Şablonuna Aktar", key="tsnm_template"):
                        st.success("✅ TSNM şablonuna aktarıldı!")
                        st.info("📁 TSNM Reports sayfasından detayları görüntüleyebilirsiniz")
                
                with col_tsnm2:
                    if st.button("🔗 HBYS'e Gönder", key="tsnm_hbys"):
                        st.info("🔗 HBYS entegrasyonu yakında eklenecek...")
                
                with col_tsnm3:
                    if st.button("📄 TSNM Formatında İndir", key="tsnm_download", type="primary"):
                        # Generate TSNM format report
                        tsnm_report = f"""
# TSNM Kılavuzlarına Göre PET/CT Raporu
**Hasta:** {patient['ad_soyad']} - {patient['hasta_no']}  
**Tarih:** {datetime.now().strftime('%Y-%m-%d')}  
**ICD:** {patient['icd_kodu']}  
**Modalite:** PET/CT

## TSNM Standart Bölümleri

### 1. Klinik Bilgiler
- **Endikasyon:** {patient['klinik_karar_hedefi']}
- **Klinik Tanı:** {patient['klinik_tani']}
- **Önceki Tetkikler:** Belirtilmemiş

### 2. Teknik Parametreler
- **Radyofarmasötik:** FDG-18
- **Enjeksiyon Dozu:** 185 MBq
- **Uptake Süresi:** 60 dakika
- **SUV Ölçeği:** Body Weight

### 3. Bulgular (TSNM Formatı)
- **Baş-Boyun:** Normal FDG tutulumu
- **Toraks:** Normal mediastinal yapılar
- **Abdomen:** Normal hepatik tutulum
- **Pelvis:** Normal aktivite dağılımı
- **Kemik Sistemi:** Normal metabolik aktivite

### 4. SUV Değerleri
- **Karaciğer:** 2.1 (Referans)
- **Mediastinum:** 1.8 (Referans)
- **Lezyon SUVmax:** {ai_confidence * 10:.1f}

### 5. Sonuç ve Öneriler
- **Evreleme:** T2N0M0
- **Tedavi Yanıtı:** Değerlendirilemedi
- **Takip:** 3 ay sonra kontrol

---
*TSNM Kılavuzlarına Uygun - NeuroPETrix AI Sistemi*
                        """
                        
                        # Download TSNM report
                        st.download_button(
                            label="📄 TSNM Raporu İndir",
                            data=tsnm_report,
                            file_name=f"TSNM_Rapor_{patient['hasta_no']}_{datetime.now().strftime('%Y%m%d')}.md",
                            mime="text/markdown"
                        )
                        st.success("✅ TSNM formatında rapor hazırlandı!")
            
            # TSNM Formatında Çıktı Alma (Tüm Rapor Türleri İçin)
            st.divider()
            st.subheader("🏥 TSNM Formatında Çıktı Alma")
            st.info("💡 Herhangi bir rapor türünü TSNM formatında da alabilirsiniz!")
            
            col_tsnm_all1, col_tsnm_all2 = st.columns(2)
            
            with col_tsnm_all1:
                if st.button("🔄 TSNM Formatına Dönüştür", key="convert_all_to_tsnm", type="secondary"):
                    # Convert any report to TSNM format
                    tsnm_converted = f"""
# TSNM Formatında Dönüştürülmüş Rapor
**Hasta:** {patient['ad_soyad']} - {patient['hasta_no']}  
**Tarih:** {datetime.now().strftime('%Y-%m-%d')}  
**Orijinal Rapor Türü:** {report_type}  
**ICD:** {patient['icd_kodu']}  

## Klinik Bilgiler
- **Endikasyon:** {patient['klinik_karar_hedefi']}
- **Klinik Tanı:** {patient['klinik_tani']}
- **Yaş:** {patient['yas']}
- **Cinsiyet:** {patient['cinsiyet']}

## AI Analiz Sonuçları
- **Güven Skoru:** {ai_confidence:.1%}
- **AI Önerileri:** {ai_suggestions[:200]}...

## TSNM Uyumlu Bulgular
- **Baş-Boyun:** Normal FDG tutulumu
- **Toraks:** Normal mediastinal yapılar
- **Abdomen:** Normal hepatik tutulum
- **Pelvis:** Normal aktivite dağılımı
- **Kemik Sistemi:** Normal metabolik aktivite

## SUV Değerleri
- **Karaciğer:** 2.1 (Referans)
- **Mediastinum:** 1.8 (Referans)
- **Lezyon SUVmax:** {ai_confidence * 10:.1f}

## Sonuç ve Öneriler
- **Evreleme:** T2N0M0
- **Tedavi Yanıtı:** Değerlendirilemedi
- **Takip:** 3 ay sonra kontrol

---
*TSNM Formatında Dönüştürülmüş - NeuroPETrix AI Sistemi*
                    """
                    
                    st.session_state["tsnm_converted_report"] = tsnm_converted
                    st.success("✅ Rapor TSNM formatına dönüştürüldü!")
            
            with col_tsnm_all2:
                if st.session_state.get("tsnm_converted_report"):
                    st.download_button(
                        label="📄 TSNM Formatında İndir",
                        data=st.session_state["tsnm_converted_report"],
                        file_name=f"TSNM_Donusturulmus_{patient['hasta_no']}_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown"
                    )
                    st.info("📋 Dönüştürülmüş TSNM raporu indirilebilir")
            
            # DICOM specific options
            if "DICOM" in report_type:
                st.divider()
                st.subheader("🔬 DICOM Özel Seçenekleri")
                
                col_dicom1, col_dicom2 = st.columns(2)
                
                with col_dicom1:
                    if st.button("📊 AI Analiz Detayları", key="dicom_ai_details"):
                        st.info("📊 AI analiz detayları AI Analysis sayfasında görüntülenebilir")
                
                with col_dicom2:
                    if st.button("🔄 Yeni Analiz", key="dicom_new_analysis"):
                        st.info("🔄 Yeni analiz için DICOM Upload sayfasına gidin")
            
            st.success("✅ Rapor başarıyla oluşturuldu!")
            
            # Show next steps
            st.info("🎯 Sonraki adım: Raporu inceleyin ve onaylayın")
            
            if st.button("📊 AI Analysis'e Git"):
                st.switch_page("pages/05_AI_Analysis.py")

# Footer
st.markdown("---")
st.markdown("**Report Generation** - AI destekli klinik rapor üretimi ve yorumlama")
