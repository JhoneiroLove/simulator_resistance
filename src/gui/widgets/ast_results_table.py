"""
Widget AST Results Table - Tabla de Resultados MIC

Tabla interactiva de resultados AST con:
- Columnas: Antibiótico, MIC, Operador, Interpretación, Guideline, Breakpoints
- Colores por categoría: S (verde), I (amarillo), R (rojo)
- Exportación a CSV y PDF
- Filtro por guideline (CLSI/EUCAST)

Autor: Sistema AST Simulator
Fecha: 11 de noviembre de 2025
"""

from typing import Optional, List, Dict
import csv
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QComboBox,
    QLabel,
    QHeaderView,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

from src.utils.ast_pdf_exporter import export_ast_to_pdf


class ASTResultsTable(QWidget):
    """
    Tabla de resultados MIC del panel AST.

    Características:
    - 7 columnas: Antibiótico, MIC, Operador, Interpretación, Guideline, BP_S, BP_R
    - Colores por categoría S/I/R
    - Exportación a CSV y PDF
    - Filtro por guideline
    - Ordenamiento por columnas

    Signals:
        antibiotic_selected: Emitido al hacer clic en fila (antibiótico, datos)
    """

    antibiotic_selected = pyqtSignal(str, dict)  # antibiótico, datos completos

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.current_results: List[Dict] = []
        self.current_guideline_filter = "Todos"

        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # Alinear todo a la izquierda
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # Establecer ancho máximo para todo el widget
        self.setMaximumWidth(600)  # Ancho máximo del contenedor
        self.setMinimumWidth(500)  # Ancho mínimo del contenedor

        # Barra de herramientas superior - ALINEADA A LA IZQUIERDA
        toolbar = QHBoxLayout()
        toolbar.setAlignment(Qt.AlignLeft)
        toolbar.setSpacing(8)

        # Título más compacto
        title = QLabel("Resultados AST")
        title.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #2c3e50;
            padding: 6px 10px;
            background-color: #ecf0f1;
            border-radius: 4px;
            min-width: 120px;
            max-width: 120px;
        """)
        title.setAlignment(Qt.AlignLeft)
        title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        toolbar.addWidget(title)

        toolbar.addStretch()

        # Filtro por guideline más compacto
        guideline_label = QLabel("Guideline:")
        guideline_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        guideline_label.setStyleSheet("font-size: 11px;")
        toolbar.addWidget(guideline_label)

        self.guideline_combo = QComboBox()
        self.guideline_combo.addItems(["Todos", "EUCAST", "CLSI"])
        self.guideline_combo.setFixedWidth(70)
        self.guideline_combo.setStyleSheet("""
            QComboBox {
                font-size: 11px; 
                padding: 2px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QComboBox:focus {
                border: 1px solid #bdc3c7; 
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        self.guideline_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.guideline_combo.currentTextChanged.connect(self._on_guideline_changed)
        toolbar.addWidget(self.guideline_combo)

        # Botones de exportación más compactos
        self.export_pdf_button = QPushButton("📄 PDF")
        self.export_pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 3px;
                min-width: 50px;
                max-width: 50px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.export_pdf_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.export_pdf_button.clicked.connect(self._export_to_pdf)
        self.export_pdf_button.setEnabled(False)
        toolbar.addWidget(self.export_pdf_button)

        self.export_csv_button = QPushButton(" CSV")
        self.export_csv_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 3px;
                min-width: 50px;
                max-width: 50px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.export_csv_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.export_csv_button.clicked.connect(self._export_to_csv)
        self.export_csv_button.setEnabled(False)
        toolbar.addWidget(self.export_csv_button)

        # Contenedor para alinear la toolbar a la izquierda
        toolbar_container = QHBoxLayout()
        toolbar_container.setAlignment(Qt.AlignLeft)
        toolbar_container.addLayout(toolbar)
        toolbar_container.addStretch()
        
        layout.addLayout(toolbar_container)

        # Tabla más compacta con ancho controlado
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Antibiótico",
                "MIC",
                "Op",
                "Int",
                "Guideline",
                "BP S",
                "BP R",
            ]
        )

        # Configuración de tabla compacta
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        
        # Política de tamaño para altura proporcional al contenido
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Scroll cuando sea necesario
        
        # Fuente más pequeña para la tabla
        font = self.table.font()
        font.setPointSize(9)
        self.table.setFont(font)
        
        # Altura de filas más pequeña
        self.table.verticalHeader().setDefaultSectionSize(28)

        # Anchos fijos para columnas - TOTAL: 120+60+40+50+70+60+60 = 460px
        self.table.setColumnWidth(0, 120)  # Antibiótico
        self.table.setColumnWidth(1, 60)   # MIC
        self.table.setColumnWidth(2, 40)   # Operador
        self.table.setColumnWidth(3, 50)   # Interpretación
        self.table.setColumnWidth(4, 70)   # Guideline
        self.table.setColumnWidth(5, 60)   # BP S
        self.table.setColumnWidth(6, 60)   # BP R

        # Ancho fijo para la tabla
        self.table.setFixedWidth(462)  # 460px + 2px de bordes
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Ocultar scroll horizontal

        # Altura mínima para cuando la tabla está vacía
        self.table.setMinimumHeight(120)

        # Conectar señal de selección
        self.table.cellClicked.connect(self._on_cell_clicked)

        # Contenedor para la tabla que la mantenga alineada a la izquierda
        table_container = QHBoxLayout()
        table_container.setAlignment(Qt.AlignLeft)
        table_container.addWidget(self.table)
        table_container.addStretch()
        
        layout.addLayout(table_container)

        # Resumen inferior más compacto
        self.summary_label = QLabel("Sin resultados cargados")
        self.summary_label.setStyleSheet("""
            color: #7f8c8d; 
            font-style: italic; 
            font-size: 11px;
            padding: 4px 8px;
            background-color: #f8f9fa;
            border-radius: 3px;
            min-width: 300px;
            max-width: 460px;
        """)
        self.summary_label.setAlignment(Qt.AlignLeft)
        self.summary_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.summary_label.setWordWrap(True)  # Permitir que el texto se ajuste
        
        # Contenedor para alinear el resumen a la izquierda
        summary_container = QHBoxLayout()
        summary_container.setAlignment(Qt.AlignLeft)
        summary_container.addWidget(self.summary_label)
        summary_container.addStretch()
        
        layout.addLayout(summary_container)

    def load_results(
        self, mic_results: List[Dict], patient_info: Optional[Dict] = None
    ):
        """
        Carga resultados MIC en la tabla.

        Args:
            mic_results: Lista de diccionarios con resultados MIC
            patient_info: Información del paciente/simulación para PDF (opcional)
        """
        self.current_results = mic_results
        self.patient_info = patient_info or {}
        self.current_guideline_filter = "Todos"
        self.guideline_combo.setCurrentText("Todos")

        self._populate_table()

        # Habilitar exportación
        has_results = len(mic_results) > 0
        self.export_csv_button.setEnabled(has_results)
        self.export_pdf_button.setEnabled(has_results)

    def _populate_table(self):
        """Puebla la tabla con los resultados actuales aplicando filtros."""
        # Filtrar por guideline si es necesario
        if self.current_guideline_filter == "Todos":
            filtered_results = self.current_results
        else:
            filtered_results = [
                r
                for r in self.current_results
                if r.get("guideline", "").upper()
                == self.current_guideline_filter.upper()
            ]

        # Limpiar tabla
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)

        # Llenar filas
        for result in filtered_results:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Columna 0: Antibiótico
            antibiotico_item = QTableWidgetItem(result.get("antibiotico", "N/A"))
            antibiotico_item.setFont(QFont("Arial", 9, QFont.Bold))
            self.table.setItem(row, 0, antibiotico_item)

            # Columna 1: MIC
            mic_value = result.get("mic_value", 0)
            mic_item = QTableWidgetItem(f"{mic_value:.2f}" if mic_value > 0 else "N/A")
            mic_item.setTextAlignment(Qt.AlignCenter)
            mic_item.setFont(QFont("Arial", 9))
            self.table.setItem(row, 1, mic_item)

            # Columna 2: Operador
            operador = result.get("mic_operador", "=")
            operador_item = QTableWidgetItem(operador)
            operador_item.setTextAlignment(Qt.AlignCenter)
            operador_item.setFont(QFont("Arial", 9))
            self.table.setItem(row, 2, operador_item)

            # Columna 3: Interpretación (con color)
            interpretacion = result.get("interpretacion", "UNKNOWN")
            interp_item = QTableWidgetItem(interpretacion)
            interp_item.setTextAlignment(Qt.AlignCenter)
            interp_item.setFont(QFont("Arial", 10, QFont.Bold))

            # Colorear según categoría
            if interpretacion == "S":
                interp_item.setBackground(QColor("#d5f4e6"))
                interp_item.setForeground(QColor("#27ae60"))
            elif interpretacion == "I":
                interp_item.setBackground(QColor("#fff9c4"))
                interp_item.setForeground(QColor("#f39c12"))
            elif interpretacion == "R":
                interp_item.setBackground(QColor("#fadbd8"))
                interp_item.setForeground(QColor("#e74c3c"))
            else:
                interp_item.setBackground(QColor("#ecf0f1"))
                interp_item.setForeground(QColor("#7f8c8d"))

            self.table.setItem(row, 3, interp_item)

            # Columna 4: Guideline (versión abreviada)
            guideline = result.get("guideline", "N/A")
            guideline_item = QTableWidgetItem(guideline)
            guideline_item.setTextAlignment(Qt.AlignCenter)
            guideline_item.setFont(QFont("Arial", 9))
            self.table.setItem(row, 4, guideline_item)

            # Columna 5: Breakpoint S
            bp_s = result.get("breakpoint_s", 0)
            bp_s_item = QTableWidgetItem(f"≤{bp_s:.1f}" if bp_s > 0 else "N/A")
            bp_s_item.setTextAlignment(Qt.AlignCenter)
            bp_s_item.setFont(QFont("Arial", 9))
            self.table.setItem(row, 5, bp_s_item)

            # Columna 6: Breakpoint R
            bp_r = result.get("breakpoint_r", 0)
            bp_r_item = QTableWidgetItem(f"≥{bp_r:.1f}" if bp_r > 0 else "N/A")
            bp_r_item.setTextAlignment(Qt.AlignCenter)
            bp_r_item.setFont(QFont("Arial", 9))
            self.table.setItem(row, 6, bp_r_item)

        # Reactivar ordenamiento
        self.table.setSortingEnabled(True)

        # Actualizar resumen
        self._update_summary(filtered_results)

    def _update_summary(self, results: List[Dict]):
        """
        Actualiza el label de resumen con estadísticas.

        Args:
            results: Lista de resultados a resumir
        """
        if not results:
            self.summary_label.setText("Sin resultados para mostrar")
            return

        # Contar por categoría
        s_count = sum(1 for r in results if r.get("interpretacion") == "S")
        i_count = sum(1 for r in results if r.get("interpretacion") == "I")
        r_count = sum(1 for r in results if r.get("interpretacion") == "R")
        total = len(results)

        # Calcular porcentajes
        s_pct = (s_count / total * 100) if total > 0 else 0
        r_pct = (r_count / total * 100) if total > 0 else 0

        # Formatear resumen más compacto
        summary = (
            f"Total: {total} | "
            f"<span style='color:#27ae60; font-weight:bold;'>S: {s_count} ({s_pct:.0f}%)</span> | "
            f"<span style='color:#f39c12;'>I: {i_count}</span> | "
            f"<span style='color:#e74c3c; font-weight:bold;'>R: {r_count} ({r_pct:.0f}%)</span>"
        )

        self.summary_label.setText(summary)

    def _on_guideline_changed(self, guideline: str):
        """
        Maneja cambio en el filtro de guideline.

        Args:
            guideline: Guideline seleccionada ('Todos', 'EUCAST', 'CLSI')
        """
        self.current_guideline_filter = guideline
        self._populate_table()

    def _on_cell_clicked(self, row: int, column: int):
        """
        Maneja clic en celda de la tabla.

        Args:
            row: Fila clickeada
            column: Columna clickeada
        """
        antibiotico_item = self.table.item(row, 0)
        if antibiotico_item is None:
            return

        antibiotico = antibiotico_item.text()

        # Buscar datos completos en resultados
        result_data = None
        for result in self.current_results:
            if result.get("antibiotico") == antibiotico:
                result_data = result
                break

        if result_data:
            self.antibiotic_selected.emit(antibiotico, result_data)

    def _export_to_csv(self):
        """Exporta la tabla actual a archivo CSV."""
        if not self.current_results:
            QMessageBox.warning(self, "Sin datos", "No hay resultados para exportar.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"ast_results_{timestamp}.csv"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar resultados como CSV",
            default_filename,
            "CSV Files (*.csv);;All Files (*)",
        )

        if not filename:
            return

        try:
            if self.current_guideline_filter == "Todos":
                results_to_export = self.current_results
            else:
                results_to_export = [
                    r
                    for r in self.current_results
                    if r.get("guideline", "").upper()
                    == self.current_guideline_filter.upper()
                ]

            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "Antibiótico",
                    "MIC (µg/mL)",
                    "Operador",
                    "Interpretación",
                    "Guideline",
                    "Versión",
                    "Breakpoint S (≤)",
                    "Breakpoint R (≥)",
                    "Confianza",
                    "Método",
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for result in results_to_export:
                    writer.writerow(
                        {
                            "Antibiótico": result.get("antibiotico", "N/A"),
                            "MIC (µg/mL)": f"{result.get('mic_value', 0):.2f}",
                            "Operador": result.get("mic_operador", "="),
                            "Interpretación": result.get("interpretacion", "UNKNOWN"),
                            "Guideline": result.get("guideline", "N/A"),
                            "Versión": result.get("version", ""),
                            "Breakpoint S (≤)": f"{result.get('breakpoint_s', 0):.1f}",
                            "Breakpoint R (≥)": f"{result.get('breakpoint_r', 0):.1f}",
                            "Confianza": result.get("confianza", "N/A"),
                            "Método": result.get("metodo", "N/A"),
                        }
                    )

            QMessageBox.information(
                self,
                "Exportación exitosa",
                f"Resultados exportados correctamente:\n{filename}\n\n"
                f"Filas exportadas: {len(results_to_export)}",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Error al exportar", f"No se pudo exportar el archivo:\n{str(e)}"
            )

    def _export_to_pdf(self):
        """Exporta la tabla actual a archivo PDF simplificado."""
        if not self.current_results:
            QMessageBox.warning(self, "Sin datos", "No hay resultados para exportar.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"antibiograma_{timestamp}.pdf"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar antibiograma como PDF",
            default_filename,
            "PDF Files (*.pdf);;All Files (*)",
        )

        if not filename:
            return

        try:
            if self.current_guideline_filter == "Todos":
                results_to_export = self.current_results
            else:
                results_to_export = [
                    r
                    for r in self.current_results
                    if r.get("guideline", "").upper()
                    == self.current_guideline_filter.upper()
                ]

            export_ast_to_pdf(
                filename=filename,
                mic_results=results_to_export,
                organism="Pseudomonas aeruginosa",
                sample_date=datetime.now().strftime("%d/%m/%Y"),
            )

            QMessageBox.information(
                self,
                "Exportación exitosa",
                f"Antibiograma generado correctamente:\n{filename}\n\n"
                f"Antibióticos: {len(results_to_export)}",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al exportar PDF",
                f"No se pudo generar el antibiograma:\n{str(e)}",
            )

    def clear(self):
        """Limpia la tabla y reinicia el widget."""
        self.current_results = []
        self.table.setRowCount(0)
        self.summary_label.setText("Sin resultados cargados")
        self.export_csv_button.setEnabled(False)
        self.export_pdf_button.setEnabled(False)
        self.guideline_combo.setCurrentText("Todos")