import streamlit as st
import requests
import json
import time
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="MONAI & PyRadiomics Analysis",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 MONAI & PyRadiomics Analysis")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model selection
    st.subheader("MONAI Model")
    model_options = {
        "nnUNet_Task501_LungLesionSegmentation": "Lung Lesion Segmentation",
        "nnUNet_Task502_LymphNodeSegmentation": "Lymph Node Segmentation", 
        "nnUNet_Task503_LiverSegmentation": "Liver Segmentation"
    }
    selected_model = st.selectbox(
        "Select Model",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x]
    )
    
    # Analysis type
    st.subheader("Analysis Type")
    analysis_type = st.selectbox(
        "Analysis Type",
        ["full", "segmentation", "radiomics"],
        format_func=lambda x: x.title()
    )
    
    # Radiomics features
    st.subheader("Radiomics Features")
    feature_groups = [
        "firstorder", "shape", "glcm", "glrlm", 
        "glszm", "ngtdm", "gldm"
    ]
    selected_features = st.multiselect(
        "Select Feature Groups",
        feature_groups,
        default=feature_groups[:3]
    )

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Analysis Dashboard")
    
    # Patient and case selection
    patient_id = st.text_input("Patient ID", value="P001")
    case_id = st.text_input("Case ID", value="C001")
    
    # Analysis controls
    if st.button("🚀 Start Analysis", type="primary"):
        with st.spinner("Starting MONAI & PyRadiomics analysis..."):
            # Prepare request
            request_data = {
                "patient_id": patient_id,
                "case_id": case_id,
                "analysis_type": analysis_type,
                "model_name": selected_model,
                "radiomics_features": selected_features
            }
            
            try:
                # Send analysis request
                response = requests.post(
                    "http://127.0.0.1:8000/monai/analyze",
                    json=request_data,
                    timeout=300
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Analysis completed successfully!")
                    
                    # Store result in session state
                    st.session_state.analysis_result = result
                    st.session_state.case_id = case_id
                    
                else:
                    st.error(f"❌ Analysis failed: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display results
    if hasattr(st.session_state, 'analysis_result'):
        result = st.session_state.analysis_result
        
        st.subheader("📈 Analysis Results")
        
        # Status
        status_col1, status_col2, status_col3 = st.columns(3)
        with status_col1:
            st.metric("Status", result.get("status", "Unknown"))
        with status_col2:
            st.metric("Processing Time", f"{result.get('processing_time', 0):.1f}s")
        with status_col3:
            st.metric("Lesion Count", result.get("radiomics_features", {}).get("shape", {}).get("Volume", 0))
        
        # SUV Measurements
        if result.get("suv_measurements"):
            st.subheader("🚀 SUV Measurements")
            suv_data = result["suv_measurements"]
            
            suv_col1, suv_col2, suv_col3, suv_col4, suv_col5 = st.columns(5)
            with suv_col1:
                st.metric("SUVmax", f"{suv_data.get('SUVmax', 0):.2f}")
            with suv_col2:
                st.metric("SUVmean", f"{suv_data.get('SUVmean', 0):.2f}")
            with suv_col3:
                st.metric("SUVpeak", f"{suv_data.get('SUVpeak', 0):.2f}")
            with suv_col4:
                st.metric("MTV (cm³)", f"{suv_data.get('MTV', 0):.1f}")
            with suv_col5:
                st.metric("TLG", f"{suv_data.get('TLG', 0):.1f}")

with col2:
    st.header("📋 Analysis Status")
    
    if hasattr(st.session_state, 'case_id'):
        case_id = st.session_state.case_id
        
        # Check status
        try:
            status_response = requests.get(f"http://127.0.0.1:8000/monai/status/{case_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                # Status indicators
                st.subheader("Progress")
                
                if status_data["status"] == "completed":
                    st.success("✅ Analysis Complete")
                    st.info("📁 Segmentation: Ready")
                    st.info("📊 Radiomics: Ready")
                elif status_data["status"] == "radiomics_processing":
                    st.warning("⏳ Radiomics Processing")
                    st.info("📁 Segmentation: Ready")
                    st.warning("📊 Radiomics: Processing")
                elif status_data["status"] == "segmentation_processing":
                    st.warning("⏳ Segmentation Processing")
                    st.warning("📁 Segmentation: Processing")
                    st.info("📊 Radiomics: Waiting")
                else:
                    st.info("⏳ Analysis Starting")
                
                # Refresh button
                if st.button("🔄 Refresh Status"):
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Status check failed: {str(e)}")

# Radiomics Features Display
if hasattr(st.session_state, 'analysis_result') and st.session_state.analysis_result.get("radiomics_features"):
    st.header("🔬 Radiomics Features")
    
    radiomics_data = st.session_state.analysis_result["radiomics_features"]
    
    # Create tabs for different feature groups
    feature_tabs = st.tabs(list(radiomics_data.keys()))
    
    for i, (feature_group, features) in enumerate(radiomics_data.items()):
        with feature_tabs[i]:
            st.subheader(f"{feature_group.title()} Features")
            
            # Convert to DataFrame for better display
            if isinstance(features, dict):
                df = pd.DataFrame(list(features.items()), columns=["Feature", "Value"])
                df["Value"] = df["Value"].round(4)
                
                # Display as table
                st.dataframe(df, use_container_width=True)
                
                # Create bar chart
                fig = px.bar(
                    df, 
                    x="Feature", 
                    y="Value",
                    title=f"{feature_group.title()} Features",
                    color="Value",
                    color_continuous_scale="viridis"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

# Model Information
st.header("🤖 Available Models")
try:
    models_response = requests.get("http://127.0.0.1:8000/monai/models")
    if models_response.status_code == 200:
        models_data = models_response.json()
        
        models_df = pd.DataFrame(models_data["models"])
        st.dataframe(models_df, use_container_width=True)
        
except Exception as e:
    st.error(f"Failed to load models: {str(e)}")

# Feature Information
st.header("🔬 Available Features")
try:
    features_response = requests.get("http://127.0.0.1:8000/monai/features")
    if features_response.status_code == 200:
        features_data = features_response.json()
        
        # Display feature groups
        for group, features in features_data["features"].items():
            with st.expander(f"{group.title()} Features"):
                st.write(", ".join(features))
                
except Exception as e:
    st.error(f"Failed to load features: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🧠 MONAI & PyRadiomics Analysis Module | NeuroPETrix v2.0</p>
    <p>Advanced AI-powered medical image analysis</p>
</div>
""", unsafe_allow_html=True)
