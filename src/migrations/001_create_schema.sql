PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS genes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    peso_resistencia REAL NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS antibioticos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    concentracion_minima REAL NOT NULL,
    concentracion_maxima REAL NOT NULL,
    tipo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS simulaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    antibiotico_id INTEGER NOT NULL REFERENCES antibioticos(id),
    concentracion REAL NOT NULL,
    resistencia_predicha REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS simulacion_genes (
    simulacion_id INTEGER NOT NULL REFERENCES simulaciones(id),
    gen_id INTEGER NOT NULL REFERENCES genes(id),
    PRIMARY KEY (simulacion_id, gen_id)
);

-- Índices para acelerar consultas
CREATE INDEX IF NOT EXISTS idx_sim_antibio ON simulaciones(antibiotico_id);
CREATE INDEX IF NOT EXISTS idx_simgen_gen ON simulacion_genes(gen_id);

-- Tabla para el control de versiones de la base de datos
CREATE TABLE IF NOT EXISTS db_version (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Asegura que solo haya una fila
    version_num INTEGER NOT NULL DEFAULT 0
);

-- Inicializa la versión si la tabla está vacía
INSERT OR IGNORE INTO db_version (id, version_num) VALUES (1, 0);

COMMIT;
PRAGMA foreign_keys = ON;