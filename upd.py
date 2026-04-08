import streamlit as st
import pandas as pd
import re
from datetime import datetime
import requests
import os
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="ECSBC Compliance Dashboard", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "compliance"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "uploaded_sim_file" not in st.session_state:
    st.session_state.uploaded_sim_file = None
if "project_context" not in st.session_state:
    st.session_state.project_context = {}

# ECSBC compliance requirements with area-based exceptions
ECSBC_REQUIREMENTS = {
    "Composite": {
        "default": {"wall": 0.44, "roof": 0.20},
        "Hospitality_below_10000": {"wall": 0.44, "roof": 0.20},  # Roof exception applies, wall unchanged
        "Business_below_10000": {"wall": 0.63, "roof": 0.20},     # Wall exception applies
        "Educational_below_10000": {"wall": 0.63, "roof": 0.20},  # Wall exception for School
        "Assembly_above_10000": {"wall": 0.44, "roof": 0.20}
    },
    "Hot-Dry": {
        "default": {"wall": 0.44, "roof": 0.20},
        "Hospitality_below_10000": {"wall": 0.44, "roof": 0.20},  # Roof exception applies, wall unchanged
        "Business_below_10000": {"wall": 0.63, "roof": 0.20},     # Wall exception applies
        "Educational_below_10000": {"wall": 0.63, "roof": 0.20},  # Wall exception for School
        "Assembly_above_10000": {"wall": 0.44, "roof": 0.20}
    },
    "Warm-Humid": {
        "default": {"wall": 0.44, "roof": 0.20},
        "Hospitality_below_10000": {"wall": 0.44, "roof": 0.20},  # Roof exception applies, wall unchanged
        "Business_below_10000": {"wall": 0.63, "roof": 0.20},     # Wall exception applies
        "Educational_below_10000": {"wall": 0.63, "roof": 0.20},  # Wall exception for School
        "Assembly_above_10000": {"wall": 0.44, "roof": 0.20}
    },
    "Moderate": {
        "default": {"wall": 0.55, "roof": 0.20},
        "Hospitality_below_10000": {"wall": 0.55, "roof": 0.20},  # Roof exception applies, wall unchanged
        "Business_below_10000": {"wall": 0.63, "roof": 0.20},     # Wall exception applies
        "Educational_below_10000": {"wall": 0.75, "roof": 0.20},  # Wall exception for School
        "Assembly_above_10000": {"wall": 0.55, "roof": 0.20}
    },
    "Cold": {
        "default": {"wall": 0.34, "roof": 0.20},
        "Hospitality_below_10000": {"wall": 0.34, "roof": 0.20},  # Roof exception applies, wall unchanged
        "Business_below_10000": {"wall": 0.40, "roof": 0.20},     # Wall exception applies
        "Educational_below_10000": {"wall": 0.40, "roof": 0.20},  # Wall exception for School
        "Assembly_above_10000": {"wall": 0.34, "roof": 0.20}
    }
}

def get_ecsbc_requirements(climate_zone, building_type, area):
    """Get ECSBC requirements based on climate zone, building type, and area"""
    requirements_dict = ECSBC_REQUIREMENTS.get(climate_zone, {})
    
    if area >= 10000:
        if building_type == "Assembly":
            exception_key = "Assembly_above_10000"
            if exception_key in requirements_dict:
                return requirements_dict[exception_key]
        elif building_type == "Hospitality":
            exception_key = "Assembly_above_10000"
            if exception_key in requirements_dict:
                return requirements_dict[exception_key]
    
    if area < 10000:
        type_mapping = {
            "Hospitality": "Hospitality_below_10000",
            "Business": "Business_below_10000",
            "Educational": "Educational_below_10000",
            "Health Care": "Business_below_10000",
            "Assembly": "Business_below_10000",
            "Shopping Complex": "Business_below_10000"
        }
        
        exception_key = type_mapping.get(building_type)
        if exception_key and exception_key in requirements_dict:
            return requirements_dict[exception_key]
    
    return requirements_dict.get("default", {"wall": 0.40, "roof": 0.26})

def extract_u_values_from_sim(sim_file_content):
    """Extract U-values from SIM file for walls, roofs, and windows"""
    
    if isinstance(sim_file_content, bytes):
        file_content = sim_file_content.decode("utf-8", errors="ignore")
    else:
        file_content = str(sim_file_content)

    start_key = "REPORT- LV-D Details of Exterior Surfaces"
    end_key = "REPORT- LV-E Details of Underground Surfaces"
    summary_start = "AVERAGE             AVERAGE         AVERAGE U-VALUE"

    filtered_lines = []
    capture = False
    summary_section = False

    for line in file_content.splitlines(keepends=True):
        if start_key in line:
            capture = True
        
        if capture and summary_start in line:
            summary_section = True
        
        if capture and summary_section:
            filtered_lines.append(line)
        
        if capture and end_key in line:
            break

    filtered_text = "".join(filtered_lines)
    
    wall_u_value = None
    roof_u_value = None
    window_u_value = None
    
    lines = filtered_text.split('\n')
    for line in lines:
        if 'ALL WALLS' in line.upper():
            parts = line.split()
            try:
                numeric_values = [float(p) for p in parts if is_float(p)]
                if len(numeric_values) >= 2:
                    # First value is window U-value, second is wall U-value
                    window_u_value = numeric_values[0] * 5.678  # Convert to W/m².K
                    wall_u_value = numeric_values[1] * 5.678
            except:
                pass
        
        elif line.strip().startswith('ROOF') and 'ROOF' in line.upper():
            parts = line.split()
            try:
                numeric_values = [float(p) for p in parts if is_float(p)]
                if len(numeric_values) >= 2:
                    roof_u_value = numeric_values[1] * 5.678
            except:
                pass
    
    return wall_u_value, roof_u_value, window_u_value, filtered_text

def is_float(value):
    """Check if a string can be converted to float"""
    try:
        float(value)
        return True
    except ValueError:
        return False

def check_compliance(actual_value, required_value):
    """Check if actual U-value complies with ECSBC requirement"""
    if actual_value is None:
        return "N/A"
    
    if actual_value <= required_value:
        return "Compliant"
    else:
        return "Not Compliant"

def create_compliance_table(climate_zone, building_type, compliance_level, 
                           wall_u_actual, roof_u_actual, window_u_actual, wall_u_required, roof_u_required,
                           project_area):
    """Create a formatted compliance table matching the reference format"""
    
    wall_status = check_compliance(wall_u_actual, wall_u_required)
    roof_status = check_compliance(roof_u_actual, roof_u_required)
    window_status = "N/A"  # Placeholder until requirements are added
    
    wall_actual_str = f"{wall_u_actual:.3f}" if wall_u_actual else "N/A"
    roof_actual_str = f"{roof_u_actual:.3f}" if roof_u_actual else "N/A"
    window_actual_str = f"{window_u_actual:.3f}" if window_u_actual else "N/A"
    wall_required_str = f"{wall_u_required:.3f}"
    roof_required_str = f"{roof_u_required:.3f}"
    
    wall_class = "compliant" if wall_status == "Compliant" else ("not-compliant" if wall_status == "Not Compliant" else "na")
    roof_class = "compliant" if roof_status == "Compliant" else ("not-compliant" if roof_status == "Not Compliant" else "na")
    window_class = "na"
    
    ecsbc_check = "✓" if compliance_level == "ECSBC Compliant" else ""
    ecsbc_plus_check = "✓" if compliance_level == "ECSBC+ Compliant" else ""
    super_ecsbc_check = "✓" if compliance_level == "Super ECSBC Compliant" else ""
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    html = f'''
    <style>
        .compliance-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-family: Arial, sans-serif;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-size: 14px;
        }}
        .compliance-table th, .compliance-table td {{
            border: 1px solid #333;
            padding: 10px;
            text-align: left;
        }}
        .compliance-table th {{
            background-color: #f0f0f0;
            font-weight: bold;
            text-align: center;
        }}
        .header-main {{
            background-color: #d0d0d0;
            font-weight: bold;
            font-size: 16px;
            text-align: center;
        }}
        .sub-header {{
            background-color: #e8e8e8;
            font-weight: bold;
        }}
        .compliant {{
            background-color: #90EE90;
            font-weight: bold;
        }}
        .not-compliant {{
            background-color: #FFB6C6;
            font-weight: bold;
        }}
        .na {{
            background-color: #FFE4B5;
        }}
        .center {{
            text-align: center;
        }}
        .field-name {{
            font-weight: 600;
            width: 25%;
            background-color: #f5f5f5;
        }}
    </style>
    
    <table class="compliance-table">
        <tr class="header-main">
            <td colspan="4">General Project Information</td>
        </tr>
        <tr>
            <td class="field-name">Date of Submission</td>
            <td colspan="3">{current_date}</td>
        </tr>
        <tr>
            <td class="field-name">Project Address</td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td class="field-name">Project Built-up Area (m²)</td>
            <td colspan="3"><strong>{project_area:.2f}</strong></td>
        </tr>
        <tr>
            <td class="field-name">Project Above-grade Area (m²)</td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td class="field-name">Project Conditioned Area (m²)</td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td class="field-name">Applicant Name and Address</td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td class="field-name">Project Climatic Zone</td>
            <td colspan="3"><strong>{climate_zone}</strong></td>
        </tr>
        <tr>
            <td class="field-name" rowspan="3">Building Classification</td>
            <td class="center">Hospitality</td>
            <td class="center">Business</td>
            <td rowspan="3" class="center"><strong>{building_type}</strong></td>
        </tr>
        <tr>
            <td class="center">Health Care</td>
            <td class="center">Educational</td>
        </tr>
        <tr>
            <td class="center">Assembly</td>
            <td class="center">Shopping Complex</td>
        </tr>
        
        <tr class="sub-header">
            <td>Building Envelope</td>
            <td class="center">Wall Compliance</td>
            <td class="center">Roof Compliance</td>
            <td class="center">Values [W/m².K]</td>
        </tr>
        <tr>
            <td class="field-name">Actual U-value</td>
            <td class="center">{wall_actual_str}</td>
            <td class="center">{roof_actual_str}</td>
            <td></td>
        </tr>
        <tr>
            <td class="field-name">ECSBC Required U-value</td>
            <td class="center">{wall_required_str}</td>
            <td class="center">{roof_required_str}</td>
            <td></td>
        </tr>
        <tr>
            <td class="field-name">Compliance Status</td>
            <td class="center {wall_class}">{wall_status}</td>
            <td class="center {roof_class}">{roof_status}</td>
            <td></td>
        </tr>
        
        <tr class="sub-header">
            <td>Vertical Fenestration</td>
            <td class="center">U-factor [W/m².K]</td>
            <td class="center">SHGC</td>
            <td class="center">VLT</td>
        </tr>
        <tr>
            <td class="field-name">Actual Value</td>
            <td class="center">{window_actual_str}</td>
            <td class="center">-</td>
            <td class="center">-</td>
        </tr>
        <tr>
            <td class="field-name">ECSBC Required Value</td>
            <td class="center">-</td>
            <td class="center">-</td>
            <td class="center">-</td>
        </tr>
        <tr>
            <td class="field-name">WWR (%)</td>
            <td class="center">-</td>
            <td class="center">-</td>
            <td class="center">-</td>
        </tr>
        <tr>
            <td class="field-name">Compliance Status</td>
            <td class="center {window_class}">{window_status}</td>
            <td class="center na">N/A</td>
            <td class="center na">N/A</td>
        </tr>
        
        <tr class="sub-header">
            <td>Compliance sought for</td>
            <td class="center">ECSBC Compliant</td>
            <td class="center">ECSBC+ Compliant</td>
            <td class="center">Super ECSBC Compliant</td>
        </tr>
        <tr>
            <td class="field-name">Selected Level</td>
            <td class="center">{ecsbc_check}</td>
            <td class="center">{ecsbc_plus_check}</td>
            <td class="center">{super_ecsbc_check}</td>
        </tr>
    </table>
    '''
    
    return html

def call_vectorshift_api(api_key, pipeline_id, sim_file_content, sim_filename, typology, climate):
    """Call VectorShift API with SIM file and parameters"""
    try:
        run_url = f"https://api.vectorshift.ai/v1/pipeline/{pipeline_id}/run"
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "inputs.Typology": typology,
            "inputs.Climate": climate
        }
        
        files = {
            "SIM": (
                sim_filename,
                BytesIO(sim_file_content),
                "application/octet-stream"
            )
        }
        
        response = requests.post(
            run_url,
            headers=headers,
            data=data,
            files=files,
            timeout=300
        )
        
        response.raise_for_status()
        response_json = response.json()
        
        formatted_text = response_json.get("outputs", {}).get("output_0", "No response from API")
        
        return {
            "status": "success",
            "response": formatted_text,
            "status_code": response.status_code
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "response": f"API Error: {str(e)}",
            "status_code": None
        }
    except Exception as e:
        return {
            "status": "error",
            "response": f"Unexpected error: {str(e)}",
            "status_code": None
        }

# ===== PAGE 1: COMPLIANCE CHECKER =====
def compliance_page():
    st.title("🏢 ECSBC Compliance Check Dashboard")
    st.markdown("---")
    
    st.markdown("""
    <style>
        .stButton > button {
            width: 100%;
            height: 3em;
            font-size: 18px;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📤 Upload SIM File")
        uploaded_file = st.file_uploader("Choose a SIM file", type=['sim', 'txt'], width=300)
        
        if uploaded_file:
            st.session_state.uploaded_sim_file = uploaded_file.getvalue()
            st.session_state.sim_filename = uploaded_file.name
    
    with col2:
        st.subheader("🏗️ Building Classification")
        building_type = st.selectbox(
            "Select Building Type",
            ["Hospitality", "Business", "Health Care", "Educational", "Assembly", "Shopping Complex"], width=300
        )
        
        compliance_level = st.selectbox(
            "Compliance Level Sought",
            ["ECSBC Compliant", "ECSBC+ Compliant", "Super ECSBC Compliant"], width=300
        )
    
    with col3:
        st.subheader("🌍 Project Details")
        climate_zone = st.selectbox(
            "Select Climate Zone",
            ["Composite", "Hot-Dry", "Warm-Humid", "Moderate", "Cold"], width=300
        )
        
        project_area = st.number_input(
            "Project Built-up Area (m²)",
            min_value=0.0,
            value=10000.0,
            step=100.0,
            help="Enter the total built-up area. Requirements vary for areas below 10,000 m²", width=300
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.session_state.project_context = {
        "building_type": building_type,
        "climate_zone": climate_zone,
        "project_area": project_area,
        "compliance_level": compliance_level
    }
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_left:
        check_button = st.button("🔍 Check Compliance", type="primary", use_container_width=False, width=300)
    
    if check_button:
        if uploaded_file is None:
            st.error("⚠️ Please upload a SIM file first!")
            return
        
        with st.spinner("Analyzing SIM file..."):
            file_content = uploaded_file.read()
            
            wall_u_value, roof_u_value, window_u_value, extracted_text = extract_u_values_from_sim(file_content)
            
            requirements = get_ecsbc_requirements(climate_zone, building_type, project_area)
            required_wall_u = requirements["wall"]
            required_roof_u = requirements["roof"]
            
            if project_area < 10000:
                st.info(f"ℹ️ Area-based exception applied: Project area ({project_area:.0f} m²) is below 10,000 m². Using relaxed U-value requirements.")
            
            st.success("✅ Analysis Complete!")
            st.markdown("---")
            
            table_html = create_compliance_table(
                climate_zone, building_type, compliance_level,
                wall_u_value, roof_u_value, window_u_value, required_wall_u, required_roof_u,
                project_area
            )
            
            st.markdown("### 📋 ECSBC Compliance Report")
            import streamlit.components.v1 as components
            
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; background-color: white;">
                {table_html}
            </body>
            </html>
            """
            
            components.html(full_html, height=1100, scrolling=True)
            
            with st.expander("📄 View Extracted SIM File Content"):
                st.text(extracted_text if extracted_text else "No content extracted")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                download_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>ECSBC Compliance Report</title>
                </head>
                <body style="margin: 20px; padding: 20px; background-color: white; font-family: Arial, sans-serif;">
                    <h1 style="text-align: center; color: #333;">ECSBC Compliance Report</h1>
                    {table_html}
                    <div style="margin-top: 30px; text-align: center; color: #666; font-size: 12px;">
                        <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                        <p>Energy Conservation Building Code Compliance Dashboard</p>
                    </div>
                </body>
                </html>
                """
                
                st.download_button(
                    label="📥 Download Report",
                    data=download_html,
                    file_name=f"ECSBC_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True,
                    type="secondary"
                )
            
            with col2:
                pass
            
            with col3:
                if st.button("💬 Chat with AI Assistant", use_container_width=True, type="primary"):
                    st.session_state.current_page = "chat"
                    st.rerun()

# ===== PAGE 2: AI CHAT =====
def chat_page():
    st.title("💬 AI Assistant - ECSBC Compliance Chat")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("⬅️ Back to Compliance", use_container_width=True):
            st.session_state.current_page = "compliance"
            st.rerun()
    
    st.markdown("---")
    
    with st.expander("⚙️ API Configuration", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            api_key = st.text_input(
                "VectorShift API Key",
                type="password",
                value=os.getenv("VECTORSHIFT_API_KEY", ""),
                help="Enter your VectorShift API key"
            )
        with col2:
            pipeline_id = st.text_input(
                "Pipeline ID",
                value="6954c79ba76af4b71858e962",
                help="Enter your VectorShift Pipeline ID"
            )
    
    if st.session_state.project_context:
        st.info(f"""
        **Current Project Context:**  
        📋 Building Type: {st.session_state.project_context.get('building_type', 'N/A')}  
        🌍 Climate Zone: {st.session_state.project_context.get('climate_zone', 'N/A')}  
        📐 Project Area: {st.session_state.project_context.get('project_area', 'N/A')} m²
        """)
    
    st.markdown("---")
    
    st.subheader("Ask me anything about ECSBC compliance")
    
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.chat_input("Type your question here...")
    
    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing with AI..."):
                if not api_key:
                    response_text = "⚠️ Please configure your VectorShift API key in the API Configuration section above."
                elif not st.session_state.uploaded_sim_file:
                    response_text = "⚠️ No SIM file uploaded. Please go back and upload a SIM file first."
                else:
                    context = st.session_state.project_context
                    result = call_vectorshift_api(
                        api_key=api_key,
                        pipeline_id=pipeline_id,
                        sim_file_content=st.session_state.uploaded_sim_file,
                        sim_filename=st.session_state.sim_filename,
                        typology=context.get("building_type", "Business"),
                        climate=context.get("climate_zone", "Composite")
                    )
                    
                    if result["status"] == "success":
                        response_text = result["response"]
                    else:
                        response_text = f"❌ {result['response']}"
                
                st.markdown(response_text)
        
        st.session_state.chat_messages.append({"role": "assistant", "content": response_text})
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
            st.session_state.chat_messages = []
            st.rerun()

# ===== MAIN APP =====
def main():
    if st.session_state.current_page == "compliance":
        compliance_page()
    elif st.session_state.current_page == "chat":
        chat_page()
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    <small>ECSBC Compliance Dashboard v1.0 | Energy Conservation Building Code</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()