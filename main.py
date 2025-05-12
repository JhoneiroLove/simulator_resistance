from src.data.database import init_db
from src.gui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    # 1) Inicializa y seedea la BD
    init_db()

    # 2) Arranca la aplicación
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())