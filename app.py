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
from io import BytesIO
import base64

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
        .main-header { direction: rtl !important; text-align: right !important; }
        .main-header h1 { direction: rtl !important; text-align: right !important; }
        .main-header p { direction: rtl !important; text-align: right !important; }
        .stButton > button { direction: rtl !important; text-align: right !important; }
        h1, h2, h3, h4, h5, h6 { direction: rtl !important; text-align: right !important; }
        p { direction: rtl !important; text-align: right !important; }
        ul, ol, li { direction: rtl !important; text-align: right !important; }
        .kpi-card { direction: rtl !important; text-align: right !important; }
        .stMetric { direction: rtl !important; text-align: right !important; }
        .stTextInput > div > div > input { direction: rtl !important; text-align: right !important; }
        .stTextArea > div > div > textarea { direction: rtl !important; text-align: right !important; }
        .add-badge { display: inline-block; background: #10b981; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
        .cut-badge { display: inline-block; background: #ef4444; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
        .reset-btn button { background: #ef4444 !important; color: white !important; border: none !important; }
    """ if rtl else """
        .add-badge { display: inline-block; background: #10b981; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
        .cut-badge { display: inline-block; background: #ef4444; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
        .reset-btn button { background: #ef4444 !important; color: white !important; border: none !important; }
    """
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        
        .main-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem; border-radius: 16px; color: white;
            margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .kpi-card {{
            background: {card_bg}; border-radius: 12px; padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08); border: 1px solid {border_color};
            transition: transform 0.2s; color: {card_text};
        }}
        .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); }}
        .kpi-card h3 {{ color: {card_text} !important; margin-bottom: 0.5rem; }}
        .kpi-card h4 {{ color: {card_text} !important; }}
        .kpi-card p {{ color: {card_text} !important; }}
        .kpi-card ul {{ color: {card_text} !important; }}
        .kpi-card li {{ color: {card_text} !important; }}
        .kpi-card div {{ color: {card_text} !important; }}
        
        .kpi-value {{ font-size: 2rem; font-weight: 700; color: {kpi_value_color} !important; margin: 0.5rem 0; }}
        .kpi-label {{ font-size: 0.875rem; color: {kpi_label_color} !important; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.05em; }}
        
        .stButton > button {{
            border-radius: 8px; padding: 0.5rem 1.2rem; font-weight: 500;
            transition: all 0.2s; border: 1px solid {border_color};
            background: {card_bg}; color: {card_text}; font-size: 0.9rem;
        }}
        .stButton > button:hover {{ transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); border-color: #667eea; }}
        
        .big-nav-btn button {{
            border-radius: 12px !important; padding: 1.5rem !important; font-weight: 400 !important;
            min-height: 220px !important; white-space: pre-line !important; text-align: left !important;
            font-size: 0.95rem !important; line-height: 1.6 !important; width: 100% !important;
        }}
        
        .reset-btn button {{ background: #ef4444 !important; color: white !important; border: none !important; }}
        .reset-btn button:hover {{ background: #dc2626 !important; }}
        
        .status-stable {{ color: #10b981 !important; font-weight: 600; }}
        .status-unstable {{ color: #ef4444 !important; font-weight: 600; }}
        .section-title {{ font-size: 1.25rem; font-weight: 600; margin: 1rem 0; color: {section_title_color}; }}
        .footer-text {{ text-align: center; opacity: 0.7; color: {footer_color}; }}
        
        {rtl_css}
        </style>
    """, unsafe_allow_html=True)

# ===== SIDEBAR - handles language/theme/page switching =====
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=COM+System", width=150)
    st.markdown("---")
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    if 'language' not in st.session_state:
        st.session_state.language = "English"
    if 'theme' not in st.session_state:
        st.session_state.theme = "Dark"
    
    # Get translations for sidebar display
    sidebar_t = lang_manager.get_translations(st.session_state.language)
    
    # Navigation - internal keys mapped to display
    nav_internal = ["Home", "2D Analysis", "3D Analysis", "STL Import", "Report Generator", "Settings"]
    nav_display = [
        sidebar_t['nav_home'], sidebar_t['nav_2d'], sidebar_t['nav_3d'],
        sidebar_t['nav_stl'], sidebar_t['nav_report'], sidebar_t['nav_settings']
    ]
    
    if st.session_state.page not in nav_internal:
        st.session_state.page = "Home"
    
    page_idx = nav_internal.index(st.session_state.page)
    page_display = st.selectbox(
        sidebar_t['nav_label'],
        nav_display,
        index=page_idx,
        label_visibility="collapsed"
    )
    st.session_state.page = nav_internal[nav_display.index(page_display)]
    
    st.markdown("---")
    
    # Theme
    theme_display = st.selectbox(
        sidebar_t['theme'],
        [sidebar_t['theme_dark'], sidebar_t['theme_light'], sidebar_t['theme_system']],
        index=["Dark", "Light", "System"].index(st.session_state.theme) if st.session_state.theme in ["Dark", "Light", "System"] else 0
    )
    if theme_display == sidebar_t['theme_dark']:
        st.session_state.theme = "Dark"
    elif theme_display == sidebar_t['theme_light']:
        st.session_state.theme = "Light"
    else:
        st.session_state.theme = "System"
    
    # Language
    lang_display = st.selectbox(
        sidebar_t['language_label'],
        [sidebar_t['lang_english'], sidebar_t['lang_persian']],
        index=0 if st.session_state.language == "English" else 1
    )
    if lang_display == sidebar_t['lang_persian']:
        st.session_state.language = "Persian"
    else:
        st.session_state.language = "English"

# ===== LOAD TRANSLATIONS (always fresh from session state) =====
language = st.session_state.language
theme = st.session_state.theme
is_rtl = (language == "Persian")

if theme == "System":
    try:
        base_theme = st.get_option("theme.base")
        load_css(base_theme if base_theme else "dark", is_rtl)
    except:
        load_css("dark", is_rtl)
else:
    load_css(theme.lower(), is_rtl)

t = lang_manager.get_translations(language)
page = st.session_state.page

st.markdown(f"""
    <div class="main-header">
        <h1>{t['title']}</h1>
        <p style="font-size: 1.1rem; opacity: 0.9;">{t['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

if 'com_data' not in st.session_state:
    st.session_state.com_data = None
if 'preview_image' not in st.session_state:
    st.session_state.preview_image = None

# Page routing
if page == "Home":
    st.markdown(f"## {t['welcome']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        btn_text_2d = f"{t['btn_2d_title']}\n\n{t['btn_2d_desc']}\n\n{t['btn_2d_list']}"
        st.markdown(f'<div class="big-nav-btn">', unsafe_allow_html=True)
        if st.button(btn_text_2d, key="btn_2d", use_container_width=True):
            st.session_state.page = "2D Analysis"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        btn_text_3d = f"{t['btn_3d_title']}\n\n{t['btn_3d_desc']}\n\n{t['btn_3d_list']}"
        st.markdown(f'<div class="big-nav-btn">', unsafe_allow_html=True)
        if st.button(btn_text_3d, key="btn_3d", use_container_width=True):
            st.session_state.page = "3D Analysis"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        btn_text_stl = f"{t['btn_stl_title']}\n\n{t['btn_stl_desc']}\n\n{t['btn_stl_list']}"
        st.markdown(f'<div class="big-nav-btn">', unsafe_allow_html=True)
        if st.button(btn_text_stl, key="btn_stl", use_container_width=True):
            st.session_state.page = "STL Import"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"## {t['quick_start_guide']}")
    st.markdown(t['quick_start_steps'])

elif page == "2D Analysis":
    st.markdown(f"## {t['2d_analysis']}")
    
    mode = st.radio(t['input_mode'], [t['simple_shapes'], t['composite_geometry'], t['coordinate_input']], horizontal=True)
    
    analyzer = COMAnalyzer()
    plotter = Plotter2D()
    
    if mode == t['simple_shapes']:
        shape_type = st.selectbox(t['shape_type'], [t['rectangle'], t['circle'], t['triangle']])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if shape_type == t['rectangle']:
                width = st.number_input(t['width'], min_value=0.1, value=10.0, step=0.1)
                height = st.number_input(t['height'], min_value=0.1, value=5.0, step=0.1)
                shape = Rectangle(width, height)
            elif shape_type == t['circle']:
                radius = st.number_input(t['radius'], min_value=0.1, value=5.0, step=0.1)
                shape = Circle(radius)
            elif shape_type == t['triangle']:
                base = st.number_input(t['base'], min_value=0.1, value=6.0, step=0.1)
                height = st.number_input(t['height'], min_value=0.1, value=4.0, step=0.1)
                shape = Triangle(base, height)
        
        with col2:
            center_x = st.number_input(t['center_x'], value=0.0, step=0.1)
            center_y = st.number_input(t['center_y'], value=0.0, step=0.1)
            shape.set_position(center_x, center_y)
        
        st.markdown(f"### {t['live_preview']}")
        results = analyzer.analyze_2d(shape)
        img_bytes = plotter.plot_shape_with_centroid(shape, results)
        st.image(img_bytes, use_column_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t['area'], f"{results['area']:.2f} {t['mm2']}")
        with col2:
            st.metric(t['centroid_x'], f"{results['centroid_x']:.2f} {t['mm']}")
        with col3:
            st.metric(t['centroid_y'], f"{results['centroid_y']:.2f} {t['mm']}")
        
        col_save, col_reset = st.columns([1, 1])
        with col_save:
            if st.button(t['save_to_report'], type="primary"):
                st.session_state.com_data = results
                st.session_state.preview_image = img_bytes
                st.success(t['results_saved'])
        with col_reset:
            st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
            if st.button(t['reset_shape'], key="reset_2d_simple"):
                st.session_state.com_data = None
                st.session_state.preview_image = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif mode == t['composite_geometry']:
        st.markdown(f"### {t['composite_shape_builder']}")
        
        if 'components' not in st.session_state:
            st.session_state.components = []
        
        with st.expander(t['add_component'], expanded=True):
            comp_type = st.selectbox(t['shape_type'], [t['rectangle'], t['circle'], t['triangle']])
            
            operation = st.radio(
                t['operation'],
                [t['add_material'], t['cut_hole']],
                horizontal=True,
            )
            is_add = (operation == t['add_material'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if comp_type == t['rectangle']:
                    w = st.number_input(t['width'], min_value=0.1, value=5.0, key="comp_w")
                    h = st.number_input(t['height'], min_value=0.1, value=3.0, key="comp_h")
                elif comp_type == t['circle']:
                    r = st.number_input(t['radius'], min_value=0.1, value=2.0, key="comp_r")
                elif comp_type == t['triangle']:
                    b = st.number_input(t['base'], min_value=0.1, value=4.0, key="comp_b")
                    h = st.number_input(t['height'], min_value=0.1, value=3.0, key="comp_h")
            
            with col2:
                cx = st.number_input(t['center_x'], value=0.0, key="comp_cx")
                cy = st.number_input(t['center_y'], value=0.0, key="comp_cy")
            
            op_label = t['add_btn'] if is_add else t['cut_btn']
            if st.button(f"{op_label} {t['add_component']}"):
                if comp_type == t['rectangle']:
                    component = Rectangle(w, h, cx, cy)
                elif comp_type == t['circle']:
                    component = Circle(r, cx, cy)
                elif comp_type == t['triangle']:
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
            st.markdown(f"### {t['components_table']}")
            
            table_data = []
            for i, comp in enumerate(st.session_state.components):
                shape = comp['shape']
                area_val = shape.get_area()
                sign = "+" if comp['operation'] == 'add' else "-"
                table_data.append({
                    '#': i+1,
                    'Op': comp['operation'].upper(),
                    'Type': comp['type'],
                    'Area': f"{sign}{area_val:.2f}",
                    'Centroid': f"({shape.get_centroid()[0]:.1f}, {shape.get_centroid()[1]:.1f})"
                })
            
            df = pd.DataFrame(table_data)
            
            st.markdown(f"#### {t['click_to_select']}")
            selection = st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun",
                key="component_table"
            )
            
            if selection.selection.rows:
                selected_row = selection.selection.rows[0]
                if selected_row < len(st.session_state.components):
                    col_del, col_info = st.columns([1, 3])
                    with col_del:
                        if st.button(t['delete_selected'], type="secondary"):
                            st.session_state.components.pop(selected_row)
                            st.rerun()
                    with col_info:
                        comp = st.session_state.components[selected_row]
                        op_text = "ADD" if comp['operation'] == 'add' else "CUT"
                        st.info(f"{t['selected_info']}: #{selected_row+1} - {comp['type']} ({op_text})")
            
            st.markdown(f"### {t['live_preview']}")
            shapes_only = [c['shape'] for c in st.session_state.components]
            operations = [c['operation'] for c in st.session_state.components]
            
            results = analyzer.analyze_composite_2d(shapes_only, operations)
            img_bytes = plotter.plot_composite_with_centroid(shapes_only, results, operations)
            st.image(img_bytes, use_column_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t['net_area'], f"{results['total_area']:.2f} {t['mm2']}")
            with col2:
                st.metric(t['centroid_x'], f"{results['centroid_x']:.2f} {t['mm']}")
            with col3:
                st.metric(t['centroid_y'], f"{results['centroid_y']:.2f} {t['mm']}")
            
            col_save, col_reset = st.columns([1, 1])
            with col_save:
                if st.button(t['save_to_report'], type="primary", key="save_comp"):
                    st.session_state.com_data = results
                    st.session_state.preview_image = img_bytes
                    st.success(t['results_saved'])
            with col_reset:
                st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
                if st.button(t['reset_all'], key="reset_2d_comp"):
                    st.session_state.components = []
                    st.session_state.com_data = None
                    st.session_state.preview_image = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif mode == t['coordinate_input']:
        st.markdown(f"### {t['polygon_coordinate_input']}")
        coordinates_text = st.text_area(
            t['enter_coordinates'],
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
                
                st.markdown(f"### {t['live_preview']}")
                img_bytes = plotter.plot_polygon_with_centroid(coordinates, results)
                st.image(img_bytes, use_column_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(t['area'], f"{results['area']:.2f} {t['mm2']}")
                with col2:
                    st.metric(t['centroid_x'], f"{results['centroid_x']:.2f} {t['mm']}")
                with col3:
                    st.metric(t['centroid_y'], f"{results['centroid_y']:.2f} {t['mm']}")
                
                col_save, col_reset = st.columns([1, 1])
                with col_save:
                    if st.button(t['save_to_report'], type="primary", key="save_poly"):
                        st.session_state.com_data = results
                        st.session_state.preview_image = img_bytes
                        st.success(t['results_saved'])
                with col_reset:
                    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
                    if st.button(t['reset_btn'], key="reset_poly"):
                        st.session_state.com_data = None
                        st.session_state.preview_image = None
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning(t['need_3_coordinates'])
        except:
            st.error(t['invalid_coordinate'])

elif page == "3D Analysis":
    st.markdown(f"## {t['3d_analysis']}")
    
    mode = st.radio(t['input_mode'], [t['simple_shapes'], t['composite_geometry']], horizontal=True)
    
    if mode == t['simple_shapes']:
        shape_type = st.selectbox(t['shape_type'], [t['cube'], t['box'], t['sphere'], t['cylinder'], t['cone'], t['pyramid']])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if shape_type == t['cube']:
                length = st.number_input(t['length'], min_value=0.1, value=10.0)
                width = st.number_input(t['width'], min_value=0.1, value=10.0)
                height = st.number_input(t['height'], min_value=0.1, value=10.0)
                shape = Cube(length, width, height)
            elif shape_type == t['box']:
                length = st.number_input(t['length'], min_value=0.1, value=8.0)
                width = st.number_input(t['width'], min_value=0.1, value=6.0)
                height = st.number_input(t['height'], min_value=0.1, value=4.0)
                shape = Box(length, width, height)
            elif shape_type == t['sphere']:
                radius = st.number_input(t['radius'], min_value=0.1, value=5.0)
                shape = Sphere(radius)
            elif shape_type == t['cylinder']:
                radius = st.number_input(t['radius'], min_value=0.1, value=3.0)
                height = st.number_input(t['height'], min_value=0.1, value=10.0)
                shape = Cylinder(radius, height)
            elif shape_type == t['cone']:
                radius = st.number_input(t['base_radius'], min_value=0.1, value=3.0)
                height = st.number_input(t['height'], min_value=0.1, value=8.0)
                shape = Cone(radius, height)
            elif shape_type == t['pyramid']:
                base_length = st.number_input(t['base_length'], min_value=0.1, value=6.0)
                base_width = st.number_input(t['base_width'], min_value=0.1, value=6.0)
                height = st.number_input(t['height'], min_value=0.1, value=8.0)
                shape = Pyramid(base_length, base_width, height)
        
        with col2:
            pos_x = st.number_input(t['position_x'], value=0.0)
            pos_y = st.number_input(t['position_y'], value=0.0)
            pos_z = st.number_input(t['position_z'], value=0.0)
            shape.set_position(pos_x, pos_y, pos_z)
        
        st.markdown(f"### {t['live_preview']}")
        analyzer = COMAnalyzer()
        results = analyzer.analyze_3d(shape)
        plotter_3d = Plotter3D()
        fig = plotter_3d.plot_3d_shape_with_centroid(shape, results)
        st.plotly_chart(fig, use_container_width=True, key="live_3d")
        
        img_bytes = fig.to_image(format="png", width=1200, height=800)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t['volume'], f"{results['volume']:.2f} {t['mm3']}")
        with col2:
            st.metric(t['centroid_x'], f"{results['centroid_x']:.2f} {t['mm']}")
        with col3:
            st.metric(t['centroid_y'], f"{results['centroid_y']:.2f} {t['mm']}")
        with col4:
            st.metric(t['centroid_z'], f"{results['centroid_z']:.2f} {t['mm']}")
        
        col_save, col_reset = st.columns([1, 1])
        with col_save:
            if st.button(t['save_to_report'], type="primary", key="save_3d"):
                st.session_state.com_data = results
                st.session_state.preview_image = img_bytes
                st.success(t['results_saved'])
        with col_reset:
            st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
            if st.button(t['reset_shape'], key="reset_3d"):
                st.session_state.com_data = None
                st.session_state.preview_image = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        if shape_type in [t['cube'], t['box'], t['cylinder']]:
            st.markdown("---")
            st.markdown(f"### {t['stability_analysis']}")
            if results['centroid_z'] < height/2:
                stability, stability_class = t['stable'], "status-stable"
            else:
                stability, stability_class = t['potentially_unstable'], "status-unstable"
            st.markdown(f'<div class="kpi-card"><h4>{t["stability_status"]}: <span class="{stability_class}">{stability}</span></h4><p>{t["centroid_height"]}: {results["centroid_z"]:.2f} {t["mm"]}</p></div>', unsafe_allow_html=True)
    
    elif mode == t['composite_geometry']:
        st.markdown(f"### {t['composite_3d_builder']}")
        
        if 'components_3d' not in st.session_state:
            st.session_state.components_3d = []
        
        with st.expander(t['add_3d_component'], expanded=True):
            comp_type = st.selectbox(t['shape_type'], [t['cube'], t['box'], t['sphere'], t['cylinder'], t['cone'], t['pyramid']])
            
            operation = st.radio(
                t['operation'],
                [t['add_material'], t['cut_hole']],
                horizontal=True,
            )
            is_add = (operation == t['add_material'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if comp_type == t['cube']:
                    l = st.number_input(t['length'], min_value=0.1, value=5.0, key="c3d_l")
                    w = st.number_input(t['width'], min_value=0.1, value=5.0, key="c3d_w")
                    h = st.number_input(t['height'], min_value=0.1, value=5.0, key="c3d_h")
                elif comp_type == t['box']:
                    l = st.number_input(t['length'], min_value=0.1, value=6.0, key="c3d_l")
                    w = st.number_input(t['width'], min_value=0.1, value=4.0, key="c3d_w")
                    h = st.number_input(t['height'], min_value=0.1, value=3.0, key="c3d_h")
                elif comp_type == t['sphere']:
                    r = st.number_input(t['radius'], min_value=0.1, value=3.0, key="c3d_r")
                elif comp_type == t['cylinder']:
                    r = st.number_input(t['radius'], min_value=0.1, value=2.0, key="c3d_r")
                    h = st.number_input(t['height'], min_value=0.1, value=6.0, key="c3d_h")
                elif comp_type == t['cone']:
                    r = st.number_input(t['base_radius'], min_value=0.1, value=2.0, key="c3d_r")
                    h = st.number_input(t['height'], min_value=0.1, value=5.0, key="c3d_h")
                elif comp_type == t['pyramid']:
                    bl = st.number_input(t['base_length'], min_value=0.1, value=4.0, key="c3d_bl")
                    bw = st.number_input(t['base_width'], min_value=0.1, value=4.0, key="c3d_bw")
                    h = st.number_input(t['height'], min_value=0.1, value=5.0, key="c3d_h")
            
            with col2:
                px = st.number_input(t['position_x'], value=0.0, key="c3d_px")
                py = st.number_input(t['position_y'], value=0.0, key="c3d_py")
                pz = st.number_input(t['position_z'], value=0.0, key="c3d_pz")
            
            op_label = t['add_btn'] if is_add else t['cut_btn']
            if st.button(f"{op_label} {t['add_component']}"):
                if comp_type == t['cube']:
                    shape = Cube(l, w, h, px, py, pz)
                elif comp_type == t['box']:
                    shape = Box(l, w, h, px, py, pz)
                elif comp_type == t['sphere']:
                    shape = Sphere(r, px, py, pz)
                elif comp_type == t['cylinder']:
                    shape = Cylinder(r, h, px, py, pz)
                elif comp_type == t['cone']:
                    shape = Cone(r, h, px, py, pz)
                elif comp_type == t['pyramid']:
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
            st.markdown(f"### {t['components_3d_table']}")
            
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
            
            st.markdown(f"#### {t['click_to_select']}")
            selection = st.dataframe(
                df, use_container_width=True, hide_index=True,
                selection_mode="single-row", on_select="rerun",
                key="component_table_3d"
            )
            
            if selection.selection.rows:
                selected_row = selection.selection.rows[0]
                if selected_row < len(st.session_state.components_3d):
                    if st.button(t['delete_selected'], type="secondary"):
                        st.session_state.components_3d.pop(selected_row)
                        st.rerun()
            
            st.markdown(f"### {t['live_preview_3d']}")
            shapes_only = [c['shape'] for c in st.session_state.components_3d]
            operations = [c['operation'] for c in st.session_state.components_3d]
            
            results_3d = analyzer.analyze_composite_3d(shapes_only, operations)
            plotter_3d = Plotter3D()
            fig = plotter_3d.plot_composite_3d(results_3d)
            st.plotly_chart(fig, use_container_width=True, key="live_3d_composite")
            
            img_bytes = fig.to_image(format="png", width=1200, height=800)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(t['net_volume'], f"{results_3d['total_volume']:.2f} {t['mm3']}")
            with col2:
                st.metric(t['centroid_x'], f"{results_3d['centroid_x']:.2f} {t['mm']}")
            with col3:
                st.metric(t['centroid_y'], f"{results_3d['centroid_y']:.2f} {t['mm']}")
            with col4:
                st.metric(t['centroid_z'], f"{results_3d['centroid_z']:.2f} {t['mm']}")
            
            col_save, col_reset = st.columns([1, 1])
            with col_save:
                if st.button(t['save_to_report'], type="primary", key="save_3d_comp"):
                    st.session_state.com_data = results_3d
                    st.session_state.preview_image = img_bytes
                    st.success(t['results_saved'])
            with col_reset:
                st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
                if st.button(t['reset_all'], key="reset_3d_comp"):
                    st.session_state.components_3d = []
                    st.session_state.com_data = None
                    st.session_state.preview_image = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

elif page == "STL Import":
    st.markdown(f"## {t['stl_import']}")
    
    uploaded_file = st.file_uploader(t['upload_stl'], type=['stl'])
    
    if uploaded_file:
        mesh_handler = MeshHandler()
        try:
            mesh_data = mesh_handler.load_stl(uploaded_file)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t['vertices'], mesh_data['num_vertices'])
            with col2:
                st.metric(t['faces'], mesh_data['num_faces'])
            with col3:
                st.metric(t['volume'], f"{mesh_data['volume']:.2f} {t['mm3']}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(t['volume'], f"{mesh_data['volume']:.2f}")
            with col2:
                st.metric(t['centroid_x'], f"{mesh_data['centroid'][0]:.2f}")
            with col3:
                st.metric(t['centroid_y'], f"{mesh_data['centroid'][1]:.2f}")
            with col4:
                st.metric(t['centroid_z'], f"{mesh_data['centroid'][2]:.2f}")
            
            plotter = Plotter3D()
            fig = plotter.plot_mesh_with_centroid(mesh_data)
            st.plotly_chart(fig, use_container_width=True)
            
            img_bytes = fig.to_image(format="png", width=1200, height=800)
            
            col_save, col_reset = st.columns([1, 1])
            with col_save:
                if st.button(t['save_to_report'], type="primary"):
                    results = {
                        'volume': mesh_data['volume'],
                        'centroid_x': mesh_data['centroid'][0],
                        'centroid_y': mesh_data['centroid'][1],
                        'centroid_z': mesh_data['centroid'][2]
                    }
                    st.session_state.com_data = results
                    st.session_state.preview_image = img_bytes
                    st.success(t['results_saved'])
            with col_reset:
                st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
                if st.button(t['reset_btn'], key="reset_stl"):
                    st.session_state.com_data = None
                    st.session_state.preview_image = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"{t['error_stl']}: {str(e)}")

elif page == "Report Generator":
    st.markdown(f"## {t['report_generator']}")
    
    if st.session_state.com_data:
        st.success(t['analysis_available'])
        
        if st.session_state.preview_image:
            st.markdown(f"### {t['preview_image_label']}")
            st.image(st.session_state.preview_image, use_column_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input(t['project_name'], "COM Analysis Project")
            engineer_name = st.text_input(t['engineer_name'], "")
            notes = st.text_area(t['additional_notes'], "")
        with col2:
            report_format = st.selectbox(t['report_format'], ["PDF", "JSON", "CSV"])
        
        if st.button(t['generate_report'], type="primary"):
            with st.spinner(t['generating_report']):
                report_gen = ReportGenerator()
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                if report_format == "PDF":
                    pdf_bytes = report_gen.generate_pdf(
                        st.session_state.com_data, 
                        project_name, 
                        engineer_name, 
                        notes,
                        st.session_state.get('preview_image', None) 
                    )
                    st.download_button(t['download_pdf'], pdf_bytes, f"com_report_{ts}.pdf", "application/pdf")
                elif report_format == "JSON":
                    json_str = report_gen.generate_json(st.session_state.com_data)
                    st.download_button(t['download_json'], json_str, f"com_report_{ts}.json", "application/json")
                elif report_format == "CSV":
                    csv_bytes = report_gen.generate_csv(st.session_state.com_data)
                    st.download_button(t['download_csv'], csv_bytes, f"com_report_{ts}.csv", "text/csv")
    else:
        st.warning(t['no_analysis_data'])

elif page == "Settings":
    st.markdown(f"## {t['settings']}")
    st.markdown(f"### {t['unit_system']}")
    unit_system = st.selectbox(t['length_unit'], [t['mm'], t['cm'], t['m'], t['in']])
    st.markdown(f"### {t['precision']}")
    decimal_places = st.slider(t['decimal_places'], 1, 6, 2)
    st.markdown(f"### {t['visualization_settings']}")
    show_grid = st.checkbox(t['show_grid'], True)
    show_axes = st.checkbox(t['show_axes'], True)
    marker_size = st.slider(t['marker_size'], 5, 20, 10)
    if st.button(t['save_settings']):
        st.success(t['settings_saved'])

# Footer
st.markdown("---")
st.markdown(
    "<div class='footer-text'>"
    "Center of Mass & Centroid Analysis System v1.0 | "
    "© 2024 Engineering Analysis Tools"
    "</div>",
    unsafe_allow_html=True
)