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


class ReportGenerator:
    """Generate various report formats"""
    
    def __init__(self):
        """Register Persian-compatible fonts"""
        try:
            # Try to register DejaVu Sans (supports Arabic/Persian)
            # Most Linux systems have this font
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/TTF/DejaVuSans.ttf',
                '/usr/share/fonts/dejavu/DejaVuSans.ttf',
                '/System/Library/Fonts/Supplemental/Arial.ttf',  # Mac fallback
            ]
            
            font_registered = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('PersianFont', font_path))
                    font_registered = True
                    break
            
            if not font_registered:
                # Fallback: use Helvetica (no Persian support but won't crash)
                self.persian_font = 'Helvetica'
            else:
                self.persian_font = 'PersianFont'
        except:
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
        
        # Detect if Persian is needed
        is_persian = any(ord(c) > 127 for c in (t('report_analysis_results', 'Analysis Results')))
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
        
        # Create styles with Persian-compatible font
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=24,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=16,
            spaceAfter=12
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=12
        )
        
        story = []
        
        # Title
        story.append(Paragraph(project_name, title_style))
        story.append(Paragraph(f"{t('report_generated_on', 'Generated')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                              normal_style))
        
        if engineer_name:
            story.append(Paragraph(f"{t('report_engineer', 'Engineer')}: {engineer_name}", normal_style))
        
        story.append(Spacer(1, 20))
        
        # Preview Image (if provided)
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
                    
                    max_width = 180 * mm
                    max_height = 120 * mm
                    
                    aspect = img_width / img_height
                    if aspect > max_width / max_height:
                        draw_width = max_width
                        draw_height = max_width / aspect
                    else:
                        draw_height = max_height
                        draw_width = max_height * aspect
                    
                    temp_img = io.BytesIO()
                    pil_img.save(temp_img, format='PNG')
                    temp_img.seek(0)
                    
                    img = Image(temp_img, width=draw_width, height=draw_height)
                    story.append(img)
                    story.append(Spacer(1, 15))
                    
            except Exception as e:
                story.append(Paragraph(f"({t('report_image_error', 'Preview image could not be rendered')})", normal_style))
                story.append(Spacer(1, 10))
        
        # Analysis Results
        story.append(Paragraph(t('report_analysis_results', 'Analysis Results'), heading_style))
        
        data = [[t('report_parameter', 'Parameter'), t('report_value', 'Value'), t('report_unit', 'Unit')]]
        
        for key, value in analysis_data.items():
            if isinstance(value, (int, float)):
                unit = 'mm'
                if 'area' in key.lower():
                    unit = 'mm²'
                elif 'volume' in key.lower():
                    unit = 'mm³'
                elif 'mass' in key.lower():
                    unit = 'kg'
                
                display_key = key.replace('_', ' ').title()
                if 'total' in key.lower():
                    display_key = display_key.replace('Total ', 'Total ')
                
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
        
        # Notes
        if notes:
            story.append(Spacer(1, 20))
            story.append(Paragraph(t('report_notes', 'Additional Notes'), heading_style))
            story.append(Paragraph(notes, normal_style))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            t('report_generated_by', 'Generated by Center of Mass & Centroid Analysis System'),
            normal_style
        ))
        
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generate_json(self, analysis_data: Dict[str, Any]) -> str:
        """Generate JSON report"""
        clean_data = {}
        for key, value in analysis_data.items():
            if isinstance(value, (int, float, str, bool, list, dict)):
                clean_data[key] = value
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_results': clean_data
        }
        return json.dumps(report, indent=2)
    
    def generate_csv(self, analysis_data: Dict[str, Any]) -> bytes:
        """Generate CSV report"""
        flat_data = {}
        for key, value in analysis_data.items():
            if not isinstance(value, (list, dict)):
                flat_data[key] = value
        
        df = pd.DataFrame([flat_data])
        return df.to_csv(index=False).encode('utf-8')