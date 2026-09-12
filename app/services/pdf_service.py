from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from typing import List, Dict, Any
import io


def generate_all_students_pdf(students: List[Dict[str, Any]]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a5f')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4a5568')
    )
    
    elements = []
    
    elements.append(Paragraph("College Student Records", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    elements.append(Paragraph(f"Total Records: {len(students)}", subtitle_style))
    elements.append(Spacer(1, 12))
    
    table_data = [
        ["Sl No", "Name", "Course", "College", "Admission Through", "Submitted Date"]
    ]
    
    for idx, student in enumerate(students, 1):
        created_at = student.get("created_at")
        if isinstance(created_at, datetime):
            date_str = created_at.strftime("%Y-%m-%d %H:%M")
        else:
            date_str = str(created_at) if created_at else ""
        
        table_data.append([
            str(idx),
            student.get("name", ""),
            student.get("course", ""),
            student.get("college", ""),
            student.get("admission_through", ""),
            date_str
        ])
    
    col_widths = [0.5*inch, 1.5*inch, 1.5*inch, 2.5*inch, 1.2*inch, 1.3*inch]
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


def generate_student_pdf(student: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1*inch,
        leftMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a5f')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4a5568')
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#2d3748'),
        fontName='Helvetica-Bold'
    )
    
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#4a5568')
    )
    
    elements = []
    
    elements.append(Paragraph("College Student Record", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    elements.append(Spacer(1, 20))
    
    student_id = student.get("id", student.get("_id", ""))
    
    fields = [
        ("Student ID", str(student_id)),
        ("Name", student.get("name", "")),
        ("Course", student.get("course", "")),
        ("College", student.get("college", "")),
        ("Admission Through", student.get("admission_through", "")),
    ]
    
    created_at = student.get("created_at")
    if isinstance(created_at, datetime):
        fields.append(("Submitted Date", created_at.strftime("%Y-%m-%d %H:%M:%S")))
    else:
        fields.append(("Submitted Date", str(created_at) if created_at else ""))
    
    updated_at = student.get("updated_at")
    if isinstance(updated_at, datetime):
        fields.append(("Last Updated", updated_at.strftime("%Y-%m-%d %H:%M:%S")))
    else:
        fields.append(("Last Updated", str(updated_at) if updated_at else ""))
    
    table_data = []
    for label, value in fields:
        table_data.append([
            Paragraph(label, label_style),
            Paragraph(value, value_style)
        ])
    
    table = Table(table_data, colWidths=[2.2*inch, 4*inch])
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#edf2f7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()