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
    - Resistencia promedio
    - Resistencia máxima
    - Tabla de resultados por antibiótico
    - Recomendaciones clínicas
    """

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Etiquetas principales
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

        # Agregar widgets al layout
        for w in (
            self.lbl_promedio,
            self.lbl_maxima,
            self.table,
            self.txt_recomendacion,
        ):
            self.layout.addWidget(w)

    def update_results(
        self,
        avg_resistencia: float,
        max_resistencia: float,
        antibiotico: str,
        antibioticos_results: list,
    ):
        # Actualizar etiquetas
        self.lbl_promedio.setText(
            f"Resistencia a {antibiotico} - Promedio: {avg_resistencia:.1%}"
        )
        self.lbl_maxima.setText(
            f"Resistencia a {antibiotico} - Máxima: {max_resistencia:.1%}"
        )

        # Rellenar tabla de antibióticos
        self.table.setRowCount(len(antibioticos_results))
        for row, (name, value, interp) in enumerate(antibioticos_results):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{value:.1%}"))
            self.table.setItem(row, 2, QTableWidgetItem(interp))

        # Recomendaciones (puedes mantener las tuyas)
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