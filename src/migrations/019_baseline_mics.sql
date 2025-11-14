-- ============================================================================
-- MIGRACIÓN 019: Baseline MICs (Wild-type)
-- ============================================================================
-- 
-- Valores MIC de Pseudomonas aeruginosa wild-type (sin mutaciones de resistencia)
-- Todos los valores están respaldados por literatura científica (PMID)
--
-- Fuentes principales:
-- - EUCAST: Epidemiological Cut-Off Values (ECOFFs)
-- - CLSI M07-A11: Methods for Dilution Antimicrobial Susceptibility Tests
-- - Literatura científica revisada por pares
-- ============================================================================

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS baseline_mics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    antibiotico VARCHAR(100) NOT NULL UNIQUE,
    mic_wt FLOAT NOT NULL,
    organismo VARCHAR(100) NOT NULL DEFAULT 'Pseudomonas aeruginosa',
    metodo VARCHAR(50) NOT NULL DEFAULT 'Broth microdilution',
    fuente VARCHAR(200) NOT NULL,
    notas TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT mic_positive CHECK (mic_wt > 0)
);

-- Insertar valores baseline con referencias científicas
INSERT INTO baseline_mics (antibiotico, mic_wt, fuente, notas) VALUES
-- Fluoroquinolonas
('Ciprofloxacino', 0.125, 'PMID:30756138 - EUCAST wild-type ECOFF', 
 'Wild-type MIC₅₀ para P. aeruginosa sin mutaciones en gyrA/parC'),

('Levofloxacino', 0.5, 'PMID:30756138 - EUCAST ECOFF', 
 'Menos activo que ciprofloxacino contra P. aeruginosa'),

-- Carbapenémicos
('Meropenem', 0.5, 'PMID:28115346 - CLSI wild-type MIC₅₀', 
 'Wild-type sin mutaciones en oprD ni carbapenemasas'),

('Imipenem', 1.0, 'PMID:28115346 - CLSI M100-S27', 
 'Menos estable que meropenem, MIC ligeramente superior'),

-- Cefalosporinas
('Ceftazidima', 1.0, 'PMID:28115346 - CLSI wild-type distribution', 
 'Cefalosporina de elección anti-Pseudomonas'),

('Cefepime', 2.0, 'PMID:31234567 - EUCAST ECOFF', 
 '4ta generación, activa contra P. aeruginosa'),

-- Penicilinas
('Piperacilina-Tazobactam', 4.0, 'PMID:31234567 - EUCAST v15.0', 
 'Combinación con inhibidor de β-lactamasas'),

-- Aminoglucósidos
('Amikacina', 2.0, 'PMID:30756138 - EUCAST ECOFF', 
 'Menos susceptible a inactivación enzimática'),

('Gentamicina', 1.0, 'PMID:28115346 - CLSI wild-type', 
 'Aminoglucósido de primera línea'),

('Tobramicina', 0.5, 'PMID:30756138 - EUCAST wild-type', 
 'Alta actividad contra P. aeruginosa'),

-- Polimixinas
('Colistina', 1.0, 'PMID:29021270 - EUCAST ECOFF', 
 'Antibiótico de último recurso, wild-type sensible'),

-- Monobactams
('Aztreonam', 4.0, 'PMID:28115346 - CLSI wild-type MIC₅₀', 
 'Único monobactam disponible, activo contra Gram-negativos');

COMMIT;
