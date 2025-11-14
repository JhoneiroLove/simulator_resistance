PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- ============================================================================
-- ESQUEMA BASE - Solo tablas científicas AST
-- ============================================================================
-- Migración refactorizada: eliminadas tablas legacy
-- Tablas eliminadas: genes, antibioticos, simulaciones, simulacion_genes,
--                    recomendaciones, simulacion_atributos, reportes_simulacion,
--                    guests, sitios_infeccion
-- Solo se mantiene db_version para control de migraciones
-- Las tablas científicas se crean en migraciones 014-018
-- ============================================================================

-- Eliminar tablas legacy si existen
DROP TABLE IF EXISTS simulacion_genes;
DROP TABLE IF EXISTS simulacion_atributos;
DROP TABLE IF EXISTS simulaciones;
DROP TABLE IF EXISTS reportes_simulacion;
DROP TABLE IF EXISTS recomendaciones;
DROP TABLE IF EXISTS antibioticos;
DROP TABLE IF EXISTS genes;
DROP TABLE IF EXISTS guests;
DROP TABLE IF EXISTS sitios_infeccion;

-- Tabla para el control de versiones de la base de datos
CREATE TABLE IF NOT EXISTS db_version (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Asegura que solo haya una fila
    version_num INTEGER NOT NULL DEFAULT 0
);

-- Inicializa la versión si la tabla está vacía
INSERT OR IGNORE INTO db_version (id, version_num) VALUES (1, 0);

COMMIT;
PRAGMA foreign_keys = ON;
