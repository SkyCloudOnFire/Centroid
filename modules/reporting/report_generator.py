# modules/reporting/report_generator.py
"""Generate engineering reports with preview images"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import json
import io
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from PIL import Image as PILImage


class ReportGenerator:
    """Generate various report formats"""
    
    def generate_pdf(self, analysis_data: Dict[str, Any], 
                     project_name: str = "COM Analysis",
                     engineer_name: str = "",
                     notes: str = "",
                     preview_image = None) -> bytes:
        """Generate PDF report with optional preview image"""
        buffer = io.BytesIO()
        
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
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12
        )
        
        story = []
        
        # Title
        story.append(Paragraph(project_name, title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                              styles['Normal']))
        
        if engineer_name:
            story.append(Paragraph(f"Engineer: {engineer_name}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Preview Image (if provided)
        if preview_image is not None:
            try:
                # Convert BytesIO to bytes if needed
                if isinstance(preview_image, io.BytesIO):
                    preview_image.seek(0)
                    img_bytes = preview_image.read()
                elif isinstance(preview_image, bytes):
                    img_bytes = preview_image
                else:
                    img_bytes = None
                
                if img_bytes and len(img_bytes) > 100:
                    story.append(Paragraph("Geometry Preview", heading_style))
                    
                    # Convert bytes to PIL Image
                    pil_img = PILImage.open(io.BytesIO(img_bytes))
                    
                    # Get image dimensions
                    img_width, img_height = pil_img.size
                    
                    # Calculate scaled size (max 180mm wide, 120mm tall)
                    max_width = 180 * mm
                    max_height = 120 * mm
                    
                    aspect = img_width / img_height
                    if aspect > max_width / max_height:
                        draw_width = max_width
                        draw_height = max_width / aspect
                    else:
                        draw_height = max_height
                        draw_width = max_height * aspect
                    
                    # Save as PNG bytes
                    temp_img = io.BytesIO()
                    pil_img.save(temp_img, format='PNG')
                    temp_img.seek(0)
                    
                    # Add to report
                    img = Image(temp_img, width=draw_width, height=draw_height)
                    story.append(img)
                    story.append(Spacer(1, 15))
                    
            except Exception as e:
                story.append(Paragraph(f"(Preview image could not be rendered)", styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Analysis Results
        story.append(Paragraph("Analysis Results", heading_style))
        
        data = [['Parameter', 'Value', 'Unit']]
        
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
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
            ]))
            story.append(table)
        
        # Notes
        if notes:
            story.append(Spacer(1, 20))
            story.append(Paragraph("Additional Notes", heading_style))
            story.append(Paragraph(notes, styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            "Generated by Center of Mass & Centroid Analysis System",
            styles['Normal']
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