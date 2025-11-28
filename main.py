from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import sys
import os
import traceback


class ApplicationLoader(QThread):
    """Thread para cargar la aplicación en segundo plano"""

    progress_updated = pyqtSignal(int, str)
    loading_complete = pyqtSignal()
    loading_failed = pyqtSignal(str)

    def run(self):
        """Carga solo los componentes que no requieren Qt"""
        try:
            # Paso 1: Configurar logging (lazy import)
            self.progress_updated.emit(20, "Configurando logging...")
            from src.utils.logging_config import setup_logging

            setup_logging()

            # Paso 2: Inicializar base de datos (lazy import)
            self.progress_updated.emit(60, "Inicializando base de datos...")
            from src.data.database import init_db

            init_db()

            # Paso 3: Finalizar
            self.progress_updated.emit(100, "¡Listo!")
            self.loading_complete.emit()

        except Exception as e:
            error_msg = f"Error durante la inicialización:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            self.loading_failed.emit(error_msg)


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
        try:
            # Importar MainWindow solo cuando se necesita
            from src.gui.main_window import MainWindow

            # Crear la ventana principal en el thread principal
            main_window = MainWindow()
            # Cerrar splash y mostrar ventana principal después de un delay
            QTimer.singleShot(500, finish_loading)

        except Exception as e:
            error_msg = f"Error al crear la ventana principal:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            on_loading_failed(error_msg)

    def on_loading_failed(error_message):
        """Maneja errores durante la carga"""
        splash.close()
        QMessageBox.critical(
            None,
            "Error de Inicialización",
            f"No se pudo iniciar la aplicación.\n\n{error_message}",
            QMessageBox.Ok,
        )
        sys.exit(1)

    def finish_loading():
        try:
            splash.finish(main_window)
            main_window.show()
        except Exception as e:
            error_msg = f"Error al mostrar la ventana:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            QMessageBox.critical(
                None,
                "Error al Mostrar Ventana",
                error_msg,
                QMessageBox.Ok,
            )
            sys.exit(1)

    # Aplicar estilos solo si existe (I/O optimizado)
    def apply_styles():
        try:
            qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf-8") as f:
                    app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Warning: No se pudieron cargar los estilos: {e}")

    apply_styles()

    # Crear y configurar loader
    loader = ApplicationLoader()
    loader.progress_updated.connect(on_progress_updated)
    loader.loading_complete.connect(on_loading_complete)
    loader.loading_failed.connect(on_loading_failed)
    loader.start()

    # Ejecutar aplicación
    sys.exit(app.exec_())
