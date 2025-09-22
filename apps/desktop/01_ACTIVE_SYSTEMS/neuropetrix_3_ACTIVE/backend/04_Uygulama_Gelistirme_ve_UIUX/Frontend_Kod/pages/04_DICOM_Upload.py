import streamlit as st
import requests
import json
from datetime import datetime

def render_dicom_upload():
    """DICOM Upload sayfasını render et"""
    
    st.header("📁 DICOM Dosya Yükleme")
    
    # Dosya yükleme
    st.subheader("DICOM Dosyaları")
    
    uploaded_files = st.file_uploader(
        "DICOM Dosyalarını Seçin",
        type=['dcm'],
        accept_multiple_files=True,
        help="Birden fazla DICOM dosyası seçebilirsiniz"
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} dosya seçildi")
        
        # Dosya listesi
        st.write("**Seçilen Dosyalar:**")
        for i, file in enumerate(uploaded_files, 1):
            st.write(f"{i}. {file.name} ({file.size} bytes)")
    
    # Yükleme seçenekleri
    st.subheader("Yükleme Seçenekleri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        upload_mode = st.selectbox(
            "Yükleme Modu",
            ["Tek Dosya", "Seri", "Çalışma"]
        )
        
        compression = st.checkbox("Sıkıştırma Uygula", value=True)
    
    with col2:
        anonymization = st.checkbox("Anonimleştirme Uygula", value=True)
        validation = st.checkbox("DICOM Validasyonu", value=True)
    
    # Hasta bilgileri
    st.subheader("Hasta Bilgileri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_name = st.text_input("Hasta Adı", "ANONYMOUS")
        patient_id = st.text_input("Hasta ID", "P-001")
        patient_age = st.number_input("Yaş", min_value=0, max_value=120, value=65)
    
    with col2:
        patient_gender = st.selectbox("Cinsiyet", ["M", "F"])
        study_date = st.date_input("Çalışma Tarihi", value=datetime.now().date())
        modality = st.selectbox("Modalite", ["PT", "CT", "MR", "PET/CT"])
    
    # Yükleme işlemi
    if st.button("📤 Dosyaları Yükle"):
        if uploaded_files:
            with st.spinner("Dosyalar yükleniyor..."):
                # Mock yükleme işlemi
                progress_bar = st.progress(0)
                
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i % 20 == 0:
                        st.write(f"Yükleme ilerlemesi: {i + 1}%")
                
                st.success("✅ Dosyalar başarıyla yüklendi!")
                
                # Yükleme özeti
                st.subheader("Yükleme Özeti")
                
                summary_data = {
                    "toplam_dosya": len(uploaded_files),
                    "toplam_boyut": sum(f.size for f in uploaded_files),
                    "modalite": modality,
                    "hasta_id": patient_id,
                    "yukleme_tarihi": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Toplam Dosya", summary_data["toplam_dosya"])
                
                with col2:
                    st.metric("Toplam Boyut", f"{summary_data['toplam_boyut'] / 1024 / 1024:.1f} MB")
                
                with col3:
                    st.metric("Modalite", summary_data["modalite"])
        else:
            st.error("❌ Lütfen dosya seçin")
    
    # DICOM meta verileri
    if uploaded_files:
        st.subheader("DICOM Meta Verileri")
        
        if st.button("🔍 Meta Verileri Görüntüle"):
            with st.spinner("Meta veriler analiz ediliyor..."):
                # Mock meta veri
                metadata = {
                    "patient_info": {
                        "name": "ANONYMOUS",
                        "id": "P-001",
                        "age": 65,
                        "gender": "M"
                    },
                    "study_info": {
                        "modality": "PT",
                        "manufacturer": "Siemens",
                        "model": "Biograph mCT",
                        "series_count": 1,
                        "image_count": 120
                    },
                    "acquisition_info": {
                        "injected_dose": "185 MBq",
                        "uptake_time": "60 minutes",
                        "reconstruction_method": "OSEM 3i24s",
                        "filter_type": "Gaussian 5mm"
                    }
                }
                
                st.success("Meta veriler analiz edildi!")
                
                # Meta verileri göster
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Hasta Bilgileri:**")
                    for key, value in metadata["patient_info"].items():
                        st.write(f"**{key.title()}:** {value}")
                
                with col2:
                    st.write("**Çalışma Bilgileri:**")
                    for key, value in metadata["study_info"].items():
                        st.write(f"**{key.title()}:** {value}")
                
                st.write("**Aküsizyon Bilgileri:**")
                for key, value in metadata["acquisition_info"].items():
                    st.write(f"**{key.title()}:** {value}")
    
    # Kalite kontrol
    st.subheader("Kalite Kontrol")
    
    if st.button("✅ Kalite Kontrolü Başlat"):
        with st.spinner("Kalite kontrolü yapılıyor..."):
            # Mock kalite kontrol sonuçları
            qc_results = {
                "dosya_bütünlüğü": "✅ Geçti",
                "dicom_uyumluluğu": "✅ Geçti",
                "görüntü_kalitesi": "✅ Geçti",
                "meta_veri_tutarlılığı": "✅ Geçti",
                "toplam_sonuç": "✅ Tüm kontroller geçti"
            }
            
            st.success("Kalite kontrolü tamamlandı!")
            
            for check, result in qc_results.items():
                if "Geçti" in result:
                    st.success(f"✅ {check.replace('_', ' ').title()}: {result}")
                else:
                    st.error(f"❌ {check.replace('_', ' ').title()}: {result}")
    
    # İşleme seçenekleri
    st.subheader("İşleme Seçenekleri")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔬 Radyomik Analiz"):
            with st.spinner("Radyomik analiz başlatılıyor..."):
                st.success("✅ Radyomik analiz başlatıldı")
    
    with col2:
        if st.button("🎯 Segmentasyon"):
            with st.spinner("Segmentasyon başlatılıyor..."):
                st.success("✅ Segmentasyon başlatıldı")
    
    with col3:
        if st.button("📊 SUV Hesaplama"):
            with st.spinner("SUV değerleri hesaplanıyor..."):
                st.success("✅ SUV hesaplama başlatıldı")
    
    # Geçmiş yüklemeler
    st.subheader("Geçmiş Yüklemeler")
    
    if st.button("📋 Geçmişi Görüntüle"):
        # Mock geçmiş verisi
        upload_history = [
            {
                "date": "2024-01-15 10:30:00",
                "patient_id": "P-001",
                "files": 120,
                "size": "45.2 MB",
                "status": "Completed"
            },
            {
                "date": "2024-01-15 09:15:00",
                "patient_id": "P-002",
                "files": 95,
                "size": "38.7 MB",
                "status": "Completed"
            },
            {
                "date": "2024-01-14 16:45:00",
                "patient_id": "P-003",
                "files": 150,
                "size": "52.1 MB",
                "status": "Failed"
            }
        ]
        
        for upload in upload_history:
            if upload['status'] == 'Completed':
                st.success(f"✅ {upload['date']} - {upload['patient_id']} ({upload['files']} dosya, {upload['size']})")
            else:
                st.error(f"❌ {upload['date']} - {upload['patient_id']} ({upload['files']} dosya, {upload['size']})")


