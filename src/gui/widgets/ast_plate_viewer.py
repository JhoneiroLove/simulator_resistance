"""
Widget AST Plate Viewer - Visualización de Placa 96 Pocillos

Visualización interactiva del panel AST como grid 8×12:
- Colores según turbidez (OD600)
- Tooltips con información de cada pocillo
- Slider temporal para ver evolución
- Marcadores de controles positivo/negativo

Autor: Sistema AST Simulator
Fecha: 11 de noviembre de 2025
"""

from typing import Optional, List, Dict
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QSlider,
    QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal


def od_to_color(od_value: float) -> str:
    """
    Convierte valor OD a código de color HTML.

    Escala de colores:
    - OD < 0.1: Blanco (claro, sin crecimiento)
    - 0.1 ≤ OD < 0.5: Amarillo muy claro (crecimiento inicial)
    - 0.5 ≤ OD < 1.5: Amarillo (crecimiento moderado)
    - OD ≥ 1.5: Naranja/marrón (crecimiento abundante)

    Args:
        od_value: Densidad óptica a 600nm

    Returns:
        Código de color hexadecimal (ej: "#ffcc00")
    """
    if od_value < 0.1:
        return "#ffffff"  # Blanco
    elif od_value < 0.5:
        return "#ffffcc"  # Amarillo muy claro
    elif od_value < 1.5:
        return "#ffcc00"  # Amarillo
    else:
        return "#cc9900"  # Naranja/turbio


def od_to_description(od_value: float) -> str:
    """
    Convierte OD a descripción textual de turbidez.

    Args:
        od_value: Densidad óptica

    Returns:
        Descripción ("Claro", "Ligero", "Moderado", "Turbio")
    """
    if od_value < 0.1:
        return "Claro"
    elif od_value < 0.5:
        return "Ligero"
    elif od_value < 1.5:
        return "Moderado"
    else:
        return "Turbio"


class WellWidget(QFrame):
    """
    Widget individual para un pocillo de la placa.

    Muestra:
    - Color de fondo según OD
    - Posición del pocillo (ej: A1)
    - Tooltip con información detallada
    - Borde especial para controles QC
    """

    clicked = pyqtSignal(str)  # Emite posición al hacer clic

    def __init__(self, position: str, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.position = position
        self.well_data = None
        self.is_control = False

        # Configuración visual
        self.setFixedSize(50, 50)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setLineWidth(2)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        # Label de posición
        self.position_label = QLabel(position)
        self.position_label.setAlignment(Qt.AlignCenter)
        self.position_label.setStyleSheet("font-size: 9px; font-weight: bold;")
        layout.addWidget(self.position_label)

        # Inicializar como vacío
        self.set_empty()

    def set_empty(self):
        """Establece el pocillo como vacío."""
        self.setStyleSheet("background-color: #f0f0f0; border: 2px solid #bdc3c7;")
        self.setToolTip(f"{self.position}: Vacío")
        self.well_data = None

    def set_control(self, control_type: str, od_value: float):
        """
        Establece el pocillo como control QC.

        Args:
            control_type: 'positivo' o 'negativo'
            od_value: Valor OD final
        """
        self.is_control = True
        self.well_data = {"tipo": control_type, "od_final": od_value}

        # Color según OD
        bg_color = od_to_color(od_value)

        # Borde especial para controles
        if control_type == "positivo":
            border_color = "#27ae60"  # Verde
            symbol = "✓"
        else:
            border_color = "#e74c3c"  # Rojo
            symbol = "✗"

        self.setStyleSheet(f"""
            background-color: {bg_color};
            border: 3px solid {border_color};
            border-radius: 5px;
        """)

        # Actualizar label
        self.position_label.setText(f"{self.position}\n{symbol}")

        # Tooltip
        turbidez = od_to_description(od_value)
        self.setToolTip(
            f"{self.position}: Control {control_type.capitalize()}\n"
            f"OD: {od_value:.3f}\n"
            f"Turbidez: {turbidez}"
        )

    def set_test_well(
        self, antibiotico: str, concentracion: float, od_value: float, crecimiento: bool
    ):
        """
        Establece el pocillo como pocillo de prueba.

        Args:
            antibiotico: Nombre del antibiótico
            concentracion: Concentración en µg/mL
            od_value: Valor OD final
            crecimiento: Si hubo crecimiento detectado
        """
        self.well_data = {
            "tipo": "test",
            "antibiotico": antibiotico,
            "concentracion": concentracion,
            "od_final": od_value,
            "crecimiento": crecimiento,
        }

        # Color según OD
        bg_color = od_to_color(od_value)

        self.setStyleSheet(f"""
            background-color: {bg_color};
            border: 2px solid #34495e;
            border-radius: 3px;
        """)

        # Tooltip detallado
        turbidez = od_to_description(od_value)
        estado = "Crecimiento" if crecimiento else "Inhibido"

        self.setToolTip(
            f"{self.position}: {antibiotico}\n"
            f"Concentración: {concentracion} µg/mL\n"
            f"OD: {od_value:.3f}\n"
            f"Turbidez: {turbidez}\n"
            f"Estado: {estado}"
        )

    def update_od(self, od_value: float):
        """
        Actualiza solo el valor OD (para slider temporal).

        Args:
            od_value: Nuevo valor OD
        """
        if self.well_data is None:
            return

        self.well_data["od_final"] = od_value

        # Actualizar color
        bg_color = od_to_color(od_value)

        if self.is_control:
            # Mantener borde de control
            border_color = (
                "#27ae60" if self.well_data["tipo"] == "positivo" else "#e74c3c"
            )
            self.setStyleSheet(f"""
                background-color: {bg_color};
                border: 3px solid {border_color};
                border-radius: 5px;
            """)
        else:
            self.setStyleSheet(f"""
                background-color: {bg_color};
                border: 2px solid #34495e;
                border-radius: 3px;
            """)

        # Actualizar tooltip
        turbidez = od_to_description(od_value)

        if self.is_control:
            self.setToolTip(
                f"{self.position}: Control {self.well_data['tipo'].capitalize()}\n"
                f"OD: {od_value:.3f}\n"
                f"Turbidez: {turbidez}"
            )
        else:
            estado = "Crecimiento" if od_value >= 0.3 else "Inhibido"
            self.setToolTip(
                f"{self.position}: {self.well_data['antibiotico']}\n"
                f"Concentración: {self.well_data['concentracion']} µg/mL\n"
                f"OD: {od_value:.3f}\n"
                f"Turbidez: {turbidez}\n"
                f"Estado: {estado}"
            )

    def mousePressEvent(self, event):
        """Emite señal al hacer clic."""
        if self.well_data is not None:
            self.clicked.emit(self.position)
        super().mousePressEvent(event)


class ASTPlateViewer(QWidget):
    """
    Visualizador de placa AST 96 pocillos (8×12 grid).

    Características:
    - Grid visual con colores según turbidez
    - Slider temporal para ver evolución (0-18h)
    - Marcadores de controles QC
    - Tooltips informativos
    - Leyenda de colores

    Signals:
        well_clicked: Emitido al hacer clic en pocillo (posición, datos)
    """

    well_clicked = pyqtSignal(str, dict)  # posición, datos

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.wells: Dict[str, WellWidget] = {}
        self.time_series_data: Optional[List[Dict]] = None
        self.current_time_index = -1  # -1 = tiempo final

        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)

        # Título
        title = QLabel("Placa AST - Vista 96 Pocillos")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Grid de pocillos
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(5)

        # Labels de columnas (1-12)
        for col in range(12):
            col_label = QLabel(str(col + 1))
            col_label.setAlignment(Qt.AlignCenter)
            col_label.setStyleSheet("font-weight: bold; color: #7f8c8d;")
            grid_layout.addWidget(col_label, 0, col + 1)

        # Filas A-H con pocillos
        rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
        for row_idx, row_letter in enumerate(rows):
            # Label de fila
            row_label = QLabel(row_letter)
            row_label.setAlignment(Qt.AlignCenter)
            row_label.setStyleSheet("font-weight: bold; color: #7f8c8d;")
            grid_layout.addWidget(row_label, row_idx + 1, 0)

            # Pocillos de la fila
            for col in range(12):
                position = f"{row_letter}{col + 1}"
                well = WellWidget(position)
                well.clicked.connect(self._on_well_clicked)
                self.wells[position] = well
                grid_layout.addWidget(well, row_idx + 1, col + 1)

        layout.addWidget(grid_container)

        # Slider temporal
        time_group = QWidget()
        time_layout = QVBoxLayout(time_group)

        time_label = QLabel("Línea temporal (0 - 18 horas)")
        time_label.setStyleSheet("font-weight: bold; color: #34495e;")
        time_layout.addWidget(time_label)

        slider_container = QHBoxLayout()

        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(18)  # 19 puntos (0-18h cada hora)
        self.time_slider.setValue(18)  # Por defecto: tiempo final
        self.time_slider.setTickPosition(QSlider.TicksBelow)
        self.time_slider.setTickInterval(3)
        self.time_slider.valueChanged.connect(self._on_time_changed)
        slider_container.addWidget(self.time_slider)

        self.time_value_label = QLabel("18.0h (Final)")
        self.time_value_label.setStyleSheet("font-weight: bold; min-width: 100px;")
        slider_container.addWidget(self.time_value_label)

        time_layout.addLayout(slider_container)
        layout.addWidget(time_group)

        # Leyenda de colores
        legend_group = QWidget()
        legend_layout = QHBoxLayout(legend_group)
        legend_layout.addWidget(QLabel("Leyenda:"))

        colors = [
            ("#ffffff", "Claro (OD<0.1)"),
            ("#ffffcc", "Ligero (0.1-0.5)"),
            ("#ffcc00", "Moderado (0.5-1.5)"),
            ("#cc9900", "Turbio (OD≥1.5)"),
        ]

        for color, desc in colors:
            color_box = QLabel("   ")
            color_box.setStyleSheet(
                f"background-color: {color}; border: 1px solid #7f8c8d;"
            )
            legend_layout.addWidget(color_box)
            legend_layout.addWidget(QLabel(desc))

        legend_layout.addStretch()
        layout.addWidget(legend_group)

    def load_well_data(self, well_data_list: List):
        """
        Carga datos de pocillos desde ASTSimulator.

        Args:
            well_data_list: Lista de objetos WellData del simulador
        """
        # Limpiar pocillos
        for well in self.wells.values():
            well.set_empty()

        # Cargar datos
        for well_data in well_data_list:
            position = well_data.posicion

            if position not in self.wells:
                continue

            well_widget = self.wells[position]

            if well_data.tipo == "control_positivo":
                well_widget.set_control("positivo", well_data.od_final)
            elif well_data.tipo == "control_negativo":
                well_widget.set_control("negativo", well_data.od_final)
            else:  # test
                well_widget.set_test_well(
                    antibiotico=well_data.antibiotico,
                    concentracion=well_data.concentracion,
                    od_value=well_data.od_final,
                    crecimiento=(well_data.od_final >= 0.3),
                )

        # Guardar serie temporal para slider
        self.time_series_data = well_data_list
        self.current_time_index = -1  # Tiempo final

    def _on_time_changed(self, value: int):
        """
        Maneja cambio en slider temporal.

        Args:
            value: Índice de tiempo (0-18 horas)
        """
        self.current_time_index = value

        # Actualizar label
        if value == 18:
            self.time_value_label.setText("18.0h (Final)")
        else:
            self.time_value_label.setText(f"{value}.0h")

        # Actualizar ODs de pocillos si hay datos de serie temporal
        if self.time_series_data:
            for well_data in self.time_series_data:
                position = well_data.posicion

                if position not in self.wells:
                    continue

                # Buscar lectura en el tiempo seleccionado
                # well_data.readings es lista de WellReading
                if hasattr(well_data, "readings") and well_data.readings:
                    # Encontrar lectura más cercana al tiempo seleccionado
                    target_time = value * 60  # Convertir horas a minutos

                    # Buscar lectura exacta o más cercana
                    reading = None
                    for r in well_data.readings:
                        if r.tiempo_minutos == target_time:
                            reading = r
                            break

                    if reading:
                        self.wells[position].update_od(reading.od_600)
                    else:
                        # Si no hay lectura exacta, usar OD final para tiempo 18h
                        if value == 18:
                            self.wells[position].update_od(well_data.od_final)

    def _on_well_clicked(self, position: str):
        """
        Maneja clic en un pocillo.

        Args:
            position: Posición del pocillo (ej: "A1")
        """
        well = self.wells.get(position)
        if well and well.well_data:
            self.well_clicked.emit(position, well.well_data)

    def clear(self):
        """Limpia todos los pocillos."""
        for well in self.wells.values():
            well.set_empty()

        self.time_series_data = None
        self.current_time_index = -1
        self.time_slider.setValue(18)
