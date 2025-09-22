import streamlit as st
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="🏥 HBYS Entegrasyon - NeuroPETrix",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if "patients" not in st.session_state:
    st.session_state["patients"] = []
if "current_patient" not in st.session_state:
    st.session_state["current_patient"] = None
if "recording" not in st.session_state:
    st.session_state["recording"] = False
if "recording_text" not in st.session_state:
    st.session_state["recording_text"] = ""
if "workflow_step" not in st.session_state:
    st.session_state["workflow_step"] = 0

# Header with Dark Mode Toggle
col_header1, col_header2, col_header3 = st.columns([3, 1, 1])

with col_header1:
    st.title("🏥 HBYS Entegrasyon - Ana Giriş")
    st.markdown("**Hasta Yönetimi ve AI Destekli Klinik Workflow**")

with col_header2:
    st.write("")  # Spacer
    st.write("")  # Spacer
    
    # Dark Mode Toggle - Küçük simge
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False
    
    if st.button("🌙" if not st.session_state["dark_mode"] else "☀️", 
                 key="hbys_dark_mode_toggle", 
                 help="Dark/Light Mode Toggle"):
        st.session_state["dark_mode"] = not st.session_state["dark_mode"]
        st.rerun()

with col_header3:
    st.write("")  # Spacer
    st.write("")  # Spacer
    
    # System Status
    try:
        import requests
        health_response = requests.get("http://127.0.0.1:8000/health", timeout=3)
        if health_response.status_code == 200:
            st.success("🟢 Backend OK")
        else:
            st.error("🔴 Backend Error")
    except:
        st.error("🔌 Backend Offline")

# Sidebar Navigation
with st.sidebar:
    st.header("🧭 Navigasyon")
    if st.button("🏠 Ana Sayfaya Dön", key="home_nav"):
        st.switch_page("streamlit_app.py")
    
    st.header("📊 Sistem Durumu")
    if st.session_state["current_patient"]:
        st.success(f"✅ Aktif Hasta: {st.session_state['current_patient']['ad_soyad']}")
        st.info(f"🔄 Workflow: {st.session_state['workflow_step']}/4")
    else:
        st.warning("⚠️ Aktif hasta yok")
    
    st.header("🎯 Hızlı İşlemler")
    if st.button("🎯 Demo Hasta Oluştur", key="demo_patient", type="primary"):
        demo_patient = {
            "hasta_no": "DEMO001",
            "ad_soyad": "Demo Hasta",
            "dogum_tarihi": "1980-01-01",
            "yas": 43,
            "cinsiyet": "Erkek",
            "icd_kodu": "C34.9",
            "icd_aciklama": "Akciğer kanseri, tanımlanmamış",
            "klinik_tani": "Sağ akciğer üst lobda şüpheli nodül",
            "klinik_karar_hedefi": "Evreleme",
            "notlar": "Demo hasta - test amaçlı",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "anamnesis": "",
            "laboratory": "",
            "pathology": "",
            "imaging": "",
            "clinical_notes": "",
            "workflow_history": []
        }
        st.session_state["patients"].append(demo_patient)
        st.session_state["current_patient"] = demo_patient
        st.session_state["workflow_step"] = 1
        st.success("✅ Demo hasta oluşturuldu!")
        st.rerun()
    
    if st.button("🧹 Tüm Verileri Temizle", key="clear_all_data", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state["patients"] = []
        st.session_state["current_patient"] = None
        st.session_state["workflow_step"] = 0
        st.success("✅ Tüm veriler temizlendi!")
        st.rerun()

# Main Content
if not st.session_state["current_patient"]:
    # No active patient - Show patient creation form
    st.header("👤 Yeni Hasta Ekle")
    st.info("📋 Yeni hasta bilgilerini girin veya demo hasta oluşturun")
    
    with st.form("new_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            hasta_no = st.text_input("Hasta No (Opsiyonel)", key="hasta_no_input")
            ad_soyad = st.text_input("Ad Soyad *", key="ad_soyad_input")
            dogum_tarihi = st.date_input("Doğum Tarihi *", key="dogum_tarihi_input")
            cinsiyet = st.selectbox("Cinsiyet *", ["Erkek", "Kadın"], key="cinsiyet_input")
        
        with col2:
            # ICD Code selection with descriptions
            icd_options = {
                "C34.9": "Akciğer kanseri, tanımlanmamış",
                "C50.9": "Meme kanseri, tanımlanmamış",
                "C61": "Prostat kanseri",
                "C16.9": "Mide kanseri, tanımlanmamış",
                "C18.9": "Kolon kanseri, tanımlanmamış",
                "C25.9": "Pankreas kanseri, tanımlanmamış",
                "C22.0": "Karaciğer hücreli karsinom",
                "C80": "Primeri bilinmeyen malignite",
                "C73": "Tiroid bezi malign neoplazmı",
                "C71.9": "Beyin, tanımlanmamış"
            }
            
            icd_selection = st.selectbox(
                "ICD Kodu ve Açıklama *",
                list(icd_options.keys()),
                format_func=lambda x: f"{x} - {icd_options[x]}",
                key="icd_selection"
            )
            
            klinik_tani = st.text_input("Klinik Tanı *", key="klinik_tani", help="Hastanın kesin tanılı hastalığı")
            klinik_karar_hedefi = st.selectbox(
                "Klinik Karar Hedefi *",
                ["Tanı", "Evreleme", "Tedavi Planlaması", "Takip", "Prognoz"],
                key="klinik_karar_hedefi"
            )
        
        # Submit button
        submitted = st.form_submit_button("✅ Hasta Ekle", type="primary")
        
        if submitted:
            # Validation
            missing_fields = []
            if not ad_soyad:
                missing_fields.append("Ad Soyad")
            if not dogum_tarihi:
                missing_fields.append("Doğum Tarihi")
            if not cinsiyet:
                missing_fields.append("Cinsiyet")
            if not icd_selection:
                missing_fields.append("ICD Kodu")
            if not klinik_tani:
                missing_fields.append("Klinik Tanı")
            if not klinik_karar_hedefi:
                missing_fields.append("Klinik Karar Hedefi")
            
            if missing_fields:
                st.error(f"❌ **ŞU ALANLAR DOLDURULMALIDIR:** {', '.join(missing_fields)}")
            else:
                # Calculate age
                from datetime import date
                today = date.today()
                age = today.year - dogum_tarihi.year - ((today.month, today.day) < (dogum_tarihi.month, dogum_tarihi.day))
                
                # Create patient
                if not hasta_no:
                    hasta_no = f"PAT{len(st.session_state['patients']) + 1:03d}"
                
                new_patient = {
                    "hasta_no": hasta_no,
                    "ad_soyad": ad_soyad,
                    "dogum_tarihi": dogum_tarihi.strftime("%Y-%m-%d"),
                    "yas": age,
                    "cinsiyet": cinsiyet,
                    "icd_kodu": icd_selection,
                    "icd_aciklama": icd_options[icd_selection],
                    "klinik_tani": klinik_tani,
                    "klinik_karar_hedefi": klinik_karar_hedefi,
                    "notlar": "",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "anamnesis": "",
                    "laboratory": "",
                    "pathology": "",
                    "imaging": "",
                    "clinical_notes": "",
                    "workflow_history": []
                }
                
                st.session_state["patients"].append(new_patient)
                st.session_state["current_patient"] = new_patient
                st.session_state["workflow_step"] = 1
                st.success("✅ Hasta başarıyla eklendi!")
                st.rerun()

# Patient List (if no active patient)
if not st.session_state["current_patient"] and st.session_state["patients"]:
    st.divider()
    st.header("📋 Mevcut Hasta Listesi")
    
    for i, patient in enumerate(st.session_state["patients"]):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"**{patient['ad_soyad']}** ({patient['hasta_no']})")
            st.markdown(f"Yaş: {patient['yas']}, {patient['cinsiyet']}")
        
        with col2:
            st.markdown(f"**ICD:** {patient['icd_kodu']} - {patient['icd_aciklama']}")
            st.markdown(f"**Hedef:** {patient['klinik_karar_hedefi']}")
        
        with col3:
            if st.button(f"Seç {i}", key=f"select_{i}"):
                st.session_state["current_patient"] = patient
                st.session_state["workflow_step"] = 1
                st.success(f"✅ {patient['ad_soyad']} seçildi!")
                st.rerun()
        
        st.divider()

# Active Patient Workflow
if st.session_state["current_patient"]:
    patient = st.session_state["current_patient"]
    
    # Patient Summary Header
    st.header("👤 Aktif Hasta Bilgileri")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"**Hasta No:** {patient['hasta_no']}")
        st.markdown(f"**Ad Soyad:** {patient['ad_soyad']}")
    
    with col2:
        st.markdown(f"**Yaş:** {patient['yas']}")
        st.markdown(f"**Cinsiyet:** {patient['cinsiyet']}")
    
    with col3:
        st.markdown(f"**ICD:** {patient['icd_kodu']}")
        st.markdown(f"**Tanı:** {patient['klinik_tani']}")
    
    with col4:
        st.markdown(f"**Hedef:** {patient['klinik_karar_hedefi']}")
        st.markdown(f"**Oluşturulma:** {patient['created_at']}")
    
    # Workflow Progress
    st.divider()
    st.header("🔄 AI Destekli Klinik Workflow")
    
    # Workflow steps
    workflow_steps = [
        "📋 1. İlk PICO Oluşturma",
        "🔍 2. Literatür Taraması ve Veri Gereksinimleri",
        "📥 3. Veri Toplama ve Giriş",
        "📚 4. Final PICO ve Literatür Analizi"
    ]
    
    # Progress bar - Ensure value is between 0.0 and 1.0
    progress_value = min(1.0, max(0.0, st.session_state["workflow_step"] / (len(workflow_steps) - 1)))
    progress = st.progress(progress_value)
    
    # Step indicators
    cols = st.columns(len(workflow_steps))
    for i, (col, step) in enumerate(zip(cols, workflow_steps)):
        if i <= st.session_state["workflow_step"]:
            col.success(f"✅ {step}")
        elif i == st.session_state["workflow_step"] + 1:
            col.info(f"🔄 {step}")
        else:
            col.markdown(f"⏳ {step}")
    
    st.divider()
    
    # Step 1: Initial PICO
    if st.session_state["workflow_step"] == 1:
        st.subheader("📋 1. İlk PICO Oluşturma")
        st.info("🎯 Minimal hasta bilgileriyle ilk PICO sorusu oluşturuluyor...")
        
        # Generate initial PICO
        initial_pico = f"""
        **İlk PICO Sorusu:**
        
        **P (Patient):** {patient['yas']} yaşında {patient['cinsiyet']}, {patient['icd_aciklama']} tanısı
        **I (Intervention):** {patient['klinik_karar_hedefi']} için PET/CT görüntüleme
        **C (Comparison):** Standart görüntüleme yöntemleri
        **O (Outcome):** Doğru evreleme ve tedavi planlaması
        
        **Sonraki Adım:** Literatür taraması ile gerekli veri türlerini belirleme
        """
        
        st.markdown(initial_pico)
        
        # Store initial PICO
        if "initial_pico_data" not in st.session_state:
            st.session_state["initial_pico_data"] = initial_pico
        
        # Navigation buttons
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
        
        with col_nav1:
            st.success("✅ Bu adım tamamlandı")
        
        with col_nav2:
            if st.button("🚀 Sonraki Adıma Geç", key="next_step_1", type="primary"):
                st.session_state["workflow_step"] = 2
                st.success("🚀 Literatür Taraması adımına geçiliyor...")
                st.rerun()
        
        with col_nav3:
            st.info("⏳ Veri Toplama")
        
        with col_nav4:
            st.info("⏳ Final PICO")
    
    # Step 2: Literature Search and Data Requirements
    elif st.session_state["workflow_step"] == 2:
        st.subheader("🔍 2. Literatür Taraması ve Veri Gereksinimleri")
        st.info("📚 Literatür taraması yapılıyor ve gerekli veri türleri belirleniyor...")
        
        if "data_requirements" not in st.session_state:
            # Simulate literature search
            with st.spinner("🔍 Literatür taraması yapılıyor..."):
                time.sleep(2)
            
            # Define data requirements based on ICD and clinical goal
            data_requirements = {
                "anamnesis": [
                    "Hastalık öyküsü ve semptomlar",
                    "Önceki tedavi öyküsü",
                    "Aile öyküsü",
                    "Risk faktörleri",
                    "Performans durumu (ECOG/Karnofsky)"
                ],
                "laboratory": [
                    "Tümör markerları (CEA, CA19-9, PSA, AFP, β-hCG)",
                    "Tam kan sayımı",
                    "Böbrek fonksiyon testleri",
                    "Karaciğer fonksiyon testleri",
                    "Koagülasyon testleri"
                ],
                "pathology": [
                    "Histopatolojik tanı",
                    "Tümör derecesi (Grading)",
                    "İmmünohistokimyasal bulgular",
                    "Moleküler test sonuçları",
                    "Hormon reseptör durumu"
                ],
                "imaging": [
                    "Önceki görüntüleme raporları",
                    "Tümör boyutları ve lokalizasyonu",
                    "Lenf nodu tutulumu",
                    "Uzak metastaz varlığı",
                    "Vasküler invazyon"
                ]
            }
            
            st.success("✅ Literatür taraması tamamlandı!")
            st.info("📋 Gerekli veri şablonu oluşturuldu!")
            
            # Display data requirements
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📋 Anamnez Verileri:**")
                for item in data_requirements["anamnesis"]:
                    st.markdown(f"• {item}")
                
                st.markdown("**🔬 Laboratuvar Verileri:**")
                for item in data_requirements["laboratory"]:
                    st.markdown(f"• {item}")
            
            with col2:
                st.markdown("**🔬 Patoloji Verileri:**")
                for item in data_requirements["pathology"]:
                    st.markdown(f"• {item}")
                
                st.markdown("**📷 Görüntüleme Verileri:**")
                for item in data_requirements["imaging"]:
                    st.markdown(f"• {item}")
            
            # Store data requirements
            st.session_state["data_requirements"] = data_requirements
        
        # Navigation buttons
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
        
        with col_nav1:
            if st.button("⬅️ Önceki Adım", key="prev_step_2"):
                st.session_state["workflow_step"] = 1
                st.rerun()
        
        with col_nav2:
            st.success("✅ Bu adım tamamlandı")
        
        with col_nav3:
            if st.button("🚀 Sonraki Adıma Geç", key="next_step_2", type="primary"):
                st.session_state["workflow_step"] = 3
                st.success("🚀 Veri Toplama adımına geçiliyor...")
                st.rerun()
        
        with col_nav4:
            st.info("⏳ Final PICO")
    
    # Step 3: Data Collection
    elif st.session_state["workflow_step"] == 3:
        st.subheader("📥 3. Veri Toplama ve Giriş")
        
        if "data_requirements" not in st.session_state:
            st.error("❌ Önce veri gereksinimleri belirlenmelidir!")
            st.session_state["workflow_step"] = 2
            st.rerun()
        
        st.info("📋 Literatür bulgularına göre gerekli verileri toplayın:")
        
        # Data collection tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Anamnez", "🔬 Laboratuvar", "🔬 Patoloji", "📷 Görüntüleme"
        ])
        
        with tab1:
            st.markdown("**📋 Anamnez Verileri:**")
            anamnesis = st.text_area(
                "Hastalık öyküsü, semptomlar, aile öyküsü, önceki tedaviler:",
                value=patient.get('anamnesis', ''),
                height=150,
                key="anamnesis_input",
                help="Hastanın detaylı anamnez bilgilerini girin"
            )
            
            # HBYS integration for anamnesis
            col_anam1, col_anam2 = st.columns([1, 1])
            with col_anam1:
                if st.button("🏥 HBYS'den Çek", key="hbys_anamnesis"):
                    st.info("🤖 HBYS'den anamnez verileri çekiliyor...")
                    time.sleep(2)
                    mock_anamnesis = f"""
                    Hasta {patient['yas']} yaşında {patient['cinsiyet']}. 
                    {patient['icd_aciklama']} tanısı ile takip ediliyor. 
                    Önceki tedavi öyküsü yok. 
                    Aile öyküsünde kanser bulunmuyor. 
                    ECOG performans durumu: 1.
                    """
                    st.success("✅ HBYS'den anamnez verileri çekildi!")
                    st.text_area("📋 HBYS'den Çekilen Veriler:", value=mock_anamnesis, height=100, key="hbys_anamnesis_display")
                    
                    if st.button("💾 Bu Verileri Kaydet", key="save_hbys_anamnesis"):
                        patient['anamnesis'] = mock_anamnesis
                        st.success("✅ Anamnez verileri kaydedildi!")
                        st.rerun()
            
            with col_anam2:
                if st.button("💾 Manuel Verileri Kaydet", key="save_anamnesis"):
                    patient['anamnesis'] = anamnesis
                    st.success("✅ Anamnez verileri kaydedildi!")
                    st.rerun()
        
        with tab2:
            st.markdown("**🔬 Laboratuvar Verileri:**")
            laboratory = st.text_area(
                "Laboratuvar sonuçları, tümör markerları, kan değerleri:",
                value=patient.get('laboratory', ''),
                height=150,
                key="laboratory_input"
            )
            
            col_lab1, col_lab2 = st.columns([1, 1])
            with col_lab1:
                if st.button("🏥 HBYS'den Çek", key="hbys_laboratory"):
                    st.info("🤖 HBYS'den laboratuvar verileri çekiliyor...")
                    time.sleep(2)
                    mock_laboratory = f"""
                    CEA: 15.2 ng/mL (Normal: <3.0)
                    CA19-9: 89 U/mL (Normal: <37)
                    Hemoglobin: 12.8 g/dL
                    Lökosit: 8.2 x10³/μL
                    Trombosit: 245 x10³/μL
                    """
                    st.success("✅ HBYS'den laboratuvar verileri çekildi!")
                    st.text_area("🔬 HBYS'den Çekilen Veriler:", value=mock_laboratory, height=100, key="hbys_laboratory_display")
                    
                    if st.button("💾 Bu Verileri Kaydet", key="save_hbys_laboratory"):
                        patient['laboratory'] = mock_laboratory
                        st.success("✅ Laboratuvar verileri kaydedildi!")
                        st.rerun()
            
            with col_lab2:
                if st.button("💾 Manuel Verileri Kaydet", key="save_laboratory"):
                    patient['laboratory'] = laboratory
                    st.success("✅ Laboratuvar verileri kaydedildi!")
                    st.rerun()
        
        with tab3:
            st.markdown("**🔬 Patoloji Verileri:**")
            pathology = st.text_area(
                "Histopatolojik tanı, grading, immünohistokimyasal bulgular:",
                value=patient.get('pathology', ''),
                height=150,
                key="pathology_input"
            )
            
            col_pat1, col_pat2 = st.columns([1, 1])
            with col_pat1:
                if st.button("🏥 HBYS'den Çek", key="hbys_pathology"):
                    st.info("🤖 HBYS'den patoloji verileri çekiliyor...")
                    time.sleep(2)
                    mock_pathology = f"""
                    Histopatolojik Tanı: Adenokarsinom
                    Grading: G2 (Moderate)
                    Tümör Boyutu: 3.2 cm
                    Lenf Nodu Tutulumu: 2/12 pozitif
                    """
                    st.success("✅ HBYS'den patoloji verileri çekildi!")
                    st.text_area("🔬 HBYS'den Çekilen Veriler:", value=mock_pathology, height=100, key="hbys_pathology_display")
                    
                    if st.button("💾 Bu Verileri Kaydet", key="save_hbys_pathology"):
                        patient['pathology'] = mock_pathology
                        st.success("✅ Patoloji verileri kaydedildi!")
                        st.rerun()
            
            with col_pat2:
                if st.button("💾 Manuel Verileri Kaydet", key="save_pathology"):
                    patient['pathology'] = pathology
                    st.success("✅ Patoloji verileri kaydedildi!")
                    st.rerun()
        
        with tab4:
            st.markdown("**📷 Görüntüleme Verileri:**")
            imaging = st.text_area(
                "Önceki görüntüleme raporları, tümör boyutları, metastaz:",
                value=patient.get('imaging', ''),
                height=150,
                key="imaging_input"
            )
            
            col_img1, col_img2 = st.columns([1, 1])
            with col_img1:
                if st.button("🏥 HBYS'den Çek", key="hbys_imaging"):
                    st.info("🤖 HBYS'den görüntüleme verileri çekiliyor...")
                    time.sleep(2)
                    mock_imaging = f"""
                    CT Toraks: Sağ üst lobda 3.2 cm nodül
                    Lenf Nodu: Hiler ve mediastinal tutulum
                    Metastaz: Kemik metastazı yok
                    Evre: T2N2M0
                    """
                    st.success("✅ HBYS'den görüntüleme verileri çekildi!")
                    st.text_area("📷 HBYS'den Çekilen Veriler:", value=mock_imaging, height=100, key="hbys_imaging_display")
                    
                    if st.button("💾 Bu Verileri Kaydet", key="save_hbys_imaging"):
                        patient['imaging'] = mock_imaging
                        st.success("✅ Görüntüleme verileri kaydedildi!")
                        st.rerun()
            
            with col_img2:
                if st.button("💾 Manuel Verileri Kaydet", key="save_imaging"):
                    patient['imaging'] = imaging
                    st.success("✅ Görüntüleme verileri kaydedildi!")
                    st.rerun()
        
        # Navigation buttons
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
        
        with col_nav1:
            if st.button("⬅️ Önceki Adım", key="prev_step_3"):
                st.session_state["workflow_step"] = 2
                st.rerun()
        
        with col_nav2:
            st.success("✅ Bu adım tamamlandı")
        
        with col_nav3:
            st.success("✅ Bu adım tamamlandı")
        
        with col_nav4:
            if st.button("🚀 Sonraki Adıma Geç", key="next_step_3", type="primary"):
                st.session_state["workflow_step"] = 4
                st.success("🚀 Final PICO ve Literatür Analizi adımına geçiliyor...")
                st.rerun()
    
    # Step 4: Final PICO and Literature Analysis
    elif st.session_state["workflow_step"] == 4:
        st.subheader("📚 4. Final PICO ve Literatür Analizi")
        
        if "data_requirements" not in st.session_state:
            st.error("❌ Önce veri toplama tamamlanmalıdır!")
            st.session_state["workflow_step"] = 3
            st.rerun()
        
        st.info("🎯 Toplanan verilerle detaylı PICO oluşturuluyor...")
        
        # Generate detailed PICO based on collected data
        collected_data = {
            "anamnesis": patient.get('anamnesis', ''),
            "laboratory": patient.get('laboratory', ''),
            "pathology": patient.get('pathology', ''),
            "imaging": patient.get('imaging', '')
        }
        
        # AI-generated detailed PICO
        detailed_pico = f"""
        **Detaylı PICO Sorusu:**
        
        **P (Patient):** {patient['yas']} yaşında {patient['cinsiyet']}, {patient['icd_aciklama']} tanısı
        **I (Intervention):** {patient['klinik_karar_hedefi']} için PET/CT görüntüleme
        **C (Comparison):** Standart görüntüleme yöntemleri ile karşılaştırma
        **O (Outcome):** Doğru evreleme, tedavi planlaması ve prognoz belirleme
        
        **Literatür Analizi Gereksinimleri:**
        - {patient['icd_aciklama']} için güncel tedavi kılavuzları
        - PET/CT'in {patient['klinik_karar_hedefi']} değeri
        - Benzer hasta gruplarında sonuçlar
        - GRADE kanıt seviyesi değerlendirmesi
        """
        
        st.markdown(detailed_pico)
        
        # Literature search simulation
        if st.button("🔍 Literatür Taraması Başlat", key="start_literature_search", type="primary"):
            st.info("🤖 Literatür taraması başlatılıyor...")
            
            # Simulate literature search
            progress_bar = st.progress(0)
            for i in range(101):
                time.sleep(0.03)
                progress_bar.progress(i)
            
            # Mock literature results
            literature_results = {
                "systematic_reviews": [
                    "2023 - PET/CT in {patient['icd_aciklama']} staging: Meta-analysis",
                    "2022 - Evidence-based guidelines for {patient['klinik_karar_hedefi']}"
                ],
                "randomized_trials": [
                    "2024 - Prospective study on PET/CT accuracy",
                    "2023 - Comparative effectiveness study"
                ],
                "clinical_guidelines": [
                    "NCCN Guidelines 2024",
                    "ESMO Clinical Practice Guidelines",
                    "Turkish Oncology Group Recommendations"
                ]
            }
            
            st.success("✅ Literatür taraması tamamlandı!")
            
            # Display results
            col_lit1, col_lit2 = st.columns(2)
            
            with col_lit1:
                st.markdown("**📚 Sistematik Derlemeler:**")
                for item in literature_results["systematic_reviews"]:
                    st.markdown(f"• {item}")
                
                st.markdown("**🔬 Randomize Çalışmalar:**")
                for item in literature_results["randomized_trials"]:
                    st.markdown(f"• {item}")
            
            with col_lit2:
                st.markdown("**📋 Klinik Kılavuzlar:**")
                for item in literature_results["clinical_guidelines"]:
                    st.markdown(f"• {item}")
                
                st.markdown("**📊 GRADE Değerlendirmesi:**")
                st.info("**Kanıt Seviyesi:** A (Yüksek)")
                st.info("**Öneri Gücü:** 1 (Güçlü)")
                st.success("✅ PET/CT kullanımı güçlü şekilde önerilmektedir")
            
            # Store literature results
            st.session_state["literature_results"] = literature_results
            
            # Final assessment button
            if st.button("🎯 Final Değerlendirme ve Rapor Oluştur", key="final_assessment", type="primary"):
                st.success("🎉 Tüm workflow adımları tamamlandı!")
                st.info("📝 Rapor oluşturma sayfasına yönlendiriliyorsunuz...")
                st.switch_page("pages/02_Rapor_Üretimi.py")
        
        # Navigation buttons
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
        
        with col_nav1:
            if st.button("⬅️ Önceki Adım", key="prev_step_4"):
                st.session_state["workflow_step"] = 3
                st.rerun()
        
        with col_nav2:
            st.success("✅ Bu adım tamamlandı")
        
        with col_nav3:
            st.success("✅ Bu adım tamamlandı")
        
        with col_nav4:
            st.success("✅ Bu adım tamamlandı")
    
    # Manual Notes Section (Outside of workflow)
    st.divider()
    st.subheader("📝 Manuel Notlar ve Ses Kaydı")
    
    col_notes1, col_notes2 = st.columns([3, 1])
    
    with col_notes1:
        clinical_notes = st.text_area(
            "Klinik notlar ve gözlemler:",
            value=patient.get('clinical_notes', ''),
            height=100,
            key="clinical_notes",
            help="Hasta ile ilgili klinik notlar ve gözlemler"
        )
        
        # Update clinical notes
        if st.button("💾 Klinik Notları Kaydet", key="save_clinical_notes"):
            patient['clinical_notes'] = clinical_notes
            st.success("✅ Klinik notlar kaydedildi!")
            st.rerun()
        
        # Enhanced Voice Recording Interface
        st.markdown("**🎤 Gelişmiş Ses Kaydı:**")
        
        # Voice recording controls
        col_voice1, col_voice2, col_voice3, col_voice4 = st.columns(4)
        
        with col_voice1:
            if st.button("🎤 Başlat", key="start_recording", type="primary"):
                st.session_state["recording"] = True
                st.session_state["recording_text"] = ""
                st.info("🎤 Ses kaydı başlatıldı! Konuşmaya başlayın...")
        
        with col_voice2:
            if st.button("⏸️ Duraklat", key="pause_recording", disabled=not st.session_state.get("recording")):
                st.info("⏸️ Ses kaydı duraklatıldı")
        
        with col_voice3:
            if st.button("⏹️ Durdur", key="stop_recording", disabled=not st.session_state.get("recording")):
                if st.session_state.get("recording"):
                    st.success("✅ Ses kaydı tamamlandı!")
                    st.info("🤖 AI transkript oluşturuluyor...")
                    
                    # Mock AI transcription with improvements
                    progress_bar = st.progress(0)
                    for i in range(101):
                        time.sleep(0.02)
                        progress_bar.progress(i)
                    
                    # AI-enhanced transcript
                    mock_transcript = f"""
                    {patient['ad_soyad']} hastası için klinik değerlendirme:
                    
                    Hasta {patient['yas']} yaşında {patient['cinsiyet']} olup {patient['icd_aciklama']} tanısı ile takip edilmektedir. 
                    Mevcut bulgular {patient['klinik_karar_hedefi']} açısından değerlendirilmiştir. 
                    PET/CT ile evreleme planlanmaktadır.
                    """
                    
                    st.success("✅ AI transkript tamamlandı!")
                    st.text_area("📝 AI Transkripti:", value=mock_transcript, height=120, key="ai_transcript")
                    
                    if st.button("📝 Notlara Ekle", key="add_ai_transcript"):
                        current_notes = patient.get('clinical_notes', '')
                        patient['clinical_notes'] = current_notes + "\n\n[AI Ses Kaydı]: " + mock_transcript
                        st.success("✅ AI transkript notlara eklendi!")
                        st.rerun()
        
        with col_voice4:
            if st.button("💾 Sakla", key="save_recording", disabled=not st.session_state.get("recording_text")):
                # Save the current recording text to clinical notes
                if st.session_state.get("recording_text"):
                    current_notes = patient.get('clinical_notes', '')
                    patient['clinical_notes'] = current_notes + "\n\n[Ses Kaydı]: " + st.session_state["recording_text"]
                    st.success("✅ Ses kaydı notlara eklendi!")
                    st.session_state["recording_text"] = ""  # Clear recording text
                    st.rerun()
                else:
                    st.warning("⚠️ Kaydedilecek ses kaydı yok!")
        
        # Recording status and text
        if st.session_state.get("recording"):
            st.error("🔴 KAYIT YAPILIYOR - Konuşmaya devam edin...")
            
            # Live transcription display
            if st.button("📝 Canlı Transkript", key="live_transcript"):
                st.info("🤖 Canlı transkript başlatılıyor...")
                # Mock live transcription
                live_text = st.text_area("📝 Canlı Transkript:", value="Hasta değerlendirmesi devam ediyor...", height=80, key="live_transcript_area")
                
                # Update recording text with live transcript
                if st.button("💾 Canlı Transkripti Kaydet", key="save_live_transcript"):
                    st.session_state["recording_text"] = live_text
                    st.success("✅ Canlı transkript kaydedildi!")
        
        # Final Değerlendirme Raporu - Ses Kaydı Alanına Entegre
        if st.session_state["workflow_step"] == 4 and "literature_results" in st.session_state:
            st.divider()
            st.subheader("📋 Final Değerlendirme Raporu")
            
            # Generate final report
            final_report = f"""
            **FINAL KLİNİK DEĞERLENDİRME RAPORU**
            
            **Hasta Bilgileri:**
            • Ad Soyad: {patient['ad_soyad']}
            • Yaş: {patient['yas']}
            • ICD: {patient['icd_kodu']} - {patient['icd_aciklama']}
            • Klinik Tanı: {patient['klinik_tani']}
            • Hedef: {patient['klinik_karar_hedefi']}
            
            **Toplanan Veriler:**
            • Anamnez: {'✅ Tamamlandı' if patient.get('anamnesis') else '❌ Eksik'}
            • Laboratuvar: {'✅ Tamamlandı' if patient.get('laboratory') else '❌ Eksik'}
            • Patoloji: {'✅ Tamamlandı' if patient.get('pathology') else '❌ Eksik'}
            • Görüntüleme: {'✅ Tamamlandı' if patient.get('imaging') else '❌ Eksik'}
            
            **Literatür Analizi:**
            • Kanıt Seviyesi: A (Yüksek)
            • Öneri Gücü: 1 (Güçlü)
            • PET/CT kullanımı güçlü şekilde önerilmektedir
            
            **Klinik Öneri:**
            Bu hasta için PET/CT ile {patient['klinik_karar_hedefi']} önerilmektedir.
            Literatür bulguları ve toplanan veriler bu yaklaşımı desteklemektedir.
            """
            
            st.markdown(final_report)
            
            # Add to clinical notes
            if st.button("📝 Final Raporu Notlara Ekle", key="add_final_report", type="primary"):
                current_notes = patient.get('clinical_notes', '')
                patient['clinical_notes'] = current_notes + "\n\n[FINAL RAPOR]: " + final_report
                st.success("✅ Final rapor notlara eklendi!")
                st.rerun()
        
        # Onay butonu - Ses kaydı tamamlandıktan sonra
        if patient.get('clinical_notes') and ('[Ses Kaydı]:' in patient.get('clinical_notes', '') or '[FINAL RAPOR]:' in patient.get('clinical_notes', '')):
            st.success("✅ İşlem tamamlandı!")
            if st.button("✅ Notları Onayla ve Sonraki Adıma Geç", key="approve_notes", type="primary"):
                if st.session_state["workflow_step"] < 4:
                    st.session_state["workflow_step"] = min(4, st.session_state["workflow_step"] + 1)
                    st.success("🚀 Sonraki workflow adımına geçiliyor...")
                    st.rerun()
                else:
                    st.success("🎉 Tüm workflow adımları tamamlandı!")
    
    with col_notes2:
        st.markdown("**🎤 Ses Kaydı Kontrolleri:**")
        st.markdown("• 🎤 Başlat - Kaydı başlat")
        st.markdown("• ⏸️ Duraklat - Geçici durdur")
        st.markdown("• ⏹️ Durdur - Kaydı sonlandır")
        st.markdown("• 💾 Sakla - Kaydı kaydet")
        st.markdown("• 📝 Canlı - Gerçek zamanlı")
        
        if st.session_state.get("recording"):
            st.error("🔴 KAYIT YAPILIYOR")
        else:
            st.success("✅ Kayıt bekleniyor")
        
        # Quick Actions
        st.divider()
        st.markdown("**⚡ Hızlı İşlemler:**")
        
        col_quick1, col_quick2 = st.columns(2)
        
        with col_quick1:
            if st.button("📁 DICOM İşleme", key="quick_dicom"):
                st.switch_page("pages/04_DICOM_Upload.py")
        
        with col_quick2:
            if st.button("🔬 AI Analiz", key="quick_ai"):
                st.switch_page("pages/05_AI_Analysis.py")
        
        if st.button("📝 Rapor Oluştur", key="quick_report"):
            st.switch_page("pages/02_Rapor_Üretimi.py")
