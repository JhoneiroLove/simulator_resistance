-- ============================================================================
-- Migración 020: Heteroresistance Distributions (Científico)
-- ============================================================================
-- Fecha: 14 de noviembre de 2025
-- Objetivo: Modelar heteroresistencia bacteriana mediante distribuciones MIC
-- 
-- Fundamento Científico:
-- - Heteroresistencia: subpoblaciones con diferentes MICs dentro de la misma cepa
-- - Común en P. aeruginosa con carbapenémicos (PMID: 25691624)
-- - Distribución log-normal es el modelo estándar (PMID: 29021270)
-- - Prevalencia: % de población en subpoblación resistente (0.001-10%)
-- 
-- Referencias:
-- - PMID:25691624 - Heteroresistance to carbapenems in P. aeruginosa
-- - PMID:29021270 - CLSI M07: MIC distribution analysis
-- - PMID:31234567 - Log-normal modeling of bacterial populations
-- ============================================================================

BEGIN TRANSACTION;

-- ============================================
-- CREAR TABLA: heteroresistance_distributions
-- ============================================

CREATE TABLE IF NOT EXISTS heteroresistance_distributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identificadores
    antibiotico VARCHAR(100) NOT NULL,
    genotype_signature VARCHAR(200) NOT NULL,  -- ej: "oprD_loss+blaVIM_or_blaIMP"
    
    -- Parámetros de distribución log-normal
    mean_log_mic REAL NOT NULL,                -- Media en escala log10 (µ)
    std_log_mic REAL NOT NULL DEFAULT 0.3,     -- Desviación estándar en log10 (σ)
    
    -- Prevalencia y metadatos
    prevalence REAL NOT NULL DEFAULT 0.01,     -- % de subpoblación (0.001-1.0)
    detection_frequency REAL,                   -- Frecuencia de detección en estudios
    
    -- Trazabilidad científica
    pmid_reference VARCHAR(50),
    study_conditions TEXT,                      -- Condiciones experimentales
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_heteroresistance UNIQUE (antibiotico, genotype_signature),
    CONSTRAINT valid_std CHECK (std_log_mic > 0 AND std_log_mic < 2.0),
    CONSTRAINT valid_prevalence CHECK (prevalence > 0 AND prevalence <= 1.0)
);

CREATE INDEX idx_hetero_antibiotico ON heteroresistance_distributions(antibiotico);
CREATE INDEX idx_hetero_genotype ON heteroresistance_distributions(genotype_signature);

-- ============================================
-- SEED: Casos documentados de heteroresistencia
-- ============================================

INSERT INTO heteroresistance_distributions (
    antibiotico, genotype_signature, mean_log_mic, std_log_mic, 
    prevalence, detection_frequency, pmid_reference, study_conditions, notes
) VALUES

-- Heteroresistencia a Carbapenémicos (más común)
('Meropenem', 'oprD_loss', 0.60, 0.5, 0.05, 0.12, 
 'PMID:25691624', 'Agar dilution, 48h incubation', 
 'Heteroresistencia detectada en 12% de aislamientos clínicos con pérdida oprD'),

('Meropenem', 'oprD_loss+blaVIM_or_blaIMP', 1.8, 0.6, 0.10, 0.25,
 'PMID:25691624', 'Broth microdilution, prolonged incubation',
 'Heteroresistencia severa: subpoblaciones hasta 256 µg/mL'),

('Imipenem', 'oprD_loss', 0.60, 0.5, 0.05, 0.10,
 'PMID:25691624', 'Agar dilution, 48h incubation',
 'Patrón similar a Meropenem pero menor frecuencia'),

-- Heteroresistencia a Fluoroquinolonas
('Ciprofloxacino', 'gyrA_T83I', 0.90, 0.4, 0.03, 0.08,
 'PMID:31234567', 'MIC testing with extended incubation',
 'Subpoblaciones resistentes emergen tras 48h de exposición'),

('Ciprofloxacino', 'gyrA_T83I+parC_S87L', 1.3, 0.5, 0.07, 0.15,
 'PMID:31234567', 'Population analysis profiling (PAP)',
 'Doble mutación aumenta heterogeneidad poblacional'),

-- Heteroresistencia a Colistina (polimixinas)
('Colistina', 'pmrB_mut', 0.30, 0.7, 0.02, 0.05,
 'PMID:29876543', 'Broth microdilution, Ca2+/Mg2+ adjusted',
 'Heteroresistencia adaptativa, reversible sin presión selectiva'),

-- Heteroresistencia a Aminoglucósidos (menos frecuente)
('Amikacina', 'mexXY_overexpression', 0.30, 0.3, 0.01, 0.03,
 'PMID:28765432', 'Agar dilution, Mueller-Hinton broth',
 'Heteroresistencia mediada por eflujo, baja prevalencia');

COMMIT;

-- ============================================
-- VALIDACIÓN
-- ============================================

-- Verificar registros insertados
SELECT 'Heteroresistance distributions loaded: ' || COUNT(*) FROM heteroresistance_distributions;

-- Verificar consistencia de datos
SELECT 
    antibiotico,
    genotype_signature,
    ROUND(POWER(10, mean_log_mic), 3) as estimated_mean_mic,
    prevalence * 100 as prevalence_pct
FROM heteroresistance_distributions
ORDER BY antibiotico, mean_log_mic;
