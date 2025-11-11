"""
Widget AST Results Table - Tabla de Resultados MIC

Tabla interactiva de resultados AST con:
- Columnas: Antibiótico, MIC, Operador, Interpretación, Guideline, Breakpoints
- Colores por categoría: S (verde), I (amarillo), R (rojo)
- Exportación a CSV
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
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont


class ASTResultsTable(QWidget):
    """
    Tabla de resultados MIC del panel AST.

    Características:
    - 7 columnas: Antibiótico, MIC, Operador, Interpretación, Guideline, BP_S, BP_R
    - Colores por categoría S/I/R
    - Exportación a CSV
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

        # Barra de herramientas superior
        toolbar = QHBoxLayout()

        # Título
        title = QLabel("Resultados AST - Antibiograma")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        toolbar.addWidget(title)

        toolbar.addStretch()

        # Filtro por guideline
        toolbar.addWidget(QLabel("Guideline:"))
        self.guideline_combo = QComboBox()
        self.guideline_combo.addItems(["Todos", "EUCAST", "CLSI"])
        self.guideline_combo.currentTextChanged.connect(self._on_guideline_changed)
        toolbar.addWidget(self.guideline_combo)

        # Botón exportar CSV
        self.export_button = QPushButton(" Exportar CSV")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.export_button.clicked.connect(self._export_to_csv)
        self.export_button.setEnabled(False)
        toolbar.addWidget(self.export_button)

        layout.addLayout(toolbar)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Antibiótico",
                "MIC (µg/mL)",
                "Operador",
                "Interpretación",
                "Guideline",
                "BP S (≤)",
                "BP R (≥)",
            ]
        )

        # Configuración de tabla
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Antibiótico
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        # Conectar señal de selección
        self.table.cellClicked.connect(self._on_cell_clicked)

        layout.addWidget(self.table)

        # Resumen inferior
        self.summary_label = QLabel("Sin resultados cargados")
        self.summary_label.setStyleSheet(
            "color: #7f8c8d; font-style: italic; padding: 5px;"
        )
        layout.addWidget(self.summary_label)

    def load_results(self, mic_results: List[Dict]):
        """
        Carga resultados MIC en la tabla.

        Args:
            mic_results: Lista de diccionarios con resultados MIC
                Cada dict debe contener:
                - antibiotico: str
                - mic_value: float
                - mic_operador: str ('=', '<=', '>=')
                - interpretacion: str ('S', 'I', 'R')
                - guideline: str ('EUCAST', 'CLSI')
                - breakpoint_s: float
                - breakpoint_r: float
                - confianza: str (opcional)
        """
        self.current_results = mic_results
        self.current_guideline_filter = "Todos"
        self.guideline_combo.setCurrentText("Todos")

        self._populate_table()

        # Habilitar exportación
        self.export_button.setEnabled(len(mic_results) > 0)

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
        self.table.setSortingEnabled(False)  # Desactivar mientras poblamos

        # Llenar filas
        for result in filtered_results:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Columna 0: Antibiótico
            antibiotico_item = QTableWidgetItem(result.get("antibiotico", "N/A"))
            antibiotico_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.table.setItem(row, 0, antibiotico_item)

            # Columna 1: MIC
            mic_value = result.get("mic_value", 0)
            mic_item = QTableWidgetItem(f"{mic_value:.2f}" if mic_value > 0 else "N/A")
            mic_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, mic_item)

            # Columna 2: Operador
            operador = result.get("mic_operador", "=")
            operador_item = QTableWidgetItem(operador)
            operador_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, operador_item)

            # Columna 3: Interpretación (con color)
            interpretacion = result.get("interpretacion", "UNKNOWN")
            interp_item = QTableWidgetItem(interpretacion)
            interp_item.setTextAlignment(Qt.AlignCenter)
            interp_item.setFont(QFont("Arial", 11, QFont.Bold))

            # Colorear según categoría
            if interpretacion == "S":
                interp_item.setBackground(QColor("#d5f4e6"))  # Verde claro
                interp_item.setForeground(QColor("#27ae60"))  # Verde oscuro
            elif interpretacion == "I":
                interp_item.setBackground(QColor("#fff9c4"))  # Amarillo claro
                interp_item.setForeground(QColor("#f39c12"))  # Naranja
            elif interpretacion == "R":
                interp_item.setBackground(QColor("#fadbd8"))  # Rojo claro
                interp_item.setForeground(QColor("#e74c3c"))  # Rojo oscuro
            else:
                interp_item.setBackground(QColor("#ecf0f1"))  # Gris
                interp_item.setForeground(QColor("#7f8c8d"))

            self.table.setItem(row, 3, interp_item)

            # Columna 4: Guideline
            guideline = result.get("guideline", "N/A")
            version = result.get("version", "")
            guideline_text = f"{guideline}"
            if version:
                guideline_text += f"\n{version}"

            guideline_item = QTableWidgetItem(guideline_text)
            guideline_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, guideline_item)

            # Columna 5: Breakpoint S
            bp_s = result.get("breakpoint_s", 0)
            bp_s_item = QTableWidgetItem(f"≤{bp_s:.1f}" if bp_s > 0 else "N/A")
            bp_s_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, bp_s_item)

            # Columna 6: Breakpoint R
            bp_r = result.get("breakpoint_r", 0)
            bp_r_item = QTableWidgetItem(f"≥{bp_r:.1f}" if bp_r > 0 else "N/A")
            bp_r_item.setTextAlignment(Qt.AlignCenter)
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

        # Formatear resumen
        summary = (
            f"Total: {total} antibióticos | "
            f"<span style='color:#27ae60; font-weight:bold;'>S: {s_count} ({s_pct:.0f}%)</span> | "
            f"<span style='color:#f39c12; font-weight:bold;'>I: {i_count}</span> | "
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
        # Obtener antibiótico de la fila
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

        # Diálogo para guardar archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"ast_results_{timestamp}.csv"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar resultados como CSV",
            default_filename,
            "CSV Files (*.csv);;All Files (*)",
        )

        if not filename:
            return  # Usuario canceló

        try:
            # Filtrar resultados según guideline actual
            if self.current_guideline_filter == "Todos":
                results_to_export = self.current_results
            else:
                results_to_export = [
                    r
                    for r in self.current_results
                    if r.get("guideline", "").upper()
                    == self.current_guideline_filter.upper()
                ]

            # Escribir CSV
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

    def clear(self):
        """Limpia la tabla y reinicia el widget."""
        self.current_results = []
        self.table.setRowCount(0)
        self.summary_label.setText("Sin resultados cargados")
        self.export_button.setEnabled(False)
        self.guideline_combo.setCurrentText("Todos")
