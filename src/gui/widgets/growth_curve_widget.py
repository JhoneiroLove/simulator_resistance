"""
Widget Growth Curve - Visualización de Curvas de Crecimiento Bacteriano

Muestra curvas de crecimiento OD vs Tiempo para diferentes concentraciones
de antibiótico, permitiendo visualizar el efecto inhibitorio y determinar MIC.

Autor: Sistema AST Simulator
Fecha: 11 de noviembre de 2025
"""

from typing import Optional, List, Dict
import numpy as np

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QGroupBox,
    QSizePolicy,
    QScrollArea,
    QFrame,
)
from PyQt5.QtCore import pyqtSignal, Qt
from pyqtgraph import PlotWidget, mkPen, InfiniteLine


class GrowthCurveWidget(QWidget):
    """
    Widget para visualizar curvas de crecimiento bacteriano.

    Características:
    - Gráfico OD vs Tiempo (pyqtgraph)
    - Múltiples curvas por concentración de antibiótico
    - Leyenda con concentraciones
    - Línea vertical marcando MIC
    - Selector de antibiótico

    Signals:
        antibiotic_changed: Emitido al cambiar antibiótico seleccionado
    """

    antibiotic_changed = pyqtSignal(str)  # nombre del antibiótico

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.current_data: Dict = {}
        self.curves: List = []
        self.mic_line: Optional[InfiniteLine] = None

        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Crear scroll area principal
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # === TÍTULO ===
        title_label = QLabel("📈 Curvas de Crecimiento Bacteriano")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 3px;
            }
        """)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(title_label)

        # === CONTENEDOR PRINCIPAL ===
        main_container = QHBoxLayout()
        main_container.setSpacing(20)

        # === COLUMNA IZQUIERDA: GRÁFICO ===
        plot_group = QGroupBox("Gráfico de Crecimiento")
        plot_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #3498db;
            }
        """)
        plot_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plot_layout = QVBoxLayout(plot_group)
        plot_layout.setContentsMargins(5, 5, 5, 5)

        # Widget de gráfico
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setMinimumSize(500, 400)
        self.plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # DESHABILITAR ZOOM Y ARRASTRE
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.hideButtons()

        # Configurar ejes
        self.plot_widget.setLabel(
            "left", "Densidad Óptica (OD 600 nm)", color="#2c3e50", size="10pt"
        )
        self.plot_widget.setLabel(
            "bottom", "Tiempo (horas)", color="#2c3e50", size="10pt"
        )
        self.plot_widget.setTitle(
            "Curvas de Crecimiento vs Concentración de Antibiótico", 
            color="#2c3e50", 
            size="12pt"
        )

        # Configurar rangos fijos
        self.plot_widget.setYRange(0, 3.5, padding=0.05)
        self.plot_widget.setXRange(0, 18, padding=0.02)

        # Añadir leyenda
        self.plot_widget.addLegend(offset=(10, 10), verSpacing=-5, horSpacing=5)

        plot_layout.addWidget(self.plot_widget)
        main_container.addWidget(plot_group, stretch=2)

        # === COLUMNA DERECHA: CONTROLES E INFORMACIÓN ===
        controls_group = QGroupBox("Controles e Información")
        controls_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #27ae60;
            }
        """)
        controls_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        controls_group.setMinimumWidth(300)
        controls_group.setMaximumWidth(400)
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setSpacing(15)

        # === SECCIÓN DE CONTROLES ===
        controls_section = QVBoxLayout()
        controls_section.setSpacing(15)

        # Selector de antibiótico
        antibiotic_layout = QVBoxLayout()
        antibiotic_layout.setSpacing(5)
        
        antibiotic_label = QLabel("Antibiótico:")
        antibiotic_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        antibiotic_layout.addWidget(antibiotic_label)
        
        self.antibiotic_combo = QComboBox()
        self.antibiotic_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        self.antibiotic_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.antibiotic_combo.currentTextChanged.connect(self._on_antibiotic_changed)
        antibiotic_layout.addWidget(self.antibiotic_combo)

        controls_section.addLayout(antibiotic_layout)
        controls_layout.addLayout(controls_section)

        # Línea separadora
        separator = QLabel()
        separator.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                min-height: 1px;
                max-height: 1px;
                margin: 5px 0px;
            }
        """)
        controls_layout.addWidget(separator)

        # === SECCIÓN DE INFORMACIÓN ===
        info_section = QVBoxLayout()
        info_section.setSpacing(10)

        info_title = QLabel("📊 Información del Gráfico")
        info_title.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                font-size: 12px;
            }
        """)
        info_section.addWidget(info_title)

        self.info_label = QLabel(
            "Seleccione un antibiótico para visualizar curvas de crecimiento"
        )
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d; 
                font-size: 11px;
                padding: 12px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #dee2e6;
            }
        """)
        self.info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        info_section.addWidget(self.info_label)

        controls_layout.addLayout(info_section)
        controls_layout.addStretch()

        main_container.addWidget(controls_group, stretch=1)

        # Agregar contenedor principal al layout
        layout.addLayout(main_container)

        layout.addStretch()

        # Configurar scroll area
        scroll_area.setWidget(main_widget)
        
        # Layout principal del widget
        widget_layout = QVBoxLayout(self)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(scroll_area)

    def load_growth_data(self, growth_data: Dict[str, List[Dict]]):
        """
        Carga datos de crecimiento para múltiples antibióticos.

        Args:
            growth_data: Diccionario con estructura:
                {
                    'antibiotico1': [
                        {
                            'concentracion': 0.0,  
                            'tiempos': [0, 1, 2, ..., 18],  
                            'ods': [0.1, 0.15, 0.25, ..., 2.5],  
                            'mic': False 
                        },
                        ...
                    ],
                    'antibiotico2': [...],
                    ...
                }
        """
        print(f"[GrowthCurveWidget] load_growth_data called")
        print(f"[GrowthCurveWidget] Received data type: {type(growth_data)}")
        print(
            f"[GrowthCurveWidget] Antibiotics: {list(growth_data.keys()) if growth_data else 'None'}"
        )

        self.current_data = growth_data

        # Actualizar combo de antibióticos
        self.antibiotic_combo.blockSignals(True)
        self.antibiotic_combo.clear()
        self.antibiotic_combo.addItems(sorted(growth_data.keys()))
        self.antibiotic_combo.blockSignals(False)

        print(
            f"[GrowthCurveWidget] Combo populated with {self.antibiotic_combo.count()} items"
        )

        # Cargar primer antibiótico si existe
        if growth_data:
            first_ab = sorted(growth_data.keys())[0]
            print(f"[GrowthCurveWidget] Setting first antibiotic: {first_ab}")
            self.antibiotic_combo.setCurrentText(first_ab)
            self._plot_antibiotic(first_ab)

    def _on_antibiotic_changed(self, antibiotic: str):
        """
        Maneja cambio de antibiótico seleccionado.

        Args:
            antibiotic: Nombre del antibiótico
        """
        if antibiotic and antibiotic in self.current_data:
            self._plot_antibiotic(antibiotic)
            self.antibiotic_changed.emit(antibiotic)

    def _plot_antibiotic(self, antibiotic: str):
        """
        Grafica las curvas de crecimiento para un antibiótico.

        Args:
            antibiotic: Nombre del antibiótico a graficar
        """
        # Limpiar gráfico anterior
        self.plot_widget.clear()
        self.plot_widget.addLegend(offset=(10, 10), verSpacing=-5, horSpacing=5)
        self.curves = []

        if antibiotic not in self.current_data:
            return

        curves_data = self.current_data[antibiotic]

        # Colores para diferentes concentraciones
        colors = [
            "#27ae60",  # Verde (control positivo)
            "#2ecc71",  # Verde claro
            "#f39c12",  # Naranja
            "#e67e22",  # Naranja oscuro
            "#e74c3c",  # Rojo
            "#c0392b",  # Rojo oscuro
            "#8e44ad",  # Púrpura
            "#2c3e50",  # Azul oscuro
        ]

        mic_concentration = None

        # Graficar cada curva
        for idx, curve_data in enumerate(curves_data):
            concentracion = curve_data.get("concentracion", 0)
            tiempos = curve_data.get("tiempos", [])
            ods = curve_data.get("ods", [])
            is_mic = curve_data.get("mic", False)

            if not tiempos or not ods:
                continue

            # Seleccionar color
            color = colors[idx % len(colors)]

            # Crear pen con estilo
            if concentracion == 0:
                # Control positivo: línea más gruesa
                pen = mkPen(color=color, width=3, style=1)  # Solid
                label = "Control (+) 0 µg/mL"
            else:
                # Otras concentraciones
                pen = mkPen(color=color, width=2)
                label = f"{concentracion:.2f} µg/mL"

                if is_mic:
                    label += " ← MIC"
                    mic_concentration = concentracion

            # Graficar curva
            curve = self.plot_widget.plot(
                tiempos,
                ods,
                pen=pen,
                name=label,
                symbol="o",
                symbolSize=4,
                symbolBrush=color,
            )
            self.curves.append(curve)

        # Actualizar información
        num_curves = len(curves_data)
        conc_range = (
            f"{curves_data[0]['concentracion']:.2f} - {curves_data[-1]['concentracion']:.2f}"
            if num_curves > 1
            else f"{curves_data[0]['concentracion']:.2f}"
        )

        info_text = f"""
        <b>Antibiótico:</b> {antibiotic}<br/>
        <b>Curvas:</b> {num_curves}<br/>
        <b>Concentraciones:</b> {conc_range} µg/mL<br/>
        """

        if mic_concentration is not None:
            info_text += f"<b>MIC:</b> {mic_concentration:.2f} µg/mL<br/>"
            info_text += "<span style='color: #27ae60;'>✓ Inhibición completa</span>"
        else:
            info_text += "<b>MIC:</b> No determinado<br/>"
            info_text += "<span style='color: #e74c3c;'>⚠ Sin inhibición completa</span>"

        self.info_label.setText(info_text)

    def clear(self):
        """Limpia el gráfico y resetea el widget."""
        self.plot_widget.clear()
        self.plot_widget.addLegend(offset=(10, 10), verSpacing=-5, horSpacing=5)
        self.curves = []
        self.mic_line = None
        self.current_data = {}
        self.antibiotic_combo.clear()
        self.info_label.setText(
            "Seleccione un antibiótico para visualizar curvas de crecimiento"
        )

    def export_to_csv(self, filename: str):
        """
        Exporta los datos de curvas a CSV.

        Args:
            filename: Ruta del archivo CSV a crear
        """
        import csv

        antibiotic = self.antibiotic_combo.currentText()
        if not antibiotic or antibiotic not in self.current_data:
            raise ValueError("No hay datos para exportar")

        curves_data = self.current_data[antibiotic]

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Header
            writer.writerow(["Antibiótico", antibiotic])
            writer.writerow([])

            # Datos por concentración
            for curve_data in curves_data:
                concentracion = curve_data.get("concentracion", 0)
                tiempos = curve_data.get("tiempos", [])
                ods = curve_data.get("ods", [])

                writer.writerow([f"Concentración: {concentracion:.2f} µg/mL"])
                writer.writerow(["Tiempo (h)", "OD 600nm"])

                for t, od in zip(tiempos, ods):
                    writer.writerow([t, f"{od:.4f}"])

                writer.writerow([])  # Línea vacía entre concentraciones


# Función auxiliar para generar datos de ejemplo
def generate_sample_growth_data() -> Dict[str, List[Dict]]:
    """
    Genera datos de crecimiento de ejemplo para testing.

    Returns:
        Diccionario con datos de ejemplo
    """
    import random

    def logistic_growth(t, od_max, k, t_mid, od_initial=0.1):
        """Modelo logístico de crecimiento."""
        return (
            od_max / (1 + np.exp(-k * (t - t_mid)))
            + od_initial
            - od_max / (1 + np.exp(k * t_mid))
        )

    antibiotics = ["Meropenem", "Ciprofloxacino", "Gentamicina"]
    concentrations = [0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
    tiempos = list(range(0, 19))  # 0 a 18 horas

    growth_data = {}

    for antibiotic in antibiotics:
        curves = []

        for conc in concentrations:
            # Inhibición proporcional a la concentración
            inhibition_factor = 1 / (1 + conc * 0.3)
            od_max = 2.8 * inhibition_factor
            k = 0.5 * inhibition_factor
            t_mid = 8.0 + conc * 0.5  # Retraso por antibiótico

            # Generar curva
            ods = [
                max(0.05, logistic_growth(t, od_max, k, t_mid) + random.gauss(0, 0.02))
                for t in tiempos
            ]

            # MIC es donde OD final < 0.3
            is_mic = (
                conc > 0
                and ods[-1] < 0.3
                and (
                    conc == concentrations[-1]
                    or growth_data.get(antibiotic, [{}])[-1].get("ods", [1])[-1] >= 0.3
                )
            )

            curves.append(
                {"concentracion": conc, "tiempos": tiempos, "ods": ods, "mic": is_mic}
            )

        growth_data[antibiotic] = curves

    return growth_data