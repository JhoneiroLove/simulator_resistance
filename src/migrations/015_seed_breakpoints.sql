-- Migración 015: Seed de Breakpoints (EUCAST v15.0 + CLSI M07)
-- Fecha de generación: 10 de noviembre de 2025
-- Fuentes: EUCAST v_15.0_Breakpoint_Tables.pdf, CLSI M07 (2023)
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
-- BREAKPOINTS CLSI M07 (2023) - FALLBACKS
-- ============================================

INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Doripenem', 'Pseudomonas aeruginosa', 2.0, 8.0, 'CLSI', 'bit-part-b-91525-_clsi_vs_fda_breakpoints-1.xlsb :: MIC BP Table', 'Desconocida', NULL);
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Gatifloxacin', 'Pseudomonas aeruginosa', 2.0, 8.0, 'CLSI', 'bit-part-b-91525-_clsi_vs_fda_breakpoints-1.xlsb :: MIC BP Table', 'Desconocida', NULL);
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Lomefloxacin', 'Pseudomonas aeruginosa', 2.0, 8.0, 'CLSI', 'bit-part-b-91525-_clsi_vs_fda_breakpoints-1.xlsb :: MIC BP Table', 'Desconocida', NULL);
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Netilmicin', 'Pseudomonas aeruginosa', 8.0, 32.0, 'CLSI', 'bit-part-b-91525-_clsi_vs_fda_breakpoints-1.xlsb :: MIC BP Table', 'Desconocida', NULL);
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Norfloxacin', 'Pseudomonas aeruginosa', 4.0, 16.0, 'CLSI', 'bit-part-b-91525-_clsi_vs_fda_breakpoints-1.xlsb :: MIC BP Table', 'Desconocida', NULL);
INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES
('Ofloxacin', 'Pseudomonas aeruginosa', 2.0, 8.0, 'CLSI', 'bit-part-b-91525-_clsi_vs_fda_breakpoints-1.xlsb :: MIC BP Table', 'Desconocida', NULL);

-- ============================================
-- VALIDACIÓN
-- ============================================
-- Verificar total de breakpoints cargados
-- SELECT COUNT(*) FROM breakpoints WHERE organismo='Pseudomonas aeruginosa';
-- Debe retornar: 23

-- Verificar breakpoints EUCAST (primarios)
-- SELECT antibiotico, s_mic, r_mic FROM breakpoints WHERE standard='EUCAST' ORDER BY antibiotico;
-- Debe retornar: 17 filas

-- Verificar breakpoints CLSI (fallbacks)
-- SELECT antibiotico FROM breakpoints WHERE standard='CLSI' ORDER BY antibiotico;
-- Debe retornar: 6 filas