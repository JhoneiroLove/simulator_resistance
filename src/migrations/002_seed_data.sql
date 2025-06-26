BEGIN TRANSACTION;

----------------- Genes --------------
INSERT INTO genes (nombre, peso_resistencia, descripcion) VALUES
  ('blaVIM',       2.5, 'Metalobetalactamasa tipo VIM'),
  ('mexAB-oprM',   1.8, 'Bomba de eflujo MexAB-OprM'),
  ('ndm1',         2.2, 'Carbapenemasa NDM-1'),
  ('oxa48',        1.9, 'Oxacilinasa OXA-48'),
  ('armA',         1.5, 'Metilasa de rRNA ArmA'),
  ('kpc',          2.4, 'Klebsiella pneumoniae carbapenemasa'),
  ('mcr1',         2.0, 'Modificación de lípidos LPS'),
  ('aac6',         1.7, 'Acetiltransferasa de aminoglucósidos'),
  ('vanA',         1.6, 'Resistencia a vancomicina'),
  ('ermB',         1.4, 'Metilasa de ARN 23S')

ON CONFLICT(nombre) DO UPDATE SET
  peso_resistencia = excluded.peso_resistencia,
  descripcion = excluded.descripcion;

-------------- Antibióticos + Cita --------------
INSERT INTO antibioticos
  (nombre, concentracion_minima, concentracion_maxima, tipo)
VALUES
  ('Meropenem',      0.03,   64.0,    'Carbapenémico'),
  ('Ciprofloxacino', 0.25,   256.0,    'Fluoroquinolona'),
  ('Colistina',      0.06,   512.0,    'Polimixina'),
  ('Amikacina',      0.5,    512.0,    'Aminoglucósido'),
  ('Piperacilina/Tazobactam', 0.5,   1024.0, 'Penicilina'),
  ('Ceftazidima',    0.25,   1024.0,    'Cefalosporina'),
  ('Gentamicina',    0.5,    512.0,    'Aminoglucósido'),
  ('Tobramicina',    0.25,   1024.0,    'Aminoglucósido'),
  ('Imipenem',       0.12,   128.0,    'Carbapenémico'),
  ('Cefepime',       1.0,    32.0,    'Cefalosporina')

ON CONFLICT(nombre) DO UPDATE SET
  concentracion_minima = excluded.concentracion_minima,
  concentracion_maxima = excluded.concentracion_maxima,
  tipo = excluded.tipo;

COMMIT;