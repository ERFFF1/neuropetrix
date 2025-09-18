"""
📊 NeuroPETRIX - Performance Monitor
Real-time system monitoring ve metrics dashboard
"""

import streamlit as st
import requests
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import os

# Page config
st.set_page_config(
    page_title="Performance Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📊 Performance Monitor")
st.markdown("**Real-time system monitoring ve metrics dashboard**")

# API configuration
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

# Sidebar
with st.sidebar:
    st.header("⚙️ Konfigürasyon")
    st.info(f"**API Base**: {API_BASE}")
    
    st.header("🔄 Auto Refresh")
    auto_refresh = st.checkbox("Otomatik Yenile", value=True)
    refresh_interval = st.slider("Yenileme Aralığı (saniye)", 1, 30, 5)
    
    st.header("📈 Metrik Seçimi")
    show_requests = st.checkbox("Request Metrikleri", value=True)
    show_workflows = st.checkbox("Workflow Metrikleri", value=True)
    show_system = st.checkbox("Sistem Metrikleri", value=True)

# Helper functions
@st.cache_data(ttl=5)
def get_metrics_data():
    """Metrics verilerini çek"""
    try:
        response = requests.get(f"{API_BASE}/metrics/health", timeout=3)
        if response.ok:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=10)
def get_workflow_cases():
    """Workflow case'lerini çek"""
    try:
        response = requests.get(f"{API_BASE}/integration/workflow/cases", timeout=5)
        if response.ok:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=5)
def get_system_health():
    """Sistem sağlık durumunu çek"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=3)
        if response.ok:
            return response.json()
        return None
    except:
        return None

# Main content
col1, col2, col3, col4 = st.columns(4)

# System Health Cards
with col1:
    st.subheader("🏥 Sistem Sağlığı")
    health_data = get_system_health()
    if health_data:
        st.success("✅ Backend Aktif")
        st.info(f"**Versiyon**: {health_data.get('version', 'N/A')}")
    else:
        st.error("❌ Backend Pasif")

with col2:
    st.subheader("📊 Metrics")
    metrics_data = get_metrics_data()
    if metrics_data:
        st.success("✅ Metrics Aktif")
        st.info(f"**Durum**: {metrics_data.get('status', 'N/A')}")
    else:
        st.warning("⚠️ Metrics Pasif")

with col3:
    st.subheader("🧩 Workflow")
    workflow_data = get_workflow_cases()
    if workflow_data:
        total_cases = workflow_data.get('total', 0)
        st.success(f"✅ {total_cases} Case")
        st.info("**Database Aktif**")
    else:
        st.warning("⚠️ Workflow Pasif")

with col4:
    st.subheader("⏱️ Uptime")
    st.info("**Sistem**: Aktif")
    st.info(f"**Son Güncelleme**: {datetime.now().strftime('%H:%M:%S')}")

# Metrics Charts
st.markdown("---")
st.subheader("📈 Real-time Metrics")

if show_requests:
    st.subheader("🌐 Request Metrikleri")
    
    # Mock request data (gerçek implementasyonda Prometheus'dan çekilecek)
    request_data = {
        'endpoint': ['/health', '/integration/workflow/start', '/cases', '/pico-monai', '/evidence'],
        'requests': [150, 45, 23, 12, 8],
        'avg_response_time': [50, 1200, 200, 800, 600]
    }
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Request count chart
        fig_requests = px.bar(
            x=request_data['endpoint'],
            y=request_data['requests'],
            title="Request Sayısı (Son 1 saat)",
            labels={'x': 'Endpoint', 'y': 'Request Sayısı'}
        )
        st.plotly_chart(fig_requests, use_container_width=True)
    
    with col_b:
        # Response time chart
        fig_response = px.bar(
            x=request_data['endpoint'],
            y=request_data['avg_response_time'],
            title="Ortalama Response Time (ms)",
            labels={'x': 'Endpoint', 'y': 'Response Time (ms)'}
        )
        st.plotly_chart(fig_response, use_container_width=True)

if show_workflows:
    st.subheader("🧩 Workflow Metrikleri")
    
    workflow_data = get_workflow_cases()
    if workflow_data and workflow_data.get('cases'):
        cases = workflow_data['cases']
        
        # Workflow status distribution
        status_counts = {}
        purpose_counts = {}
        
        for case in cases:
            status = case.get('status', 'unknown')
            purpose = case.get('purpose', 'unknown')
            
            status_counts[status] = status_counts.get(status, 0) + 1
            purpose_counts[purpose] = purpose_counts.get(purpose, 0) + 1
        
        col_c, col_d = st.columns(2)
        
        with col_c:
            # Status distribution
            if status_counts:
                fig_status = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    title="Case Status Dağılımı"
                )
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col_d:
            # Purpose distribution
            if purpose_counts:
                fig_purpose = px.pie(
                    values=list(purpose_counts.values()),
                    names=list(purpose_counts.keys()),
                    title="Klinik Amaç Dağılımı"
                )
                st.plotly_chart(fig_purpose, use_container_width=True)
        
        # Recent cases table
        st.subheader("📋 Son Case'ler")
        df_cases = pd.DataFrame(cases)
        if not df_cases.empty:
            # Format datetime columns
            if 'created_at' in df_cases.columns:
                df_cases['created_at'] = pd.to_datetime(df_cases['created_at'])
            
            # Select and display columns
            display_columns = ['case_id', 'patient_id', 'purpose', 'status', 'created_at']
            available_columns = [col for col in display_columns if col in df_cases.columns]
            
            st.dataframe(
                df_cases[available_columns],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("Henüz workflow case'i bulunmuyor")

if show_system:
    st.subheader("💻 Sistem Metrikleri")
    
    # Mock system metrics
    system_metrics = {
        'CPU Usage': 45,
        'Memory Usage': 62,
        'Disk Usage': 38,
        'Network I/O': 23
    }
    
    col_e, col_f = st.columns(2)
    
    with col_e:
        # System metrics gauge
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = system_metrics['CPU Usage'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "CPU Kullanımı (%)"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col_f:
        # Memory usage
        fig_memory = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = system_metrics['Memory Usage'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Memory Kullanımı (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 60], 'color': "lightgray"},
                    {'range': [60, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ]
            }
        ))
        fig_memory.update_layout(height=300)
        st.plotly_chart(fig_memory, use_container_width=True)

# Auto refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**📊 NeuroPETRIX Performance Monitor** - Real-time system monitoring")

