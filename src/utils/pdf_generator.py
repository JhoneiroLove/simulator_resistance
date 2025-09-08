import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.units import inch

def clean_html(html_text):
    """
    Limpia el texto HTML simple para que sea compatible con ReportLab.
    - Reemplaza <br> con <br/>.
    - ReportLab Paragraph maneja <b> y <i>, así que los dejamos.
    """
    # ReportLab espera <br/> en lugar de <br>
    text = html_text.replace('<br>', '<br/>')
    return text

def generate_pdf(path, summary_html, table_data, chart_image_path):
    """
    Genera un reporte en PDF con el resumen, la tabla de resultados y el gráfico.

    Args:
        path (str): Ruta donde se guardará el archivo PDF.
        summary_html (str): Texto del resumen en formato HTML simple.
        table_data (list of lists): Datos para la tabla de resultados.
        chart_image_path (str): Ruta a la imagen del gráfico.
    """
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    styles = getSampleStyleSheet()
    elements = []

    # --- Estilos personalizados ---
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=22,
        leading=28,
        spaceAfter=20,
        textColor=colors.HexColor("#000050")
    )
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['h2'],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor("#000080"),
        borderBottomWidth=1,
        borderBottomColor=colors.HexColor("#000080"),
        borderPadding=(0, 2, 0, 2)
    )
    body_style = styles['BodyText']
    body_style.leading = 14

    # --- Título y Fecha ---
    elements.append(Paragraph("Informe de Simulación de Resistencia Bacteriana", title_style))
    elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 0.25 * inch))

    # --- Resumen de la Simulación ---
    elements.append(Paragraph("Resumen Ejecutivo", header_style))
    cleaned_summary = clean_html(summary_html)
    summary_paragraph = Paragraph(cleaned_summary, body_style)
    elements.append(summary_paragraph)
    elements.append(Spacer(1, 0.25 * inch))

    # --- Gráfico de Atributos ---
    if chart_image_path:
        elements.append(Paragraph("Evolución de Atributos Biológicos", header_style))
        img = Image(chart_image_path, width=6.7 * inch, height=2.5 * inch) # Ancho aumentado y altura fija para estirar horizontalmente
        elements.append(img)
        elements.append(Spacer(1, 0.25 * inch))

    # --- Fases de Tratamiento y Recomendaciones ---
    elements.append(Paragraph("Resultados por Fase de Tratamiento", header_style))
    
    # Convertir datos de la tabla a Paragraphs para un formato consistente
    data_p = []
    for i, row in enumerate(table_data):
        if i == 0: # Encabezado
            data_p.append([Paragraph(f"<b>{cell}</b>", styles['Normal']) for cell in row])
        else: # Datos
            data_p.append([Paragraph(clean_html(cell), body_style) for cell in row])

    table = Table(data_p, hAlign='LEFT', colWidths=['25%', '20%', '55%'])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    doc.build(elements)
