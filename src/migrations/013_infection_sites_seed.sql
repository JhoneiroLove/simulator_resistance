BEGIN TRANSACTION;

-- Limpiar datos existentes de sitios de infección (solo para desarrollo/pruebas)
DELETE FROM sitios_infeccion;

-- Insertar 5 sitios de infección para pruebas
INSERT INTO sitios_infeccion (nombre, ph, capacidad_carga, perfusion_sanguinea) VALUES
    ('pulmon', 7.4, 1000000.0, 0.85),
    ('sangre', 7.35, 10000.0, 0.95),
    ('orina', 6.0, 500000.0, 0.70),
    ('herida_superficial', 7.2, 750000.0, 0.60),
    ('liquido_cefalorraquideo', 7.3, 5000.0, 0.80);

-- Actualizar la versión de la base de datos
UPDATE db_version SET version_num = 13 WHERE id = 1;

COMMIT;