import json
from src.data.database import get_session
from src.data.models import ReporteSimulacion


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
