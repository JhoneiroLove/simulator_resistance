from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QComboBox,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QScrollArea,
    QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from src.data.database import get_session
from src.data.models import Gen, Antibiotico

class InputForm(QWidget):
    simulation_triggered = pyqtSignal(int, list)  # int: antibiotico_id, list: genes_ids

    def __init__(self):
        super().__init__()
        self.session = get_session()
        self.main_layout = QVBoxLayout()
        
        # Estilo general
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QCheckBox {
                spacing: 5px;
            }
        """)

        # Cargar datos
        self.load_data()

        # Crear secciones con GroupBox
        self.create_gene_selection()
        self.create_antibiotic_selection()
        self.create_simulation_button()

        # Añadir un spacer para empujar todo hacia arriba
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

    def load_data(self):
        self.genes = self.session.query(Gen).all()
        self.antibioticos = self.session.query(Antibiotico).all()

    def create_gene_selection(self):
        """Crea la sección de selección de genes con scroll"""
        gene_group = QGroupBox("1. Selección de Genes")
        gene_layout = QVBoxLayout()
        
        # Crear área de scroll para los genes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        self.gene_checkboxes = self.create_gene_checkboxes()
        for cb in self.gene_checkboxes.values():
            scroll_layout.addWidget(cb)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        
        gene_layout.addWidget(scroll)
        gene_group.setLayout(gene_layout)
        self.main_layout.addWidget(gene_group)

    def create_antibiotic_selection(self):
        """Crea la sección de selección de antibióticos"""
        ab_group = QGroupBox("2. Selección de Antibiótico")
        ab_layout = QVBoxLayout()
        
        self.antibiotico_combo = self.create_antibiotico_combo()
        ab_layout.addWidget(self.antibiotico_combo)
        
        ab_group.setLayout(ab_layout)
        self.main_layout.addWidget(ab_group)

    def create_simulation_button(self):
        """Crea la sección del botón de simulación"""
        sim_group = QGroupBox("3. Ejecutar Simulación")
        sim_layout = QVBoxLayout()
        
        self.simular_btn = QPushButton("Iniciar Simulación")
        self.simular_btn.setFont(QFont('Segoe UI', 10, QFont.Bold))
        self.simular_btn.clicked.connect(self.on_simulate)
        
        sim_layout.addWidget(self.simular_btn, 0, Qt.AlignCenter)
        sim_group.setLayout(sim_layout)
        self.main_layout.addWidget(sim_group)

    def create_gene_checkboxes(self):
        return {
            gen.id: QCheckBox(f"{gen.nombre} ({gen.descripcion})") for gen in self.genes
        }

    def create_antibiotico_combo(self):
        combo = QComboBox()
        combo.setFont(QFont('Segoe UI', 10))
        for ab in self.antibioticos:
            combo.addItem(ab.nombre, userData=ab.id)
        return combo

    def on_simulate(self):
        selected_genes = [
            id for id, cb in self.gene_checkboxes.items() if cb.isChecked()
        ]
        antibiotico_id = self.antibiotico_combo.currentData()
        
        if self.antibiotico_combo.currentText() == "Meropenem" and any(gen == "blaVIM" for gen in selected_genes):
            QMessageBox.warning(self, "Alerta", "blaVIM confiere resistencia alta a carbapenémicos.")

        if not selected_genes:
            QMessageBox.warning(self, "Error", "Seleccione al menos un gen.")
            return
        if not antibiotico_id:
            QMessageBox.warning(self, "Error", "Seleccione un antibiótico.")
            return

        self.simulation_triggered.emit(antibiotico_id, selected_genes)