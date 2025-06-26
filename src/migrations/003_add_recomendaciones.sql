BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS recomendaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    antibiotico_id INTEGER NOT NULL,
    texto TEXT NOT NULL,
    FOREIGN KEY (antibiotico_id) REFERENCES antibioticos(id)
);

-- Recomendaciones clínicas por antibiótico

INSERT INTO recomendaciones (antibiotico_id, texto)
SELECT id, '• Evaluar riesgo de carbapenemasa (KPC, NDM, OXA).\n• En caso de resistencia, considerar ceftazidima-avibactam o colistina.\n• Útil como terapia empírica en infecciones nosocomiales graves.'
FROM antibioticos WHERE nombre = 'Meropenem';

INSERT INTO recomendaciones (antibiotico_id, texto)
SELECT id, '• Confirmar susceptibilidad mediante antibiograma.\n• Riesgo de rápida resistencia por sobreexpresión de bombas de eflujo (ej. MexAB-OprM).\n• Evitar uso prolongado; considerar levofloxacino o moxifloxacino en infecciones respiratorias.'
FROM antibioticos WHERE nombre = 'Ciprofloxacino';

INSERT INTO recomendaciones (antibiotico_id, texto)
SELECT id, '• Considerar como último recurso en cepas multirresistentes.\n• Monitorear función renal por toxicidad.\n• Puede combinarse con carbapenémicos o fosfomicina en terapia dual.'
FROM antibioticos WHERE nombre = 'Colistina';

INSERT INTO recomendaciones (antibiotico_id, texto)
SELECT id, '• Alta eficacia frente a enterobacterias resistentes.\n• Útil en combinación con beta-lactámicos o fluoroquinolonas.\n• Riesgo de nefrotoxicidad; usar en ciclos cortos y con monitoreo de niveles plasmáticos.'
FROM antibioticos WHERE nombre = 'Amikacina';

INSERT INTO recomendaciones (antibiotico_id, texto)
SELECT id, '• Combinado con tazobactam es útil contra P. aeruginosa sensible.\n• Menor efectividad frente a beta-lactamasas tipo ESBL y AmpC.\n• Terapia empírica válida en sepsis sin sospecha de BLEE.'
FROM antibioticos WHERE nombre = 'Piperacilina/Tazobactam';

INSERT INTO recomendaciones (antibiotico_id, texto)
SELECT id, '• Activa frente a enterobacterias BLEE y algunas carbapenemasa-producidoras.\n• No usar en bacteriemias graves por baja concentración sérica.\n• Opción útil en infecciones intraabdominales y tejidos blandos multirresistentes.'
FROM antibioticos WHERE nombre = 'Tigeciclina';

COMMIT;