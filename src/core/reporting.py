import json
import numpy as np
import time
from src.data.database import get_session
from src.data.models import ReporteSimulacion, MetricaReporte

def save_simulation_report(ga, saved_params, sim_start_time):
    """
    Registra las métricas globales de la simulación ejecutada.
    ga: instancia de GeneticAlgorithm (con históricos).
    saved_params: dict con parámetros de simulación y contexto.
    sim_start_time: timestamp de inicio de simulación.
    """
    # 1. Serializar parámetros de entrada
    parametros_json = json.dumps(saved_params)

    # 2. Costo computacional
    tiempo_total = time.time() - sim_start_time

    # 3. Crear registro de reporte
    session = get_session()
    reporte = ReporteSimulacion(
        simulacion_id=ga.current_simulation_id,
        generaciones_totales=saved_params["generations"],
        parametros_input=parametros_json,
    )
    session.add(reporte)
    session.commit()
    reporte_id = reporte.id

    # 4. Métricas principales
    metricas = {
        "best_fitness": ga.best_hist,
        "avg_fitness": ga.avg_hist,
        "diversidad_genetica": ga.div_hist,
        "tasa_mutacion": ga.mut_hist,
        "tasa_convergencia": [
            abs(y2 - y1) for y1, y2 in zip(ga.avg_hist[:-1], ga.avg_hist[1:])
        ],
    }

    for nombre, valores in metricas.items():
        if not valores:
            continue
        media = float(np.mean(valores))
        std = float(np.std(valores))
        session.add(
            MetricaReporte(
                reporte_id=reporte_id,
                nombre_indicador=nombre,
                valor_promedio=media,
                desviacion_estandar=std,
            )
        )

    # 5. Costo computacional
    session.add(
        MetricaReporte(
            reporte_id=reporte_id,
            nombre_indicador="costo_computacional_segundos",
            valor_promedio=tiempo_total,
            desviacion_estandar=0.0,
        )
    )

    session.commit()
    session.close()
