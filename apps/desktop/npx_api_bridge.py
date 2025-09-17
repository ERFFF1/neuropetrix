import os, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("NPX_API_BASE","http://localhost:8080")
import streamlit as st
from packages.engines.api_client import start_analysis, get_status
st.set_page_config(page_title="NeuroPETRIX API Bridge", page_icon="🔗", layout="wide")
st.title("🔗 NeuroPETRIX API Bridge (Streamlit)")
case_id = st.text_input("Case ID", "demo-001")
if st.button("📊 PyRadiomics Analizi Başlat"):
    try:
        resp = start_analysis(case_id, ["radiomics"])
        st.success(f"Job accepted: {resp['job_id']}")
        st.json(get_status(resp["job_id"]))
    except Exception as e:
        st.error(f"Hata: {e}")
