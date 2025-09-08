CREATE TABLE IF NOT EXISTS reportes_simulacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulacion_id INTEGER NOT NULL,
    fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generaciones_totales INTEGER NOT NULL,
    parametros_input TEXT NOT NULL, -- Almacenado como un string JSON
    FOREIGN KEY (simulacion_id) REFERENCES simulaciones(id)
);