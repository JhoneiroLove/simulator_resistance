-- Migración 015: Seed de Breakpoints (EUCAST v15.0 + CLSI M07)
-- Fecha de generación: 11 de noviembre de 2025
-- Fuentes: 
--   - eucast_pseudomonas_aeruginosa_v15_2025.csv (17 breakpoints EUCAST)
--   - pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv (14 breakpoints CLSI)
-- Total: 31 breakpoints (17 EUCAST primarios + 14 CLSI fallbacks)
-- Nota: Colistina solo tiene breakpoint CLSI (EUCAST no define para P. aeruginosa)
-- Organismo: Pseudomonas aeruginosa (hardcoded)

CREATE TABLE IF NOT EXISTS breakpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    antibiotico TEXT NOT NULL,
    organismo TEXT NOT NULL DEFAULT 'Pseudomonas aeruginosa',
    s_mic REAL NOT NULL,       -- Susceptible si MIC ≤ este valor
    r_mic REAL NOT NULL,       -- Resistente si MIC > este valor
    standard TEXT NOT NULL,    -- 'EUCAST' o 'CLSI'
    fuente TEXT NOT NULL,      -- Referencia oficial
    familia TEXT,              -- Familia antibiótica
    mecanismo TEXT,            -- Mecanismo de acción
    UNIQUE(antibiotico, standard)
);

-- ============================================
-- BREAKPOINTS EUCAST v15.0 (2025) - PRIMARIOS
-- ============================================

INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Piperacilina', 'Pseudomonas aeruginosa', 0.001, 16.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', NULL, NULL);
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Piperacilina/Tazobactam', 'Pseudomonas aeruginosa', 0.001, 16.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'β-lactámico + inhibidor β-lactamasa', 'Inhibe síntesis de pared y bloquea β-lactamasas');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Ticarcilina/Clavulanato', 'Pseudomonas aeruginosa', 0.001, 16.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', NULL, NULL);
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Cefepime', 'Pseudomonas aeruginosa', 0.001, 8.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Cefalosporina (4ta gen)', 'Inhibe síntesis de peptidoglucano');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Ceftazidima', 'Pseudomonas aeruginosa', 8.0, 8.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Cefalosporina (3ra gen)', 'Interfiere en la pared celular bacteriana');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Ceftazidima/Avibactam', 'Pseudomonas aeruginosa', 8.0, 8.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Cefalosporina + inhibidor β-lactamasa', 'Bloquea β-lactamasas clase A y C');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Ceftolozano/Tazobactam', 'Pseudomonas aeruginosa', 4.0, 4.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Cefalosporina + inhibidor β-lactamasa', 'Alta afinidad por PBPs, estable ante AmpC');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Cefiderocol', 'Pseudomonas aeruginosa', 2.0, 2.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Cefalosporina sideróforo', 'Usa transporte dependiente de hierro');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Imipenem', 'Pseudomonas aeruginosa', 2.0, 8.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Carbapenémico', 'Inhibe la síntesis de pared bacteriana');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Meropenem', 'Pseudomonas aeruginosa', 2.0, 8.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Carbapenémico', 'Inhibe la síntesis de pared bacteriana');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Meropenem/Vaborbactam', 'Pseudomonas aeruginosa', 8.0, 8.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', NULL, NULL);
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Aztreonam', 'Pseudomonas aeruginosa', 0.001, 16.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', NULL, NULL);
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Ciprofloxacino', 'Pseudomonas aeruginosa', 0.001, 0.5, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Fluoroquinolona', 'Inhibe ADN girasa y topoisomerasa IV');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Levofloxacino', 'Pseudomonas aeruginosa', 0.001, 2.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Fluoroquinolona', 'Inhibe replicación del ADN bacteriano');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Amikacina', 'Pseudomonas aeruginosa', 16.0, 16.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Aminoglucósido', 'Inhibe síntesis proteica (30S ribosomal)');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Tobramicina', 'Pseudomonas aeruginosa', 2.0, 2.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Aminoglucósido', 'Inhibe síntesis proteica');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Colistina', 'Pseudomonas aeruginosa', 4.0, 4.0, 'EUCAST', 'v_15.0_Breakpoint_Tables.pdf', 'Polimixina', 'Altera la membrana externa bacteriana');

-- ============================================
-- BREAKPOINTS CLSI M07 (2023) - FALLBACKS PARA PANEL DE 15
-- ============================================

-- Carbapenémicos
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Meropenem', 'Pseudomonas aeruginosa', 2.0, 8.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Carbapenémicos', 'Inhibición síntesis pared celular');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Imipenem', 'Pseudomonas aeruginosa', 2.0, 8.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Carbapenémicos', 'Inhibición síntesis pared celular');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Doripenem', 'Pseudomonas aeruginosa', 2.0, 8.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Carbapenémicos', 'Inhibición síntesis pared celular');

-- Cefalosporinas
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Ceftazidima', 'Pseudomonas aeruginosa', 8.0, 32.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Cefalosporinas 3G (Ceftazidima)', 'Inhibición síntesis pared celular');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Cefepime', 'Pseudomonas aeruginosa', 8.0, 32.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Cefalosporinas 4G (Cefepime)', 'Inhibición síntesis pared celular');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Ceftazidima/Avibactam', 'Pseudomonas aeruginosa', 8.0, 16.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Cefalosporinas + Inhibidor β-lactamasa', 'Inhibición síntesis pared + inhibidor enzimático');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Ceftolozano/Tazobactam', 'Pseudomonas aeruginosa', 4.0, 16.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Cefalosporinas + Inhibidor β-lactamasa', 'Inhibición síntesis pared + inhibidor enzimático');

-- Monobactams
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Aztreonam', 'Pseudomonas aeruginosa', 8.0, 32.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Monobactam (Aztreonam)', 'Inhibición síntesis pared celular');

-- Penicilinas + Inhibidor
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Piperacilina/Tazobactam', 'Pseudomonas aeruginosa', 16.0, 64.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Penicilina + Inhibidor β-lactamasa', 'Inhibición síntesis pared + inhibidor enzimático');

-- Aminoglucósidos
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Amikacina', 'Pseudomonas aeruginosa', 16.0, 64.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Aminoglucósidos', 'Inhibición síntesis proteica (30S)');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Tobramicina', 'Pseudomonas aeruginosa', 1.0, 4.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Aminoglucósidos', 'Inhibición síntesis proteica (30S)');

-- Fluoroquinolonas
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Ciprofloxacino', 'Pseudomonas aeruginosa', 0.5, 2.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Fluoroquinolonas', 'Inhibición DNA girasa/topoisomerasa IV');
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Levofloxacino', 'Pseudomonas aeruginosa', 1.0, 4.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Fluoroquinolonas', 'Inhibición DNA girasa/topoisomerasa IV');

-- Polimixinas
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Colistina', 'Pseudomonas aeruginosa', 2.0, 4.0, 'CLSI', 'pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv', 'Polimixinas', 'Disrupción membrana bacteriana');

-- ============================================
-- VALIDACIÓN
-- ============================================
-- Verificar total de breakpoints cargados
-- SELECT COUNT(*) FROM breakpoints WHERE organismo='Pseudomonas aeruginosa';
-- Debe retornar: 31 (17 EUCAST + 14 CLSI)

-- Verificar breakpoints EUCAST (primarios)
-- SELECT antibiotico, s_mic, r_mic FROM breakpoints WHERE standard='EUCAST' ORDER BY antibiotico;
-- Debe retornar: 17 filas

-- Verificar breakpoints CLSI (fallbacks para panel de 15)
-- SELECT antibiotico, s_mic, r_mic FROM breakpoints WHERE standard='CLSI' ORDER BY antibiotico;
-- Debe retornar: 14 filas (13 del panel + Colistina que solo existe en CLSI)

-- Verificar cobertura de panel de 15 antibióticos
-- SELECT DISTINCT antibiotico FROM breakpoints 
-- WHERE antibiotico IN (
--   'Meropenem', 'Imipenem', 'Doripenem',
--   'Ceftazidima', 'Cefepime', 'Ceftazidima/Avibactam', 'Ceftolozano/Tazobactam',
--   'Aztreonam', 'Piperacilina/Tazobactam',
--   'Amikacina', 'Tobramicina',
--   'Ciprofloxacino', 'Levofloxacino',
--   'Colistina', 'Cefiderocol'
-- ) ORDER BY antibiotico;
-- Debe retornar: 15 filas
-- Nota: Cefiderocol solo EUCAST, Colistina solo CLSI, resto tienen ambos estándares