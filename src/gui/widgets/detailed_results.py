from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from datetime import datetime
import csv


class DetailedResults(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Labels de historial
        self.lbl_best_hist = QLabel("Mejor Fitness Histórico: -")
        self.lbl_avg_hist = QLabel("Resistencia Promedio Final (última gen): -")
        self.lbl_div_hist = QLabel("Diversidad Final (Shannon): -")
        for lbl in (self.lbl_best_hist, self.lbl_avg_hist, self.lbl_div_hist):
            lbl.setFont(QFont("Arial", 11))

        # Tabla de resultados por antibiótico
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["Antibiótico", "% Resistencia", "Interpretación"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Área de recomendaciones clínicas (texto libre)
        self.txt_recomendacion = QTextEdit()
        self.txt_recomendacion.setReadOnly(True)
        self.txt_recomendacion.setStyleSheet("""
            QTextEdit {
                background-color: #F0F0F0;
                border: 2px solid #CCCCCC;
                padding: 10px;
            }
        """)

        # Botones de exportación
        self.export_csv_btn = QPushButton("Exportar CSV de Resultados")
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.export_pdf_btn = QPushButton("Exportar PDF de Resultados")
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)

        # Agregar widgets
        for w in (
            self.lbl_best_hist,
            self.lbl_avg_hist,
            self.lbl_div_hist,
            self.table,
            self.txt_recomendacion,
            self.export_csv_btn,
            self.export_pdf_btn,
        ):
            self.layout.addWidget(w)

        # Almacén de historial para exportar
        self.best_hist = []
        self.avg_hist = []
        self.div_hist = []

    def update_results(
        self,
        avg_resistencia: float,
        max_resistencia: float,
        antibiotico: str,
        antibioticos_results: list,
        best_hist: list,
        avg_hist: list,
        div_hist: list,
    ):
        # Guardar historial
        self.best_hist = best_hist
        self.avg_hist = avg_hist
        self.div_hist = div_hist

        # Actualizar labels
        self.lbl_best_hist.setText(f"Mejor Fitness Histórico: {max(best_hist):.4f}")
        self.lbl_avg_hist.setText(
            f"Resistencia Promedio Última Generación: {avg_hist[-1]:.4f}"
        )
        self.lbl_div_hist.setText(f"Diversidad Final (Shannon): {div_hist[-1]:.4f}")

        # Llenar tabla por antibiótico
        self.table.setRowCount(len(antibioticos_results))
        for row, (name, value, interp) in enumerate(antibioticos_results):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{value:.1%}"))
            self.table.setItem(row, 2, QTableWidgetItem(interp))

        # Recomendaciones clínicas
        all_texts = "\n\n".join(
            f"• {name}: {interp}" for name, _, interp in antibioticos_results
        )
        self.txt_recomendacion.setText(all_texts)

    def export_to_csv(self):
        if not self.best_hist:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "", "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Generación", "Best_Fitness", "Avg_Resistencia", "Diversidad_Shannon"]
            )
            for i, (b, a, d) in enumerate(
                zip(self.best_hist, self.avg_hist, self.div_hist), start=1
            ):
                writer.writerow([i, f"{b:.4f}", f"{a:.4f}", f"{d:.4f}"])

    def export_to_pdf(self):
        if not self.best_hist:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "", "PDF (*.pdf)")
        if not path:
            return

        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Portada
        title_style = styles["Title"]
        elements.append(Paragraph("Informe de Simulación Evolutiva", title_style))
        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(
                f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 24))

        # Métricas clave
        hdr_style = ParagraphStyle(
            "hdr", parent=styles["Heading2"], spaceAfter=6, textColor=colors.darkblue
        )
        elements.append(Paragraph("Métricas Clave", hdr_style))
        metrics_data = [
            ["Mejor Fitness Histórico", f"{max(self.best_hist):.4f}"],
            ["Resistencia Promedio Final", f"{self.avg_hist[-1]:.4f}"],
            ["Diversidad Final (Shannon)", f"{self.div_hist[-1]:.4f}"],
        ]
        tbl = Table(metrics_data, hAlign="LEFT", colWidths=[200, 100])
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ]
            )
        )
        elements.append(tbl)
        elements.append(Spacer(1, 24))

        # Historial completo
        elements.append(Paragraph("Historial por Generación", hdr_style))
        hist_data = [["Gen", "Best_Fit", "Avg_Res", "Div_Shannon"]]
        for i, (b, a, d) in enumerate(
            zip(self.best_hist, self.avg_hist, self.div_hist), start=1
        ):
            hist_data.append([str(i), f"{b:.4f}", f"{a:.4f}", f"{d:.4f}"])
        hist_tbl = Table(hist_data, hAlign="LEFT")
        hist_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        elements.append(hist_tbl)
        elements.append(Spacer(1, 24))

        # Recomendaciones clínicas
        elements.append(Paragraph("Recomendaciones Clínicas", hdr_style))
        text = self.txt_recomendacion.toPlainText().replace("\n", "<br/>")
        elements.append(Paragraph(text, styles["BodyText"]))

        # Generar PDF
        doc.build(elements)
        QMessageBox.information(
            self, "Exportación PDF", f"Informe guardado en:\n{path}"
        )