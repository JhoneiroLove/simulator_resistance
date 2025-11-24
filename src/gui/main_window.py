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

        # Tamaño inicial más compacto ajustado al contenido centrado
        screen = QApplication.primaryScreen().availableGeometry()

        # Ancho: 1100px (contenido 900px + márgenes + scrollbar)
        # Alto: 85% de la pantalla para mantener altura cómoda
        initial_width = min(1100, int(screen.width() * 0.7))
        initial_height = int(screen.height() * 0.85)
        self.resize(initial_width, initial_height)

        # Establecer tamaño mínimo más compacto
        self.setMinimumSize(950, 700)

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
        self.setStatusBar(QStatusBar())

    def closeEvent(self, event):
        """Limpiar recursos al cerrar."""
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
