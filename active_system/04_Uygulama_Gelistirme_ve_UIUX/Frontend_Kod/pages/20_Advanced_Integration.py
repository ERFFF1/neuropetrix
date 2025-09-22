"""
🧠 NeuroPETRIX v2.0 - Advanced Integration Workflow
PICO → MONAI → Evidence → Decision → Report tam entegrasyon
"""

import streamlit as st
import requests
import json
import time
import uuid
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Page config
st.set_page_config(
    page_title="Advanced Integration",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🔗 Advanced Integration Workflow")
st.markdown("**PICO → MONAI → Evidence → Decision → Report tam entegrasyon**")

# Initialize session state
if 'workflow_steps' not in st.session_state:
    st.session_state.workflow_steps = []
if 'current_case_id' not in st.session_state:
    st.session_state.current_case_id = None
if 'workflow_status' not in st.session_state:
    st.session_state.workflow_status = "idle"

# Sidebar
with st.sidebar:
    st.header("🎯 Workflow Kontrolü")
    
    # Case management
    st.subheader("📋 Vaka Yönetimi")
    
    if st.button("🆕 Yeni Vaka Başlat"):
        st.session_state.current_case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        st.session_state.workflow_steps = []
        st.session_state.workflow_status = "started"
        st.success(f"Yeni vaka başlatıldı: {st.session_state.current_case_id}")
    
    if st.session_state.current_case_id:
        st.info(f"📋 Aktif Vaka: {st.session_state.current_case_id}")
        
        if st.button("🔄 Workflow'u Sıfırla"):
            st.session_state.workflow_steps = []
            st.session_state.workflow_status = "idle"
            st.experimental_rerun()
    
    # Workflow configuration
    st.subheader("⚙️ Workflow Ayarları")
    
    clinical_goal = st.selectbox(
        "🎯 Klinik Hedef",
        ["diagnosis", "treatment", "prognosis", "follow_up"],
        index=0
    )
    
    workflow_mode = st.selectbox(
        "🖥️ Workflow Modu",
        ["desktop", "server", "cloud"],
        index=0
    )
    
    # Auto-execution
    auto_execute = st.checkbox("🤖 Otomatik Yürütme", value=False)
    
    if auto_execute:
        st.info("🤖 Workflow otomatik olarak yürütülecek")

# Main content
if st.session_state.current_case_id:
    st.header(f"📋 Vaka: {st.session_state.current_case_id}")
    
    # Workflow progress
    st.subheader("🔄 Workflow İlerlemesi")
    
    # Create workflow steps
    workflow_steps = [
        {"name": "1. PICO Tanımlama", "status": "pending", "icon": "🎯"},
        {"name": "2. HBYS Entegrasyonu", "status": "pending", "icon": "🏥"},
        {"name": "3. DICOM Yükleme", "status": "pending", "icon": "🖼️"},
        {"name": "4. MONAI Analizi", "status": "pending", "icon": "🧠"},
        {"name": "5. PyRadiomics", "status": "pending", "icon": "📊"},
        {"name": "6. SUV Trend", "status": "pending", "icon": "📈"},
        {"name": "7. Evidence Toplama", "status": "pending", "icon": "📚"},
        {"name": "8. GRADE Değerlendirme", "status": "pending", "icon": "⭐"},
        {"name": "9. Karar Desteği", "status": "pending", "icon": "🎯"},
        {"name": "10. Rapor Üretimi", "status": "pending", "icon": "📄"}
    ]
    
    # Display workflow steps
    cols = st.columns(5)
    for i, step in enumerate(workflow_steps):
        col_idx = i % 5
        with cols[col_idx]:
            if step["status"] == "completed":
                st.success(f"{step['icon']} {step['name']}")
            elif step["status"] == "processing":
                st.info(f"{step['icon']} {step['name']}")
            else:
                st.info(f"{step['icon']} {step['name']}")
    
    # Workflow execution
    st.subheader("⚡ Workflow Yürütme")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Workflow'u Başlat"):
            try:
                payload = {
                    "clinical_goal": clinical_goal,
                    "workflow_mode": workflow_mode,
                    "case_id": st.session_state.current_case_id
                }
                
                response = requests.post(
                    "http://127.0.0.1:8000/integration/workflow/start",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    st.success("✅ Workflow başlatıldı!")
                    st.session_state.workflow_status = "running"
                    
                    # Update first step
                    workflow_steps[0]["status"] = "completed"
                    st.session_state.workflow_steps = workflow_steps
                    
                else:
                    st.error(f"❌ Workflow başlatılamadı: {response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ Hata: {e}")
    
    with col2:
        if st.button("⏸️ Duraklat"):
            st.session_state.workflow_status = "paused"
            st.warning("⏸️ Workflow duraklatıldı")
    
    with col3:
        if st.button("⏹️ Durdur"):
            st.session_state.workflow_status = "stopped"
            st.error("⏹️ Workflow durduruldu")
    
    # Step-by-step execution
    if st.session_state.workflow_status == "running":
        st.subheader("🔧 Adım Adım Yürütme")
        
        # Execute each step
        for i, step in enumerate(workflow_steps):
            if step["status"] == "pending":
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"{step['icon']} {step['name']}")
                
                with col2:
                    if st.button(f"▶️ Çalıştır", key=f"step_{i}"):
                        # Simulate step execution
                        step["status"] = "processing"
                        st.session_state.workflow_steps = workflow_steps
                        
                        # Simulate processing time
                        with st.spinner(f"{step['name']} işleniyor..."):
                            time.sleep(2)
                        
                        # Mark as completed
                        step["status"] = "completed"
                        st.session_state.workflow_steps = workflow_steps
                        st.success(f"✅ {step['name']} tamamlandı!")
                        
                        # Auto-execute next step if enabled
                        if auto_execute and i < len(workflow_steps) - 1:
                            st.info("🤖 Sonraki adım otomatik başlatılıyor...")
                            time.sleep(1)
                            st.experimental_rerun()
                        
                        break
        
        # Check if all steps are completed
        if all(step["status"] == "completed" for step in workflow_steps):
            st.success("🎉 Tüm workflow adımları tamamlandı!")
            st.session_state.workflow_status = "completed"
    
    # Results display
    if st.session_state.workflow_status == "completed":
        st.subheader("📊 Sonuçlar")
        
        # Create sample results
        results = {
            "pico": {
                "patient": "65 yaş, erkek",
                "intervention": "PET/CT taraması",
                "comparison": "Önceki tarama ile",
                "outcome": "Tümör progresyonu"
            },
            "monai": {
                "segmentation_accuracy": "94.2%",
                "lesion_count": 3,
                "processing_time": "2.3s"
            },
            "radiomics": {
                "features_extracted": 156,
                "significant_features": 23,
                "classification_accuracy": "89.7%"
            },
            "suv_trend": {
                "baseline_suv": 8.5,
                "current_suv": 12.3,
                "change_percent": "+44.7%"
            },
            "evidence": {
                "papers_found": 47,
                "grade_quality": "B",
                "recommendation_strength": "Moderate"
            }
        }
        
        # Display results in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 PICO", "🧠 MONAI", "📊 Radiomics", "📈 SUV Trend", "📚 Evidence"
        ])
        
        with tab1:
            st.json(results["pico"])
            
        with tab2:
            st.json(results["monai"])
            
            # MONAI visualization
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Accuracy", "Speed", "Efficiency"],
                y=[94.2, 87.5, 91.8],
                name="MONAI Performance"
            ))
            fig.update_layout(title="MONAI Analiz Performansı")
            st.plotly_chart(fig, use_container_width=True)
            
        with tab3:
            st.json(results["radiomics"])
            
            # Radiomics features
            features_df = pd.DataFrame({
                "Feature": [f"Feature_{i}" for i in range(1, 11)],
                "Value": np.random.normal(0, 1, 10),
                "Significance": np.random.choice([True, False], 10, p=[0.3, 0.7])
            })
            
            st.dataframe(features_df)
            
        with tab4:
            st.json(results["suv_trend"])
            
            # SUV trend chart
            times = pd.date_range(start=datetime.now() - timedelta(days=30), 
                               end=datetime.now(), freq='7d')
            suv_values = [8.5, 9.2, 10.1, 11.5, 12.3]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=suv_values,
                mode='lines+markers',
                name='SUV Trend',
                line=dict(color='red', width=3)
            ))
            fig.update_layout(
                title="SUV Trend Analizi (30 Gün)",
                xaxis_title="Tarih",
                yaxis_title="SUV Değeri"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with tab5:
            st.json(results["evidence"])
            
            # Evidence quality chart
            fig = px.pie(
                values=[30, 15, 2],
                names=["Grade A", "Grade B", "Grade C"],
                title="Kanıt Kalitesi Dağılımı"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Workflow logs
    st.subheader("📝 Workflow Logları")
    
    if st.session_state.workflow_steps:
        for step in st.session_state.workflow_steps:
            if step["status"] == "completed":
                st.success(f"✅ {step['name']} - {datetime.now().strftime('%H:%M:%S')}")
            elif step["status"] == "processing":
                st.info(f"🔄 {step['name']} - {datetime.now().strftime('%H:%M:%S')}")
            else:
                st.info(f"⏳ {step['name']} - Bekliyor")

else:
    st.info("🎯 Lütfen sidebar'dan yeni bir vaka başlatın")

# Footer
st.markdown("---")
st.markdown("**🧠 NeuroPETRIX v2.0 - Advanced Integration Workflow**")
st.markdown("*PICO → MONAI → Evidence → Decision → Report tam entegrasyon*")

# Auto-refresh for real-time updates
if st.session_state.workflow_status == "running":
    time.sleep(2)
    st.experimental_rerun()


