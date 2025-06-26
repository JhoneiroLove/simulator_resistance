from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,  
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QGroupBox,  
    QAbstractItemView,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np
import tempfile
import os
from src.utils.pdf_generator import generate_pdf 

class DetailedResults(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from ..main_window import get_app_icon
        self.setWindowIcon(get_app_icon())
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.setSpacing(15)

        # --- Métricas Clave (Grid Layout) ---
        metrics_group = QGroupBox("Métricas Clave de la Simulación")
        metrics_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        metrics_layout = QGridLayout(metrics_group)
        self.lbl_best_hist = QLabel("Mejor Fitness Histórico: <b>-</b>")
        self.lbl_avg_hist = QLabel("Resistencia Promedio Final: <b>-</b>")
        self.lbl_div_hist = QLabel("Diversidad Final (Shannon): <b>-</b>")
        for i, lbl in enumerate([self.lbl_best_hist, self.lbl_avg_hist, self.lbl_div_hist]):
            lbl.setFont(QFont("Segoe UI", 10))
            metrics_layout.addWidget(lbl, 0, i)

        # --- Resumen Inteligente ---
        summary_group = QGroupBox("Resumen de la Simulación")
        summary_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        summary_layout = QVBoxLayout(summary_group)
        self.summary_text = QLabel("Aún no se ha generado un resumen.")
        self.summary_text.setFont(QFont("Segoe UI", 10))
        self.summary_text.setWordWrap(True)
        self.summary_text.setAlignment(Qt.AlignTop)
        summary_layout.addWidget(self.summary_text)

        # --- Tabla de Tratamientos ---
        self.table = QTableWidget(0, 3) # Ampliado a 3 columnas
        self.table.setHorizontalHeaderLabels(["Fase de Tratamiento", "Resistencia Final", "Interpretación Clínica"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        # Usar un temporizador para debouncing del evento de redimensionamiento
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.setInterval(150)  # Retraso en ms
        self.resize_timer.timeout.connect(self._adjust_row_heights)
        header.sectionResized.connect(self.on_section_resized)

        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(100)

        # --- Gráfico de Atributos Biológicos ---
        self.attributes_chart = pg.PlotWidget()
        self.attributes_chart.setBackground('w')
        self.attributes_chart.setTitle("Evolución de Atributos Biológicos", color="k", size="12pt")
        self.attributes_chart.getAxis('left').setLabel('Valor Promedio', color='k')
        self.attributes_chart.getAxis('bottom').setLabel('Atributo', color='k')
        self.attributes_chart.showGrid(x=True, y=True, alpha=0.3)
        self.attributes_chart.setMinimumHeight(250)

        # --- Botones de Exportación ---
        self.export_pdf_btn = QPushButton("Exportar Reporte a PDF")
        self.export_pdf_btn.setFixedHeight(40)
        self.export_pdf_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)

        # Agregar widgets al layout principal
        self.layout.addWidget(metrics_group)
        self.layout.addWidget(summary_group)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.attributes_chart)
        self.layout.addWidget(self.export_pdf_btn)

        # Almacén de datos para el reporte
        self.best_hist = []
        self.avg_hist = []
        self.div_hist = []
        self.antibioticos_results = []
        self.initial_attributes = {}
        self.final_attributes = {}

    def update_results(
        self,
        antibioticos_results: list,
        best_hist: list,
        avg_hist: list,
        div_hist: list,
        initial_attributes: dict,
        final_attributes: dict,
    ):
        # Guardar datos
        self.best_hist = best_hist
        self.avg_hist = avg_hist
        self.div_hist = div_hist
        self.antibioticos_results = antibioticos_results
        self.initial_attributes = initial_attributes
        self.final_attributes = final_attributes

        # Actualizar labels
        self.lbl_best_hist.setText(f"Mejor Fitness Histórico: <b>{max(best_hist):.4f}</b>")
        self.lbl_avg_hist.setText(f"Resistencia Promedio Final: <b>{avg_hist[-1]:.4f}</b>")
        self.lbl_div_hist.setText(f"Diversidad Final (Shannon): <b>{div_hist[-1]:.4f}</b>")

        # Llenar tabla de tratamientos
        self.table.setRowCount(len(antibioticos_results))
        for row, (name, value, interp) in enumerate(antibioticos_results):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{value:.4f}"))

            # Usar un QLabel con word-wrap para la interpretación
            # Reemplazar '\n' literal por saltos de línea HTML
            interp_text = interp.replace('\\n', '<br>')
            interp_label = QLabel(interp_text)
            interp_label.setWordWrap(True)
            interp_label.setAlignment(Qt.AlignTop)
            self.table.setCellWidget(row, 2, interp_label)
        # Ajustar las filas después de que el ciclo de eventos se procese
        QTimer.singleShot(0, self._adjust_row_heights)

        # Generar contenido dinámico
        self._generate_summary()
        self._update_attributes_chart()

    def _generate_summary(self):
        res_final = self.avg_hist[-1]
        div_final = self.div_hist[-1]

        summary = f"La simulación concluyó con una <b>resistencia promedio de {res_final:.4f}</b>. "
        if res_final > 0.8:
            summary += "Este es un <b>nivel CRÍTICO</b>, indicando que la población es mayormente inmune a los tratamientos aplicados."
        elif res_final > 0.5:
            summary += "Este es un <b>nivel considerable</b> de resistencia, sugiriendo una adaptación significativa de la población."
        else:
            summary += "La población mantiene un <b>nivel bajo</b> de resistencia."
        
        summary += f"<br><br>La <b>diversidad final (Shannon) de {div_final:.4f}</b> indica "
        if div_final > 3.0:
            summary += "un <b>alto potencial evolutivo</b>. La colonia es heterogénea y podría adaptarse rápidamente a futuros antibióticos."
        elif div_final > 1.5:
            summary += "una <b>diversidad moderada</b>, manteniendo capacidad de adaptación."
        else:
            summary += "una <b>baja diversidad</b>, lo que la hace más homogénea y potencialmente vulnerable a nuevos tipos de estrés."
        
        self.summary_text.setText(summary)

    def _update_attributes_chart(self):
        self.attributes_chart.clear()
        if not self.initial_attributes or not self.final_attributes:
            return

        attributes = list(self.initial_attributes.keys())
        x_labels = [(i, name.capitalize()) for i, name in enumerate(attributes)]
        
        initial_values = list(self.initial_attributes.values())
        final_values = list(self.final_attributes.values())

        bar_width = 0.4
        x = np.arange(len(attributes))

        bar_initial = pg.BarGraphItem(x=x - bar_width/2, height=initial_values, width=bar_width, brush=(100, 100, 255, 150), name='Inicial')
        bar_final = pg.BarGraphItem(x=x + bar_width/2, height=final_values, width=bar_width, brush=(255, 100, 100, 150), name='Final')
        
        self.attributes_chart.addItem(bar_initial)
        self.attributes_chart.addItem(bar_final)
        
        ax = self.attributes_chart.getAxis('bottom')
        ax.setTicks([x_labels])
        self.attributes_chart.addLegend(offset=(-1,1))

    def _adjust_row_heights(self):
        """Ajusta manualmente la altura de cada fila para que se ajuste al contenido."""
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 2)
            if widget:
                height = widget.heightForWidth(self.table.columnWidth(2))
                self.table.setRowHeight(row, height)

    def on_section_resized(self, logicalIndex, oldSize, newSize):
        """Inicia el temporizador para ajustar las filas después de un redimensionamiento de sección."""
        # Solo nos interesa el cambio en la columna de interpretación para evitar ciclos.
        if logicalIndex == 2:
            self.resize_timer.start()

    def export_to_pdf(self):
        """
        Recolecta los datos, guarda el gráfico como imagen temporal y llama
        al generador de PDF para crear el reporte.
        """
        if not hasattr(self, 'antibioticos_results') or not self.antibioticos_results:
            QMessageBox.warning(self, "Sin Datos", "No hay datos de simulación para exportar.")
            return

        # 1. Abrir diálogo para guardar archivo
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte PDF", "Reporte_Simulacion.pdf", "Archivos PDF (*.pdf)"
        )
        if not path:
            return

        chart_image_path = None
        try:
            # 2. Recolectar datos
            summary = self.summary_text.text()
            
            table_data = [["Fase de Tratamiento", "Resistencia Final", "Interpretación Clínica"]]
            for i in range(self.table.rowCount()):
                fase = self.table.item(i, 0).text()
                resistencia = self.table.item(i, 1).text()
                interpretacion_widget = self.table.cellWidget(i, 2)
                interpretacion = interpretacion_widget.text() if interpretacion_widget else ""
                table_data.append([fase, resistencia, interpretacion])

            # 3. Guardar el gráfico como una imagen temporal
            exporter = pg.exporters.ImageExporter(self.attributes_chart.getPlotItem())
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                chart_image_path = tmp_file.name
            exporter.export(chart_image_path)
            
            # 4. Llamar al generador de PDF
            generate_pdf(path, summary, table_data, chart_image_path)

            QMessageBox.information(self, "Exportación Exitosa", f"El reporte ha sido guardado exitosamente en:\n{path}")

        except Exception as e:
            QMessageBox.critical(self, "Error de Exportación", f"Ocurrió un error al generar el PDF: {e}")
        
        finally:
            # 5. Limpieza del archivo temporal
            if chart_image_path and os.path.exists(chart_image_path):
                os.remove(chart_image_path)