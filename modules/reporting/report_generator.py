# modules/reporting/report_generator.py
"""Generate engineering reports with preview images"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import io
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from PIL import Image as PILImage
import os
import urllib.request
import tempfile


class ReportGenerator:
    """Generate various report formats"""
    
    FONT_URL = "https://github.com/google/fonts/raw/main/ofl/vazirmatn/Vazirmatn-Regular.ttf"
    FONT_PATH = os.path.join(tempfile.gettempdir(), "Vazirmatn-Regular.ttf")
    
    def __init__(self):
        """Download and register Persian font if needed"""
        self.persian_font = 'Helvetica'
        self._ensure_font()
    
    def _ensure_font(self):
        """Download Vazirmatn font (Persian/Arabic) if not present"""
        try:
            if not os.path.exists(self.FONT_PATH):
                urllib.request.urlretrieve(self.FONT_URL, self.FONT_PATH)
            
            if os.path.exists(self.FONT_PATH):
                pdfmetrics.registerFont(TTFont('PersianFont', self.FONT_PATH))
                self.persian_font = 'PersianFont'
        except Exception:
            self.persian_font = 'Helvetica'
    
    def generate_pdf(self, analysis_data: Dict[str, Any], 
                     project_name: str = "COM Analysis",
                     engineer_name: str = "",
                     notes: str = "",
                     preview_image = None,
                     translations: dict = None) -> bytes:
        """Generate PDF report with optional preview image and language support"""
        buffer = io.BytesIO()
        
        if translations is None:
            translations = {}
        
        t = lambda key, default: translations.get(key, default)
        
        test_text = t('report_analysis_results', 'Analysis Results')
        is_persian = any(ord(c) > 127 for c in test_text)
        font_name = self.persian_font if is_persian else 'Helvetica'
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'],
            fontName=font_name, fontSize=24, spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading', parent=styles['Heading2'],
            fontName=font_name, fontSize=16, spaceAfter=12
        )
        normal_style = ParagraphStyle(
            'CustomNormal', parent=styles['Normal'],
            fontName=font_name, fontSize=12
        )
        
        story = []
        
        story.append(Paragraph(project_name, title_style))
        story.append(Paragraph(
            f"{t('report_generated_on', 'Generated')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
            normal_style
        ))
        
        if engineer_name:
            story.append(Paragraph(f"{t('report_engineer', 'Engineer')}: {engineer_name}", normal_style))
        
        story.append(Spacer(1, 20))
        
        # Preview Image
        if preview_image is not None:
            try:
                if isinstance(preview_image, io.BytesIO):
                    preview_image.seek(0)
                    img_bytes = preview_image.read()
                elif isinstance(preview_image, bytes):
                    img_bytes = preview_image
                else:
                    img_bytes = None
                
                if img_bytes and len(img_bytes) > 100:
                    story.append(Paragraph(t('report_title', 'Geometry Preview'), heading_style))
                    pil_img = PILImage.open(io.BytesIO(img_bytes))
                    img_width, img_height = pil_img.size
                    max_width, max_height = 180 * mm, 120 * mm
                    aspect = img_width / img_height
                    draw_width = max_width if aspect > max_width/max_height else max_height * aspect
                    draw_height = max_width/aspect if aspect > max_width/max_height else max_height
                    temp_img = io.BytesIO()
                    pil_img.save(temp_img, format='PNG')
                    temp_img.seek(0)
                    story.append(Image(temp_img, width=draw_width, height=draw_height))
                    story.append(Spacer(1, 15))
            except Exception:
                pass
        
        # Analysis Results
        story.append(Paragraph(t('report_analysis_results', 'Analysis Results'), heading_style))
        
        data = [[t('report_parameter', 'Parameter'), t('report_value', 'Value'), t('report_unit', 'Unit')]]
        
        for key, value in analysis_data.items():
            if isinstance(value, (int, float)):
                unit = 'mm'
                if 'area' in key.lower(): unit = 'mm²'
                elif 'volume' in key.lower(): unit = 'mm³'
                elif 'mass' in key.lower(): unit = 'kg'
                display_key = key.replace('_', ' ').title()
                data.append([display_key, f"{value:.3f}", unit])
        
        if len(data) > 1:
            table = Table(data, colWidths=[80*mm, 60*mm, 40*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
            ]))
            story.append(table)
        
        if notes:
            story.append(Spacer(1, 20))
            story.append(Paragraph(t('report_notes', 'Additional Notes'), heading_style))
            story.append(Paragraph(notes, normal_style))
        
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            t('report_generated_by', 'Generated by Center of Mass & Centroid Analysis System'),
            normal_style
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def generate_json(self, analysis_data: Dict[str, Any]) -> str:
        clean_data = {k: v for k, v in analysis_data.items() if isinstance(v, (int, float, str, bool, list, dict))}
        return json.dumps({'timestamp': datetime.now().isoformat(), 'analysis_results': clean_data}, indent=2)
    
    def generate_csv(self, analysis_data: Dict[str, Any]) -> bytes:
        flat_data = {k: v for k, v in analysis_data.items() if not isinstance(v, (list, dict))}
        return pd.DataFrame([flat_data]).to_csv(index=False).encode('utf-8')