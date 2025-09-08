import sys
import os
import math
from PyQt5.QtWidgets import (
    QApplication,
    QSplashScreen,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import (
    QPixmap,
    QPainter,
    QFont,
    QColor,
    QBrush,
    QLinearGradient,
    QRadialGradient,
    QPen,
)

class AnimatedSplashScreen(QSplashScreen):
    """Splash screen avanzado con animaciones y efectos visuales"""

    def __init__(self):
        # Crear pixmap base
        self.base_pixmap = self.create_base_pixmap()
        super().__init__(self.base_pixmap, Qt.WindowStaysOnTopHint)

        # Variables de animación
        self.animation_frame = 0
        self.pulse_factor = 0
        self.rotation_angle = 0

        # Setup UI
        self.setup_ui()
        self.setup_animations()

        # Datos de carga
        self.current_progress = 0
        self.loading_tasks = [
            "Inicializando núcleo del sistema...",
            "Estableciendo conexión con base de datos...",
            "Configurando algoritmos evolutivos...",
            "Cargando modelos de resistencia bacteriana...",
            "Preparando motor de simulación...",
            "Inicializando interfaz gráfica...",
            "Aplicando configuraciones de usuario...",
            "Verificando integridad de dependencias...",
            "Optimizando rendimiento del sistema...",
            "Finalizando proceso de inicialización...",
        ]
        self.current_task = 0

    def create_base_pixmap(self):
        """Crea el pixmap base con diseño científico/médico"""
        width, height = 700, 450
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fondo con gradiente radial usando los colores rojos del programa
        center_gradient = QRadialGradient(
            width // 2, height // 2, min(width, height) // 2
        )
        center_gradient.setColorAt(0, QColor("#641212"))  # Rojo muy oscuro
        center_gradient.setColorAt(
            0.6, QColor("#841C1C")
        )  # Rojo principal del programa
        center_gradient.setColorAt(1, QColor("#A93232"))  # Rojo más claro

        painter.fillRect(0, 0, width, height, QBrush(center_gradient))

        # Efecto de partículas/moléculas flotantes en tonos rojos
        painter.setPen(QPen(QColor(255, 150, 150, 80), 1))
        painter.setBrush(QBrush(QColor(255, 100, 100, 40)))

        # Generar partículas en posiciones pseudo-aleatorias
        import random

        random.seed(42)  # Seed fijo para consistencia

        for _ in range(25):
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)
            size = random.randint(3, 12)

            # Dibujar partícula con efecto de brillo
            painter.drawEllipse(x - size // 2, y - size // 2, size, size)

            # Líneas de conexión entre partículas cercanas
            for _ in range(3):
                x2 = x + random.randint(-80, 80)
                y2 = y + random.randint(-80, 80)
                if 0 < x2 < width and 0 < y2 < height:
                    painter.setPen(QPen(QColor(255, 150, 150, 30), 1))
                    painter.drawLine(x, y, x2, y2)

        # Logo/Título principal
        painter.setPen(QPen(QColor(255, 255, 255), 2))

        # Dibujar logo científico (ADN estilizado) en colores rojos
        self.draw_dna_helix(painter, 80, height // 2 - 60, 40, 120)

        # Título (movido más a la derecha para no chocar con el ADN)
        title_font = QFont("Segoe UI", 36, QFont.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(200, height // 2 - 20, "SRB")

        # Subtítulo (también movido)
        subtitle_font = QFont("Segoe UI", 16, QFont.Normal)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(255, 220, 220))
        painter.drawText(200, height // 2 + 10, "Simulador de Resistencia Bacteriana")

        # Información adicional (también movida)
        info_font = QFont("Segoe UI", 11)
        painter.setFont(info_font)
        painter.setPen(QColor(255, 180, 180))
        painter.drawText(
            200, height // 2 + 35, "Sistema Avanzado de Modelado Evolutivo"
        )
        painter.drawText(200, height // 2 + 55, "Versión 1.0 • © 2025 JhoneiroLove")

        painter.end()
        return pixmap

    def draw_dna_helix(self, painter, x, y, width, height):
        """Dibuja una hélice de ADN estilizada"""
        painter.setPen(QPen(QColor(255, 150, 150), 3))

        steps = 50
        for i in range(steps):
            t = i / steps
            y_pos = int(y + t * height)

            # Coordenadas de la hélice
            x1 = int(x + width // 2 + (width // 4) * math.sin(t * 6 * math.pi))
            x2 = int(
                x + width // 2 + (width // 4) * math.sin(t * 6 * math.pi + math.pi)
            )

            if i > 0:
                # Dibujar segmentos de la hélice
                prev_t = (i - 1) / steps
                prev_y = int(y + prev_t * height)
                prev_x1 = int(
                    x + width // 2 + (width // 4) * math.sin(prev_t * 6 * math.pi)
                )
                prev_x2 = int(
                    x
                    + width // 2
                    + (width // 4) * math.sin(prev_t * 6 * math.pi + math.pi)
                )

                painter.drawLine(prev_x1, prev_y, x1, y_pos)
                painter.drawLine(prev_x2, prev_y, x2, y_pos)

            # Conectores entre cadenas (cada 5 pasos)
            if i % 5 == 0:
                painter.setPen(QPen(QColor(255, 200, 200, 150), 2))
                painter.drawLine(x1, y_pos, x2, y_pos)
                painter.setPen(QPen(QColor(255, 150, 150), 3))

    def setup_ui(self):
        """Configura la interfaz de usuario del splash"""
        # Widget contenedor
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(60, 350, 60, 40)
        layout.setSpacing(20)

        # Label de estado con estilo mejorado
        self.status_label = QLabel("Iniciando sistema...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                font-family: 'Segoe UI';
                font-size: 15px;
                font-weight: 500;
                background: transparent;
                padding: 5px 0px;
            }
        """)
        layout.addWidget(self.status_label)

        # Barra de progreso mejorada
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.1);
                text-align: center;
                color: white;
                font-weight: bold;
                font-size: 12px;
                height: 24px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #841C1C, stop:0.5 #A93232, stop:1 #D98880);
                border-radius: 10px;
                margin: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def setup_animations(self):
        """Configura las animaciones del splash"""
        # Timer para animaciones
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20 FPS

        # Timer para progreso (más lento)
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)

    def start_loading(self):
        """Inicia el proceso de carga"""
        self.progress_timer.start(400)  # Actualizar cada 400ms

    def update_animation(self):
        """Actualiza las animaciones visuales"""
        self.animation_frame += 1
        self.pulse_factor = (math.sin(self.animation_frame * 0.1) + 1) / 2
        self.rotation_angle = (self.animation_frame * 2) % 360

        # Crear pixmap animado
        animated_pixmap = QPixmap(self.base_pixmap.size())
        animated_pixmap.fill(Qt.transparent)

        painter = QPainter(animated_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Dibujar pixmap base
        painter.drawPixmap(0, 0, self.base_pixmap)

        # Agregar efectos animados
        self.draw_animated_effects(painter)

        painter.end()

        # Actualizar el pixmap del splash
        self.setPixmap(animated_pixmap)

    def draw_animated_effects(self, painter):
        """Dibuja efectos visuales animados"""
        width = self.base_pixmap.width()
        height = self.base_pixmap.height()

        # Efecto de pulso en el logo
        pulse_alpha = int(80 + 60 * self.pulse_factor)
        painter.setPen(QPen(QColor(255, 150, 150, pulse_alpha), 2))
        painter.setBrush(Qt.NoBrush)

        # Círculos concéntricos pulsantes alrededor del logo
        center_x, center_y = 100, height // 2
        for i in range(3):
            radius = int(30 + i * 15 + 10 * self.pulse_factor)
            painter.drawEllipse(
                center_x - radius, center_y - radius, radius * 2, radius * 2
            )

        # Partículas flotantes animadas
        painter.setPen(QPen(QColor(255, 150, 150, 100), 1))
        painter.setBrush(QBrush(QColor(255, 100, 100, 60)))

        for i in range(8):
            angle = (self.rotation_angle + i * 45) * math.pi / 180
            orbit_radius = 150 + 20 * math.sin(self.animation_frame * 0.05 + i)

            particle_x = int(width // 2 + orbit_radius * math.cos(angle))
            particle_y = int(height // 2 + orbit_radius * math.sin(angle))

            size = int(4 + 2 * math.sin(self.animation_frame * 0.1 + i))
            painter.drawEllipse(
                particle_x - size, particle_y - size, size * 2, size * 2
            )

    def update_progress(self, progress=None, message=None):
        """Actualiza el progreso de carga"""
        if progress is not None:
            self.current_progress = progress
        else:
            if self.current_progress >= 100:
                self.progress_timer.stop()
                return

            # Incremento de progreso automático
            increment = 100 // len(self.loading_tasks)
            self.current_progress = min(100, self.current_progress + increment)

        # Actualizar barra de progreso con animación suave
        self.animate_progress_bar(self.current_progress)

        # Actualizar mensaje de estado
        if message is not None:
            self.status_label.setText(message)
        elif self.current_task < len(self.loading_tasks):
            self.status_label.setText(self.loading_tasks[self.current_task])
            self.current_task += 1

    def animate_progress_bar(self, target_value):
        """Anima la barra de progreso hacia el valor objetivo"""
        if hasattr(self, "progress_animation"):
            self.progress_animation.stop()

        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(300)
        self.progress_animation.setStartValue(self.progress_bar.value())
        self.progress_animation.setEndValue(target_value)
        self.progress_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.progress_animation.start()

    def finish_loading(self):
        """Finaliza la pantalla de carga con animación"""
        self.current_progress = 100
        self.animate_progress_bar(100)
        self.status_label.setText("¡Sistema listo para usar!")

        # Detener animaciones
        if hasattr(self, "animation_timer"):
            self.animation_timer.stop()

    def closeEvent(self, event):
        """Maneja el evento de cierre"""
        # Detener todas las animaciones
        if hasattr(self, "animation_timer"):
            self.animation_timer.stop()
        if hasattr(self, "progress_timer"):
            self.progress_timer.stop()
        if hasattr(self, "progress_animation"):
            self.progress_animation.stop()

        super().closeEvent(event)

# Alias para compatibilidad
SplashScreen = AnimatedSplashScreen

if __name__ == "__main__":
    # Demo de la splash screen
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()
    splash.start_loading()

    # Simular carga
    import time

    for i in range(11):
        time.sleep(0.5)
        app.processEvents()

    splash.finish_loading()
    time.sleep(1)
    splash.close()

    sys.exit()