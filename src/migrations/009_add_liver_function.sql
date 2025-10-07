BEGIN TRANSACTION;

-- Agregar campos de función hepática a la tabla guests
ALTER TABLE guests ADD COLUMN alt REAL; -- Alanina aminotransferasa (U/L)
ALTER TABLE guests ADD COLUMN ast REAL; -- Aspartato aminotransferasa (U/L)
ALTER TABLE guests ADD COLUMN bilirrubina_total REAL; -- Bilirrubina total (mg/dL)

-- Crear índice compuesto para consultas de función hepática
CREATE INDEX IF NOT EXISTS idx_guests_liver_function ON guests(alt, ast, bilirrubina_total);

-- Actualizar la versión de la base de datos
UPDATE db_version SET version_num = 9 WHERE id = 1;

COMMIT;