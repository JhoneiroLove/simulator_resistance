BEGIN TRANSACTION;

-- Agregar campo de estado inmune a la tabla guests
ALTER TABLE guests ADD COLUMN estado_inmune TEXT NOT NULL DEFAULT 'normal' 
    CHECK (estado_inmune IN ('normal', 'inmunodeprimido', 'inmunodeprimido_severo'));

-- Crear índice para consultas por estado inmune
CREATE INDEX IF NOT EXISTS idx_guests_immune_status ON guests(estado_inmune);

-- Actualizar la versión de la base de datos
UPDATE db_version SET version_num = 10 WHERE id = 1;

COMMIT;