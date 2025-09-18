import streamlit as st
import requests
import json
import psutil
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(
    page_title="System Monitor - NeuroPETrix",
    page_icon="📊",
    layout="wide"
)

# Page title
st.title("📊 System Monitor - Sistem İzleme ve Performans")
st.markdown("**Real-time sistem durumu, performans metrikleri ve kaynak kullanımı**")

# Backend URL configuration
if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = "http://127.0.0.1:8000"

backend_url = st.sidebar.text_input("Backend URL", st.session_state["backend_url"])
st.session_state["backend_url"] = st.session_state["backend_url"]

# Sidebar navigation
st.sidebar.title("🧭 Hızlı Navigasyon")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Ana Sayfa", key="monitor_nav_home", use_container_width=True):
    st.switch_page("streamlit_app.py")

if st.sidebar.button("📊 Dashboard", key="monitor_nav_dashboard", use_container_width=True):
    st.switch_page("pages/00_Dashboard.py")

if st.sidebar.button("🔧 Script Management", key="monitor_nav_script", use_container_width=True):
    st.switch_page("pages/10_Script_Management.py")

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
if "monitor_data" not in st.session_state:
    st.session_state["monitor_data"] = []

# ---- REAL-TIME METRICS ----
st.header("🔄 Real-Time Sistem Metrikleri")

col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)

with col_metrics1:
    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    st.metric("🖥️ CPU Kullanımı", f"{cpu_percent}%")
    
    # CPU cores
    cpu_count = psutil.cpu_count()
    st.caption(f"Çekirdek: {cpu_count}")

with col_metrics2:
    # Memory Usage
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    st.metric("🧠 RAM Kullanımı", f"{memory_percent}%")
    
    # Memory details
    memory_gb = memory.used / (1024**3)
    memory_total_gb = memory.total / (1024**3)
    st.caption(f"Kullanılan: {memory_gb:.1f}GB / {memory_total_gb:.1f}GB")

with col_metrics3:
    # Disk Usage
    disk = psutil.disk_usage('/')
    disk_percent = (disk.used / disk.total) * 100
    st.metric("💾 Disk Kullanımı", f"{disk_percent:.1f}%")
    
    # Disk details
    disk_gb = disk.used / (1024**3)
    disk_total_gb = disk.total / (1024**3)
    st.caption(f"Kullanılan: {disk_gb:.1f}GB / {disk_total_gb:.1f}GB")

with col_metrics4:
    # Network
    try:
        network = psutil.net_io_counters()
        network_mb = network.bytes_sent / (1024**2)
        st.metric("🌐 Ağ Trafiği", f"{network_mb:.1f}MB")
        st.caption("Gönderilen veri")
    except:
        st.metric("🌐 Ağ Trafiği", "N/A")

st.write("")

# ---- PERFORMANCE CHARTS ----
st.header("📈 Performans Grafikleri")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # CPU Trend
    st.subheader("🖥️ CPU Kullanım Trendi")
    
    # Mock CPU data (in real system, this would come from monitoring)
    cpu_data = {
        'time': pd.date_range(start='2025-01-24 00:00', periods=24, freq='H'),
        'cpu': [45, 52, 38, 67, 73, 81, 89, 92, 88, 76, 65, 58, 45, 52, 38, 67, 73, 81, 89, 92, 88, 76, 65, 58]
    }
    
    df_cpu = pd.DataFrame(cpu_data)
    
    fig_cpu = px.line(df_cpu, x='time', y='cpu', title='24 Saatlik CPU Kullanımı')
    fig_cpu.update_layout(height=400)
    st.plotly_chart(fig_cpu, use_container_width=True)

with col_chart2:
    # Memory Trend
    st.subheader("🧠 RAM Kullanım Trendi")
    
    # Mock memory data
    memory_data = {
        'time': pd.date_range(start='2025-01-24 00:00', periods=24, freq='H'),
        'memory': [67, 72, 68, 75, 78, 82, 85, 88, 86, 83, 79, 76, 67, 72, 68, 75, 78, 82, 85, 88, 86, 83, 79, 76]
    }
    
    df_memory = pd.DataFrame(memory_data)
    
    fig_memory = px.line(df_memory, x='time', y='memory', title='24 Saatlik RAM Kullanımı')
    fig_memory.update_layout(height=400)
    st.plotly_chart(fig_memory, use_container_width=True)

st.write("")

# ---- PROCESS MONITORING ----
st.header("🔍 Süreç İzleme")

col_process1, col_process2 = st.columns(2)

with col_process1:
    st.subheader("📊 Aktif Süreçler")
    
    # Get top processes by CPU usage
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        top_processes = processes[:10]
        
        # Create DataFrame
        df_processes = pd.DataFrame(top_processes)
        df_processes = df_processes[df_processes['cpu_percent'] > 0]  # Filter out 0% processes
        
        if not df_processes.empty:
            st.dataframe(df_processes, use_container_width=True)
        else:
            st.info("📊 Aktif süreç bulunamadı")
            
    except Exception as e:
        st.error(f"❌ Süreç bilgisi alınamadı: {e}")

with col_process2:
    st.subheader("🌐 Port Kullanımı")
    
    # Check specific ports
    ports_to_check = [8000, 8501, 5432, 3306]
    
    port_status = []
    for port in ports_to_check:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                port_status.append({"Port": port, "Durum": "🟢 Açık", "Servis": "Aktif"})
            else:
                port_status.append({"Port": port, "Durum": "🔴 Kapalı", "Servis": "Pasif"})
        except:
            port_status.append({"Port": port, "Durum": "❓ Bilinmiyor", "Servis": "N/A"})
    
    df_ports = pd.DataFrame(port_status)
    st.dataframe(df_ports, use_container_width=True)

st.write("")

# ---- SYSTEM ACTIONS ----
st.header("🔧 Sistem İşlemleri")

col_action1, col_action2, col_action3 = st.columns(3)

with col_action1:
    if st.button("🔄 Metrikleri Yenile", key="monitor_refresh", type="primary", use_container_width=True):
        st.rerun()

with col_action2:
    if st.button("📊 Log Dosyalarını Göster", key="monitor_logs", use_container_width=True):
        st.info("📊 Log dosyaları yakında eklenecek")

with col_action3:
    if st.button("⚡ Sistem Optimizasyonu", key="monitor_optimize", use_container_width=True):
        st.info("⚡ Sistem optimizasyonu yakında eklenecek")

# ---- ALERT SYSTEM ----
st.header("🚨 Uyarı Sistemi")

# Check for critical thresholds
alerts = []

if cpu_percent > 80:
    alerts.append({"Seviye": "🔴 Kritik", "Mesaj": f"CPU kullanımı yüksek: {cpu_percent}%"})

if memory_percent > 85:
    alerts.append({"Seviye": "🟡 Uyarı", "Mesaj": f"RAM kullanımı yüksek: {memory_percent}%"})

if disk_percent > 90:
    alerts.append({"Seviye": "🔴 Kritik", "Mesaj": f"Disk kullanımı kritik: {disk_percent:.1f}%"})

if alerts:
    for alert in alerts:
        if "🔴 Kritik" in alert["Seviye"]:
            st.error(f"{alert['Seviye']} {alert['Mesaj']}")
        else:
            st.warning(f"{alert['Seviye']} {alert['Mesaj']}")
else:
    st.success("✅ Tüm sistem metrikleri normal seviyede")

# Footer
st.markdown("---")
st.markdown("**System Monitor v1.0** - Real-time sistem izleme ve performans analizi")














