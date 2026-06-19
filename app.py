# app.py
"""
Center of Mass & Centroid Analysis System
Main Application Entry Point
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from modules.utils.config import ConfigManager
from modules.utils.theme import ThemeManager
from modules.utils.language import LanguageManager
from modules.geometry.shapes_2d import Rectangle, Circle, Triangle, Polygon
from modules.geometry.shapes_3d import Cube, Box, Sphere, Cylinder, Cone, Pyramid
from modules.analysis.com_analyzer import COMAnalyzer
from modules.visualization.plotter_2d import Plotter2D
from modules.visualization.plotter_3d import Plotter3D
from modules.reporting.report_generator import ReportGenerator
from modules.mesh.mesh_handler import MeshHandler

# Initialize configurations
config = ConfigManager()
theme_manager = ThemeManager()
lang_manager = LanguageManager()

# Page configuration
st.set_page_config(
    page_title="COM & Centroid Analysis System",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css(theme, rtl=False):
    """Load custom CSS based on theme"""
    if theme == "dark":
        bg_color = "#0e1117"
        text_color = "#fafafa"
        card_bg = "#1e1e1e"
        card_text = "#fafafa"
        border_color = "#333333"
        kpi_value_color = "#7b8cff"
        kpi_label_color = "#cccccc"
        section_title_color = "#fafafa"
        footer_color = "#cccccc"
    else:
        bg_color = "#ffffff"
        text_color = "#1a1a1a"
        card_bg = "#f8f9fa"
        card_text = "#1a1a1a"
        border_color = "#dee2e6"
        kpi_value_color = "#4a5acd"
        kpi_label_color = "#555555"
        section_title_color = "#1a1a1a"
        footer_color = "#555555"
    
    rtl_css = """
        /* RTL for Persian text - content only, NOT layout */
        .main-header {
            direction: rtl !important;
            text-align: right !important;
        }
        .main-header h1 {
            direction: rtl !important;
            text-align: right !important;
        }
        .main-header p {
            direction: rtl !important;
            text-align: right !important;
        }
        .stButton > button {
            direction: rtl !important;
            text-align: right !important;
        }
        h1, h2, h3, h4, h5, h6 {
            direction: rtl !important;
            text-align: right !important;
        }
        p {
            direction: rtl !important;
            text-align: right !important;
        }
        ul, ol, li {
            direction: rtl !important;
            text-align: right !important;
        }
        .kpi-card {
            direction: rtl !important;
            text-align: right !important;
        }
        .stMetric {
            direction: rtl !important;
            text-align: right !important;
        }
        .stTextInput > div > div > input {
            direction: rtl !important;
            text-align: right !important;
        }
        .stTextArea > div > div > textarea {
            direction: rtl !important;
            text-align: right !important;
        }
    """ if rtl else ""
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        .main-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 16px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .kpi-card {{
            background: {card_bg};
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
            border: 1px solid {border_color};
            transition: transform 0.2s;
            color: {card_text};
        }}
        
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        .kpi-card h3 {{
            color: {card_text} !important;
            margin-bottom: 0.5rem;
        }}
        
        .kpi-card h4 {{
            color: {card_text} !important;
        }}
        
        .kpi-card p {{
            color: {card_text} !important;
        }}
        
        .kpi-card ul {{
            color: {card_text} !important;
        }}
        
        .kpi-card li {{
            color: {card_text} !important;
        }}
        
        .kpi-card div {{
            color: {card_text} !important;
        }}
        
        .kpi-value {{
            font-size: 2rem;
            font-weight: 700;
            color: {kpi_value_color} !important;
            margin: 0.5rem 0;
        }}
        
        .kpi-label {{
            font-size: 0.875rem;
            color: {kpi_label_color} !important;
            opacity: 0.85;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .stButton > button {{
            border-radius: 12px;
            padding: 1.5rem;
            font-weight: 400;
            transition: all 0.2s;
            border: 1px solid {border_color};
            background: {card_bg};
            color: {card_text};
            height: 100%;
            min-height: 220px;
            white-space: pre-line;
            text-align: left;
            font-size: 0.95rem;
            line-height: 1.6;
            width: 100%;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border-color: #667eea;
            background: {card_bg};
            color: {card_text};
        }}
        
        .status-stable {{
            color: #10b981 !important;
            font-weight: 600;
        }}
        
        .status-unstable {{
            color: #ef4444 !important;
            font-weight: 600;
        }}
        
        .section-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin: 1rem 0;
            color: {section_title_color};
        }}
        
        .footer-text {{
            text-align: center;
            opacity: 0.7;
            color: {footer_color};
        }}
        
        {rtl_css}
        </style>
    """, unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=COM+System", width=150)
    st.markdown("---")
    
    # Initialize page in session state if not exists
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Home", "2D Analysis", "3D Analysis", "STL Import", "Report Generator", "Settings"],
        label_visibility="collapsed",
        index=["Home", "2D Analysis", "3D Analysis", "STL Import", "Report Generator", "Settings"].index(st.session_state.page)
    )
    
    # Update session state when radio changes
    st.session_state.page = page
    
    st.markdown("---")
    
    # Theme selector
    theme = st.selectbox(
        "Theme",
        ["Dark", "Light", "System"],
        key="theme_selector"
    )
    
    # Language selector
    language = st.selectbox(
        "Language / زبان",
        ["English", "Persian"],
        key="language_selector"
    )

# Check if RTL needed (Persian)
is_rtl = (language == "Persian")

# Apply theme with system detection
if theme == "System":
    try:
        base_theme = st.get_option("theme.base")
        load_css(base_theme if base_theme else "light", is_rtl)
    except:
        load_css("light", is_rtl)
else:
    load_css(theme.lower(), is_rtl)

translations = lang_manager.get_translations(language)

# Header
st.markdown(f"""
    <div class="main-header">
        <h1>{translations['title']}</h1>
        <p style="font-size: 1.1rem; opacity: 0.9;">{translations['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state for data
if 'com_data' not in st.session_state:
    st.session_state.com_data = None
if 'visualization_data' not in st.session_state:
    st.session_state.visualization_data = None

# Page routing
if page == "Home":
    st.markdown(f"## {translations['welcome']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        btn_text_2d = f"{translations['btn_2d_title']}\n\n{translations['btn_2d_desc']}\n\n{translations['btn_2d_list']}"
        if st.button(btn_text_2d, key="btn_2d", use_container_width=True):
            st.session_state.page = "2D Analysis"
            st.rerun()
    
    with col2:
        btn_text_3d = f"{translations['btn_3d_title']}\n\n{translations['btn_3d_desc']}\n\n{translations['btn_3d_list']}"
        if st.button(btn_text_3d, key="btn_3d", use_container_width=True):
            st.session_state.page = "3D Analysis"
            st.rerun()
    
    with col3:
        btn_text_stl = f"{translations['btn_stl_title']}\n\n{translations['btn_stl_desc']}\n\n{translations['btn_stl_list']}"
        if st.button(btn_text_stl, key="btn_stl", use_container_width=True):
            st.session_state.page = "STL Import"
            st.rerun()
    
    st.markdown("---")
    
    # Quick start guide
    st.markdown(f"## {translations['quick_start_guide']}")
    st.markdown(translations['quick_start_steps'])

elif page == "2D Analysis":
    st.markdown(f"## {translations['2d_analysis']}")
    
    mode = st.radio(
        "Input Mode",
        ["Simple Shapes", "Composite Geometry", "Coordinate Input"],
        horizontal=True
    )
    
    analyzer = COMAnalyzer()
    
    if mode == "Simple Shapes":
        shape_type = st.selectbox("Shape Type", ["Rectangle", "Circle", "Triangle"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if shape_type == "Rectangle":
                width = st.number_input("Width", min_value=0.1, value=10.0, step=0.1)
                height = st.number_input("Height", min_value=0.1, value=5.0, step=0.1)
                shape = Rectangle(width, height)
            elif shape_type == "Circle":
                radius = st.number_input("Radius", min_value=0.1, value=5.0, step=0.1)
                shape = Circle(radius)
            elif shape_type == "Triangle":
                base = st.number_input("Base", min_value=0.1, value=6.0, step=0.1)
                height = st.number_input("Height", min_value=0.1, value=4.0, step=0.1)
                shape = Triangle(base, height)
        
        with col2:
            center_x = st.number_input("Center X", value=0.0, step=0.1)
            center_y = st.number_input("Center Y", value=0.0, step=0.1)
            shape.set_position(center_x, center_y)
        
        if st.button("Calculate", type="primary"):
            results = analyzer.analyze_2d(shape)
            st.session_state.com_data = results
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Area</div><div class="kpi-value">{results["area"]:.2f}</div><div>mm²</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Centroid X</div><div class="kpi-value">{results["centroid_x"]:.2f}</div><div>mm</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Centroid Y</div><div class="kpi-value">{results["centroid_y"]:.2f}</div><div>mm</div></div>', unsafe_allow_html=True)
            
            plotter = Plotter2D()
            fig = plotter.plot_shape_with_centroid(shape, results)
            st.plotly_chart(fig, use_container_width=True)
    
    elif mode == "Composite Geometry":
        st.markdown("### Composite Shape Builder")
        
        if 'components' not in st.session_state:
            st.session_state.components = []
        
        with st.expander("Add Component", expanded=True):
            comp_type = st.selectbox("Component Type", ["Rectangle", "Circle", "Triangle"])
            
            if comp_type == "Rectangle":
                w = st.number_input("Width", min_value=0.1, value=5.0, key="comp_w")
                h = st.number_input("Height", min_value=0.1, value=3.0, key="comp_h")
                cx = st.number_input("Center X", value=0.0, key="comp_cx")
                cy = st.number_input("Center Y", value=0.0, key="comp_cy")
                if st.button("Add Component"):
                    component = Rectangle(w, h, cx, cy)
                    st.session_state.components.append(component)
                    st.rerun()
            elif comp_type == "Circle":
                r = st.number_input("Radius", min_value=0.1, value=2.0, key="comp_r")
                cx = st.number_input("Center X", value=0.0, key="comp_cx")
                cy = st.number_input("Center Y", value=0.0, key="comp_cy")
                if st.button("Add Component"):
                    component = Circle(r, cx, cy)
                    st.session_state.components.append(component)
                    st.rerun()
        
        if st.session_state.components:
            st.markdown("### Current Components")
            for i, comp in enumerate(st.session_state.components):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"Component {i+1}: {comp.__class__.__name__}")
                with col2:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.components.pop(i)
                        st.rerun()
            
            if st.button("Calculate Composite", type="primary"):
                results = analyzer.analyze_composite_2d(st.session_state.components)
                st.session_state.com_data = results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Area", f"{results['total_area']:.2f} mm²")
                with col2:
                    st.metric("Centroid X", f"{results['centroid_x']:.2f} mm")
                with col3:
                    st.metric("Centroid Y", f"{results['centroid_y']:.2f} mm")
                plotter = Plotter2D()
                fig = plotter.plot_composite_with_centroid(st.session_state.components, results)
                st.plotly_chart(fig, use_container_width=True)
    
    elif mode == "Coordinate Input":
        st.markdown("### Polygon Coordinate Input")
        input_method = st.radio("Input Method", ["Manual Entry", "CSV Upload"])
        
        if input_method == "Manual Entry":
            coordinates_text = st.text_area(
                "Enter coordinates (one per line: x,y)",
                "0,0\n10,0\n10,5\n5,8\n0,5",
                height=150
            )
            try:
                coordinates = [
                    [float(x.strip()) for x in line.split(",")]
                    for line in coordinates_text.strip().split("\n")
                ]
                if len(coordinates) >= 3:
                    polygon = Polygon(coordinates)
                    if st.button("Calculate", type="primary"):
                        results = analyzer.analyze_2d(polygon)
                        st.session_state.com_data = results
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Area", f"{results['area']:.2f} mm²")
                        with col2:
                            st.metric("Centroid X", f"{results['centroid_x']:.2f} mm")
                        with col3:
                            st.metric("Centroid Y", f"{results['centroid_y']:.2f} mm")
                        plotter = Plotter2D()
                        fig = plotter.plot_polygon_with_centroid(coordinates, results)
                        st.plotly_chart(fig, use_container_width=True)
            except:
                st.error("Invalid coordinate format")
        else:
            uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
            if uploaded_file:
                import pandas as pd
                df = pd.read_csv(uploaded_file)
                st.dataframe(df)

elif page == "3D Analysis":
    st.markdown(f"## {translations['3d_analysis']}")
    
    mode = st.radio(
        "Input Mode",
        ["Simple Shapes", "Composite Geometry"],
        horizontal=True
    )
    
    if mode == "Simple Shapes":
        shape_type = st.selectbox("Shape Type", ["Cube", "Box", "Sphere", "Cylinder", "Cone", "Pyramid"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if shape_type == "Cube":
                length = st.number_input("Length", min_value=0.1, value=10.0)
                width = st.number_input("Width", min_value=0.1, value=10.0)
                height = st.number_input("Height", min_value=0.1, value=10.0)
                shape = Cube(length, width, height)
            elif shape_type == "Box":
                length = st.number_input("Length", min_value=0.1, value=8.0)
                width = st.number_input("Width", min_value=0.1, value=6.0)
                height = st.number_input("Height", min_value=0.1, value=4.0)
                shape = Box(length, width, height)
            elif shape_type == "Sphere":
                radius = st.number_input("Radius", min_value=0.1, value=5.0)
                shape = Sphere(radius)
            elif shape_type == "Cylinder":
                radius = st.number_input("Radius", min_value=0.1, value=3.0)
                height = st.number_input("Height", min_value=0.1, value=10.0)
                shape = Cylinder(radius, height)
            elif shape_type == "Cone":
                radius = st.number_input("Base Radius", min_value=0.1, value=3.0)
                height = st.number_input("Height", min_value=0.1, value=8.0)
                shape = Cone(radius, height)
            elif shape_type == "Pyramid":
                base_length = st.number_input("Base Length", min_value=0.1, value=6.0)
                base_width = st.number_input("Base Width", min_value=0.1, value=6.0)
                height = st.number_input("Height", min_value=0.1, value=8.0)
                shape = Pyramid(base_length, base_width, height)
        
        with col2:
            pos_x = st.number_input("Position X", value=0.0)
            pos_y = st.number_input("Position Y", value=0.0)
            pos_z = st.number_input("Position Z", value=0.0)
            shape.set_position(pos_x, pos_y, pos_z)
        
        if st.button("Calculate", type="primary"):
            analyzer = COMAnalyzer()
            results = analyzer.analyze_3d(shape)
            st.session_state.com_data = results
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Volume</div><div class="kpi-value">{results["volume"]:.2f}</div><div>mm³</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Centroid X</div><div class="kpi-value">{results["centroid_x"]:.2f}</div><div>mm</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Centroid Y</div><div class="kpi-value">{results["centroid_y"]:.2f}</div><div>mm</div></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Centroid Z</div><div class="kpi-value">{results["centroid_z"]:.2f}</div><div>mm</div></div>', unsafe_allow_html=True)
            
            plotter = Plotter3D()
            fig = plotter.plot_3d_shape_with_centroid(shape, results)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### Stability Analysis")
            
            if shape_type in ["Cube", "Box", "Cylinder"]:
                if results['centroid_z'] < height/2:
                    stability = "Stable"
                    stability_class = "status-stable"
                else:
                    stability = "Potentially Unstable"
                    stability_class = "status-unstable"
                
                st.markdown(f'<div class="kpi-card"><h4>Stability Status: <span class="{stability_class}">{stability}</span></h4><p>The centroid is at height {results["centroid_z"]:.2f} mm.</p></div>', unsafe_allow_html=True)

elif page == "STL Import":
    st.markdown(f"## {translations['stl_import']}")
    
    uploaded_file = st.file_uploader("Upload STL File", type=['stl'])
    
    if uploaded_file:
        mesh_handler = MeshHandler()
        try:
            mesh_data = mesh_handler.load_stl(uploaded_file)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Vertices", mesh_data['num_vertices'])
            with col2:
                st.metric("Faces", mesh_data['num_faces'])
            with col3:
                st.metric("Volume", f"{mesh_data['volume']:.2f} mm³")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Volume", f"{mesh_data['volume']:.2f}")
            with col2:
                st.metric("Centroid X", f"{mesh_data['centroid'][0]:.2f}")
            with col3:
                st.metric("Centroid Y", f"{mesh_data['centroid'][1]:.2f}")
            with col4:
                st.metric("Centroid Z", f"{mesh_data['centroid'][2]:.2f}")
            
            plotter = Plotter3D()
            fig = plotter.plot_mesh_with_centroid(mesh_data)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error processing STL file: {str(e)}")

elif page == "Report Generator":
    st.markdown(f"## {translations['report_generator']}")
    
    if st.session_state.com_data:
        st.success("Analysis data available for report generation")
        
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("Project Name", "COM Analysis Project")
            engineer_name = st.text_input("Engineer Name", "")
            notes = st.text_area("Additional Notes", "")
        with col2:
            include_visualization = st.checkbox("Include Visualizations", True)
            include_calculations = st.checkbox("Include Detailed Calculations", True)
            report_format = st.selectbox("Report Format", ["PDF", "JSON", "CSV"])
        
        if st.button("Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                report_gen = ReportGenerator()
                if report_format == "PDF":
                    pdf_bytes = report_gen.generate_pdf(st.session_state.com_data, project_name, engineer_name, notes)
                    st.download_button("Download PDF Report", pdf_bytes, f"com_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", "application/pdf")
                elif report_format == "JSON":
                    json_str = report_gen.generate_json(st.session_state.com_data)
                    st.download_button("Download JSON Report", json_str, f"com_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json")
                elif report_format == "CSV":
                    csv_bytes = report_gen.generate_csv(st.session_state.com_data)
                    st.download_button("Download CSV Report", csv_bytes, f"com_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")
    else:
        st.warning("No analysis data available. Please perform an analysis first.")

elif page == "Settings":
    st.markdown(f"## {translations['settings']}")
    st.markdown("### Unit System")
    unit_system = st.selectbox("Length Unit", ["mm", "cm", "m", "in"])
    st.markdown("### Precision")
    decimal_places = st.slider("Decimal Places", 1, 6, 2)
    st.markdown("### Visualization Settings")
    show_grid = st.checkbox("Show Grid", True)
    show_axes = st.checkbox("Show Axes", True)
    marker_size = st.slider("Marker Size", 5, 20, 10)
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

# Footer
st.markdown("---")
st.markdown(
    "<div class='footer-text'>"
    "Center of Mass & Centroid Analysis System v1.0 | "
    "© 2024 Engineering Analysis Tools"
    "</div>",
    unsafe_allow_html=True
)