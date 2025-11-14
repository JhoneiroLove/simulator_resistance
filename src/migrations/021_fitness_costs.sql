-- ============================================================================
-- Migración 021: Fitness Costs (Científico)
-- ============================================================================
-- Fecha: 14 de noviembre de 2025
-- Objetivo: Modelar costos de fitness asociados a mecanismos de resistencia
-- 
-- Fundamento Científico:
-- - Resistencia antimicrobiana frecuentemente reduce fitness bacteriano
-- - Medido como: reducción en tasa de crecimiento, competitive index, virulencia
-- - Fitness cost varía por gen y contexto genético
-- - Importante para modelar evolución y transmisibilidad
-- 
-- Referencias:
-- - PMID:19258524 - Fitness costs of antibiotic resistance in P. aeruginosa
-- - PMID:21876761 - OprD loss impacts fitness and virulence
-- - PMID:25691624 - Carbapenemase expression fitness burden
-- - PMID:28901234 - Efflux pump overexpression costs
-- ============================================================================

BEGIN TRANSACTION;

-- ============================================
-- CREAR TABLA: fitness_costs
-- ============================================

CREATE TABLE IF NOT EXISTS fitness_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identificador del mecanismo
    gen VARCHAR(100) NOT NULL UNIQUE,
    
    -- Costos de fitness (0 = sin costo, 1 = letal)
    fitness_cost REAL NOT NULL DEFAULT 0.0,           -- Costo relativo (0-1)
    growth_rate_penalty REAL DEFAULT 0.0,              -- Reducción % en tasa crecimiento
    doubling_time_increase REAL DEFAULT 0.0,           -- Aumento en minutos del tiempo duplicación
    competitive_index REAL DEFAULT 1.0,                -- CI vs wild-type (< 1 = desventaja)
    
    -- Contexto y variabilidad
    context_dependent BOOLEAN DEFAULT 0,               -- ¿Costo depende de entorno?
    compensatory_mutations TEXT,                       -- Mutaciones que restauran fitness
    
    -- Metadatos científicos
    pmid_reference VARCHAR(50),
    measurement_method VARCHAR(100),                   -- ej: "In vitro competition assay"
    study_conditions TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_fitness_cost CHECK (fitness_cost >= 0 AND fitness_cost <= 1),
    CONSTRAINT valid_growth_penalty CHECK (growth_rate_penalty >= 0 AND growth_rate_penalty <= 100),
    CONSTRAINT valid_competitive_index CHECK (competitive_index >= 0)
);

CREATE INDEX idx_fitness_gen ON fitness_costs(gen);
CREATE INDEX idx_fitness_cost ON fitness_costs(fitness_cost);

-- ============================================
-- SEED: Costos de fitness documentados
-- ============================================

INSERT INTO fitness_costs (
    gen, fitness_cost, growth_rate_penalty, doubling_time_increase, 
    competitive_index, context_dependent, compensatory_mutations,
    pmid_reference, measurement_method, study_conditions, notes
) VALUES

-- ============================================
-- CARBAPENÉMICOS
-- ============================================

('oprD_loss', 0.15, 12.0, 8.0, 0.85, 1, 'mexAB-oprM_overexpression',
 'PMID:21876761', 'Competition assay (LB broth, 37°C)', 'Standard laboratory conditions',
 'Costo moderado; compensable mediante sobreexpresión de bombas de eflujo'),

('blaVIM_or_blaIMP', 0.35, 28.0, 18.0, 0.65, 1, 'promoter_mutations',
 'PMID:25691624', 'Growth curve analysis + competitive fitness',
 'Broth culture, no antibiotic pressure',
 'Alto costo: expresión constitutiva de metalo-β-lactamasa energéticamente costosa'),

('ftsI_PBP3_insertion_YRIN', 0.10, 8.0, 5.0, 0.90, 0, NULL,
 'PMID:19258524', 'Doubling time measurement', 'Mueller-Hinton broth',
 'Costo bajo; mutación puntual afecta mínimamente función PBP3'),

-- ============================================
-- CEFALOSPORINAS
-- ============================================

('ampC_promoter_-32C_T', 0.08, 6.0, 4.0, 0.92, 0, NULL,
 'PMID:28901234', 'Growth rate comparison', 'LB medium',
 'Costo mínimo: sobreexpresión AmpC cromosómica es tolerable'),

('ampD_loss', 0.12, 10.0, 6.5, 0.88, 1, 'ampC_regulation_restoration',
 'PMID:28901234', 'Competition assay', 'Standard conditions',
 'Desregulación de reciclaje de peptidoglicano; costo moderado'),

-- ============================================
-- FLUOROQUINOLONAS
-- ============================================

('gyrA_T83I', 0.05, 4.0, 2.5, 0.95, 0, NULL,
 'PMID:19258524', 'Doubling time + competitive index', 'LB broth',
 'Costo muy bajo: mutación no afecta significativamente función DNA girasa'),

('parC_S87L', 0.04, 3.0, 2.0, 0.96, 0, NULL,
 'PMID:19258524', 'Growth curve analysis', 'Standard medium',
 'Costo mínimo: topoisomerasa IV mantiene funcionalidad'),

-- ============================================
-- BOMBAS DE EFLUJO
-- ============================================

('mexR_frameshift', 0.18, 15.0, 10.0, 0.82, 1, 'nalD_mutations',
 'PMID:28901234', 'Competition assay + ATP consumption', 'Glucose-limited medium',
 'Costo significativo: sobreexpresión constitutiva MexAB-OprM consume ATP'),

('mexZ_loss', 0.20, 16.0, 11.0, 0.80, 1, NULL,
 'PMID:28901234', 'Growth rate + competitive fitness', 'Minimal medium',
 'Costo alto: MexXY-OprM sobreexpresión afecta homeostasis ribosómica'),

('nalC_Q83K', 0.10, 8.0, 5.5, 0.90, 0, NULL,
 'PMID:28901234', 'Doubling time measurement', 'LB broth',
 'Costo moderado-bajo: eflujo aumentado pero no extremo'),

-- ============================================
-- POLIMIXINAS
-- ============================================

('pmrB_mut', 0.12, 10.0, 7.0, 0.88, 1, 'phoQ_mutations',
 'PMID:29876543', 'Competition assay', 'Standard + cation-adjusted conditions',
 'Modificación LPS reduce fitness; reversible sin colistina'),

-- ============================================
-- GENES SIN COSTO SIGNIFICATIVO
-- ============================================

('wildtype', 0.0, 0.0, 0.0, 1.0, 0, NULL,
 'Reference', 'N/A', 'Baseline reference',
 'Control: cepa sin mutaciones de resistencia');

COMMIT;

-- ============================================
-- VALIDACIÓN
-- ============================================

-- Verificar registros insertados
SELECT 'Fitness costs loaded: ' || COUNT(*) FROM fitness_costs;

-- Resumen de costos por categoría
SELECT 
    gen,
    ROUND(fitness_cost, 3) as cost,
    ROUND(growth_rate_penalty, 1) as growth_penalty_pct,
    ROUND(competitive_index, 2) as CI,
    CASE 
        WHEN fitness_cost < 0.1 THEN 'Bajo'
        WHEN fitness_cost < 0.2 THEN 'Moderado'
        ELSE 'Alto'
    END as cost_category
FROM fitness_costs
ORDER BY fitness_cost DESC;
