import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QStatusBar,
    QApplication,
)
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
        self.resize(1280, 720)

        # Centrar la ventana en la pantalla
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
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
        self.statusBar().showMessage(
            "✅ Simulador AST científico - Versión refactorizada"
        )

    def closeEvent(self, event):
        """Limpiar recursos al cerrar."""
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
