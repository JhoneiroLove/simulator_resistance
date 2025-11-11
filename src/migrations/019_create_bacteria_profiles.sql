-- Migracion 019: Tabla bacteria_profiles
-- Fecha de creacion: 11 de noviembre de 2025
-- Proposito: Almacenar perfiles bacterianos generados in-silico

-- ============================================
-- TABLA: bacteria_profiles
-- ============================================

CREATE TABLE IF NOT EXISTS bacteria_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organismo TEXT NOT NULL DEFAULT 'Pseudomonas aeruginosa',
    escenario TEXT NOT NULL,           -- 'comunitario' o 'hospitalizado'
    origen_muestra TEXT,                -- 'hemocultivo', 'esputo', 'orina', 'herida', 'cateter'
    antibioticos_previos TEXT,          -- JSON: ['Ciprofloxacino', 'Meropenem']
    genotipo TEXT NOT NULL,             -- JSON: {'gyrA': 'T83I', 'oprD': 'functional', ...}
    mics_calculated TEXT NOT NULL,      -- JSON: {'Meropenem': 64.0, 'Ciprofloxacino': 1.0, ...}
    mutaciones_aplicadas TEXT,          -- JSON: [{'gen': 'gyrA_T83I', 'trigger': 'Ciprofloxacino', ...}]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDICES PARA OPTIMIZACION
-- ============================================

CREATE INDEX IF NOT EXISTS idx_bacteria_profiles_escenario 
ON bacteria_profiles(escenario);

CREATE INDEX IF NOT EXISTS idx_bacteria_profiles_created_at 
ON bacteria_profiles(created_at DESC);

-- ============================================
-- VALIDACION
-- ============================================

-- 1. Verificar estructura de tabla
-- PRAGMA table_info(bacteria_profiles);
-- Debe retornar: 9 columnas

-- 2. Verificar indices creados
-- SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='bacteria_profiles';
-- Debe retornar: 2 indices + 1 automatico (PRIMARY KEY)

-- 3. Insertar perfil de ejemplo (wild-type)
-- INSERT INTO bacteria_profiles (
--     organismo, 
--     escenario, 
--     origen_muestra, 
--     genotipo, 
--     mics_calculated
-- ) VALUES (
--     'Pseudomonas aeruginosa',
--     'comunitario',
--     'hemocultivo',
--     '{"gyrA": "wild-type", "parC": "wild-type", "oprD": "functional"}',
--     '{"Meropenem": 0.5, "Ciprofloxacino": 0.125}'
-- );

-- 4. Consultar perfiles comunitarios
-- SELECT id, escenario, origen_muestra, created_at 
-- FROM bacteria_profiles 
-- WHERE escenario = 'comunitario'
-- ORDER BY created_at DESC;
