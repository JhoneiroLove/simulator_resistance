# src/gui/widgets/detailed_results.py
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
    - CIM, CPM
    - EPCIM, PCCPM, ECMDR
    - Identificación MDR/XDR
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

        self.lbl_cim = QLabel("CIM: ")
        self.lbl_cim.setFont(QFont("Arial", 14, QFont.Bold))

        self.lbl_cpm = QLabel("CPM: ")
        self.lbl_cpm.setFont(QFont("Arial", 14, QFont.Bold))

        self.lbl_epcim = QLabel("EPCIM: ")
        self.lbl_epcim.setFont(QFont("Arial", 14, QFont.Bold))

        self.lbl_pccpm = QLabel("PCCPM: ")
        self.lbl_pccpm.setFont(QFont("Arial", 14, QFont.Bold))

        self.lbl_ecmdr = QLabel("ECMDR: ")
        self.lbl_ecmdr.setFont(QFont("Arial", 14, QFont.Bold))

        self.lbl_mdr_xdr = QLabel("MDR/XDR: ")
        self.lbl_mdr_xdr.setFont(QFont("Arial", 14, QFont.Bold))

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
            self.lbl_cim,
            self.lbl_cpm,
            self.lbl_epcim,
            self.lbl_pccpm,
            self.lbl_ecmdr,
            self.lbl_mdr_xdr,
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
        cim: float,
        cpm: float,
        epcim_val: float,
        pccpm_val: float,
        ecmdr_val: float,
        es_MDR: bool,
        es_XDR: bool,
    ):
        # Actualizar etiquetas
        self.lbl_promedio.setText(
            f"Resistencia a {antibiotico} - Promedio: {avg_resistencia:.1%}"
        )
        self.lbl_maxima.setText(
            f"Resistencia a {antibiotico} - Máxima: {max_resistencia:.1%}"
        )
        self.lbl_cim.setText(f"CIM: {cim}")
        self.lbl_cpm.setText(f"CPM: {cpm}")
        self.lbl_epcim.setText(f"EPCIM: {epcim_val:.2f}%")
        self.lbl_pccpm.setText(f"PCCPM: {pccpm_val:.2f}%")
        self.lbl_ecmdr.setText(f"ECMDR: {ecmdr_val:.2f}%")
        self.lbl_mdr_xdr.setText(
            f"MDR: {'Sí' if es_MDR else 'No'}   XDR: {'Sí' if es_XDR else 'No'}"
        )

        # Rellenar tabla de antibióticos
        self.table.setRowCount(len(antibioticos_results))
        for row, (name, value, interp) in enumerate(antibioticos_results):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{value:.1%}"))
            self.table.setItem(row, 2, QTableWidgetItem(interp))

        # Recomendaciones clínicas (igual que antes)
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