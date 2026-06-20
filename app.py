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
import pandas as pd
import numpy as np
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
        .add-badge {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .cut-badge {
            display: inline-block;
            background: #ef4444;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
    """ if rtl else """
        .add-badge {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .cut-badge {
            display: inline-block;
            background: #ef4444;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
    """
    
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
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            font-weight: 500;
            transition: all 0.2s;
            border: 1px solid {border_color};
            background: {card_bg};
            color: {card_text};
            font-size: 0.9rem;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-color: #667eea;
        }}
        
        .big-nav-btn button {{
            border-radius: 12px !important;
            padding: 1.5rem !important;
            font-weight: 400 !important;
            min-height: 220px !important;
            white-space: pre-line !important;
            text-align: left !important;
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
            width: 100% !important;
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
    
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    
    page = st.radio(
        "Navigation",
        ["Home", "2D Analysis", "3D Analysis", "STL Import", "Report Generator", "Settings"],
        label_visibility="collapsed",
        index=["Home", "2D Analysis", "3D Analysis", "STL Import", "Report Generator", "Settings"].index(st.session_state.page)
    )
    
    st.session_state.page = page
    
    st.markdown("---")
    
    theme = st.selectbox(
        "Theme",
        ["Dark", "Light", "System"],
        key="theme_selector"
    )
    
    language = st.selectbox(
        "Language / زبان",
        ["English", "Persian"],
        key="language_selector"
    )

is_rtl = (language == "Persian")

if theme == "System":
    try:
        base_theme = st.get_option("theme.base")
        load_css(base_theme if base_theme else "dark", is_rtl)
    except:
        load_css("dark", is_rtl)
else:
    load_css(theme.lower(), is_rtl)

translations = lang_manager.get_translations(language)

st.markdown(f"""
    <div class="main-header">
        <h1>{translations['title']}</h1>
        <p style="font-size: 1.1rem; opacity: 0.9;">{translations['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

if 'com_data' not in st.session_state:
    st.session_state.com_data = None

# Page routing
if page == "Home":
    st.markdown(f"## {translations['welcome']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        btn_text_2d = f"{translations['btn_2d_title']}\n\n{translations['btn_2d_desc']}\n\n{translations['btn_2d_list']}"
        st.markdown(f'<div class="big-nav-btn">', unsafe_allow_html=True)
        if st.button(btn_text_2d, key="btn_2d", use_container_width=True):
            st.session_state.page = "2D Analysis"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        btn_text_3d = f"{translations['btn_3d_title']}\n\n{translations['btn_3d_desc']}\n\n{translations['btn_3d_list']}"
        st.markdown(f'<div class="big-nav-btn">', unsafe_allow_html=True)
        if st.button(btn_text_3d, key="btn_3d", use_container_width=True):
            st.session_state.page = "3D Analysis"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        btn_text_stl = f"{translations['btn_stl_title']}\n\n{translations['btn_stl_desc']}\n\n{translations['btn_stl_list']}"
        st.markdown(f'<div class="big-nav-btn">', unsafe_allow_html=True)
        if st.button(btn_text_stl, key="btn_stl", use_container_width=True):
            st.session_state.page = "STL Import"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
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
    plotter = Plotter2D()
    
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
        
        st.markdown("### Live Preview")
        results = analyzer.analyze_2d(shape)
        fig = plotter.plot_shape_with_centroid(shape, results)
        st.plotly_chart(fig, use_container_width=True, key="live_2d")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Area", f"{results['area']:.2f} mm²")
        with col2:
            st.metric("Centroid X", f"{results['centroid_x']:.2f} mm")
        with col3:
            st.metric("Centroid Y", f"{results['centroid_y']:.2f} mm")
        
        if st.button("💾 Save to Report", type="primary"):
            st.session_state.com_data = results
            st.success("Results saved! Go to Report Generator to export.")
    
    elif mode == "Composite Geometry":
        st.markdown("### Composite Shape Builder")
        
        if 'components' not in st.session_state:
            st.session_state.components = []
        
        with st.expander("➕ Add Component", expanded=True):
            comp_type = st.selectbox("Component Type", ["Rectangle", "Circle", "Triangle"])
            
            # Add/Cut toggle
            operation = st.radio(
                "Operation",
                ["🟢 Add Material", "🔴 Cut Hole"],
                horizontal=True,
                help="Add: adds to total area. Cut: subtracts from total area (creates holes)"
            )
            is_add = (operation == "🟢 Add Material")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if comp_type == "Rectangle":
                    w = st.number_input("Width", min_value=0.1, value=5.0, key="comp_w")
                    h = st.number_input("Height", min_value=0.1, value=3.0, key="comp_h")
                elif comp_type == "Circle":
                    r = st.number_input("Radius", min_value=0.1, value=2.0, key="comp_r")
                elif comp_type == "Triangle":
                    b = st.number_input("Base", min_value=0.1, value=4.0, key="comp_b")
                    h = st.number_input("Height", min_value=0.1, value=3.0, key="comp_h")
            
            with col2:
                cx = st.number_input("Center X", value=0.0, key="comp_cx")
                cy = st.number_input("Center Y", value=0.0, key="comp_cy")
            
            op_label = "➕ Add" if is_add else "🔴 Cut"
            if st.button(f"{op_label} Component"):
                if comp_type == "Rectangle":
                    component = Rectangle(w, h, cx, cy)
                elif comp_type == "Circle":
                    component = Circle(r, cx, cy)
                elif comp_type == "Triangle":
                    component = Triangle(b, h, cx, cy)
                
                comp_info = {
                    'name': f"Comp {len(st.session_state.components)+1}",
                    'type': comp_type,
                    'shape': component,
                    'operation': 'add' if is_add else 'cut'
                }
                st.session_state.components.append(comp_info)
                st.rerun()
        
        if st.session_state.components:
            st.markdown("### Components Table")
            
            table_data = []
            for i, comp in enumerate(st.session_state.components):
                shape = comp['shape']
                op_badge = "<span class='add-badge'>ADD</span>" if comp['operation'] == 'add' else "<span class='cut-badge'>CUT</span>"
                area_val = shape.get_area()
                sign = "+" if comp['operation'] == 'add' else "-"
                table_data.append({
                    '#': i+1,
                    'Op': op_badge,
                    'Type': comp['type'],
                    'Area': f"{sign}{area_val:.2f}",
                    'Centroid': f"({shape.get_centroid()[0]:.1f}, {shape.get_centroid()[1]:.1f})"
                })
            
            df = pd.DataFrame(table_data)
            
            st.markdown("#### Click a row to select, then press delete:")
            # Use columns without the HTML Op column for selection
            df_display = df[['#', 'Type', 'Area', 'Centroid']].copy()
            df_display['Op'] = [c['operation'].upper() for c in st.session_state.components]
            df_display = df_display[['#', 'Op', 'Type', 'Area', 'Centroid']]
            
            selection = st.dataframe(
                df_display, 
                use_container_width=True, 
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun",
                key="component_table"
            )
            
            if selection.selection.rows:
                selected_row = selection.selection.rows[0]
                comp = st.session_state.components[selected_row]
                op_text = "🟢 ADD" if comp['operation'] == 'add' else "🔴 CUT"
                col_del, col_info = st.columns([1, 3])
                with col_del:
                    if st.button("🗑️ Delete Selected", type="secondary"):
                        st.session_state.components.pop(selected_row)
                        st.rerun()
                with col_info:
                    st.info(f"Selected: #{selected_row+1} - {comp['type']} ({op_text})")
            
            # LIVE PREVIEW with add/cut coloring
            st.markdown("### Live Preview")
            shapes_only = [c['shape'] for c in st.session_state.components]
            operations = [c['operation'] for c in st.session_state.components]
            
            # Calculate composite with add/cut
            total_area = 0
            weighted_x = 0
            weighted_y = 0
            for shape, op in zip(shapes_only, operations):
                area = shape.get_area()
                centroid = shape.get_centroid()
                if op == 'add':
                    total_area += area
                    weighted_x += area * centroid[0]
                    weighted_y += area * centroid[1]
                else:
                    total_area -= area
                    weighted_x -= area * centroid[0]
                    weighted_y -= area * centroid[1]
            
            if total_area > 0:
                com_x = weighted_x / total_area
                com_y = weighted_y / total_area
            else:
                com_x, com_y = 0, 0
            
            results = {
                'total_area': total_area,
                'centroid_x': com_x,
                'centroid_y': com_y
            }
            
            # Use composite plotter with add/cut colors
            fig = plotter.plot_composite_with_centroid(shapes_only, results, operations)
            st.plotly_chart(fig, use_container_width=True, key="live_composite")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Net Area", f"{results['total_area']:.2f} mm²")
            with col2:
                st.metric("Centroid X", f"{results['centroid_x']:.2f} mm")
            with col3:
                st.metric("Centroid Y", f"{results['centroid_y']:.2f} mm")
            
            if st.button("💾 Save to Report", type="primary"):
                st.session_state.com_data = results
                st.success("Results saved! Go to Report Generator to export.")
    
    elif mode == "Coordinate Input":
        st.markdown("### Polygon Coordinate Input")
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
                results = analyzer.analyze_2d(polygon)
                
                st.markdown("### Live Preview")
                fig = plotter.plot_polygon_with_centroid(coordinates, results)
                st.plotly_chart(fig, use_container_width=True, key="live_polygon")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Area", f"{results['area']:.2f} mm²")
                with col2:
                    st.metric("Centroid X", f"{results['centroid_x']:.2f} mm")
                with col3:
                    st.metric("Centroid Y", f"{results['centroid_y']:.2f} mm")
                
                if st.button("💾 Save to Report", type="primary"):
                    st.session_state.com_data = results
                    st.success("Results saved! Go to Report Generator to export.")
            else:
                st.warning("Please enter at least 3 coordinates")
        except:
            st.error("Invalid coordinate format")

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
        
        st.markdown("### Live Preview")
        analyzer = COMAnalyzer()
        results = analyzer.analyze_3d(shape)
        plotter_3d = Plotter3D()
        fig = plotter_3d.plot_3d_shape_with_centroid(shape, results)
        st.plotly_chart(fig, use_container_width=True, key="live_3d")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Volume", f"{results['volume']:.2f} mm³")
        with col2:
            st.metric("Centroid X", f"{results['centroid_x']:.2f} mm")
        with col3:
            st.metric("Centroid Y", f"{results['centroid_y']:.2f} mm")
        with col4:
            st.metric("Centroid Z", f"{results['centroid_z']:.2f} mm")
        
        if st.button("💾 Save to Report", type="primary"):
            st.session_state.com_data = results
            st.success("Results saved! Go to Report Generator to export.")
        
        if shape_type in ["Cube", "Box", "Cylinder"]:
            st.markdown("---")
            st.markdown("### Stability Analysis")
            if results['centroid_z'] < height/2:
                stability, stability_class = "Stable", "status-stable"
            else:
                stability, stability_class = "Potentially Unstable", "status-unstable"
            st.markdown(f'<div class="kpi-card"><h4>Stability: <span class="{stability_class}">{stability}</span></h4><p>Centroid height: {results["centroid_z"]:.2f} mm</p></div>', unsafe_allow_html=True)
    
    elif mode == "Composite Geometry":
        st.markdown("### 3D Composite Builder")
        
        if 'components_3d' not in st.session_state:
            st.session_state.components_3d = []
        
        with st.expander("➕ Add 3D Component", expanded=True):
            comp_type = st.selectbox("Component Type", ["Cube", "Box", "Sphere", "Cylinder", "Cone", "Pyramid"])
            
            operation = st.radio(
                "Operation",
                ["🟢 Add Material", "🔴 Cut Hole"],
                horizontal=True,
                help="Add: adds to total volume. Cut: subtracts from total volume"
            )
            is_add = (operation == "🟢 Add Material")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if comp_type == "Cube":
                    l = st.number_input("Length", min_value=0.1, value=5.0, key="c3d_l")
                    w = st.number_input("Width", min_value=0.1, value=5.0, key="c3d_w")
                    h = st.number_input("Height", min_value=0.1, value=5.0, key="c3d_h")
                elif comp_type == "Box":
                    l = st.number_input("Length", min_value=0.1, value=6.0, key="c3d_l")
                    w = st.number_input("Width", min_value=0.1, value=4.0, key="c3d_w")
                    h = st.number_input("Height", min_value=0.1, value=3.0, key="c3d_h")
                elif comp_type == "Sphere":
                    r = st.number_input("Radius", min_value=0.1, value=3.0, key="c3d_r")
                elif comp_type == "Cylinder":
                    r = st.number_input("Radius", min_value=0.1, value=2.0, key="c3d_r")
                    h = st.number_input("Height", min_value=0.1, value=6.0, key="c3d_h")
                elif comp_type == "Cone":
                    r = st.number_input("Base Radius", min_value=0.1, value=2.0, key="c3d_r")
                    h = st.number_input("Height", min_value=0.1, value=5.0, key="c3d_h")
                elif comp_type == "Pyramid":
                    bl = st.number_input("Base Length", min_value=0.1, value=4.0, key="c3d_bl")
                    bw = st.number_input("Base Width", min_value=0.1, value=4.0, key="c3d_bw")
                    h = st.number_input("Height", min_value=0.1, value=5.0, key="c3d_h")
            
            with col2:
                px = st.number_input("Position X", value=0.0, key="c3d_px")
                py = st.number_input("Position Y", value=0.0, key="c3d_py")
                pz = st.number_input("Position Z", value=0.0, key="c3d_pz")
            
            op_label = "➕ Add" if is_add else "🔴 Cut"
            if st.button(f"{op_label} Component"):
                if comp_type == "Cube":
                    shape = Cube(l, w, h, px, py, pz)
                elif comp_type == "Box":
                    shape = Box(l, w, h, px, py, pz)
                elif comp_type == "Sphere":
                    shape = Sphere(r, px, py, pz)
                elif comp_type == "Cylinder":
                    shape = Cylinder(r, h, px, py, pz)
                elif comp_type == "Cone":
                    shape = Cone(r, h, px, py, pz)
                elif comp_type == "Pyramid":
                    shape = Pyramid(bl, bw, h, px, py, pz)
                
                comp_info = {
                    'name': f"Comp {len(st.session_state.components_3d)+1}",
                    'type': comp_type,
                    'shape': shape,
                    'operation': 'add' if is_add else 'cut'
                }
                st.session_state.components_3d.append(comp_info)
                st.rerun()
        
        if st.session_state.components_3d:
            st.markdown("### 3D Components Table")
            
            table_data = []
            for i, comp in enumerate(st.session_state.components_3d):
                shape = comp['shape']
                vol_val = shape.get_volume()
                sign = "+" if comp['operation'] == 'add' else "-"
                table_data.append({
                    '#': i+1,
                    'Op': comp['operation'].upper(),
                    'Type': comp['type'],
                    'Volume': f"{sign}{vol_val:.2f}",
                    'Centroid': f"({shape.get_centroid()[0]:.1f}, {shape.get_centroid()[1]:.1f}, {shape.get_centroid()[2]:.1f})"
                })
            
            df = pd.DataFrame(table_data)
            
            st.markdown("#### Click a row to select, then press delete:")
            selection = st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun",
                key="component_table_3d"
            )
            
            if selection.selection.rows:
                selected_row = selection.selection.rows[0]
                if st.button("🗑️ Delete Selected", type="secondary"):
                    st.session_state.components_3d.pop(selected_row)
                    st.rerun()
            
            # Calculate composite 3D
            shapes_only = [c['shape'] for c in st.session_state.components_3d]
            operations = [c['operation'] for c in st.session_state.components_3d]
            
            total_volume = 0
            weighted_x = 0
            weighted_y = 0
            weighted_z = 0
            for shape, op in zip(shapes_only, operations):
                vol = shape.get_volume()
                centroid = shape.get_centroid()
                if op == 'add':
                    total_volume += vol
                    weighted_x += vol * centroid[0]
                    weighted_y += vol * centroid[1]
                    weighted_z += vol * centroid[2]
                else:
                    total_volume -= vol
                    weighted_x -= vol * centroid[0]
                    weighted_y -= vol * centroid[1]
                    weighted_z -= vol * centroid[2]
            
            if total_volume > 0:
                com_x = weighted_x / total_volume
                com_y = weighted_y / total_volume
                com_z = weighted_z / total_volume
            else:
                com_x, com_y, com_z = 0, 0, 0
            
            results_3d = {
                'volume': total_volume,
                'centroid_x': com_x,
                'centroid_y': com_y,
                'centroid_z': com_z
            }
            
            st.markdown("### Live Preview (3D Composite)")
            plotter_3d = Plotter3D()
            # Plot first add shape as reference
            for shape, op in zip(shapes_only, operations):
                if op == 'add':
                    fig = plotter_3d.plot_3d_shape_with_centroid(shape, results_3d)
                    st.plotly_chart(fig, use_container_width=True, key="live_3d_composite")
                    break
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Net Volume", f"{results_3d['volume']:.2f} mm³")
            with col2:
                st.metric("Centroid X", f"{results_3d['centroid_x']:.2f} mm")
            with col3:
                st.metric("Centroid Y", f"{results_3d['centroid_y']:.2f} mm")
            with col4:
                st.metric("Centroid Z", f"{results_3d['centroid_z']:.2f} mm")
            
            if st.button("💾 Save to Report", type="primary"):
                st.session_state.com_data = results_3d
                st.success("Results saved! Go to Report Generator to export.")

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
            report_format = st.selectbox("Report Format", ["PDF", "JSON", "CSV"])
        
        if st.button("Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                report_gen = ReportGenerator()
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                if report_format == "PDF":
                    pdf_bytes = report_gen.generate_pdf(st.session_state.com_data, project_name, engineer_name, notes)
                    st.download_button("Download PDF", pdf_bytes, f"com_report_{ts}.pdf", "application/pdf")
                elif report_format == "JSON":
                    json_str = report_gen.generate_json(st.session_state.com_data)
                    st.download_button("Download JSON", json_str, f"com_report_{ts}.json", "application/json")
                elif report_format == "CSV":
                    csv_bytes = report_gen.generate_csv(st.session_state.com_data)
                    st.download_button("Download CSV", csv_bytes, f"com_report_{ts}.csv", "text/csv")
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
    unsafe_allow_html=True)