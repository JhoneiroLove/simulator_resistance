-- Se crean las tablas para el registro de reportes y sus métricas
-- por cada simulación ejecutada.

-- Tabla principal para el encabezado del reporte
CREATE TABLE IF NOT EXISTS reportes_simulacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulacion_id INTEGER NOT NULL,
    fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generaciones_totales INTEGER NOT NULL,
    parametros_input TEXT NOT NULL, -- Almacenado como un string JSON
    FOREIGN KEY (simulacion_id) REFERENCES simulaciones(id)
);

-- Tabla para las métricas detalladas de cada reporte
CREATE TABLE IF NOT EXISTS metricas_reporte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reporte_id INTEGER NOT NULL,
    nombre_indicador TEXT NOT NULL,
    valor_promedio REAL NOT NULL,
    desviacion_estandar REAL,
    FOREIGN KEY (reporte_id) REFERENCES reportes_simulacion(id)
);