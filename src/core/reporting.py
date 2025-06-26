import numpy as np
import psutil
import json
from src.data.database import get_session
from src.data.models import ReporteSimulacion, MetricaGeneracion

def compute_convergence_slopes(avg_hist, window_size=10):
    """
    Devuelve una lista del mismo tamaño que avg_hist, donde cada valor
    es el slope (pendiente absoluta) en ventana de 'window_size' generaciones.
    Para las primeras generaciones (donde no hay suficientes datos), retorna 0.0.
    """
    slopes = []
    for i in range(len(avg_hist)):
        if i < window_size - 1:
            slopes.append(0.0)
        else:
            window = avg_hist[i - window_size + 1 : i + 1]
            slope = np.polyfit(range(window_size), window, 1)[0]
            slopes.append(abs(slope))
    return slopes

def save_simulation_report(ga, saved_params):
    """
    Guarda el reporte principal de la simulación, con los parámetros de entrada como JSON.
    Devuelve el ID del reporte creado.
    """
    parametros_json = json.dumps(saved_params, ensure_ascii=False)
    session = get_session()

    reporte_existente = (
        session.query(ReporteSimulacion)
        .filter_by(simulacion_id=ga.current_simulation_id)
        .first()
    )
    if reporte_existente:
        session.close()
        return reporte_existente.id

    reporte = ReporteSimulacion(
        simulacion_id=ga.current_simulation_id,
        generaciones_totales=saved_params.get("generations", 0),
        parametros_input=parametros_json,
    )
    session.add(reporte)
    session.commit()
    reporte_id = reporte.id
    session.close()
    return reporte_id

def save_generation_metrics(ga, simulacion_id, window_size=10):
    """
    Guarda los valores de los indicadores por generación para una simulación.
    Incluye métricas evolutivas y de costo computacional (CPU/RAM).
    Registra la tasa de convergencia como el slope absoluto en ventana móvil.
    """
    process = psutil.Process()
    session = get_session()
    num_generaciones = len(ga.avg_hist)

    # Calcula la tasa de convergencia como pendiente en ventana móvil
    convergence_hist = compute_convergence_slopes(ga.avg_hist, window_size=window_size)

    for gen in range(num_generaciones):
        valores = {
            "avg_fitness": ga.avg_hist[gen],
            "best_fitness": ga.best_hist[gen],
            "diversidad_genetica": ga.div_hist[gen],
            "tasa_mutacion": ga.mut_hist[gen],
            # Tasa de convergencia - slope de ventana móvil:
            "tasa_convergencia": convergence_hist[gen],
            "cpu_time_sec": process.cpu_times().user,  # Tiempo de CPU total hasta ese punto
            "ram_mb": process.memory_info().rss / (1024**2),  # RAM usada (MB)
        }
        for nombre, valor in valores.items():
            metrica = MetricaGeneracion(
                simulacion_id=simulacion_id,
                generacion=gen + 1,
                nombre_indicador=nombre,
                valor=float(valor),
            )
            session.add(metrica)
    session.commit()
    session.close()