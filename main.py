from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import sys
import os

class ApplicationLoader(QThread):
    """Thread para cargar la aplicación en segundo plano"""

    progress_updated = pyqtSignal(int, str)
    loading_complete = pyqtSignal()

    def run(self):
        """Carga solo los componentes que no requieren Qt"""
        # Paso 1: Configurar logging
        self.progress_updated.emit(20, "Configurando logging...")
        from src.utils.logging_config import setup_logging

        setup_logging()

        # Paso 2: Inicializar base de datos
        self.progress_updated.emit(60, "Inicializando base de datos...")
        from src.data.database import init_db

        init_db()

        # Paso 3: Finalizar
        self.progress_updated.emit(100, "¡Listo!")

        self.loading_complete.emit()

if __name__ == "__main__":
    # Crear aplicación
    app = QApplication(sys.argv)

    # Importar splash screen solo cuando se necesita
    from splash_screen import SplashScreen

    # Crear y mostrar splash
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    # Variables para gestionar la carga
    main_window = None

    def on_progress_updated(progress, message):
        splash.update_progress(progress, message)
        app.processEvents()

    def on_loading_complete():
        global main_window
        # Importar MainWindow solo cuando se necesita
        from src.gui.main_window import MainWindow

        # Crear la ventana principal en el thread principal
        main_window = MainWindow()
        # Cerrar splash y mostrar ventana principal después de un delay
        QTimer.singleShot(500, finish_loading)

    def finish_loading():
        splash.finish(main_window)
        main_window.show()

    # Aplicar estilos después de que todo esté cargado
    def apply_styles():
        qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())

    # Aplicar estilos cuando se complete la carga
    apply_styles()

    # Crear y configurar loader
    loader = ApplicationLoader()
    loader.progress_updated.connect(on_progress_updated)
    loader.loading_complete.connect(on_loading_complete)
    loader.start()

    # Ejecutar aplicación
    sys.exit(app.exec_())