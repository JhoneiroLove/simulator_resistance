from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QComboBox,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import pyqtSignal
from src.data.database import get_session
from src.data.models import Gen, Antibiotico

class InputForm(QWidget):
    simulation_triggered = pyqtSignal(int, list)  # int: antibiotico_id, list: genes_ids

    def __init__(self):
        super().__init__()
        self.session = get_session()
        self.layout = QVBoxLayout()

        # Cargar datos
        self.load_data()

        # Widgets
        self.gene_checkboxes = self.create_gene_checkboxes()
        self.antibiotico_combo = self.create_antibiotico_combo()
        self.simular_btn = QPushButton("Iniciar Simulación", clicked=self.on_simulate)

        # Layout
        for cb in self.gene_checkboxes.values():
            self.layout.addWidget(cb)
        self.layout.addWidget(self.antibiotico_combo)
        self.layout.addWidget(self.simular_btn)
        self.setLayout(self.layout)

    def load_data(self):
        self.genes = self.session.query(Gen).all()
        self.antibioticos = self.session.query(Antibiotico).all()

    def create_gene_checkboxes(self):
        return {
            gen.id: QCheckBox(f"{gen.nombre} ({gen.descripcion})") for gen in self.genes
        }

    def create_antibiotico_combo(self):
        combo = QComboBox()
        for ab in self.antibioticos:
            combo.addItem(ab.nombre, userData=ab.id)
        return combo

    def on_simulate(self):
        selected_genes = [
            id for id, cb in self.gene_checkboxes.items() if cb.isChecked()
        ]
        antibiotico_id = self.antibiotico_combo.currentData()

        if not selected_genes:
            QMessageBox.warning(self, "Error", "Seleccione al menos un gen.")
            return
        if not antibiotico_id:
            QMessageBox.warning(self, "Error", "Seleccione un antibiótico.")
            return

        self.simulation_triggered.emit(antibiotico_id, selected_genes)