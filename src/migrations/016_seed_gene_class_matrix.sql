-- Migración 016: Seed de Matriz Gen × Clase (Multiplicadores MIC)
-- Fecha de generación: 10 de noviembre de 2025
-- Fuente: matriz_genes_x_clases_MIC_multiplicadores_LONG_utf8_bom.csv
-- Referencias: CARD, ResFinder, NCBI AMR, publicaciones PMID

-- Genes documentados (11):
--   • ampC_promoter_-32C_T
--   • ampD_loss
--   • blaVIM_or_blaIMP
--   • ftsI_PBP3_insertion_YRIN
--   • gyrA_T83I
--   • mexR_frameshift
--   • mexZ_loss
--   • nalC_Q83K
--   • oprD_loss
--   • parC_S87L
--   • pmrB_mut

-- Clases de antibióticos (10):
--   • aminoglucosidos: Amikacina, Tobramicina
--   • carbapenemicos: Meropenem, Imipenem, Doripenem
--   • cef_3G_ceftazidima: Ceftazidima
--   • cef_4G_cefepime: Cefepime
--   • cef_inhibidor: Ceftazidima/Avibactam, Ceftolozano/Tazobactam
--   • fluoroquinolonas: Ciprofloxacino, Levofloxacino
--   • monobactam_aztreonam: Aztreonam
--   • penicilina_inhibidor: Piperacilina/Tazobactam
--   • polimixinas: Colistina
--   • sideroforo_cefiderocol: Cefiderocol

-- ============================================
-- TABLA: gene_class_multipliers
-- ============================================

CREATE TABLE IF NOT EXISTS gene_class_multipliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gen TEXT NOT NULL,                      -- Nombre del gen mutado
    clase_antibiotico TEXT NOT NULL,        -- Clase de antibiótico afectada
    multiplicador_mic REAL NOT NULL,        -- Factor de incremento MIC (1.0 = sin efecto)
    UNIQUE(gen, clase_antibiotico)
);

-- ============================================
-- MULTIPLICADORES POR CLASE
-- ============================================

-- Clase: aminoglucosidos (Amikacina, Tobramicina)
-- Genes con efecto (multiplicador > 1.0): 1
--   mexZ_loss: ×4.0

INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('gyrA_T83I', 'aminoglucosidos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('parC_S87L', 'aminoglucosidos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('oprD_loss', 'aminoglucosidos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampC_promoter_-32C_T', 'aminoglucosidos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampD_loss', 'aminoglucosidos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexR_frameshift', 'aminoglucosidos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('nalC_Q83K', 'aminoglucosidos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexZ_loss', 'aminoglucosidos', 4.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ftsI_PBP3_insertion_YRIN', 'aminoglucosidos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('blaVIM_or_blaIMP', 'aminoglucosidos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('pmrB_mut', 'aminoglucosidos', 1.0);

-- Clase: carbapenemicos (Meropenem, Imipenem, Doripenem)
-- Genes con efecto (multiplicador > 1.0): 3
--   oprD_loss: ×8.0
--   ftsI_PBP3_insertion_YRIN: ×2.0
--   blaVIM_or_blaIMP: ×16.0

INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('gyrA_T83I', 'carbapenemicos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('parC_S87L', 'carbapenemicos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('oprD_loss', 'carbapenemicos', 8.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampC_promoter_-32C_T', 'carbapenemicos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampD_loss', 'carbapenemicos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexR_frameshift', 'carbapenemicos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('nalC_Q83K', 'carbapenemicos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexZ_loss', 'carbapenemicos', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ftsI_PBP3_insertion_YRIN', 'carbapenemicos', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('blaVIM_or_blaIMP', 'carbapenemicos', 16.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('pmrB_mut', 'carbapenemicos', 1.0);

-- Clase: cef_3G_ceftazidima (Ceftazidima)
-- Genes con efecto (multiplicador > 1.0): 5
--   ampC_promoter_-32C_T: ×4.0
--   ampD_loss: ×8.0
--   mexR_frameshift: ×2.0
--   ftsI_PBP3_insertion_YRIN: ×2.0
--   blaVIM_or_blaIMP: ×16.0

INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('gyrA_T83I', 'cef_3G_ceftazidima', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('parC_S87L', 'cef_3G_ceftazidima', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('oprD_loss', 'cef_3G_ceftazidima', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampC_promoter_-32C_T', 'cef_3G_ceftazidima', 4.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampD_loss', 'cef_3G_ceftazidima', 8.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexR_frameshift', 'cef_3G_ceftazidima', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('nalC_Q83K', 'cef_3G_ceftazidima', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexZ_loss', 'cef_3G_ceftazidima', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ftsI_PBP3_insertion_YRIN', 'cef_3G_ceftazidima', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('blaVIM_or_blaIMP', 'cef_3G_ceftazidima', 16.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('pmrB_mut', 'cef_3G_ceftazidima', 1.0);

-- Clase: cef_4G_cefepime (Cefepime)
-- Genes con efecto (multiplicador > 1.0): 5
--   ampC_promoter_-32C_T: ×4.0
--   ampD_loss: ×8.0
--   mexR_frameshift: ×2.0
--   ftsI_PBP3_insertion_YRIN: ×2.0
--   blaVIM_or_blaIMP: ×16.0

INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('gyrA_T83I', 'cef_4G_cefepime', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('parC_S87L', 'cef_4G_cefepime', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('oprD_loss', 'cef_4G_cefepime', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampC_promoter_-32C_T', 'cef_4G_cefepime', 4.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampD_loss', 'cef_4G_cefepime', 8.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexR_frameshift', 'cef_4G_cefepime', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('nalC_Q83K', 'cef_4G_cefepime', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexZ_loss', 'cef_4G_cefepime', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ftsI_PBP3_insertion_YRIN', 'cef_4G_cefepime', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('blaVIM_or_blaIMP', 'cef_4G_cefepime', 16.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('pmrB_mut', 'cef_4G_cefepime', 1.0);

-- Clase: cef_inhibidor (Ceftazidima/Avibactam, Ceftolozano/Tazobactam)
-- Genes con efecto (multiplicador > 1.0): 3
--   ampD_loss: ×2.0
--   ftsI_PBP3_insertion_YRIN: ×2.0
--   blaVIM_or_blaIMP: ×16.0

INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('gyrA_T83I', 'cef_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('parC_S87L', 'cef_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('oprD_loss', 'cef_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampC_promoter_-32C_T', 'cef_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampD_loss', 'cef_inhibidor', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexR_frameshift', 'cef_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('nalC_Q83K', 'cef_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexZ_loss', 'cef_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ftsI_PBP3_insertion_YRIN', 'cef_inhibidor', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('blaVIM_or_blaIMP', 'cef_inhibidor', 16.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('pmrB_mut', 'cef_inhibidor', 1.0);

-- Clase: fluoroquinolonas (Ciprofloxacino, Levofloxacino)
-- Genes con efecto (multiplicador > 1.0): 4
--   gyrA_T83I: ×8.0
--   parC_S87L: ×4.0
--   mexR_frameshift: ×4.0
--   nalC_Q83K: ×2.0

INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('gyrA_T83I', 'fluoroquinolonas', 8.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('parC_S87L', 'fluoroquinolonas', 4.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('oprD_loss', 'fluoroquinolonas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampC_promoter_-32C_T', 'fluoroquinolonas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampD_loss', 'fluoroquinolonas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexR_frameshift', 'fluoroquinolonas', 4.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('nalC_Q83K', 'fluoroquinolonas', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexZ_loss', 'fluoroquinolonas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ftsI_PBP3_insertion_YRIN', 'fluoroquinolonas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('blaVIM_or_blaIMP', 'fluoroquinolonas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('pmrB_mut', 'fluoroquinolonas', 1.0);

-- Clase: monobactam_aztreonam (Aztreonam)
-- Genes con efecto (multiplicador > 1.0): 3
--   ampC_promoter_-32C_T: ×2.0
--   ampD_loss: ×4.0
--   ftsI_PBP3_insertion_YRIN: ×2.0

INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('gyrA_T83I', 'monobactam_aztreonam', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('parC_S87L', 'monobactam_aztreonam', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('oprD_loss', 'monobactam_aztreonam', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampC_promoter_-32C_T', 'monobactam_aztreonam', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampD_loss', 'monobactam_aztreonam', 4.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexR_frameshift', 'monobactam_aztreonam', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('nalC_Q83K', 'monobactam_aztreonam', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexZ_loss', 'monobactam_aztreonam', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ftsI_PBP3_insertion_YRIN', 'monobactam_aztreonam', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('blaVIM_or_blaIMP', 'monobactam_aztreonam', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('pmrB_mut', 'monobactam_aztreonam', 1.0);

-- Clase: penicilina_inhibidor (Piperacilina/Tazobactam)
-- Genes con efecto (multiplicador > 1.0): 4
--   ampC_promoter_-32C_T: ×2.0
--   ampD_loss: ×4.0
--   mexR_frameshift: ×2.0
--   ftsI_PBP3_insertion_YRIN: ×2.0

INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('gyrA_T83I', 'penicilina_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('parC_S87L', 'penicilina_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('oprD_loss', 'penicilina_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampC_promoter_-32C_T', 'penicilina_inhibidor', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampD_loss', 'penicilina_inhibidor', 4.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexR_frameshift', 'penicilina_inhibidor', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('nalC_Q83K', 'penicilina_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexZ_loss', 'penicilina_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ftsI_PBP3_insertion_YRIN', 'penicilina_inhibidor', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('blaVIM_or_blaIMP', 'penicilina_inhibidor', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('pmrB_mut', 'penicilina_inhibidor', 1.0);

-- Clase: polimixinas (Colistina)
-- Genes con efecto (multiplicador > 1.0): 1
--   pmrB_mut: ×8.0

INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('gyrA_T83I', 'polimixinas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('parC_S87L', 'polimixinas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('oprD_loss', 'polimixinas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampC_promoter_-32C_T', 'polimixinas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampD_loss', 'polimixinas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexR_frameshift', 'polimixinas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('nalC_Q83K', 'polimixinas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexZ_loss', 'polimixinas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ftsI_PBP3_insertion_YRIN', 'polimixinas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('blaVIM_or_blaIMP', 'polimixinas', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('pmrB_mut', 'polimixinas', 8.0);

-- Clase: sideroforo_cefiderocol (Cefiderocol)
-- Genes con efecto (multiplicador > 1.0): 1
--   blaVIM_or_blaIMP: ×2.0

INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('gyrA_T83I', 'sideroforo_cefiderocol', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('parC_S87L', 'sideroforo_cefiderocol', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('oprD_loss', 'sideroforo_cefiderocol', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampC_promoter_-32C_T', 'sideroforo_cefiderocol', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ampD_loss', 'sideroforo_cefiderocol', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexR_frameshift', 'sideroforo_cefiderocol', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('nalC_Q83K', 'sideroforo_cefiderocol', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('mexZ_loss', 'sideroforo_cefiderocol', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('ftsI_PBP3_insertion_YRIN', 'sideroforo_cefiderocol', 1.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('blaVIM_or_blaIMP', 'sideroforo_cefiderocol', 2.0);
INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
('pmrB_mut', 'sideroforo_cefiderocol', 1.0);

-- ============================================
-- TABLA: antibiotic_classes (Mapeo)
-- ============================================

CREATE TABLE IF NOT EXISTS antibiotic_classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    antibiotico TEXT NOT NULL,
    clase TEXT NOT NULL,                     -- FK a gene_class_multipliers.clase_antibiotico
    UNIQUE(antibiotico)
);

-- Mapeo Antibiótico → Clase

INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Amikacina', 'aminoglucosidos');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Tobramicina', 'aminoglucosidos');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Meropenem', 'carbapenemicos');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Imipenem', 'carbapenemicos');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Doripenem', 'carbapenemicos');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Ceftazidima', 'cef_3G_ceftazidima');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Cefepime', 'cef_4G_cefepime');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Ceftazidima/Avibactam', 'cef_inhibidor');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Ceftolozano/Tazobactam', 'cef_inhibidor');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Ciprofloxacino', 'fluoroquinolonas');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Levofloxacino', 'fluoroquinolonas');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Aztreonam', 'monobactam_aztreonam');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Piperacilina/Tazobactam', 'penicilina_inhibidor');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Colistina', 'polimixinas');
INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
('Cefiderocol', 'sideroforo_cefiderocol');

-- ============================================
-- VALIDACIÓN CIENTÍFICA
-- ============================================

-- 1. Verificar total de combinaciones gen × clase
-- SELECT COUNT(*) FROM gene_class_multipliers;
-- Debe retornar: 110

-- 2. Genes críticos en carbapenem (alta resistencia)
-- SELECT gen, multiplicador_mic FROM gene_class_multipliers
-- WHERE clase_antibiotico='carbapenemicos' AND multiplicador_mic > 1
-- ORDER BY multiplicador_mic DESC;
-- Debe retornar: blaVIM_or_blaIMP (16.0), oprD_loss (8.0), ftsI_PBP3_insertion_YRIN (2.0)

-- 3. Genes críticos en fluoroquinolonas
-- SELECT gen, multiplicador_mic FROM gene_class_multipliers
-- WHERE clase_antibiotico='fluoroquinolonas' AND multiplicador_mic > 1
-- ORDER BY multiplicador_mic DESC;
-- Debe retornar: gyrA_T83I (8.0), parC_S87L (4.0), mexR_frameshift (4.0), nalC_Q83K (2.0)

-- 4. Verificar mapeo antibióticos → clases
-- SELECT antibiotico, clase FROM antibiotic_classes ORDER BY clase, antibiotico;
-- Debe retornar: 15 filas

-- 5. Ejemplo de cálculo MIC con acumulación (oprD_loss + blaVIM en Meropenem)
-- SELECT g.gen, g.multiplicador_mic
-- FROM gene_class_multipliers g
-- JOIN antibiotic_classes a ON a.clase = g.clase_antibiotico
-- WHERE a.antibiotico = 'Meropenem' AND g.gen IN ('oprD_loss', 'blaVIM_or_blaIMP');
-- Debe retornar: oprD_loss (8.0), blaVIM_or_blaIMP (16.0)
-- Cálculo: MIC_base (0.5) × 8 × 16 = 64 µg/mL (Resistente)