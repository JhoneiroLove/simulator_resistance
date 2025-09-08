BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS simulacion_atributos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulacion_id INTEGER NOT NULL REFERENCES simulaciones(id),
    generacion INTEGER NOT NULL,
    antibiotico_id INTEGER REFERENCES antibioticos(id),
    atributo TEXT NOT NULL,
    valor_promedio REAL NOT NULL,
    desviacion_std REAL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_simulacion_atributos_sim ON simulacion_atributos(simulacion_id);
CREATE INDEX IF NOT EXISTS idx_simulacion_atributos_ab  ON simulacion_atributos(antibiotico_id);
CREATE INDEX IF NOT EXISTS idx_simulacion_atributos_attr ON simulacion_atributos(atributo);

COMMIT;
