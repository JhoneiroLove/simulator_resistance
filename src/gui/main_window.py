import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QStatusBar,
    QApplication,
)
from PyQt5.QtCore import Qt
from src.gui.workflows.ast_workflow import ASTWorkflow
from PyQt5.QtGui import QIcon


def get_app_icon():
    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.abspath(os.path.dirname(__file__))
    icon_path = os.path.join(base_dir, "simulador_evolutivo.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(base_dir, "..", "..", "simulador_evolutivo.ico")
    return QIcon(icon_path)


class MainWindow(QMainWindow):
    """
    Ventana principal del Simulador Evolutivo de Resistencia Bacteriana.

    VERSIÓN REFACTORIZADA - Solo contiene el workflow AST científico.
    El código legacy (tabs 1-3 con simulación GA manual) fue deprecado.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRB - AST Simulator")

        # Deshabilitar botón de maximizar/pantalla completa
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        # Tamaño inicial más amplio para mejor legibilidad
        screen = QApplication.primaryScreen().availableGeometry()

        # Ancho: 1280px para mostrar todo el contenido sin comprimir
        # Alto: 90% de la pantalla para comodidad
        initial_width = min(1280, int(screen.width() * 0.8))
        initial_height = int(screen.height() * 0.90)
        self.resize(initial_width, initial_height)

        # Establecer tamaño mínimo para que todo se vea correctamente
        self.setMinimumSize(1100, 750)

        # Centrar
        qr = self.frameGeometry()
        cp = screen.center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.setWindowIcon(get_app_icon())

        # ---- Tab AST (único workflow científico) ----
        self.ast_tab = ASTWorkflow()

        # ---- Pestañas ----
        self.tabs = QTabWidget()
        self.tabs.addTab(self.ast_tab, "🧬 AST Antibiograma")
        self.setCentralWidget(self.tabs)

        # Status bar con mensaje inicial
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(
            "✓ Aplicación lista | Navegación: Ctrl+Tab (siguiente) | Ayuda: F1", 5000
        )

    def closeEvent(self, event):
        """Limpiar recursos al cerrar."""
        event.accept()

    def keyPressEvent(self, event):
        """Manejar atajos de teclado globales."""
        # F1: Mostrar ayuda rápida
        if event.key() == Qt.Key_F1:
            self.status_bar.showMessage(
                "Atajos: Ctrl+Tab (siguiente tab) | Shift+Ctrl+Tab (tab anterior) | "
                "Ctrl+N (nueva simulación) | ESC (cancelar)",
                8000,
            )
        # Ctrl+N: Nueva simulación (reiniciar workflow)
        elif event.key() == Qt.Key_N and event.modifiers() == Qt.ControlModifier:
            if hasattr(self.ast_tab, "_restart_workflow"):
                self.ast_tab._restart_workflow()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
