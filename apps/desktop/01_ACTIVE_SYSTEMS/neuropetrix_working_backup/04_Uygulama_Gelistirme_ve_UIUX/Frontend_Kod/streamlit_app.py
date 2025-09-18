import streamlit as st
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="NeuroPETrix - AI-Powered PET-CT Analysis",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = Path(__file__).parent / "assets" / "styles.css"
if css_path.exists():
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize session state
if "current_workflow" not in st.session_state:
    st.session_state["current_workflow"] = "dashboard"
if "demo_mode" not in st.session_state:
    st.session_state["demo_mode"] = True

# Sidebar configuration
with st.sidebar:
    st.title("🧠 NeuroPETrix")
    st.markdown("**AI-Powered PET-CT Analysis Platform**")
    st.markdown("---")
    
    # Backend URL configuration
    if "backend_url" not in st.session_state:
        st.session_state["backend_url"] = "http://127.0.0.1:8000"
    
    backend = st.text_input("Backend URL", st.session_state["backend_url"])
    st.session_state["backend_url"] = backend
    
    # Demo Mode Toggle
    demo_mode = st.toggle("🎭 Demo Mode", value=st.session_state["demo_mode"])
    st.session_state["demo_mode"] = demo_mode
    
    st.markdown("---")
    
    # Navigation
    st.header("🧭 Navigation")
    
    if st.button("🏠 Dashboard", use_container_width=True, type="primary"):
        st.session_state["current_workflow"] = "dashboard"
        st.rerun()
    
    if st.button("🔬 GRADE Scoring", use_container_width=True):
        st.switch_page("pages/01_GRADE_Ön_Tarama.py")
    
    if st.button("📊 AI Analysis", use_container_width=True):
        st.switch_page("pages/05_AI_Analysis.py")
    
    if st.button("📝 Report Generation", use_container_width=True):
        st.switch_page("pages/02_Rapor_Üretimi.py")
    
    if st.button("🏥 HBYS Integration", use_container_width=True):
        st.switch_page("pages/03_HBYS_Entegrasyon.py")
    
    if st.button("📁 DICOM Upload", use_container_width=True):
        st.switch_page("pages/04_DICOM_Upload.py")
    
    if st.button("📈 TSNM Reports", use_container_width=True):
        st.switch_page("pages/06_TSNM_Reports.py")
    
    if st.button("🎤 ASR Panel", use_container_width=True):
        st.switch_page("pages/07_ASR_Panel.py")
    
    if st.button("📈 SUV Trend", use_container_width=True):
        st.switch_page("pages/08_SUV_Trend.py")
    
    if st.button("📚 Evidence Panel", use_container_width=True):
        st.switch_page("pages/09_Evidence_Panel.py")
    
    st.markdown("---")
    
    # System status
    st.header("📊 System Status")
    try:
        health_response = requests.get(f"{backend}/health", timeout=3)
        if health_response.status_code == 200:
            st.success("🟢 Backend OK")
            health_data = health_response.json()
            st.caption(f"Last check: {health_data.get('timestamp', 'N/A')}")
        else:
            st.error("🔴 Backend Error")
    except:
        st.error("🔌 Backend Offline")
        if st.session_state["demo_mode"]:
            st.info("🎭 Demo mode active - using mock data")

# Main content based on workflow
if st.session_state["current_workflow"] == "dashboard":
    # ---- HERO SECTION ----
    col_hero1, col_hero2 = st.columns([2, 1])
    
    with col_hero1:
        st.markdown("""
        <div class="hero">
            <div>
                <h1>🧠 NeuroPETrix AI Platform</h1>
                <div class="subtitle">Intelligent PET-CT Analysis & Clinical Decision Support</div>
            </div>
            <div>
                <span class="badge ok">AI Ready</span>
                <span class="badge">Clinical Grade</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_hero2:
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("🚀 Start New Analysis", type="primary", use_container_width=True):
            st.session_state["current_workflow"] = "new_analysis"
            st.rerun()
        
        if st.button("📊 View Dashboard", use_container_width=True):
            st.switch_page("pages/00_Dashboard.py")
    
    st.write("")
    
    # ---- MAIN DASHBOARD ----
    st.header("📊 System Overview")
    
    # Metrics row
    col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
    
    with col_metrics1:
        if st.session_state["demo_mode"]:
            st.metric("📈 Total Cases", "1,247", "+12%")
        else:
            try:
                # Get real metrics from backend
                response = requests.get(f"{backend}/metrics", timeout=5)
                if response.status_code == 200:
                    metrics = response.json()
                    st.metric("📈 Total Cases", metrics.get("total_cases", "N/A"))
                else:
                    st.metric("📈 Total Cases", "N/A")
            except:
                st.metric("📈 Total Cases", "N/A")
    
    with col_metrics2:
        if st.session_state["demo_mode"]:
            st.metric("🤖 AI Analyses", "892", "+8%")
        else:
            st.metric("🤖 AI Analyses", "N/A")
    
    with col_metrics3:
        if st.session_state["demo_mode"]:
            st.metric("📝 Reports", "1,156", "+15%")
        else:
            st.metric("📝 Reports", "N/A")
    
    with col_metrics4:
        if st.session_state["demo_mode"]:
            st.metric("⏱️ Avg. Time", "2.3 min", "-18%")
        else:
            st.metric("⏱️ Avg. Time", "N/A")
    
    st.write("")
    
    # ---- FEATURE HIGHLIGHTS ----
    st.header("🚀 Feature Highlights")
    
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    
    with col_feat1:
        st.markdown("**🎤 ASR Panel**")
        st.markdown("Speech recognition and dictation system with Whisper AI")
        if st.button("🎤 Go to ASR", key="asr_main"):
            st.switch_page("pages/07_ASR_Panel.py")
    
    with col_feat2:
        st.markdown("**📈 SUV Trend**")
        st.markdown("SUV value tracking and trend analysis over time")
        if st.button("📈 Go to SUV Trend", key="suv_main"):
            st.switch_page("pages/08_SUV_Trend.py")
    
    with col_feat3:
        st.markdown("**📚 Evidence Panel**")
        st.markdown("Evidence-based clinical decision support with PICO")
        if st.button("📚 Go to Evidence", key="evidence_main"):
            st.switch_page("pages/09_Evidence_Panel.py")
    
    st.write("")
    
    # ---- WORKFLOW OVERVIEW ----
    st.header("🔄 Clinical Workflow")
    
    col_workflow1, col_workflow2 = st.columns(2)
    
    with col_workflow1:
        st.markdown("### 📋 Current Workflow Status")
        
        # Workflow steps
        workflow_steps = [
            {"step": "1", "title": "Patient Registration", "status": "✅", "description": "HBYS integration"},
            {"step": "2", "title": "DICOM Upload", "status": "✅", "description": "PET/CT images"},
            {"step": "3", "title": "AI Analysis", "status": "🔄", "description": "In progress"},
            {"step": "4", "title": "Report Generation", "status": "⏳", "description": "Pending"},
            {"step": "5", "title": "Clinical Review", "status": "⏳", "description": "Pending"}
        ]
        
        for step in workflow_steps:
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.2rem;">{step['status']}</span>
                    <div>
                        <strong>Step {step['step']}: {step['title']}</strong><br>
                        <small>{step['description']}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_workflow2:
        st.markdown("### 🎯 Recent Activities")
        
        if st.session_state["demo_mode"]:
            activities = [
                {"time": "2 min ago", "action": "AI Analysis started", "patient": "Case #1234"},
                {"time": "5 min ago", "action": "DICOM upload completed", "patient": "Case #1233"},
                {"time": "12 min ago", "action": "Report generated", "patient": "Case #1232"},
                {"time": "18 min ago", "action": "Patient registered", "patient": "Case #1231"}
            ]
            
            for activity in activities:
                st.markdown(f"""
                <div class="card">
                    <small style="color: #6b7280;">{activity['time']}</small><br>
                    <strong>{activity['action']}</strong><br>
                    <small>{activity['patient']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.write("")
    
    # ---- AI CAPABILITIES ----
    st.header("🤖 AI Capabilities")
    
    col_ai1, col_ai2, col_ai3 = st.columns(3)
    
    with col_ai1:
        st.markdown("""
        <div class="card">
            <div class="icon">🔬</div>
            <h3>GRADE Scoring</h3>
            <p>Literature quality assessment using AI-powered GRADE methodology</p>
            <strong>Accuracy: 94.2%</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col_ai2:
        st.markdown("""
        <div class="card">
            <div class="icon">📊</div>
            <h3>Image Segmentation</h3>
            <p>MONAI-powered PET/CT image segmentation and analysis</p>
            <strong>Dice Score: 0.89</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col_ai3:
        st.markdown("""
        <div class="card">
            <div class="icon">🧮</div>
            <h3>Radiomics Analysis</h3>
            <p>PyRadiomics feature extraction and clinical correlation</p>
            <strong>Features: 1,316</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # ---- PERFORMANCE CHARTS ----
    st.header("📈 Performance Analytics")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 Daily Case Volume")
        
        if st.session_state["demo_mode"]:
            # Demo data
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            cases = np.random.randint(15, 45, 30)
            
            fig = px.line(x=dates, y=cases, 
                         title="Daily Case Volume (Last 30 Days)",
                         labels={'x': 'Date', 'y': 'Cases'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        st.subheader("🎯 AI Analysis Success Rate")
        
        if st.session_state["demo_mode"]:
            # Demo data
            categories = ['Segmentation', 'Radiomics', 'GRADE', 'Clinical']
            success_rates = [94.2, 91.8, 96.5, 89.3]
            
            fig = px.bar(x=categories, y=success_rates,
                        title="AI Analysis Success Rates (%)",
                        labels={'x': 'Analysis Type', 'y': 'Success Rate (%)'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    st.write("")
    
    # ---- QUICK ACTIONS ----
    st.header("⚡ Quick Actions")
    
    col_action1, col_action2, col_action3, col_action4 = st.columns(4)
    
    with col_action1:
        if st.button("🔬 Start GRADE Analysis", use_container_width=True):
            st.switch_page("pages/01_GRADE_Ön_Tarama.py")
    
    with col_action2:
        if st.button("📁 Upload DICOM", use_container_width=True):
            st.switch_page("pages/04_DICOM_Upload.py")
    
    with col_action3:
        if st.button("🤖 AI Analysis", use_container_width=True):
            st.switch_page("pages/05_AI_Analysis.py")
    
    with col_action4:
        if st.button("📝 Generate Report", use_container_width=True):
            st.switch_page("pages/02_Rapor_Üretimi.py")

elif st.session_state["current_workflow"] == "new_analysis":
    st.header("🚀 New Analysis Workflow")
    st.info("Starting new clinical analysis workflow...")
    
    # Workflow steps
    steps = ["Patient Registration", "DICOM Upload", "AI Analysis", "Report Generation"]
    current_step = st.selectbox("Select starting step:", steps)
    
    if st.button("Continue to Selected Step"):
        if current_step == "Patient Registration":
            st.switch_page("pages/03_HBYS_Entegrasyon.py")
        elif current_step == "DICOM Upload":
            st.switch_page("pages/04_DICOM_Upload.py")
        elif current_step == "AI Analysis":
            st.switch_page("pages/05_AI_Analysis.py")
        elif current_step == "Report Generation":
            st.switch_page("pages/02_Rapor_Üretimi.py")

# Footer
st.markdown("---")
st.markdown("**NeuroPETrix v2.0.0** - AI-Powered Medical Imaging Analysis Platform")
st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
