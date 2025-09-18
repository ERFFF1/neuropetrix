import streamlit as st
import requests
import json
from datetime import datetime

def render_hbys_integration():
    """HBYS Entegrasyon sayfasını render et"""
    
    st.header("🏥 HBYS Entegrasyonu")
    
    # Bağlantı durumu
    st.subheader("Bağlantı Durumu")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔗 HBYS Bağlantısını Test Et"):
            with st.spinner("Bağlantı test ediliyor..."):
                # Mock bağlantı testi
                st.success("✅ HBYS bağlantısı başarılı")
    
    with col2:
        if st.button("🔄 Veri Senkronizasyonu"):
            with st.spinner("Veriler senkronize ediliyor..."):
                st.success("✅ Veri senkronizasyonu tamamlandı")
    
    with col3:
        if st.button("📊 Sistem Durumu"):
            with st.spinner("Sistem durumu kontrol ediliyor..."):
                st.info("🟢 Tüm sistemler çalışıyor")
    
    # Hasta arama
    st.subheader("Hasta Arama")
    
    search_method = st.selectbox(
        "Arama Yöntemi",
        ["Hasta No", "Ad Soyad", "TC Kimlik No"]
    )
    
    search_query = st.text_input("Arama Sorgusu", "P-001")
    
    if st.button("🔍 Hasta Ara"):
        with st.spinner("Hasta aranıyor..."):
            # Mock hasta verisi
            patient_data = {
                "id": "P-001",
                "name": "Ahmet Yılmaz",
                "age": 65,
                "gender": "M",
                "diagnosis": "Lung cancer",
                "admission_date": "2024-01-15",
                "room": "301",
                "department": "Nükleer Tıp"
            }
            
            st.success("Hasta bulundu!")
            
            # Hasta bilgilerini göster
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Hasta Bilgileri:**")
                st.write(f"**ID:** {patient_data['id']}")
                st.write(f"**Ad Soyad:** {patient_data['name']}")
                st.write(f"**Yaş:** {patient_data['age']}")
                st.write(f"**Cinsiyet:** {patient_data['gender']}")
            
            with col2:
                st.write("**Klinik Bilgiler:**")
                st.write(f"**Tanı:** {patient_data['diagnosis']}")
                st.write(f"**Yatış Tarihi:** {patient_data['admission_date']}")
                st.write(f"**Oda:** {patient_data['room']}")
                st.write(f"**Servis:** {patient_data['department']}")
    
    # Laboratuvar sonuçları
    st.subheader("Laboratuvar Sonuçları")
    
    if st.button("🔬 Laboratuvar Sonuçlarını Getir"):
        with st.spinner("Laboratuvar sonuçları getiriliyor..."):
            # Mock laboratuvar verisi
            lab_results = {
                "glucose": 110,
                "creatinine": 0.9,
                "egfr": 90,
                "psa": None,
                "cea": 5.2,
                "ca125": None,
                "hemoglobin": 14.2,
                "wbc": 7.5,
                "platelets": 250
            }
            
            st.success("Laboratuvar sonuçları getirildi!")
            
            # Sonuçları göster
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Biyokimya:**")
                st.write(f"Glikoz: {lab_results['glucose']} mg/dL")
                st.write(f"Kreatinin: {lab_results['creatinine']} mg/dL")
                st.write(f"eGFR: {lab_results['egfr']} mL/min")
            
            with col2:
                st.write("**Tümör Belirteçleri:**")
                st.write(f"PSA: {lab_results['psa'] or 'N/A'}")
                st.write(f"CEA: {lab_results['cea']} ng/mL")
                st.write(f"CA125: {lab_results['ca125'] or 'N/A'}")
            
            with col3:
                st.write("**Tam Kan Sayımı:**")
                st.write(f"Hemoglobin: {lab_results['hemoglobin']} g/dL")
                st.write(f"WBC: {lab_results['wbc']} K/μL")
                st.write(f"Trombosit: {lab_results['platelets']} K/μL")
    
    # İlaç listesi
    st.subheader("İlaç Listesi")
    
    if st.button("💊 İlaç Listesini Getir"):
        with st.spinner("İlaç listesi getiriliyor..."):
            # Mock ilaç verisi
            medications = [
                {
                    "name": "Metformin",
                    "dosage": "500mg",
                    "frequency": "twice daily",
                    "start_date": "2024-01-10",
                    "status": "Active"
                },
                {
                    "name": "Aspirin",
                    "dosage": "100mg",
                    "frequency": "once daily",
                    "start_date": "2024-01-12",
                    "status": "Active"
                },
                {
                    "name": "Omeprazole",
                    "dosage": "20mg",
                    "frequency": "once daily",
                    "start_date": "2024-01-08",
                    "status": "Discontinued"
                }
            ]
            
            st.success("İlaç listesi getirildi!")
            
            # İlaçları tablo halinde göster
            st.write("**Aktif İlaçlar:**")
            for med in medications:
                if med['status'] == 'Active':
                    st.write(f"• {med['name']} {med['dosage']} - {med['frequency']}")
            
            st.write("**Durdurulan İlaçlar:**")
            for med in medications:
                if med['status'] == 'Discontinued':
                    st.write(f"• {med['name']} {med['dosage']} - {med['frequency']}")
    
    # Rapor entegrasyonu
    st.subheader("Rapor Entegrasyonu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Raporu HBYS'e Gönder"):
            with st.spinner("Rapor HBYS'e gönderiliyor..."):
                st.success("✅ Rapor başarıyla HBYS'e gönderildi")
    
    with col2:
        if st.button("📥 HBYS'den Rapor Al"):
            with st.spinner("HBYS'den rapor alınıyor..."):
                st.success("✅ Rapor HBYS'den alındı")
    
    # Veri güncelleme
    st.subheader("Veri Güncelleme")
    
    update_type = st.selectbox(
        "Güncelleme Türü",
        ["Hasta Durumu", "Laboratuvar Sonuçları", "İlaç Listesi", "Rapor Durumu"]
    )
    
    update_value = st.text_input("Güncelleme Değeri", "Completed")
    
    if st.button("🔄 Veriyi Güncelle"):
        with st.spinner("Veri güncelleniyor..."):
            st.success(f"✅ {update_type} başarıyla güncellendi: {update_value}")
    
    # Log görüntüleme
    st.subheader("Entegrasyon Logları")
    
    if st.button("📋 Logları Görüntüle"):
        # Mock log verisi
        logs = [
            {
                "timestamp": "2024-01-15 10:30:00",
                "action": "Hasta verisi alındı",
                "status": "Success",
                "details": "P-001 hasta bilgileri başarıyla alındı"
            },
            {
                "timestamp": "2024-01-15 10:25:00",
                "action": "Laboratuvar sonuçları senkronize edildi",
                "status": "Success",
                "details": "Tüm laboratuvar sonuçları güncellendi"
            },
            {
                "timestamp": "2024-01-15 10:20:00",
                "action": "Rapor HBYS'e gönderildi",
                "status": "Success",
                "details": "PET/CT raporu başarıyla gönderildi"
            }
        ]
        
        for log in logs:
            if log['status'] == 'Success':
                st.success(f"✅ {log['timestamp']} - {log['action']}")
            else:
                st.error(f"❌ {log['timestamp']} - {log['action']}")
            st.write(f"   {log['details']}")
            st.write("---")


