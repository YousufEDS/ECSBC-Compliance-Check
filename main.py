import streamlit as st
import pandas as pd
import re
from datetime import datetime
import requests

st.write("Through Programming")
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
    
    # Special case for Assembly and Hospitality with area > 10,000 m²
    if area >= 10000:
        if building_type == "Assembly":
            exception_key = "Assembly_above_10000"
            if exception_key in requirements_dict:
                return requirements_dict[exception_key]
        elif building_type == "Hospitality":
            exception_key = "Assembly_above_10000"
            if exception_key in requirements_dict:
                return requirements_dict[exception_key]
    
    # Check if area-based exception applies for buildings < 10,000 m²
    if area < 10000:
        # Map building types to their requirement keys
        type_mapping = {
            "Hospitality": "Hospitality_below_10000",
            "Business": "Business_below_10000",
            "Educational": "Educational_below_10000",
            "Health Care": "Business_below_10000",  # Treat same as Business
            "Assembly": "Business_below_10000",  # Treat same as Business for < 10k
            "Shopping Complex": "Business_below_10000"  # Treat same as Business
        }
        
        exception_key = type_mapping.get(building_type)
        if exception_key and exception_key in requirements_dict:
            return requirements_dict[exception_key]
    
    # Return default requirements
    return requirements_dict.get("default", {"wall": 0.40, "roof": 0.26})

def extract_u_values_from_sim(sim_file_content):
    """Extract U-values from SIM file for walls and roofs"""
    
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
        
        # Only capture lines after the summary table header
        if capture and summary_start in line:
            summary_section = True
        
        if capture and summary_section:
            filtered_lines.append(line)
        
        if capture and end_key in line:
            break

    filtered_text = "".join(filtered_lines)
    
    # Extract U-values for ALL WALLS and ROOF from the specific table format
    wall_u_value = None
    roof_u_value = None
    
    lines = filtered_text.split('\n')
    for line in lines:
        # Look for the "ALL WALLS" line
        if 'ALL WALLS' in line.upper():
            parts = line.split()
            try:
                numeric_values = [float(p) for p in parts if is_float(p)]
                if len(numeric_values) >= 2:
                    # Convert from BTU/HR-SQFT-F to W/m².K
                    wall_u_value = numeric_values[1] * 5.678
            except:
                pass
        
        # Look for the "ROOF" line
        elif line.strip().startswith('ROOF') and 'ROOF' in line.upper():
            parts = line.split()
            try:
                numeric_values = [float(p) for p in parts if is_float(p)]
                if len(numeric_values) >= 2:
                    # Convert from BTU/HR-SQFT-F to W/m².K
                    roof_u_value = numeric_values[1] * 5.678
            except:
                pass
    
    return wall_u_value, roof_u_value, filtered_text

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
                           wall_u_actual, roof_u_actual, wall_u_required, roof_u_required,
                           project_area):
    """Create a formatted compliance table matching the reference format"""
    
    # Check compliance status
    wall_status = check_compliance(wall_u_actual, wall_u_required)
    roof_status = check_compliance(roof_u_actual, roof_u_required)
    
    # Format values
    wall_actual_str = f"{wall_u_actual:.3f}" if wall_u_actual else "N/A"
    roof_actual_str = f"{roof_u_actual:.3f}" if roof_u_actual else "N/A"
    wall_required_str = f"{wall_u_required:.3f}"
    roof_required_str = f"{roof_u_required:.3f}"
    
    # Determine CSS classes
    wall_class = "compliant" if wall_status == "Compliant" else ("not-compliant" if wall_status == "Not Compliant" else "na")
    roof_class = "compliant" if roof_status == "Compliant" else ("not-compliant" if roof_status == "Not Compliant" else "na")
    
    # Check marks for compliance level
    ecsbc_check = "✓" if compliance_level == "ECSBC Compliant" else ""
    ecsbc_plus_check = "✓" if compliance_level == "ECSBC+ Compliant" else ""
    super_ecsbc_check = "✓" if compliance_level == "Super ECSBC Compliant" else ""
    
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create HTML table using f-string
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
            <td class="center">Wall Compliance [W/m².K]</td>
            <td class="center">Roof Compliance [W/m².K]</td>
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

def query_llm(question):
    """Query the LLM API with a question"""
    url = "https://api.vectorshift.ai/v1/pipeline/6954c79ba76af4b71858e962/run"
    
    payload = {"inputs": {"Input": question}}
    headers = {
        "Authorization": "Bearer sk_UUzE2PgugFATCpHwS8mAenzgMowmV6RpSg02UhTMhTYY7w8z",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse the JSON response
        response_data = response.json()
        
        # Extract the actual message from the outputs
        if "outputs" in response_data and "output_0" in response_data["outputs"]:
            return response_data["outputs"]["output_0"]
        else:
            # Fallback: return the entire response if structure is different
            return str(response_data)
            
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error parsing response: {str(e)}"

def compliance_page():
    """Main compliance check page"""
    # Create header with title and button
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("   ECSBC Compliance Check Dashboard")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        if st.button("🤖 Ask AI Assistant", type="primary", use_container_width=False, width=300):
            st.session_state.page = "AI Assistant"
            st.rerun()
    
    st.markdown("---")
    
    # Create three columns for inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Upload SIM File")
        uploaded_file = st.file_uploader("Choose a SIM file", type=['sim', 'txt'], width=300)
    
    with col2:
        st.subheader("Building Classification")
        building_type = st.selectbox(
            "Select Building Type",
            ["Hospitality", "Business", "Health Care", "Educational", "Assembly", "Shopping Complex"], width=300
        )
        
        compliance_level = st.selectbox(
            "Compliance Level Sought",
            ["ECSBC Compliant", "ECSBC+ Compliant", "Super ECSBC Compliant"], width=300
        )
    
    with col3:
        st.subheader("Project Details")
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

    st.markdown("---")
    
    if st.button("🔍 Check Compliance", type="primary"):
        if uploaded_file is None:
            st.error("⚠️ Please upload a SIM file first!")
            return
        
        with st.spinner("Analyzing SIM file..."):
            # Read the uploaded file
            file_content = uploaded_file.read()
            
            # Extract U-values
            wall_u_value, roof_u_value, extracted_text = extract_u_values_from_sim(file_content)
            
            # Get ECSBC requirements based on area
            requirements = get_ecsbc_requirements(climate_zone, building_type, project_area)
            required_wall_u = requirements["wall"]
            required_roof_u = requirements["roof"]
            
            # Display area exception notice if applicable
            if project_area < 10000:
                st.info(f"ℹ️ Area-based exception applied: Project area ({project_area:.0f} m²) is below 10,000 m². Using relaxed U-value requirements.")
            
            # Display results
            st.success("Analysis Complete!")
            st.markdown("---")
            
            # Create and display compliance table
            table_html = create_compliance_table(
                climate_zone, building_type, compliance_level,
                wall_u_value, roof_u_value, required_wall_u, required_roof_u,
                project_area
            )
            
            # Display the table with proper HTML rendering
            st.markdown("### ECSBC Compliance Report")
            # Use components.html for better rendering
            import streamlit.components.v1 as components
            
            # Wrap the table in a complete HTML document for proper rendering
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
            
            # Render with components.html for pixel-perfect display
            components.html(full_html, height=900, scrolling=True)
            
            # Show extracted text in expander
            with st.expander("View Extracted SIM File Content"):
                st.text(extracted_text if extracted_text else "No content extracted")
            
            # Download button for report
            st.markdown("<br>", unsafe_allow_html=True)
            col_left, col_center, col_right = st.columns([1, 2, 1])
            with col_center:
                # Create complete HTML document for download
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
                    label="Download Compliance Report",
                    data=download_html,
                    file_name=f"ECSBC_Compliance_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True,
                    type="secondary"
                )

def chatbot_page():
    """AI Assistant chatbot page"""
    
    # Add back button
    if st.button("← Back to Compliance Check", type="secondary"):
        st.session_state.page = "Compliance Check"
        st.rerun()
    
    st.title("🤖 ECSBC AI Assistant")
    st.markdown("Ask questions about ECSBC compliance, building codes, and energy efficiency.")
    st.markdown("---")
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about ECSBC compliance...", ):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = query_llm(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

def main():
    st.set_page_config(
        page_title="ECSBC Compliance Dashboard", 
        layout="wide",
        page_icon="🏢"
    )
    
    if "page" not in st.session_state:
        st.session_state.page = "Compliance Check"
    
    if st.session_state.page == "Compliance Check":
        compliance_page()
    elif st.session_state.page == "AI Assistant":
        chatbot_page()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    <small>ECSBC Compliance Dashboard v2.0 | Energy Conservation Building Code</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()