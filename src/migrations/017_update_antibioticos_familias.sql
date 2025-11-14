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
('Meropenem', 'Carbapenémico'),
('Imipenem', 'Carbapenémico'),
('Cefepime', 'Cefalosporina (4ta gen)'),
('Ceftazidima', 'Cefalosporina (3ra gen)'),
('Amikacina', 'Aminoglucósido'),
('Tobramicina', 'Aminoglucósido'),
('Gentamicina', 'Aminoglucósido'),
('Ciprofloxacino', 'Fluoroquinolona'),
('Levofloxacino', 'Fluoroquinolona'),
('Colistina', 'Polimixina'),
('Piperacilina/Tazobactam', 'β-lactámico + inhibidor β-lactamasa'),
('Ceftazidima/Avibactam', 'Cefalosporina + inhibidor β-lactamasa'),
('Ceftolozano/Tazobactam', 'Cefalosporina + inhibidor β-lactamasa'),
('Cefiderocol', 'Cefalosporina sideróforo'),
('Aztreonam', 'Monobactámico');

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
