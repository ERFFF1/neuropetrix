"""
Performance Monitor Sayfası
NeuroPETRIX v3.0 - Sistem Performans İzleme
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from datetime import datetime, timedelta
import sys
from pathlib import Path

def performance_monitor_page():
    st.title("📊 Performance Monitor")
    st.markdown("### Sistem Performans İzleme ve Analiz")
    
    # Performance Monitor'ü import et
    try:
        sys.path.append(str(Path(__file__).parent.parent.parent / "06_INTEGRATION" / "Performance_Monitor"))
        from performance_monitor import get_system_status, get_performance_summary, start_performance_monitoring, stop_performance_monitoring
        
        # Monitoring kontrolü
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🟢 Monitoring Başlat", type="primary"):
                start_performance_monitoring(30)  # 30 saniye interval
                st.success("Performance monitoring başlatıldı!")
        
        with col2:
            if st.button("🔴 Monitoring Durdur"):
                stop_performance_monitoring()
                st.warning("Performance monitoring durduruldu!")
        
        with col3:
            if st.button("🔄 Verileri Yenile"):
                st.rerun()
        
        st.markdown("---")
        
        # Sistem durumu
        st.subheader("🖥️ Sistem Durumu")
        
        try:
            status = get_system_status()
            
            if "error" in status:
                st.error(f"Sistem durumu alınamadı: {status['error']}")
                return
            
            # Sistem metrikleri
            system = status.get("system", {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                cpu_percent = system.get("cpu_percent", 0)
                st.metric(
                    label="CPU Kullanımı",
                    value=f"{cpu_percent:.1f}%",
                    delta=None
                )
                
                # CPU gauge
                fig_cpu = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = cpu_percent,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "CPU %"},
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
                fig_cpu.update_layout(height=200)
                st.plotly_chart(fig_cpu, use_container_width=True)
            
            with col2:
                memory_percent = system.get("memory_percent", 0)
                st.metric(
                    label="Bellek Kullanımı",
                    value=f"{memory_percent:.1f}%",
                    delta=None
                )
                
                # Memory gauge
                fig_memory = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = memory_percent,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Memory %"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkgreen"},
                        'steps': [
                            {'range': [0, 60], 'color': "lightgray"},
                            {'range': [60, 85], 'color': "yellow"},
                            {'range': [85, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig_memory.update_layout(height=200)
                st.plotly_chart(fig_memory, use_container_width=True)
            
            with col3:
                disk_percent = system.get("disk_percent", 0)
                st.metric(
                    label="Disk Kullanımı",
                    value=f"{disk_percent:.1f}%",
                    delta=None
                )
                
                # Disk gauge
                fig_disk = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = disk_percent,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Disk %"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkorange"},
                        'steps': [
                            {'range': [0, 70], 'color': "lightgray"},
                            {'range': [70, 90], 'color': "yellow"},
                            {'range': [90, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 95
                        }
                    }
                ))
                fig_disk.update_layout(height=200)
                st.plotly_chart(fig_disk, use_container_width=True)
            
            with col4:
                connections = system.get("active_connections", 0)
                st.metric(
                    label="Aktif Bağlantılar",
                    value=connections,
                    delta=None
                )
                
                # Connections bar
                fig_conn = go.Figure(go.Bar(
                    x=['Aktif Bağlantılar'],
                    y=[connections],
                    marker_color='lightblue'
                ))
                fig_conn.update_layout(
                    height=200,
                    showlegend=False,
                    yaxis_title="Bağlantı Sayısı"
                )
                st.plotly_chart(fig_conn, use_container_width=True)
            
            st.markdown("---")
            
            # API Endpoints durumu
            st.subheader("🌐 API Endpoints Durumu")
            
            api_endpoints = status.get("api_endpoints", [])
            if api_endpoints:
                df_api = pd.DataFrame(api_endpoints)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Response time chart
                    fig_response = px.bar(
                        df_api, 
                        x='endpoint', 
                        y='response_time',
                        title="API Response Time (ms)",
                        color='response_time',
                        color_continuous_scale='RdYlGn_r'
                    )
                    fig_response.update_layout(height=400)
                    st.plotly_chart(fig_response, use_container_width=True)
                
                with col2:
                    # Status code chart
                    fig_status = px.bar(
                        df_api, 
                        x='endpoint', 
                        y='status_code',
                        title="API Status Codes",
                        color='status_code',
                        color_continuous_scale='RdYlGn'
                    )
                    fig_status.update_layout(height=400)
                    st.plotly_chart(fig_status, use_container_width=True)
                
                # API tablosu
                st.dataframe(df_api, use_container_width=True)
            else:
                st.info("API endpoint verisi bulunamadı.")
            
            st.markdown("---")
            
            # Son hatalar
            st.subheader("⚠️ Son Hatalar")
            
            recent_errors = status.get("recent_errors", [])
            if recent_errors:
                df_errors = pd.DataFrame(recent_errors)
                st.dataframe(df_errors, use_container_width=True)
            else:
                st.success("Son 24 saatte hata kaydı bulunamadı.")
            
            st.markdown("---")
            
            # Performans özeti
            st.subheader("📈 Performans Özeti")
            
            # Zaman aralığı seçimi
            time_range = st.selectbox(
                "Zaman Aralığı",
                [1, 6, 12, 24, 48, 72],
                index=3,  # 24 saat default
                format_func=lambda x: f"Son {x} saat"
            )
            
            summary = get_performance_summary(time_range)
            
            if "error" in summary:
                st.error(f"Performans özeti alınamadı: {summary['error']}")
            else:
                # Sistem performansı
                system_perf = summary.get("system_performance", {})
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Ortalama CPU", f"{system_perf.get('avg_cpu_percent', 0):.1f}%")
                with col2:
                    st.metric("Ortalama Bellek", f"{system_perf.get('avg_memory_percent', 0):.1f}%")
                with col3:
                    st.metric("Ortalama Disk", f"{system_perf.get('avg_disk_percent', 0):.1f}%")
                with col4:
                    st.metric("Maksimum CPU", f"{system_perf.get('max_cpu_percent', 0):.1f}%")
                with col5:
                    st.metric("Hata Sayısı", summary.get("error_count", 0))
                
                # API performansı
                api_perf = summary.get("api_performance", [])
                if api_perf:
                    df_api_perf = pd.DataFrame(api_perf)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_avg_response = px.bar(
                            df_api_perf,
                            x='endpoint',
                            y='avg_response_time',
                            title=f"Ortalama Response Time (Son {time_range} saat)",
                            color='avg_response_time',
                            color_continuous_scale='RdYlGn_r'
                        )
                        st.plotly_chart(fig_avg_response, use_container_width=True)
                    
                    with col2:
                        fig_request_count = px.bar(
                            df_api_perf,
                            x='endpoint',
                            y='request_count',
                            title=f"Request Sayısı (Son {time_range} saat)",
                            color='request_count',
                            color_continuous_scale='Blues'
                        )
                        st.plotly_chart(fig_request_count, use_container_width=True)
            
        except Exception as e:
            st.error(f"Performance monitor hatası: {str(e)}")
            st.exception(e)
    
    except ImportError as e:
        st.error(f"Performance Monitor modülü yüklenemedi: {e}")
        st.info("Modül geliştirme aşamasında...")
        
        # Fallback - basit sistem durumu
        st.subheader("🖥️ Basit Sistem Durumu")
        
        import psutil
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cpu_percent = psutil.cpu_percent(interval=1)
            st.metric("CPU Kullanımı", f"{cpu_percent:.1f}%")
        
        with col2:
            memory = psutil.virtual_memory()
            st.metric("Bellek Kullanımı", f"{memory.percent:.1f}%")
        
        with col3:
            disk = psutil.disk_usage('/')
            st.metric("Disk Kullanımı", f"{disk.percent:.1f}%")
        
        with col4:
            connections = len(psutil.net_connections())
            st.metric("Aktif Bağlantılar", connections)

if __name__ == "__main__":
    performance_monitor_page()