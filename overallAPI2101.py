import streamlit as st
import requests
import os
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="ECSBC Compliance Check",
    # page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to match the design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .dashboard-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 40px;
        padding: 20px 0;
        border-bottom: 2px solid #e9ecef;
    }
    
    .dashboard-title {
        font-size: 32px;
        font-weight: 700;
        color: #212529;
        margin: 0;
    }
    
    .icon-box {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        height: 100%;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    /*.card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }*/
    
    .card-icon {
        font-size: 24px;
    }
    
    .card-title {
        font-size: 20px;
        font-weight: 600;
        color: #212529;
        margin: 0;
    }
    
    .section-label {
        font-size: 14px;
        font-weight: 500;
        color: #6c757d;
        margin-bottom: 8px;
    }
    
    /* Upload area styling */
    .upload-area {
        border: 2px dashed #dee2e6;
        border-radius: 8px;
        padding: 40px 20px;
        text-align: center;
        background-color: #f8f9fa;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: #667eea;
        background-color: #f0f2ff;
    }
    
    .upload-text {
        font-size: 14px;
        color: #6c757d;
        margin-top: 10px;
    }
    
    .file-info {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #f8f9fa;
        padding: 12px 16px;
        border-radius: 8px;
        margin-top: 12px;
    }
    
    .file-name {
        font-size: 14px;
        color: #212529;
        font-weight: 500;
    }
    
    .file-size {
        font-size: 12px;
        color: #6c757d;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #ff4757 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 32px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.3s !important;
        margin-top: 20px;
    }
    
    .stButton > button:hover {
        background-color: #ff3447 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3) !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border-color: #dee2e6 !important;
    }
    
    /* Number input styling */
    .stNumberInput > div > div > input {
        border-radius: 8px !important;
        border-color: #dee2e6 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Deploy button styling */
    .deploy-button {
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: white;
        color: #212529;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">ECSBC Compliance Check</h1>
</div>
""", unsafe_allow_html=True)

# API Configuration
API_KEY = "sk_94sj9Jnzk4GCLgieWb1EvS1qWEwGp1dXyXA7WuKTMu8OkGy5"
PIPELINE_ID = "694277f13a21ec44ea253d4a"
RUN_URL = f"https://api.vectorshift.ai/v1/pipeline/{PIPELINE_ID}/run"

# Create three columns for the main layout
col1, col2, col3 = st.columns([1, 1, 1], gap="large")

# Column 1: Upload SIM File
with col1:
    st.markdown("""
    <div class="card">
        <h3>Upload SIM File</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-label">Choose a SIM file</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a SIM file",
        type=['sim', 'txt'],
        label_visibility="collapsed",
        help="Limit 200MB per file • SIM, TXT"
    )
    
    if uploaded_file:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.markdown(f"""
        <div class="file-info">
            <div>
                <div class="file-name">📄 {uploaded_file.name}</div>
                <div class="file-size">{file_size_mb:.2f}MB</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Drag and drop file here\n\nLimit 200MB per file • SIM, TXT")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Column 2: Building Classification
with col2:
    st.markdown("""
    <div class="card">
        <div>
            <h3>Building Classification</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-label">Select Building Type</p>', unsafe_allow_html=True)
    building_type = st.selectbox(
        "Select Building Type",
        ["No Star Hotel", "School", "Business", "Residential", "Healthcare"],
        label_visibility="collapsed"
    )
    
    st.markdown('<p class="section-label" style="margin-top: 20px;">Compliance Level Sought</p>', unsafe_allow_html=True)
    compliance_level = st.selectbox(
        "Compliance Level Sought",
        ["ECSBC Compliant", "Partially Compliant", "Non-Compliant"],
        label_visibility="collapsed"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

# Column 3: Project Details
with col3:
    st.markdown("""
    <div class="card">
        <div>
            <h3>Project Details</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-label">Select Climate Zone</p>', unsafe_allow_html=True)
    climate_zone = st.selectbox(
        "Select Climate Zone",
        ["Composite", "Hot & Dry", "Warm & Humid", "Cold", "Temperate"],
        label_visibility="collapsed"
    )
    
    st.markdown('<p class="section-label" style="margin-top: 20px;">Project Built-up Area (m²)</p>', unsafe_allow_html=True)
    built_up_area = st.number_input(
        "Project Built-up Area (m²)",
        min_value=0.0,
        value=10000.00,
        step=100.0,
        format="%.2f",
        label_visibility="collapsed"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

# Check Compliance Button (full width)
st.markdown("<br>", unsafe_allow_html=True)

# Initialize session state for results
if 'compliance_result' not in st.session_state:
    st.session_state.compliance_result = None
if 'checking' not in st.session_state:
    st.session_state.checking = False

if st.button("🔍 Check Compliance", use_container_width=False, width=300):
    if uploaded_file is None:
        st.error("⚠️ Please upload a SIM file first!")
    else:
        st.session_state.checking = True
        
        with st.spinner("Checking compliance... This may take a few moments."):
            try:
                # Prepare the API request
                headers = {
                    "Authorization": f"Bearer {API_KEY}"
                }
                
                # Map building type to match API expected values
                building_type_map = {
                    "Hospitality": "Hospitality",
                    "School": "School",
                    "Office": "Office",
                    "Residential": "Residential",
                    "Healthcare": "Healthcare",
                    "Retail": "Retail",
                    "Industrial": "Industrial"
                }
                
                # Map climate zone to match API expected values
                climate_map = {
                    "Composite": "Composite",
                    "Hot & Dry": "Hot",
                    "Warm & Humid": "Warm",
                    "Cold": "Cold",
                    "Temperate": "Temperate",
                    "Moderate": "Moderate"
                }
                
                data = {
                    "inputs.Typology": building_type_map.get(building_type, building_type),
                    "inputs.Climate": climate_map.get(climate_zone, climate_zone),
                    "inputs.Area": str(int(built_up_area))
                }
                
                # Reset file pointer to beginning
                uploaded_file.seek(0)
                
                files = {
                    "SIM": (
                        uploaded_file.name,
                        uploaded_file,
                        "application/octet-stream"
                    )
                }
                
                # Make the API request
                response = requests.post(
                    RUN_URL,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=300
                )
                
                if response.status_code == 200:
                    response_json = response.json()
                    formatted_text = response_json.get("outputs", {}).get("output_0", "No output received")
                    st.session_state.compliance_result = formatted_text
                    st.success("✅ Compliance check completed successfully!")
                else:
                    st.error(f"❌ Error: API returned status code {response.status_code}")
                    st.error(f"Response: {response.text}")
                    st.session_state.compliance_result = None
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The compliance check is taking longer than expected. Please try again.")
                st.session_state.compliance_result = None
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.session_state.compliance_result = None
        
        st.session_state.checking = False

# Display results if available
if st.session_state.compliance_result:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <span class="card-icon">📊</span>
            <h2 class="card-title">Compliance Check Results</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the result in an expandable section
    with st.expander("📄 View Full Report", expanded=True):
        st.markdown(st.session_state.compliance_result)
    
    # Download button for the results
    col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
    with col_dl2:
        st.download_button(
            label="📥 Download Report",
            data=st.session_state.compliance_result,
            file_name="ecsbc_compliance_report.txt",
            mime="text/plain",
            use_container_width=True
        )

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 14px; padding: 20px;">
    ECSBC Compliance Check Dashboard • Powered by VectorShift API
</div>
""", unsafe_allow_html=True)