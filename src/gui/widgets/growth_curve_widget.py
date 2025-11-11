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
    QPushButton,
    QGroupBox,
)
from PyQt5.QtCore import pyqtSignal
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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # === BARRA DE CONTROL ===
        control_layout = QHBoxLayout()

        # Selector de antibiótico
        control_layout.addWidget(QLabel("Antibiótico:"))
        self.antibiotic_combo = QComboBox()
        self.antibiotic_combo.setMinimumWidth(200)
        self.antibiotic_combo.currentTextChanged.connect(self._on_antibiotic_changed)
        control_layout.addWidget(self.antibiotic_combo)

        control_layout.addStretch()

        # Botón limpiar
        self.clear_button = QPushButton("🗑️ Limpiar")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.clear_button.clicked.connect(self.clear)
        control_layout.addWidget(self.clear_button)

        layout.addLayout(control_layout)

        # === GRÁFICO ===
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Configurar ejes
        self.plot_widget.setLabel(
            "left", "Densidad Óptica (OD 600 nm)", color="#2c3e50", size="12pt"
        )
        self.plot_widget.setLabel(
            "bottom", "Tiempo (horas)", color="#2c3e50", size="12pt"
        )
        self.plot_widget.setTitle(
            "Curvas de Crecimiento Bacteriano", color="#2c3e50", size="14pt"
        )

        # Configurar rango Y
        self.plot_widget.setYRange(0, 3.5, padding=0.05)
        self.plot_widget.setXRange(0, 18, padding=0.02)

        # Añadir leyenda
        self.plot_widget.addLegend(offset=(10, 10))

        layout.addWidget(self.plot_widget)

        # === INFO BOX ===
        info_group = QGroupBox("Información")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        info_layout = QVBoxLayout(info_group)

        self.info_label = QLabel(
            "Seleccione un antibiótico para visualizar curvas de crecimiento"
        )
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #7f8c8d; font-size: 10pt;")
        info_layout.addWidget(self.info_label)

        layout.addWidget(info_group)

    def load_growth_data(self, growth_data: Dict[str, List[Dict]]):
        """
        Carga datos de crecimiento para múltiples antibióticos.

        Args:
            growth_data: Diccionario con estructura:
                {
                    'antibiotico1': [
                        {
                            'concentracion': 0.0,  # µg/mL
                            'tiempos': [0, 1, 2, ..., 18],  # horas
                            'ods': [0.1, 0.15, 0.25, ..., 2.5],  # OD 600nm
                            'mic': False  # Si esta concentración es el MIC
                        },
                        ...
                    ],
                    'antibiotico2': [...],
                    ...
                }
        """
        self.current_data = growth_data

        # Actualizar combo de antibióticos
        self.antibiotic_combo.blockSignals(True)
        self.antibiotic_combo.clear()
        self.antibiotic_combo.addItems(sorted(growth_data.keys()))
        self.antibiotic_combo.blockSignals(False)

        # Cargar primer antibiótico si existe
        if growth_data:
            first_ab = sorted(growth_data.keys())[0]
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
        self.plot_widget.addLegend(offset=(10, 10))
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

        # Agregar línea vertical en MIC si existe
        if mic_concentration is not None:
            # Buscar el tiempo aproximado donde alcanza el MIC
            # (simplificación: usar tiempo final)
            self.mic_line = InfiniteLine(
                pos=mic_concentration,
                angle=90,
                pen=mkPen("#e74c3c", width=2, style=2),  # Línea punteada roja
                label="MIC",
                labelOpts={"position": 0.95, "color": "#e74c3c"},
            )
            # No agregamos la línea vertical por ahora, solo horizontal en OD

        # Actualizar info
        num_curves = len(curves_data)
        conc_range = (
            f"{curves_data[0]['concentracion']:.2f} - {curves_data[-1]['concentracion']:.2f}"
            if num_curves > 1
            else f"{curves_data[0]['concentracion']:.2f}"
        )

        info_text = f"""
        <b>Antibiótico:</b> {antibiotic}<br/>
        <b>Curvas graficadas:</b> {num_curves}<br/>
        <b>Rango de concentraciones:</b> {conc_range} µg/mL<br/>
        """

        if mic_concentration is not None:
            info_text += f"<b>MIC detectado:</b> {mic_concentration:.2f} µg/mL"

        self.info_label.setText(info_text)

    def clear(self):
        """Limpia el gráfico y resetea el widget."""
        self.plot_widget.clear()
        self.plot_widget.addLegend(offset=(10, 10))
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
