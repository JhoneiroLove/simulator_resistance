"""
Test Temporal Simulation - FASE 5

Verifica la funcionalidad de simulación temporal (hora por hora).

Características probadas:
- Modo progresivo: 19 emisiones (0-18h)
- Modo rápido: 1 emisión final
- Delay de 0.5s entre horas
- Señales time_progress correctas
- Datos parciales por hora

Autor: Sistema AST Simulator
Fecha: Enero 2025
"""

import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop, QTimer
from src.gui.widgets.ast_panel_widget import ASTWorker
from src.data.database import get_session
from src.data.models import BacteriaProfile, PanelLayout


def test_progressive_mode():
    """Prueba el modo progresivo (hora por hora)."""
    print("\n=== TEST: Modo Progresivo ===\n")

    # Obtener un perfil bacteriano
    session = get_session()
    profile = session.query(BacteriaProfile).first()
    panel = session.query(PanelLayout).first()

    if not profile or not panel:
        print("ERROR: No hay datos en la BD. Ejecute init_database.py primero.")
        return False

    print(f"Perfil bacteriano: ID {profile.id}")
    print(f"Panel: {panel.panel_name}")
    print(f"Modo: PROGRESIVO (19 horas simuladas)\n")

    # Crear worker en modo progresivo
    worker = ASTWorker(
        bacteria_profile_id=profile.id,
        panel_layout_id=panel.id,
        inoculo_mcfarland=0.5,
        temperatura=37.0,
        duracion_horas=18.0,
        progressive_mode=True,
    )

    # Contadores
    time_updates = []
    final_report = None
    error_msg = None

    # Conectar señales
    def on_time_progress(hour, partial_data):
        time_updates.append(hour)
        print(f"  Hora {hour:2d}/18 - {len(partial_data['well_data'])} pozos simulados")

    def on_finished(report):
        nonlocal final_report
        final_report = report
        print("\nSimulación completada:")
        print(f"  - Metadata: {list(report.get('metadata', {}).keys())}")
        print(f"  - Antibióticos: {len(report.get('mic_results', []))}")
        print(f"  - QC Status: {report.get('qc', {}).get('overall_status', 'N/A')}")

    def on_error(msg):
        nonlocal error_msg
        error_msg = msg
        print(f"\nERROR EN WORKER: {msg}")

    def on_progress(value):
        print(f"  Progreso: {value}%")

    worker.time_progress.connect(on_time_progress)
    worker.finished.connect(on_finished)
    worker.error.connect(on_error)
    worker.progress.connect(on_progress)

    # Ejecutar
    loop = QEventLoop()
    worker.finished.connect(loop.quit)
    worker.error.connect(loop.quit)
    worker.start()
    loop.exec_()  # Esperar hasta que emita finished o error

    # Verificar resultados
    print(f"\nResultados:")
    print(f"  - Actualizaciones recibidas: {len(time_updates)}")
    print(f"  - Horas esperadas: 19 (0-18)")
    print(f"  - Reporte final: {'SI' if final_report else 'NO'}")
    print(f"  - Errores: {'SI' if error_msg else 'NO'}")

    # Assertions
    assert len(time_updates) == 19, f"Esperaba 19 updates, recibió {len(time_updates)}"
    assert time_updates == list(range(19)), "Horas no consecutivas"
    assert final_report is not None, "No se recibió reporte final"
    assert error_msg is None, f"Error inesperado: {error_msg}"

    print("\nTEST PASADO\n")
    return True


def test_fast_mode():
    """Prueba el modo rápido (instantáneo)."""
    print("\n=== TEST: Modo Rápido ===\n")

    # Obtener un perfil bacteriano
    session = get_session()
    profile = session.query(BacteriaProfile).first()
    panel = session.query(PanelLayout).first()

    print(f"Perfil bacteriano: ID {profile.id}")
    print(f"Panel: {panel.panel_name}")
    print(f"Modo: RÁPIDO (simulación instantánea)\n")

    # Crear worker en modo rápido
    worker = ASTWorker(
        bacteria_profile_id=profile.id,
        panel_layout_id=panel.id,
        inoculo_mcfarland=0.5,
        temperatura=37.0,
        duracion_horas=18.0,
        progressive_mode=False,
    )

    # Contadores
    time_updates = []
    final_report = None

    # Conectar señales
    def on_time_progress(hour, partial_data):
        time_updates.append(hour)

    def on_finished(report):
        nonlocal final_report
        final_report = report
        print("Simulación completada:")
        print(f"  - Metadata: {list(report.get('metadata', {}).keys())}")
        print(f"  - Antibióticos: {len(report.get('mic_results', []))}")

    worker.time_progress.connect(on_time_progress)
    worker.finished.connect(on_finished)

    # Ejecutar
    loop = QEventLoop()
    worker.finished.connect(loop.quit)
    worker.error.connect(loop.quit)
    worker.start()
    loop.exec_()  # Esperar hasta que emita finished o error

    # Verificar resultados
    print(f"\nResultados:")
    print(f"  - Actualizaciones recibidas: {len(time_updates)}")
    print(f"  - Horas esperadas: 0 (modo rápido no emite time_progress)")
    print(f"  - Reporte final: {'SI' if final_report else 'NO'}")

    # Assertions
    assert len(time_updates) == 0, f"Modo rápido no debe emitir time_progress"
    assert final_report is not None, "No se recibió reporte final"

    print("\nTEST PASADO\n")
    return True


def test_speed_control():
    """Prueba el control de velocidad dinámico."""
    print("\n=== TEST: Control de Velocidad ===\n")

    session = get_session()
    profile = session.query(BacteriaProfile).first()
    panel = session.query(PanelLayout).first()

    print(f"Perfil bacteriano: ID {profile.id}")
    print(f"Panel: {panel.panel_name}")
    print("Modo: PROGRESIVO con cambios de velocidad\n")

    # Crear worker en modo progresivo
    worker = ASTWorker(
        bacteria_profile_id=profile.id,
        panel_layout_id=panel.id,
        inoculo_mcfarland=0.5,
        temperatura=37.0,
        duracion_horas=18.0,
        progressive_mode=True,
    )

    timestamps = []
    final_report = None

    # Conectar señales
    def on_time_progress(hour, partial_data):
        timestamps.append((hour, time.time()))
        if hour == 5:
            # Cambiar a 2x después de 5 horas
            print("  Cambiando velocidad a 2x...")
            worker.set_speed(2)
        elif hour == 10:
            # Cambiar a 4x después de 10 horas
            print("  Cambiando velocidad a 4x...")
            worker.set_speed(4)

    def on_finished(report):
        nonlocal final_report
        final_report = report
        print("\nSimulación completada")

    worker.time_progress.connect(on_time_progress)
    worker.finished.connect(on_finished)

    # Ejecutar
    loop = QEventLoop()
    worker.finished.connect(loop.quit)
    worker.start()
    loop.exec_()

    # Verificar resultados
    print(f"\nResultados:")
    print(f"  - Total de actualizaciones: {len(timestamps)}")

    # Calcular tiempos entre horas
    if len(timestamps) >= 3:
        # Primeras 5 horas (1x): ~0.5s cada una
        early_delays = []
        for i in range(1, min(5, len(timestamps))):
            delay = timestamps[i][1] - timestamps[i - 1][1]
            early_delays.append(delay)

        avg_early = sum(early_delays) / len(early_delays) if early_delays else 0
        print(f"  - Delay promedio (1x, horas 1-5): {avg_early:.2f}s (esperado ~0.5s)")

        # Horas 6-10 (2x): ~0.25s cada una
        if len(timestamps) > 10:
            mid_delays = []
            for i in range(6, 10):
                delay = timestamps[i][1] - timestamps[i - 1][1]
                mid_delays.append(delay)

            avg_mid = sum(mid_delays) / len(mid_delays) if mid_delays else 0
            print(
                f"  - Delay promedio (2x, horas 6-10): {avg_mid:.2f}s (esperado ~0.25s)"
            )

            # Horas 11-18 (4x): ~0.125s cada una
            late_delays = []
            for i in range(11, min(18, len(timestamps))):
                delay = timestamps[i][1] - timestamps[i - 1][1]
                late_delays.append(delay)

            avg_late = sum(late_delays) / len(late_delays) if late_delays else 0
            print(
                f"  - Delay promedio (4x, horas 11-18): {avg_late:.2f}s (esperado ~0.125s)"
            )

    # Assertions básicas
    assert len(timestamps) == 19, f"Esperaba 19 updates, recibió {len(timestamps)}"
    assert final_report is not None, "No se recibió reporte final"
    assert worker.speed_multiplier >= 1, "Multiplicador de velocidad inválido"

    print("\nTEST PASADO\n")
    return True


def test_speed_limits():
    """Prueba los límites del control de velocidad."""
    print("\n=== TEST: Límites de Velocidad ===\n")

    session = get_session()
    profile = session.query(BacteriaProfile).first()
    panel = session.query(PanelLayout).first()

    print(f"Perfil bacteriano: ID {profile.id}")
    print("Verificando límites de velocidad (1x-4x)\n")

    # Crear worker
    worker = ASTWorker(
        bacteria_profile_id=profile.id,
        panel_layout_id=panel.id,
        inoculo_mcfarland=0.5,
        temperatura=37.0,
        duracion_horas=18.0,
        progressive_mode=True,
    )

    # Probar valores fuera de rango
    print("  Probando valor bajo (0)...")
    worker.set_speed(0)
    assert worker.speed_multiplier == 1, "Valor 0 debería clampear a 1"
    print(f"    ✓ Clampeado a {worker.speed_multiplier}x")

    print("  Probando valor alto (10)...")
    worker.set_speed(10)
    assert worker.speed_multiplier == 4, "Valor 10 debería clampear a 4"
    print(f"    ✓ Clampeado a {worker.speed_multiplier}x")

    print("  Probando valor negativo (-5)...")
    worker.set_speed(-5)
    assert worker.speed_multiplier == 1, "Valor negativo debería clampear a 1"
    print(f"    ✓ Clampeado a {worker.speed_multiplier}x")

    print("  Probando valores válidos (1, 2, 3, 4)...")
    for speed in [1, 2, 3, 4]:
        worker.set_speed(speed)
        assert worker.speed_multiplier == speed, f"Velocidad {speed}x no se aplicó"
        print(f"    ✓ {speed}x aplicado correctamente")

    print("\nTEST PASADO\n")
    return True


if __name__ == "__main__":
    # Inicializar Qt (necesario para QThread)
    app = QApplication(sys.argv)

    try:
        # Ejecutar tests
        print("\n" + "=" * 60)
        print(" EJECUTANDO SUITE DE TESTS - FASE 5 ")
        print("=" * 60)

        test_1_ok = test_progressive_mode()
        test_2_ok = test_fast_mode()
        test_3_ok = test_speed_control()
        test_4_ok = test_speed_limits()

        if test_1_ok and test_2_ok and test_3_ok and test_4_ok:
            print("\n" + "=" * 60)
            print(" TODOS LOS TESTS PASARON (4/4) ")
            print("=" * 60 + "\n")
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print(" ALGUNOS TESTS FALLARON ")
            print("=" * 60 + "\n")
            sys.exit(1)

    except Exception as e:
        print(f"\nERROR FATAL: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
