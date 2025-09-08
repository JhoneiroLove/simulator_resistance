BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS metricas_generacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulacion_id INTEGER NOT NULL REFERENCES simulaciones(id),
    generacion INTEGER NOT NULL,
    nombre_indicador TEXT NOT NULL,
    valor REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_metricas_generacion_sim ON metricas_generacion(simulacion_id);
CREATE INDEX IF NOT EXISTS idx_metricas_generacion_gen ON metricas_generacion(generacion);
CREATE INDEX IF NOT EXISTS idx_metricas_generacion_indicador ON metricas_generacion(nombre_indicador);

COMMIT;