BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS recomendaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    antibiotico_id INTEGER NOT NULL,
    texto TEXT NOT NULL,
    FOREIGN KEY (antibiotico_id) REFERENCES antibioticos(id)
);

-- Recomendaciones clínicas por antibiótico

INSERT INTO recomendaciones (antibiotico_id, texto)
VALUES
-- MEROPENEM
((SELECT id FROM antibioticos WHERE nombre = 'Meropenem'),
'• Evaluar riesgo de carbapenemasa (KPC, NDM, OXA).\n• En caso de resistencia, considerar ceftazidima-avibactam o colistina.\n• Útil como terapia empírica en infecciones nosocomiales graves.'),

-- CIPROFLOXACINO
((SELECT id FROM antibioticos WHERE nombre = 'Ciprofloxacino'),
'• Confirmar susceptibilidad mediante antibiograma.\n• Riesgo de rápida resistencia por sobreexpresión de bombas de eflujo (ej. MexAB-OprM).\n• Evitar uso prolongado; considerar levofloxacino o moxifloxacino en infecciones respiratorias.'),

-- COLISTINA
((SELECT id FROM antibioticos WHERE nombre = 'Colistina'),
'• Considerar como último recurso en cepas multirresistentes.\n• Monitorear función renal por toxicidad.\n• Puede combinarse con carbapenémicos o fosfomicina en terapia dual.'),

-- AMIKACINA
((SELECT id FROM antibioticos WHERE nombre = 'Amikacina'),
'• Alta eficacia frente a enterobacterias resistentes.\n• Útil en combinación con beta-lactámicos o fluoroquinolonas.\n• Riesgo de nefrotoxicidad; usar en ciclos cortos y con monitoreo de niveles plasmáticos.'),

-- PIPERACILINA
((SELECT id FROM antibioticos WHERE nombre = 'Piperacilina'),
'• Combinado con tazobactam es útil contra P. aeruginosa sensible.\n• Menor efectividad frente a beta-lactamasas tipo ESBL y AmpC.\n• Terapia empírica válida en sepsis sin sospecha de BLEE.'),

-- TIGECICLINA
((SELECT id FROM antibioticos WHERE nombre = 'Tigeciclina'),
'• Activa frente a enterobacterias BLEE y algunas carbapenemasa-producidoras.\n• No usar en bacteriemias graves por baja concentración sérica.\n• Opción útil en infecciones intraabdominales y tejidos blandos multirresistentes.');

COMMIT;