-- Migracion 017: Seed de Panel Layouts (96 Wells)
-- Fecha de generacion: 11 de noviembre de 2025
-- Fuente: pseudomonas_aeruginosa_concentraciones_simuladas.csv

-- Total wells: 93

CREATE TABLE IF NOT EXISTS panel_layouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    panel_name TEXT NOT NULL,
    well_position TEXT NOT NULL,
    antibiotico TEXT,
    concentracion REAL,
    tipo TEXT NOT NULL,
    UNIQUE(panel_name, well_position)
);

-- Amikacina (6 wells): 2.0-64.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F2', 'Amikacina', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F3', 'Amikacina', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F4', 'Amikacina', 8.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F5', 'Amikacina', 16.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F6', 'Amikacina', 32.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F7', 'Amikacina', 64.0, 'test');

-- Cefepime (8 wells): 0.25-32.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B6', 'Cefepime', 0.25, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B7', 'Cefepime', 0.5, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B8', 'Cefepime', 1.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B9', 'Cefepime', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B10', 'Cefepime', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B11', 'Cefepime', 8.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B12', 'Cefepime', 16.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C1', 'Cefepime', 32.0, 'test');

-- Cefiderocol (6 wells): 0.25-8.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G2', 'Cefiderocol', 0.25, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G3', 'Cefiderocol', 0.5, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G4', 'Cefiderocol', 1.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G5', 'Cefiderocol', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G6', 'Cefiderocol', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G7', 'Cefiderocol', 8.0, 'test');

-- Ceftazidima (9 wells): 0.25-64.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A1', 'Ceftazidima', 0.25, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A2', 'Ceftazidima', 0.5, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A3', 'Ceftazidima', 1.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A4', 'Ceftazidima', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A5', 'Ceftazidima', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A6', 'Ceftazidima', 8.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A7', 'Ceftazidima', 16.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A8', 'Ceftazidima', 32.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A9', 'Ceftazidima', 64.0, 'test');

-- Ceftazidima/Avibactam (6 wells): 0.5-16.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G8', 'Ceftazidima/Avibactam', 0.5, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G9', 'Ceftazidima/Avibactam', 1.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G10', 'Ceftazidima/Avibactam', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G11', 'Ceftazidima/Avibactam', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G12', 'Ceftazidima/Avibactam', 8.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'H1', 'Ceftazidima/Avibactam', 16.0, 'test');

-- Ceftolozano/Tazobactam (6 wells): 0.25-8.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'H2', 'Ceftolozano/Tazobactam', 0.25, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'H3', 'Ceftolozano/Tazobactam', 0.5, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'H4', 'Ceftolozano/Tazobactam', 1.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'H5', 'Ceftolozano/Tazobactam', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'H6', 'Ceftolozano/Tazobactam', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'H7', 'Ceftolozano/Tazobactam', 8.0, 'test');

-- Ciprofloxacino (7 wells): 0.06-3.84 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D12', 'Ciprofloxacino', 0.06, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E1', 'Ciprofloxacino', 0.12, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E2', 'Ciprofloxacino', 0.24, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E3', 'Ciprofloxacino', 0.48, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E4', 'Ciprofloxacino', 0.96, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E5', 'Ciprofloxacino', 1.92, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E6', 'Ciprofloxacino', 3.84, 'test');

-- Colistina (7 wells): 0.25-16.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E7', 'Colistina', 0.25, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E8', 'Colistina', 0.5, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E9', 'Colistina', 1.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E10', 'Colistina', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E11', 'Colistina', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'E12', 'Colistina', 8.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F1', 'Colistina', 16.0, 'test');

-- Imipenem (7 wells): 0.25-16.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D5', 'Imipenem', 0.25, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D6', 'Imipenem', 0.5, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D7', 'Imipenem', 1.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D8', 'Imipenem', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D9', 'Imipenem', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D10', 'Imipenem', 8.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D11', 'Imipenem', 16.0, 'test');

-- Levofloxacino (8 wells): 0.06-7.68 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A10', 'Levofloxacino', 0.06, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A11', 'Levofloxacino', 0.12, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'A12', 'Levofloxacino', 0.24, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B1', 'Levofloxacino', 0.48, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B2', 'Levofloxacino', 0.96, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B3', 'Levofloxacino', 1.92, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B4', 'Levofloxacino', 3.84, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'B5', 'Levofloxacino', 7.68, 'test');

-- Meropenem (7 wells): 0.25-16.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C10', 'Meropenem', 0.25, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C11', 'Meropenem', 0.5, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C12', 'Meropenem', 1.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D1', 'Meropenem', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D2', 'Meropenem', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D3', 'Meropenem', 8.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'D4', 'Meropenem', 16.0, 'test');

-- Piperacilina/Tazobactam (8 wells): 1.0-128.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C2', 'Piperacilina/Tazobactam', 1.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C3', 'Piperacilina/Tazobactam', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C4', 'Piperacilina/Tazobactam', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C5', 'Piperacilina/Tazobactam', 8.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C6', 'Piperacilina/Tazobactam', 16.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C7', 'Piperacilina/Tazobactam', 32.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C8', 'Piperacilina/Tazobactam', 64.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'C9', 'Piperacilina/Tazobactam', 128.0, 'test');

-- Tobramicina (6 wells): 0.5-16.0 ug/mL
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F8', 'Tobramicina', 0.5, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F9', 'Tobramicina', 1.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F10', 'Tobramicina', 2.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F11', 'Tobramicina', 4.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'F12', 'Tobramicina', 8.0, 'test');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'G1', 'Tobramicina', 16.0, 'test');

-- Controles QC
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'H11', NULL, NULL, 'control_positivo');
INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', 'H12', NULL, NULL, 'control_negativo');