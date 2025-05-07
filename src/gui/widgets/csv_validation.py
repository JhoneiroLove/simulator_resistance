from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
)
from PyQt5.QtCore import Qt

class CSVValidationWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar layout
        self.layout = QVBoxLayout(self)

        # Botón de carga
        self.btn_load = QPushButton("Cargar CSV Histórico")
        self.btn_load.clicked.connect(self.load_csv)

        # Tabla de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            [
                "Antibiótico",
                "Resistencia Observada",
                "Resistencia Predicha",
                "Diferencia Absoluta",
                "Error Relativo (%)",
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        # Añadir elementos al layout
        self.layout.addWidget(self.btn_load)
        self.layout.addWidget(self.table)

    def load_csv(self):
        """Carga un archivo CSV y muestra comparaciones."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar CSV Histórico", "", "CSV Files (*.csv)"
        )

        if path:
            from src.core.validation import CSVValidator

            validator = CSVValidator(path)
            results = validator.compare_with_simulations()

            # Configurar tabla
            self.table.setRowCount(results.shape[0])
            for row_idx, row in results.iterrows():
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(
                        f"{value:.2f}" if isinstance(value, float) else str(value)
                    )
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)