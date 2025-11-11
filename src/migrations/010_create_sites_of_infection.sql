BEGIN TRANSACTION;

-- Crear tabla de sitios de infección
CREATE TABLE IF NOT EXISTS sitios_infeccion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    ph REAL NOT NULL,
    capacidad_carga REAL NOT NULL
);

-- Insertar sitios de infección comunes para P. aeruginosa
INSERT INTO sitios_infeccion (nombre, ph, capacidad_carga) VALUES
    ('Tracto respiratorio inferior', 7.4, 1000000.0),
    ('Tracto urinario', 6.0, 500000.0),
    ('Torrente sanguíneo', 7.35, 10000.0),
    ('Heridas y quemaduras', 7.2, 750000.0),
    ('Oído externo', 6.5, 100000.0),
    ('Córnea', 7.4, 50000.0),
    ('Hueso y articulaciones', 7.4, 200000.0),
    ('Sistema nervioso central', 7.3, 5000.0),
    ('Tracto gastrointestinal', 5.5, 1500000.0),
    ('Piel', 5.5, 300000.0);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_sitios_infeccion_nombre ON sitios_infeccion(nombre);
CREATE INDEX IF NOT EXISTS idx_sitios_infeccion_ph ON sitios_infeccion(ph);

-- Actualizar la versión de la base de datos
UPDATE db_version SET version_num = 11 WHERE id = 1;

COMMIT;