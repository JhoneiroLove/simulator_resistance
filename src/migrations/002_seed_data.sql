BEGIN TRANSACTION;

-- -------------- Genes --------------
INSERT OR IGNORE INTO genes (nombre, peso_resistencia, descripcion) VALUES
  ('blaVIM',       2.5, 'Metalobetalactamasa tipo VIM'),
  ('mexAB-oprM',   1.8, 'Bomba de eflujo MexAB-OprM'),
  ('ndm1',         2.2, 'Carbapenemasa NDM-1'),
  ('oxa48',        1.9, 'Oxacilinasa OXA-48'),
  ('armA',         1.5, 'Metilasa de rRNA ArmA'),
  ('kpc',          2.4, 'Klebsiella pneumoniae carbapenemasa'),
  ('mcr1',         2.0, 'Modificación de lípidos LPS'),
  ('aac6',         1.7, 'Acetiltransferasa de aminoglucósidos'),
  ('vanA',         1.6, 'Resistencia a vancomicina'),
  ('ermB',         1.4, 'Metilasa de ARN 23S');

-- ----------- Antibióticos -----------
INSERT OR IGNORE INTO antibioticos
  (nombre, concentracion_minima, concentracion_maxima, tipo)
VALUES
  ('Meropenem',     0.125, 16.0,  'Carbapenémico'),
  ('Ciprofloxacino',0.06,  32.0,  'Fluoroquinolona'),
  ('Colistina',     0.5,   64.0,  'Polimixina'),
  ('Amikacina',     1.0,   32.0,  'Aminoglucósido'),
  ('Piperacilina',  4.0,  128.0,  'Penicilina'),
  ('Tigeciclina',   0.25,   8.0,  'Glicilciclina');

COMMIT;