"""
🧩 NeuroPETRIX - Entegrasyon Akışı
Tek tıkla vaka başlatma ve job durumu takibi
"""

import streamlit as st
import requests
import time
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Integration Workflow",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🧩 Entegrasyon Akışı")
st.markdown("**Tek tıkla vaka başlatma ve job durumu takibi**")

# API configuration
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

# Sidebar
with st.sidebar:
    st.header("⚙️ Konfigürasyon")
    st.info(f"**API Base**: {API_BASE}")
    
    st.header("📊 Job Yönetimi")
    if st.button("🗑️ Tamamlanan Job'ları Temizle"):
        try:
            # Job clear endpoint'i yok, session state'i temizle
            if "last_workflow" in st.session_state:
                del st.session_state.last_workflow
            if "job_status" in st.session_state:
                del st.session_state.job_status
            st.success("Job'lar temizlendi!")
            st.rerun()
        except Exception as e:
            st.error(f"Job temizleme hatası: {e}")
    
    st.header("📈 Sistem Durumu")
    try:
        health_response = requests.get(f"{API_BASE}/health", timeout=3)
        if health_response.ok:
            st.success("✅ Backend")
        else:
            st.error("❌ Backend")
    except:
        st.error("❌ Backend")

# Main content
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🚀 Vaka Başlat")
    
    # Form
    patient_id = st.text_input("Hasta ID (opsiyonel)", "")
    purpose = st.selectbox("Klinik Amaç", ["staging", "diagnosis", "followup"], index=0)
    icd_code = st.text_input("ICD-10 (opsiyonel)", "C34.9")
    
    # Start button
    if st.button("🚀 Vaka Başlat", type="primary", use_container_width=True):
        with st.spinner("Vaka başlatılıyor..."):
            try:
                payload = {
                    "patient_id": patient_id if patient_id else None,
                    "purpose": purpose,
                    "icd_code": icd_code if icd_code else None
                }
                
                response = requests.post(
                    f"{API_BASE}/integration/workflow/start",
                    json=payload,
                    timeout=10
                )
                
                if response.ok:
                    result = response.json()
                    st.session_state.last_workflow = result
                    st.success("✅ Vaka başarıyla başlatıldı!")
                    st.rerun()
                else:
                    st.error(f"❌ Vaka başlatma hatası: {response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ Sistem hatası: {e}")

with col2:
    st.header("📋 Vaka Durumu")
    
    # Display last workflow
    if "last_workflow" in st.session_state:
        data = st.session_state.last_workflow
        
        # Info box
        st.info(f"""
        **Case ID**: {data.get('case_id', 'N/A')}  
        **Job ID**: {data.get('job_id', 'N/A')}  
        **Status**: {data.get('workflow', {}).get('status', 'N/A')}
        """)
        
        # Job status monitoring
        if "job_id" in data:
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("🔄 Durumu Güncelle", use_container_width=True):
                    try:
                        status_response = requests.get(
                            f"{API_BASE}/integration/workflow/job/{data['job_id']}", 
                            timeout=5
                        )
                        if status_response.ok:
                            job_status = status_response.json()
                            st.session_state.job_status = job_status
                        else:
                            st.error("Job durumu alınamadı")
                    except Exception as e:
                        st.error(f"Job durumu hatası: {e}")
            
            with col_b:
                if st.button("📊 Detayları Göster", use_container_width=True):
                    st.session_state.show_details = True
            
            # Display job status
            if "job_status" in st.session_state:
                job = st.session_state.job_status
                
                # Status indicator
                status_color = {
                    "queued": "🟡",
                    "running": "🔵", 
                    "done": "🟢",
                    "failed": "🔴"
                }.get(job.get("status"), "⚪")
                
                st.metric(
                    "Job Durumu",
                    f"{status_color} {job.get('status', 'unknown').upper()}"
                )
                
                # Job details
                if job.get("status") == "done":
                    st.success("✅ Job tamamlandı!")
                    if "result" in job:
                        st.json(job["result"])
                elif job.get("status") == "failed":
                    st.error("❌ Job başarısız!")
                    if "error" in job:
                        st.error(f"Hata: {job['error']}")
                elif job.get("status") == "running":
                    st.info("🔄 Job çalışıyor...")
                else:
                    st.info("⏳ Job kuyrukta bekliyor...")
            
            # Show details
            if st.session_state.get("show_details", False):
                st.subheader("📊 Job Detayları")
                if "last_workflow" in st.session_state:
                    st.json(st.session_state.last_workflow)
    else:
        st.info("🎯 Lütfen sol taraftan yeni bir vaka başlatın")

# Bottom section
st.markdown("---")
st.subheader("📊 Sistem Metrikleri")

col3, col4, col5 = st.columns(3)

with col3:
    try:
        metrics_response = requests.get(f"{API_BASE}/metrics/health", timeout=3)
        if metrics_response.ok:
            st.success("✅ Metrics aktif")
        else:
            st.warning("⚠️ Metrics pasif")
    except:
        st.error("❌ Metrics erişilemiyor")

with col4:
    try:
        fhir_response = requests.get(f"{API_BASE}/fhir/health", timeout=3)
        if fhir_response.ok:
            fhir_status = fhir_response.json()
            if fhir_status.get("status") == "connected":
                st.success("✅ FHIR bağlı")
            else:
                st.warning(f"⚠️ FHIR: {fhir_status.get('status')}")
        else:
            st.warning("⚠️ FHIR pasif")
    except:
        st.error("❌ FHIR erişilemiyor")

with col5:
    try:
        # Job stats (if available)
        st.info("📈 Job istatistikleri")
    except:
        st.info("📈 Job stats")

# Auto-refresh for running jobs
if "last_workflow" in st.session_state and "job_id" in st.session_state.last_workflow:
    if st.session_state.get("job_status", {}).get("status") == "running":
        time.sleep(2)
        st.rerun()

