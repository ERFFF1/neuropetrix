import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="HBYS Integration",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 HBYS Integration")
st.markdown("**HL7 FHIR-based Hospital Information System Integration**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Connection status
    st.subheader("🔗 Connection Status")
    try:
        health_response = requests.get("http://127.0.0.1:8000/hbys/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            if health_data["status"] == "connected":
                st.success("✅ Connected to HBYS")
                st.info(f"Available Patients: {health_data['available_patients']}")
            else:
                st.error("❌ Disconnected")
        else:
            st.error("❌ Connection Failed")
    except:
        st.error("❌ Cannot reach HBYS")
    
    st.markdown("---")
    
    # Patient selection
    st.subheader("👤 Patient Selection")
    try:
        patients_response = requests.get("http://127.0.0.1:8000/hbys/patients", timeout=5)
        if patients_response.status_code == 200:
            patients_data = patients_response.json()
            patient_options = {f"{p['name']} ({p['patient_id']})": p['patient_id'] for p in patients_data['patients']}
            selected_patient = st.selectbox("Select Patient", options=list(patient_options.keys()))
            selected_patient_id = patient_options[selected_patient]
        else:
            selected_patient_id = st.text_input("Patient ID", value="P001")
    except:
        selected_patient_id = st.text_input("Patient ID", value="P001")
    
    st.markdown("---")
    
    # Data type selection
    st.subheader("📊 Data Type")
    data_type = st.selectbox(
        "Select Data Type",
        ["all", "demographics", "lab_results", "diagnoses"],
        format_func=lambda x: x.replace("_", " ").title()
    )

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 Patient Data")
    
    # Fetch data button
    if st.button("🔄 Fetch Data", type="primary"):
        with st.spinner("Fetching data from HBYS..."):
            try:
                request_data = {
                    "patient_id": selected_patient_id,
                    "request_type": data_type
                }
                
                response = requests.post(
                    "http://127.0.0.1:8000/hbys/fetch",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.hbys_data = data
                    st.success("✅ Data fetched successfully!")
                else:
                    st.error(f"❌ Failed to fetch data: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display data
    if hasattr(st.session_state, 'hbys_data'):
        data = st.session_state.hbys_data
        
        # Demographics
        if data.get("demographics"):
            st.subheader("👤 Demographics")
            demo = data["demographics"]
            
            demo_col1, demo_col2 = st.columns(2)
            with demo_col1:
                st.metric("Name", f"{demo['first_name']} {demo['last_name']}")
                st.metric("MRN", demo['mrn'])
                st.metric("Date of Birth", demo['date_of_birth'])
            with demo_col2:
                st.metric("Gender", demo['gender'].title())
                st.metric("Phone", demo.get('phone', 'N/A'))
                st.metric("Email", demo.get('email', 'N/A'))
            
            if demo.get('address'):
                st.info(f"📍 Address: {demo['address']}")
        
        # Laboratory Results
        if data.get("laboratory_results"):
            st.subheader("🔬 Laboratory Results")
            lab_results = data["laboratory_results"]
            
            # Create DataFrame
            lab_df = pd.DataFrame(lab_results)
            lab_df['status_color'] = lab_df['status'].map({
                'normal': 'green',
                'high': 'red',
                'low': 'orange',
                'critical': 'darkred'
            })
            
            # Display table
            st.dataframe(lab_df[['test_name', 'result_value', 'unit', 'reference_range', 'status', 'result_date']], 
                        use_container_width=True)
            
            # Status summary
            status_counts = lab_df['status'].value_counts()
            st.subheader("📊 Results Summary")
            
            status_col1, status_col2, status_col3, status_col4 = st.columns(4)
            with status_col1:
                st.metric("Normal", status_counts.get('normal', 0))
            with status_col2:
                st.metric("High", status_counts.get('high', 0))
            with status_col3:
                st.metric("Low", status_counts.get('low', 0))
            with status_col4:
                st.metric("Critical", status_counts.get('critical', 0))
            
            # Lab trends
            if len(lab_results) > 1:
                st.subheader("📈 Laboratory Trends")
                
                # Create trend chart
                fig = px.scatter(
                    lab_df,
                    x='test_name',
                    y='result_value',
                    color='status',
                    size='result_value',
                    hover_data=['unit', 'reference_range'],
                    title="Laboratory Results by Test"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Diagnoses
        if data.get("diagnoses"):
            st.subheader("🏥 Diagnoses")
            diagnoses = data["diagnoses"]
            
            # Create DataFrame
            diag_df = pd.DataFrame(diagnoses)
            
            # Display table
            st.dataframe(diag_df[['icd_code', 'diagnosis_name', 'diagnosis_date', 'severity', 'status']], 
                        use_container_width=True)
            
            # Severity distribution
            severity_counts = diag_df['severity'].value_counts()
            st.subheader("📊 Diagnosis Severity")
            
            severity_col1, severity_col2, severity_col3 = st.columns(3)
            with severity_col1:
                st.metric("Mild", severity_counts.get('mild', 0))
            with severity_col2:
                st.metric("Moderate", severity_counts.get('moderate', 0))
            with severity_col3:
                st.metric("Severe", severity_counts.get('severe', 0))
            
            # Status distribution
            status_counts = diag_df['status'].value_counts()
            st.subheader("📊 Diagnosis Status")
            
            status_col1, status_col2, status_col3 = st.columns(3)
            with status_col1:
                st.metric("Active", status_counts.get('active', 0))
            with status_col2:
                st.metric("Chronic", status_counts.get('chronic', 0))
            with status_col3:
                st.metric("Resolved", status_counts.get('resolved', 0))

with col2:
    st.header("🔄 Sync Operations")
    
    # Sync button
    if st.button("🔄 Sync to NeuroPETrix", type="secondary"):
        with st.spinner("Syncing data to NeuroPETrix..."):
            try:
                sync_response = requests.post(
                    f"http://127.0.0.1:8000/hbys/sync?patient_id={selected_patient_id}",
                    timeout=30
                )
                
                if sync_response.status_code == 200:
                    sync_data = sync_response.json()
                    st.success("✅ Sync completed!")
                    
                    # Display sync summary
                    st.subheader("📊 Sync Summary")
                    st.metric("Demographics", "✅" if sync_data['synced_data']['demographics'] else "❌")
                    st.metric("Lab Results", sync_data['synced_data']['laboratory_results'])
                    st.metric("Diagnoses", sync_data['synced_data']['diagnoses'])
                    st.info(f"Sync Time: {sync_data['sync_time']}")
                else:
                    st.error(f"❌ Sync failed: {sync_response.text}")
                    
            except Exception as e:
                st.error(f"❌ Sync error: {str(e)}")
    
    st.markdown("---")
    
    # Lab trends analysis
    st.header("📈 Lab Trends Analysis")
    
    if st.button("📊 Analyze Trends"):
        with st.spinner("Analyzing laboratory trends..."):
            try:
                trends_response = requests.get(
                    f"http://127.0.0.1:8000/hbys/lab-trends/{selected_patient_id}",
                    timeout=30
                )
                
                if trends_response.status_code == 200:
                    trends_data = trends_response.json()
                    st.session_state.lab_trends = trends_data
                    st.success("✅ Trends analysis completed!")
                else:
                    st.error(f"❌ Trends analysis failed: {trends_response.text}")
                    
            except Exception as e:
                st.error(f"❌ Trends error: {str(e)}")
    
    # Display trends
    if hasattr(st.session_state, 'lab_trends'):
        trends_data = st.session_state.lab_trends
        
        st.subheader("📈 Laboratory Trends")
        
        for test_name, trend_data in trends_data['trends'].items():
            with st.expander(f"📊 {test_name}"):
                if len(trend_data) > 1:
                    # Create trend chart
                    df = pd.DataFrame(trend_data)
                    df['date'] = pd.to_datetime(df['date'])
                    
                    fig = px.line(
                        df,
                        x='date',
                        y='value',
                        color='status',
                        title=f"{test_name} Trend",
                        labels={'value': f'Value ({df["unit"].iloc[0]})'}
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"Single measurement: {trend_data[0]['value']} {trend_data[0]['unit']}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🏥 HBYS Integration Module | NeuroPETrix v2.0</p>
    <p>HL7 FHIR-based hospital information system integration</p>
</div>
""", unsafe_allow_html=True)
