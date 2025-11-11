BEGIN TRANSACTION;

-- Agregar campo de perfusión sanguínea a la tabla sitios_infeccion
ALTER TABLE sitios_infeccion ADD COLUMN perfusion_sanguinea REAL NOT NULL DEFAULT 0.5 
    CHECK (perfusion_sanguinea >= 0.0 AND perfusion_sanguinea <= 1.0);

-- Actualizar valores de perfusión para cada sitio de infección
-- 1.0 = perfusión excelente, 0.0 = perfusión nula
UPDATE sitios_infeccion SET perfusion_sanguinea = 0.95 WHERE nombre = 'Torrente sanguíneo';
UPDATE sitios_infeccion SET perfusion_sanguinea = 0.85 WHERE nombre = 'Tracto respiratorio inferior';
UPDATE sitios_infeccion SET perfusion_sanguinea = 0.70 WHERE nombre = 'Tracto urinario';
UPDATE sitios_infeccion SET perfusion_sanguinea = 0.60 WHERE nombre = 'Heridas y quemaduras';
UPDATE sitios_infeccion SET perfusion_sanguinea = 0.75 WHERE nombre = 'Oído externo';
UPDATE sitios_infeccion SET perfusion_sanguinea = 0.50 WHERE nombre = 'Córnea';
UPDATE sitios_infeccion SET perfusion_sanguinea = 0.40 WHERE nombre = 'Hueso y articulaciones';
UPDATE sitios_infeccion SET perfusion_sanguinea = 0.80 WHERE nombre = 'Sistema nervioso central';
UPDATE sitios_infeccion SET perfusion_sanguinea = 0.90 WHERE nombre = 'Tracto gastrointestinal';
UPDATE sitios_infeccion SET perfusion_sanguinea = 0.65 WHERE nombre = 'Piel';

-- Crear índice para consultas por perfusión
CREATE INDEX IF NOT EXISTS idx_sitios_infeccion_perfusion ON sitios_infeccion(perfusion_sanguinea);

-- Actualizar la versión de la base de datos
UPDATE db_version SET version_num = 12 WHERE id = 1;

COMMIT;