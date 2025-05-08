from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtGui import QFont

class DetailedResults(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar layout
        self.layout = QVBoxLayout(self)

        # Etiqueta de resistencia
        self.lbl_resistencia = QLabel("Resistencia Predicha: ")
        self.lbl_resistencia.setFont(QFont("Arial", 14, QFont.Bold))

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

        # Añadir elementos
        self.layout.addWidget(self.lbl_resistencia)
        self.layout.addWidget(self.txt_recomendacion)

    def update_results(self, resistencia, antibiotico):
        """Actualiza la interfaz con nuevos resultados."""
        self.lbl_resistencia.setText(f"Resistencia a {antibiotico}: {resistencia:.2%}")

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
                "Consulte con el servicio de infectología para recomendaciones personalizadas.",
            )
        )