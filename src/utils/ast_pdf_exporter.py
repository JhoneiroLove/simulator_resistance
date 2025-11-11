"""
Exportador de resultados AST a PDF - Formato clínico profesional

Módulo dedicado para generación de informes PDF de antibiogramas.
Separado del widget para mantener responsabilidad única.

Autor: Sistema AST Simulator
Fecha: 11 de noviembre de 2025
"""

from typing import List, Dict, Optional
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table as RLTable,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def export_ast_to_pdf(
    filename: str,
    mic_results: List[Dict],
    organism: str = "Pseudomonas aeruginosa",
    sample_date: Optional[str] = None,
) -> None:
    """
    Exporta resultados AST a PDF con formato clínico profesional.

    Args:
        filename: Ruta del archivo PDF a generar
        mic_results: Lista de resultados MIC
            Cada dict debe contener:
            - antibiotico: str
            - mic_value: float
            - mic_operador: str ('=', '<=', '>=')
            - interpretacion: str ('S', 'I', 'R')
            - guideline: str ('EUCAST', 'CLSI')
            - version: str (opcional)
        organism: Nombre del organismo aislado
        sample_date: Fecha de muestra (opcional, usa fecha actual si no se provee)

    Raises:
        ValueError: Si mic_results está vacío
        Exception: Si falla la generación del PDF
    """
    if not mic_results:
        raise ValueError("No hay resultados para exportar")

    # Fecha por defecto
    if sample_date is None:
        sample_date = datetime.now().strftime("%d/%m/%Y")

    # Crear documento
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    elements = []
    styles = getSampleStyleSheet()

    # === ESTILOS ===
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=rl_colors.HexColor("#2c3e50"),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName="Helvetica-Bold",
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=rl_colors.HexColor("#34495e"),
        alignment=TA_CENTER,
        spaceAfter=30,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=rl_colors.HexColor("#2c3e50"),
        spaceAfter=12,
        spaceBefore=20,
        fontName="Helvetica-Bold",
    )

    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=rl_colors.HexColor("#7f8c8d"),
        alignment=TA_LEFT,
    )

    # === ENCABEZADO ===
    elements.append(Paragraph("Informe de Antibiograma", title_style))
    elements.append(
        Paragraph(
            f"Simulador AST - {datetime.now().strftime('%d de %B de %Y')}",
            subtitle_style,
        )
    )

    # === INFORMACIÓN GENERAL ===
    elements.append(Paragraph("Información de la Muestra", section_style))

    info_data = [
        ["Organismo:", organism],
        ["Fecha de análisis:", sample_date],
        ["Método:", "Microdilución en caldo (simulado)"],
        ["Total de antibióticos:", str(len(mic_results))],
    ]

    info_table = RLTable(info_data, colWidths=[2.0 * inch, 4.0 * inch])
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(info_table)
    elements.append(Spacer(1, 0.3 * inch))

    # === RESUMEN EJECUTIVO ===
    s_count = sum(1 for r in mic_results if r.get("interpretacion") == "S")
    i_count = sum(1 for r in mic_results if r.get("interpretacion") == "I")
    r_count = sum(1 for r in mic_results if r.get("interpretacion") == "R")
    total = len(mic_results)

    elements.append(Paragraph("Resumen de Sensibilidad", section_style))

    summary_data = [
        ["Categoría", "Cantidad", "Porcentaje"],
        ["Sensible (S)", str(s_count), f"{(s_count / total * 100):.1f}%"],
        ["Intermedio (I)", str(i_count), f"{(i_count / total * 100):.1f}%"],
        ["Resistente (R)", str(r_count), f"{(r_count / total * 100):.1f}%"],
    ]

    summary_table = RLTable(
        summary_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch]
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#34495e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 1, rl_colors.HexColor("#bdc3c7")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                # Colorear filas según categoría
                ("BACKGROUND", (0, 1), (-1, 1), rl_colors.HexColor("#d5f4e6")),
                ("BACKGROUND", (0, 2), (-1, 2), rl_colors.HexColor("#fff9c4")),
                ("BACKGROUND", (0, 3), (-1, 3), rl_colors.HexColor("#fadbd8")),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 0.4 * inch))

    # === TABLA DE RESULTADOS DETALLADOS ===
    elements.append(Paragraph("Resultados Detallados", section_style))

    # Header
    table_data = [["Antibiótico", "MIC (µg/mL)", "Interpretación", "Guideline"]]

    # Datos
    for result in mic_results:
        antibiotico = result.get("antibiotico", "N/A")
        mic_value = result.get("mic_value", 0)
        mic_op = result.get("mic_operador", "=")
        interpretacion = result.get("interpretacion", "UNKNOWN")
        guideline = result.get("guideline", "N/A")
        version = result.get("version", "")

        # Formatear MIC
        if mic_op == ">=":
            mic_str = f"≥{mic_value:.1f}"
        elif mic_op == "<=":
            mic_str = f"≤{mic_value:.1f}"
        else:
            mic_str = f"{mic_value:.2f}"

        # Guideline con versión
        guideline_str = f"{guideline} {version}" if version else guideline

        table_data.append([antibiotico, mic_str, interpretacion, guideline_str])

    # Crear tabla
    results_table = RLTable(
        table_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1.0 * inch]
    )

    # Estilos base
    table_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#34495e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#bdc3c7")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [rl_colors.white, rl_colors.HexColor("#ecf0f1")],
        ),
    ]

    # Colorear columna de interpretación
    for i, result in enumerate(mic_results, start=1):
        interpretacion = result.get("interpretacion", "UNKNOWN")
        if interpretacion == "S":
            table_styles.append(
                ("BACKGROUND", (2, i), (2, i), rl_colors.HexColor("#27ae60"))
            )
            table_styles.append(("TEXTCOLOR", (2, i), (2, i), rl_colors.white))
            table_styles.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))
        elif interpretacion == "I":
            table_styles.append(
                ("BACKGROUND", (2, i), (2, i), rl_colors.HexColor("#f39c12"))
            )
            table_styles.append(("TEXTCOLOR", (2, i), (2, i), rl_colors.white))
            table_styles.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))
        elif interpretacion == "R":
            table_styles.append(
                ("BACKGROUND", (2, i), (2, i), rl_colors.HexColor("#e74c3c"))
            )
            table_styles.append(("TEXTCOLOR", (2, i), (2, i), rl_colors.white))
            table_styles.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))

    results_table.setStyle(TableStyle(table_styles))
    elements.append(results_table)

    # === PIE DE PÁGINA ===
    elements.append(Spacer(1, 0.5 * inch))

    leyenda = """
    <b>Interpretación:</b><br/>
    <b>S</b> = Sensible | <b>I</b> = Intermedio | <b>R</b> = Resistente<br/>
    <b>MIC</b> = Concentración Mínima Inhibitoria (µg/mL)<br/>
    <br/>
    <i>Este informe fue generado automáticamente por el Sistema Simulador AST.</i><br/>
    <i>Fecha de generación: {}</i>
    """.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    elements.append(Paragraph(leyenda, footer_style))

    # Construir PDF
    doc.build(elements)


def get_pdf_filename_with_timestamp(base_name: str = "antibiograma") -> str:
    """
    Genera nombre de archivo PDF con timestamp.

    Args:
        base_name: Nombre base del archivo

    Returns:
        Nombre de archivo con formato: base_name_YYYYMMDD_HHMMSS.pdf
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.pdf"
