from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt5.QtGui import QFont

class DetailedResults(QWidget):
    """
    Widget para mostrar los resultados detallados de la simulación:
    - Resistencia promedio de la población
    - Resistencia máxima (clón más resistente)
    - Tabla de resultados por antibiótico
    - Recomendaciones clínicas según el antibiótico
    """

    def __init__(self):
        super().__init__()

        # Layout principal
        self.layout = QVBoxLayout(self)

        # Etiquetas para resistencias
        self.lbl_promedio = QLabel("Resistencia Promedio: ")
        self.lbl_promedio.setFont(QFont("Arial", 14, QFont.Bold))

        self.lbl_maxima = QLabel("Resistencia Máxima: ")
        self.lbl_maxima.setFont(QFont("Arial", 14, QFont.Bold))

        # Tabla de resultados por antibiótico
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["Antibiótico", "% Resistencia", "Interpretación"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Área de recomendaciones
        self.txt_recomendacion = QTextEdit()
        self.txt_recomendacion.setReadOnly(True)
        self.txt_recomendacion.setStyleSheet("""
            QTextEdit {
                background-color: #F0F0F0;
                border: 2px solid #CCCCCC;
                padding: 10px;
            }
        """)

        # Añadir widgets al layout
        self.layout.addWidget(self.lbl_promedio)
        self.layout.addWidget(self.lbl_maxima)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.txt_recomendacion)

    def update_results(
        self, avg_resistencia, max_resistencia, antibiotico, antibioticos_results
    ):
        """
        Actualiza los valores mostrados:
        :param avg_resistencia: float (0.0–1.0) resistencia promedio
        :param max_resistencia: float (0.0–1.0) resistencia máxima
        :param antibiotico: str, antibiótico principal evaluado
        :param antibioticos_results: list de tuplas (nombre, valor_float, interpretacion_str)
        """
        # Formatear y mostrar porcentajes principales
        self.lbl_promedio.setText(f"Resistencia Promedio: {avg_resistencia:.1%}")
        self.lbl_maxima.setText(f"Resistencia Máxima: {max_resistencia:.1%}")

        # Rellenar tabla de antibióticos
        self.table.setRowCount(len(antibioticos_results))
        for row, (name, value, interp) in enumerate(antibioticos_results):
            item_name = QTableWidgetItem(name)
            item_val = QTableWidgetItem(f"{value:.1%}")
            item_interp = QTableWidgetItem(interp)
            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_val)
            self.table.setItem(row, 2, item_interp)

        # Recomendaciones clínicas para el antibiótico principal
        recomendaciones = {
            "Meropenem": (
                "Recomendación Clínica:\n"
                "• Considerar alternativas no carbapenémicas:\n"
                "  - Ceftazidima/Avibactam\n"
                "  - Colistina + Fosfomicina"
            ),
            "Ciprofloxacino": (
                "Recomendación Clínica:\n"
                "• Evaluar sensibilidad a fluoroquinolonas.\n"
                "• Considerar Levofloxacino + Aminoglucósido."
            ),
        }

        self.txt_recomendacion.setText(
            recomendaciones.get(
                antibiotico,
                "Consulte con infectología para recomendaciones personalizadas.",
            )
        )