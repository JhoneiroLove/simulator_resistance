BEGIN TRANSACTION;

-- Agregar campo huesped_id a la tabla simulaciones
ALTER TABLE simulaciones ADD COLUMN huesped_id INTEGER REFERENCES guests(id);

-- Crear índice para optimizar consultas por huésped
CREATE INDEX IF NOT EXISTS idx_simulaciones_huesped ON simulaciones(huesped_id);

-- Actualizar la versión de la base de datos
UPDATE db_version SET version_num = 14 WHERE id = 1;

COMMIT;