-- ============================================================================
-- Migración 017: Seed de antibiotic_classes (Científico)
-- ============================================================================
-- Fecha: 14 de noviembre de 2025 (Refactorizado)
-- Fuente: familias_antibioticas_y_especies_base_utf8_bom.csv + breakpoints
-- Total: 15 clases antibióticas

-- CAMBIOS vs versión legacy:
-- - Tabla antibioticos ELIMINADA (era legacy)
-- - Ahora usa antibiotic_classes (mapeo antibiótico→clase)
-- - Datos extraídos de breakpoints EUCAST/CLSI
-- ============================================================================

BEGIN TRANSACTION;

-- ============================================
-- CREAR TABLA: antibiotic_classes
-- ============================================

CREATE TABLE IF NOT EXISTS antibiotic_classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    antibiotico TEXT NOT NULL UNIQUE,  -- Nombre del antibiótico
    clase TEXT NOT NULL                -- Clase/familia antibiótica
);

-- ============================================
-- SEED: Clases antibióticas (15 registros)
-- ============================================

INSERT OR REPLACE INTO antibiotic_classes (antibiotico, clase) VALUES
('Meropenem', 'carbapenemicos'),
('Imipenem', 'carbapenemicos'),
('Doripenem', 'carbapenemicos'),
('Cefepime', 'cef_4G_cefepime'),
('Ceftazidima', 'cef_3G_ceftazidima'),
('Amikacina', 'aminoglucosidos'),
('Tobramicina', 'aminoglucosidos'),
('Gentamicina', 'aminoglucosidos'),
('Ciprofloxacino', 'fluoroquinolonas'),
('Levofloxacino', 'fluoroquinolonas'),
('Colistina', 'polimixinas'),
('Piperacilina/Tazobactam', 'penicilina_inhibidor'),
('Ceftazidima/Avibactam', 'cef_inhibidor'),
('Ceftolozano/Tazobactam', 'cef_inhibidor'),
('Cefiderocol', 'sideroforo_cefiderocol'),
('Aztreonam', 'monobactam_aztreonam');

COMMIT;

-- ============================================
-- VALIDACIÓN
-- ============================================

-- 1. Verificar total de clases
-- SELECT COUNT(*) FROM antibiotic_classes;
-- Debe retornar: 15

-- 2. Verificar familias únicas
-- SELECT DISTINCT clase FROM antibiotic_classes ORDER BY clase;
-- Debe retornar: 9 familias

-- 3. Listar todas las clases
-- SELECT antibiotico, clase FROM antibiotic_classes ORDER BY clase, antibiotico;
