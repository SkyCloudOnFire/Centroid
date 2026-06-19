# modules/reporting/report_generator.py
"""Generate engineering reports"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing
import json
import io
import pandas as pd
from datetime import datetime
from typing import Dict, Any


class ReportGenerator:
    """Generate various report formats"""
    
    def generate_pdf(self, analysis_data: Dict[str, Any], 
                     project_name: str = "COM Analysis",
                     engineer_name: str = "",
                     notes: str = "") -> bytes:
        """Generate PDF report"""
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Styles
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
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph(project_name, title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                              styles['Normal']))
        
        if engineer_name:
            story.append(Paragraph(f"Engineer: {engineer_name}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Analysis Results
        story.append(Paragraph("Analysis Results", heading_style))
        
        # Create results table
        data = [['Parameter', 'Value', 'Unit']]
        
        for key, value in analysis_data.items():
            if isinstance(value, (int, float)):
                if 'centroid' in key or 'area' in key or 'volume' in key or 'mass' in key:
                    unit = 'mm'
                    if 'area' in key:
                        unit = 'mm²'
                    elif 'volume' in key:
                        unit = 'mm³'
                    elif 'mass' in key:
                        unit = 'kg'
                    
                    data.append([key.replace('_', ' ').title(), f"{value:.3f}", unit])
        
        if len(data) > 1:
            table = Table(data, colWidths=[80*mm, 60*mm, 40*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        # Notes
        if notes:
            story.append(Spacer(1, 20))
            story.append(Paragraph("Additional Notes", heading_style))
            story.append(Paragraph(notes, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generate_json(self, analysis_data: Dict[str, Any]) -> str:
        """Generate JSON report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_results': analysis_data
        }
        return json.dumps(report, indent=2)
    
    def generate_csv(self, analysis_data: Dict[str, Any]) -> bytes:
        """Generate CSV report"""
        # Flatten nested data
        flat_data = {}
        for key, value in analysis_data.items():
            if not isinstance(value, (list, dict)):
                flat_data[key] = value
        
        df = pd.DataFrame([flat_data])
        return df.to_csv(index=False).encode('utf-8')